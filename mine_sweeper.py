import tkinter as tk
from random import shuffle
import os
import queue

# installs pygame if you don't have it yet
try:
    import pygame
except ModuleNotFoundError:
    os.system("pip install pygame --pre")

# global settings for the game
SETTINGS = {}
WIDTH, HEIGHT = 700, 700
TILE_WIDTH, TILE_HEIGHT = 10, 10

# color tuples
BG_COLOR = (100, 100, 100)
VISIBLE_TILE_COLOR = (210, 210, 210)
HIDDEN_TILE_COLOR = (140, 140, 140)
BLACK = (0, 0, 0)

# necessary for font
pygame.init()


# a basic class for every tile
class Tile:
    # static variables to keep track of how many things are on board
    numOfMinesFlagged = 0
    numOfHiddenTiles = 0
    numOfFlagsOnBoard = 0
    
    
    def __init__(self, x, y, isMine, numOfMinesAround, mineImg, flagImg, font):
        self.x = x
        self.y = y
        self.isMine = isMine
        self.isVisible = False
        self.isFlag = False
        self.numOfMinesAround = numOfMinesAround
        self.mineImg = mineImg
        self.flagImg = flagImg
        self.font = font

        Tile.numOfHiddenTiles += 1
        
    def draw(self, WIN):
        # set the color of a tile to hidden/visible
        if self.isVisible:
            color = VISIBLE_TILE_COLOR
        else:
            color = HIDDEN_TILE_COLOR
        pygame.draw.rect(WIN, color, (self.x*TILE_WIDTH, self.y*TILE_HEIGHT, TILE_WIDTH-2, TILE_HEIGHT-2))
        
        # draw a mine if the tile is visible
        if self.isVisible:
            if self.isMine:
                WIN.blit(self.mineImg, (self.x * TILE_WIDTH + TILE_WIDTH / 2 - self.mineImg.get_width() / 2, self.y * TILE_HEIGHT + TILE_HEIGHT / 2 - self.mineImg.get_height() / 2))
            
            # print a number of neighboring mines
            elif self.numOfMinesAround != 0:
                textWidth, textHeight = self.font.size(f"{self.numOfMinesAround}")
                WIN.blit(self.font.render(f"{self.numOfMinesAround}", True, BLACK), (self.x * TILE_WIDTH + TILE_WIDTH / 2 - textWidth / 2, self.y * TILE_HEIGHT + TILE_HEIGHT / 2 - textHeight / 2))
                
        # draw flag
        else:
            if self.isFlag:
                WIN.blit(self.flagImg, (self.x * TILE_WIDTH + TILE_WIDTH / 2 - self.flagImg.get_width() / 2, self.y * TILE_HEIGHT + TILE_HEIGHT / 2 - self.flagImg.get_height() / 2))
                
    
    def setVisible(self):
        self.isVisible = True
        Tile.numOfHiddenTiles -= 1
    
    # show/hide flag
    # keep track of how many flags are on board
    def toggleFlag(self):
        if self.isFlag:
            Tile.numOfFlagsOnBoard -= 1
            self.isFlag = False
        elif not self.isFlag and Tile.numOfFlagsOnBoard < SETTINGS["numOfMines"]:
            Tile.numOfFlagsOnBoard += 1
            self.isFlag = True
            
        #keep track of how many mines are flagged
        if self.isFlag and self.isMine:
            Tile.numOfMinesFlagged += 1
        elif not self.isFlag and self.isMine:
            Tile.numOfMinesFlagged -= 1
    
    def getNeighbors(self):
        return self.numOfMinesAround


