import pygame
import numpy as np
import threading
import time
import json

# define constants
SCREEN_WIDTH = 768
SCREEN_HEIGHT = 768

config = json.load(open("config.json"))
MINE_COUNT = config["numberOfMines"]
ASSET_PACK = config["assetPack"]

fail = False
win = False

lose_messages = [
    "You lose!",
    "Better luck next time!",
    ":3",
    "bro is NOT getting the minesweeper badge in eut"
]
lose_current = ""

pygame.font.init()
my_font = pygame.font.SysFont('SystemBold', 35)

class Base(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()

    def draw(self,surface):
        surface.blit(self.image,self.rect)

class GridCell:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.checked = False

        self.status = 0
        self.is_mine = mineGrid[x][y]
        self.is_open = False
        self.is_flagged = False

        self.mouseHeld = False

    def draw(self, surface):
        #setup cell
        image = None
        global flagCount, win
        try:
            if fail and self.is_flagged and not self.is_mine:
                image = pygame.image.load(f"Assets/{ASSET_PACK}/FlagWrong.png")
            elif fail and self.is_mine:
                image = pygame.image.load(f"Assets/{ASSET_PACK}/Mine.png")
            elif self.is_flagged:
                image = pygame.image.load(f"Assets/{ASSET_PACK}/Flag.png")
            elif self.is_open == False:
                image = pygame.image.load(f"Assets/{ASSET_PACK}/Base.png")
            elif self.is_mine:
                image = pygame.image.load(f"Assets/{ASSET_PACK}/Mine.png")
            else:
                image = pygame.image.load(f"Assets/{ASSET_PACK}/{self.status}.png")
        except:
            if fail and self.is_flagged and not self.is_mine:
                image = pygame.image.load("Assets/basil/FlagWrong.png")
            elif fail and self.is_mine:
                image = pygame.image.load("Assets/basil/Mine.png")
            elif self.is_flagged:
                image = pygame.image.load("Assets/basil/Flag.png")
            elif self.is_open == False:
                image = pygame.image.load("Assets/basil/Base.png")
            elif self.is_mine:
                image = pygame.image.load("Assets/basil/Mine.png")
            else:
                image = pygame.image.load(f"Assets/basil/{self.status}.png")
        rect = image.get_rect()
        rect.topleft = (self.x * 48, self.y * 48)
        # check inputs
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        if rect.collidepoint(mouse_pos) and not fail: 
            if mouse_buttons[0] == 1:
                if self.is_open == False and self.is_flagged == False:
                    self.open()
                elif self.status > 0:
                    flaggedCount = 0
                    for x in range(-1, 2):
                        for y in range(-1, 2):
                            if 0 <= self.x + x < SCREEN_WIDTH // 48 and 0 <= self.y + y < SCREEN_HEIGHT // 48:
                                if grid[self.x + x][self.y + y].is_flagged:
                                    flaggedCount += 1
                    if flaggedCount == self.status: 
                        for x in range(-1, 2):
                            for y in range(-1, 2):
                                if 0 <= self.x + x < SCREEN_WIDTH // 48 and 0 <= self.y + y < SCREEN_HEIGHT // 48:
                                    if grid[self.x + x][self.y + y].is_open == False and grid[self.x + x][self.y + y].is_flagged == False:
                                        grid[self.x + x][self.y + y].open()
                                        grid[self.x + x][self.y + y].checked = True
            elif mouse_buttons[2] == 1 and self.mouseHeld == False:
                if self.is_open == False or self.is_flagged == True:
                    self.is_flagged = not self.is_flagged
                    if self.is_flagged:
                        flagCount += 1
                    else:
                        flagCount -= 1

                self.mouseHeld = True
            elif mouse_buttons[2] == 0:
                self.mouseHeld = False

        # draw cell
        surface.blit(image,rect)

    def open(self):
        global exposedCount
        # open cell
        if self.is_open == False:
            self.is_open = True
            exposedCount += 1
        else:
            return
        # check if cell is a mine
        if self.is_mine:
            global fail,lose_current
            lose_current = np.random.choice(lose_messages)
            fail = True
            def WaitUntilPress():
                global alive
                while True:
                    pygame.time.delay(300)
                    mouse_buttons = pygame.mouse.get_pressed()
                    if mouse_buttons[0] == 1:
                        alive = False
                        return
            threading.Thread(target=WaitUntilPress).start()
            
        else:
            # count adjacent mines
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if 0 <= self.x + x < SCREEN_WIDTH // 48 and 0 <= self.y + y < SCREEN_HEIGHT // 48:
                        if grid[self.x + x][self.y + y].is_mine:
                            self.status += 1
            # propagate to adjacent cells
            if self.status == 0:
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        if x == 0 and y == 0:
                            continue
                        if 0 <= self.x + x < SCREEN_WIDTH // 48 and 0 <= self.y + y < SCREEN_HEIGHT // 48:
                            if grid[self.x + x][self.y + y].checked:
                                continue
                            if grid[self.x + x][self.y + y].is_open:
                                continue
                            grid[self.x + x][self.y + y].checked = True
                            grid[self.x + x][self.y + y].open()

class Display(Base):
    def __init__(self,posX,posY) -> None:
        super().__init__()

        self.position = (posX,posY)

    def draw(self,surface,text,colour,transparency = 255):
        self.textDisplay = my_font.render(text,False,colour)
        self.size = self.textDisplay.get_size()

        self.textDisplay.set_alpha(transparency)

        surface.blit(self.textDisplay,(self.position[0] - self.size[0]//2,self.position[1] - self.size[1]//2))

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Minesweeper")


while True:
    alive = True

    flagCount = 0
    exposedCount = 0
    mineGrid = np.zeros((SCREEN_WIDTH // 48, SCREEN_HEIGHT // 48))
    
    delta = time.time()
    i = 0
    while i < MINE_COUNT:
        x = np.random.randint(0, SCREEN_WIDTH // 48)
        y = np.random.randint(0, SCREEN_HEIGHT // 48)
        if mineGrid[x][y] == 0:
            mineGrid[x][y] = 1
            i += 1
    mineGrid = np.array(mineGrid, dtype=bool)
    info = Display(SCREEN_WIDTH//2,20)
    stopwatch = Display(SCREEN_WIDTH//2,SCREEN_HEIGHT-20)

    # generate grid
    grid = [[GridCell(x, y) for y in range(SCREEN_HEIGHT // 48)] for x in range(SCREEN_WIDTH // 48)]

    while alive:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        screen.fill((0, 0, 0))

        if 256 - MINE_COUNT == exposedCount and not (win or fail):
            win = True
            def WaitUntilPress():
                global alive
                while True:
                    pygame.time.delay(300)
                    mouse_buttons = pygame.mouse.get_pressed()
                    if mouse_buttons[0] == 1:
                        alive = False
                        return
            threading.Thread(target=WaitUntilPress).start()

        # draw grid
        for row in grid:
            for cell in row:
                cell.draw(screen)

        # draw gui

        if win:
            info.draw(screen,"You Win!",(0,255,0)) 
        elif fail:
            info.draw(screen,f"{lose_current}",(255,0,0))
        else:
            info.draw(screen,f"Flags: {flagCount}/{MINE_COUNT}",(255,255,255))

        stopwatch.draw(screen,f"{time.time() - delta :.3f}s",(255,255,255))

        pygame.display.flip()

    grid.clear()
    fail = False
    win = False
    alive = True