# the first window where you select the settings
def settings():
    
    # gets called after you press the button
    # sets the values of width, height and number of mines
    def start_the_game(root, width, height, numOfMines, mode):
        # modes:
        # none - user inputs width, height and num of mines
        # easy - 8x8x10
        # normal - 16x16x40
        # hard - 25x25x100
        if mode == "none":
            try:
                width = int(width)
                height = int(height)
                numOfMines = int(numOfMines)
            except ValueError:
                return
            else:
                if width < 2 or height < 2 or numOfMines < 0 or numOfMines > width * height:
                    return
        elif mode == "easy":
            width = 8
            height = 8
            numOfMines = 10
        elif mode == "medium":
            width = 16
            height = 16
            numOfMines = 40
        elif mode == "hard":
            width = 25
            height = 25
            numOfMines = 100
        
        SETTINGS["width"] = width
        SETTINGS["height"] = height
        SETTINGS["numOfMines"] = numOfMines
        
        root.destroy()
    
    root = tk.Tk()
    root.title("Settings")

    main_font = ("Arial", 15)
    smaller_font = ("Arial", 13, "italic")

    # width label
    tk.Label(text="Enter width:", font=main_font).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
    widthEntry = tk.Entry(root, font=main_font)
    widthEntry.grid(row=0, column=1, padx=10, pady=10, ipady=2, sticky=tk.W)

    # height label
    tk.Label(text="Enter height:", font=main_font).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
    heightEntry = tk.Entry(root, font=main_font)
    heightEntry.grid(row=1, column=1, padx=10, pady=10, ipady=2, sticky=tk.W)
    
    # numOfMines label
    tk.Label(text="How many mines?:", font=main_font).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
    minesEntry = tk.Entry(root, font=main_font)
    minesEntry.grid(row=2, column=1, padx=10, pady=10, ipady=2, sticky=tk.W)

    tk.Label(text="").grid(row=3, column=0)
    tk.Label(text="Or choose one of those:", font=main_font).grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)

    # mode buttons
    modeVar = tk.StringVar(value="none")
    tk.Radiobutton(root, text="Easy: 8x8x10", variable=modeVar, value="easy", font=smaller_font).grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
    tk.Radiobutton(root, text="Medium: 16x16x40", variable=modeVar, value="medium", font=smaller_font).grid(row=6, column=0, padx=10, pady=10, sticky=tk.W)
    tk.Radiobutton(root, text="Hard: 25x25x100", variable=modeVar, value="hard", font=smaller_font).grid(row=7, column=0, padx=10, pady=10, sticky=tk.W)

    # start button
    tk.Button(text="Start", font=main_font, command=lambda: start_the_game(root, widthEntry.get(), heightEntry.get(), minesEntry.get(), modeVar.get())).grid(row=11, column=0, columnspan=2, padx=10, pady=10, ipadx=30, ipady=10)

    root.mainloop()

# function draws tiles on the window
def draw(board, WIN):
    WIN.fill(BG_COLOR)
    for row in board:
        for tile in row:
            tile.draw(WIN)
    pygame.display.update()

# function calculates how many mines are around the clicked tile
def num_of_mines_around(board, y, x):
    # 1.(x-1,y-1)     2.(x,y-1)     3.(x+1,y-1)
    # 8.(x-1,y)         (x,y)       4.(x+1,y)
    # 7.(x-1,y+1)     6.(x,y+1)     5.(x+1,y+1)
    
    numOfMines = 0
    
    if x > 0 and y > 0:
        if board[y-1][x-1] == "*":
            numOfMines += 1
    
    if y > 0:
        if board[y-1][x] == "*":
            numOfMines += 1
    
    try:
        board[y-1][x+1]
    except IndexError:
        pass
    else:
        if y > 0:
            if board[y-1][x+1] == "*":
                numOfMines += 1
    
    try:
        board[y][x+1]
    except IndexError:
        pass
    else:
        if board[y][x+1] == "*":
            numOfMines += 1
    
    try:
        board[y+1][x+1]
    except IndexError:
        pass
    else:
        if board[y+1][x+1] == "*":
            numOfMines += 1
    
    try:
        board[y+1][x]
    except IndexError:
        pass
    else:
        if board[y+1][x] == "*":
            numOfMines += 1
    
    try:
        board[y+1][x-1]
    except IndexError:
        pass
    else:
        if board[y+1][x-1] == "*":
            numOfMines += 1
    
    if x > 0:
        if board[y][x-1] == "*":
            numOfMines += 1
    
    return numOfMines

# function finds all neighboring tiles that have no mines around them
def find_neighbors(board, x, y):
    #           (x,y-1)
    # (x-1,y)               (x+1,y)
    #           (x,y+1)
    
    neighbors = []
    
    if y > 0:
        if not board[y-1][x].isMine and board[y-1][x].getNeighbors() == 0:
            neighbors.append((x, y-1))
    
    try:
        board[y][x+1]
    except IndexError:
        pass
    else:
        if not board[y][x+1].isMine and board[y][x+1].getNeighbors() == 0:
            neighbors.append((x+1, y))
    
    try:
        board[y+1][x]
    except IndexError:
        pass
    else:
        if not board[y+1][x].isMine and board[y+1][x].getNeighbors() == 0:
            neighbors.append((x, y+1))
    
    if x > 0:
        if not board[y][x-1].isMine and board[y][x-1].getNeighbors() == 0:
            neighbors.append((x-1, y))
    
    return neighbors

# breadth first search algorithm for finding all neighboring tiles with no mines around
def set_neighbors_visible(board, startX, startY):
    visited = []
    q = queue.Queue()
    q.put((startX, startY))
    
    while not q.empty():
        current_pos = q.get()
        x, y = current_pos
        
        neighbors = find_neighbors(board, x, y)
        for neighbor in neighbors:
            if neighbor in visited:
                continue
            
            q.put((neighbor))
            visited.append(neighbor)
    
    for tileX, tileY in visited:
        board[tileY][tileX].setVisible()

# gets called every time a mouse is clicked
def mouse_clicked(board, mouse_pos, button):
    # button 0 - Left Mouse Button
    # button 1 - Middle Mouse Button (scroll)
    # button 2 - Right Mouse Button
    if not button[0] and not button[2]:
        return
    
    leftMouseButton = button[0]
    rightMouseButton = button[2]
    
    # sets the x and y coordinate of the mouse
    mouseX = mouse_pos[0] // TILE_WIDTH
    mouseY = mouse_pos[1] // TILE_HEIGHT
    
    # finds which tile was clicked on
    for i, row in enumerate(board):
        for j, tile in enumerate(row):
            if(mouseX, mouseY) != (j, i):
                continue
            
            if leftMouseButton:
                tile.setVisible()
                # if you left clicked a mine, set all mine tiles as visible
                if tile.isMine:
                    for tempRow in board:
                        for tempTile in tempRow:
                            if tempTile.isMine:
                                tempTile.setVisible()
                    return 1
                
                # finds all neighboring tiles that have no mines around them
                set_neighbors_visible(board, j, i)
            
            elif rightMouseButton:
                tile.toggleFlag()


def main():
    # creates a pygame window
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("MINE SWEEPER")
    
    boardWidth, boardHeight = SETTINGS["width"], SETTINGS["height"]
    # creates a help board to set mines
    board = [[" " for j in range(boardWidth)] for i in range(boardHeight)]
    
    global TILE_WIDTH
    global TILE_HEIGHT
    TILE_WIDTH, TILE_HEIGHT = WIDTH / boardWidth, HEIGHT / boardHeight
    
    font = pygame.font.SysFont(None, int(min(TILE_WIDTH, TILE_HEIGHT) * .8))
    mineImg = pygame.Surface.convert_alpha(pygame.transform.scale(pygame.image.load(os.path.join("assets/mine.png")), (TILE_WIDTH * .8, TILE_HEIGHT * .8)))
    flagImg = pygame.Surface.convert_alpha(pygame.transform.scale(pygame.image.load(os.path.join("assets/flag.png")), (TILE_WIDTH * .8, TILE_HEIGHT * .8)))
    
    # putting mines onto board
    stopLoop = False
    totalMines = SETTINGS["numOfMines"]
    for i in range(boardHeight):
        for j in range(boardWidth):
            board[j][i] = "*"
            totalMines -= 1
            if totalMines == 0:
                stopLoop = True
                break
        if stopLoop:
            break
    
    # randomize mines position
    for row in board:
        shuffle(row)
    shuffle(board)
    
    # creates a list of lists containing Tile objects
    tileBoard = [[Tile(j, i, False, num_of_mines_around(board, i, j), mineImg, flagImg, font) if board[i][j] == " " else Tile(j, i, True, num_of_mines_around(board, i, j), mineImg, flagImg, font) for j in range(boardWidth)] for i in range(boardHeight)]
    
    # main loop
    gameRunning = True
    while gameRunning:
        draw(tileBoard, WIN)
        
        # the program waits until the user closes the window or clicks any mouse button
        pause = True
        while pause:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                gameRunning = False
                pause = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mouse_clicked(tileBoard, pygame.mouse.get_pos(), pygame.mouse.get_pressed()) == 1:
                    draw(tileBoard, WIN)
                    while True:
                        event = pygame.event.wait()
                        if event.type == pygame.QUIT:
                            gameRunning = False
                            break
                pause = False
        
        # checks if all non-mine fields are visible or all mine tiles are flagged
        # if so then the user wins the game
        # no win screen yet
        if Tile.numOfHiddenTiles == SETTINGS["numOfMines"] or Tile.numOfMinesFlagged == SETTINGS["numOfMines"]:
            draw(tileBoard, WIN)
            while True:
                event = pygame.event.wait()
                if event.type == pygame.QUIT:
                    gameRunning = False
                    break
    
    pygame.quit()


if __name__ == "__main__":
    settings()
    main()
