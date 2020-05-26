from collections import deque
from pygame.locals import *
import pygame
import time

class Player:
    x =  20
    y = 20
    xs = deque()
    ys = deque()
    # speed = 1

    def __init__(self):
        self._direction = "RIGHT"
        self._bSize = 20

    def moveRight(self):
        self._direction = "RIGHT"

    def moveLeft(self):
        self._direction = "LEFT"

    def moveUp(self):
        self._direction = "UP"

    def moveDown(self):
        self._direction = "DOWN"
        
    def addBlock(self):
        self.xs.append(self.x)
        self.ys.append(self.y)
        if self._direction == "RIGHT":
            self.x = self.x + self._bSize
        if self._direction == "LEFT":
            self.x = self.x - self._bSize
        if self._direction == "UP":
            self.y = self.y - self._bSize
        if self._direction == "DOWN":
            self.y = self.y + self._bSize

    def reset(self):
        self.x = 20
        self.y = 20
        self.xs = deque()
        self.ys = deque()
        self._direction = "RIGHT"

class App:

    windowHeight = 1600
    windowWidth = 3000
    player = 0
    
    # COLOR CONSTANTS
    BLACK = (0,0,0)
    YELLOW = (255,255,0)
    WHITE = (255,255,255)
    DARKRED = (153,0,76)
    DARKREDHOVER = (169,0,102)
    RED = (255,0,0)
    DARKTEAL = (27,70,65)
    DARKTEALHOVER = (55,84,76)

    def __init__(self):
        self._running = True
        self._game_over = False
        self._display_surf = True
        self.player = Player()

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.HWSURFACE)
        self._running = True
        self._game_over = False

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False

    def on_loop(self):
        if not self._game_over: self.player.addBlock()
        # collision detection: wall
        if self.player.x < 0 or self.player.y < 0 or self.player.y + 20 > self.windowHeight or self.player.x + 20 > self.windowWidth:
            self._game_over = True
        # collision detection: self
        for coord in zip(self.player.xs, self.player.ys):
            if coord == (self.player.x, self.player.y): self._game_over = True

    def on_render(self):
        self._display_surf.fill(self.BLACK)
        
        for coord in zip(self.player.xs, self.player.ys):
            pygame.draw.rect(self._display_surf, self.YELLOW, (coord[0], coord[1], 20, 20), 0)
        pygame.draw.rect(self._display_surf, self.YELLOW, (self.player.x, self.player.y, 20, 20), 0)
        if self._game_over: self._render_gameover()

        pygame.display.flip()

    def on_cleanup(self): 
        pygame.quit()

    def on_reset(self):
        self.player.reset()
        self._game_over = False

    def on_execute(self):
        if self.on_init() == False:
            self._running == False

        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
            
            keys = pygame.key.get_pressed()
            if keys[K_ESCAPE]: self._running = False

            if keys[K_RIGHT]: self.player.moveRight()
            if keys[K_LEFT]: self.player.moveLeft()
            if keys[K_UP]: self.player.moveUp()
            if keys[K_DOWN]: self.player.moveDown()

            self.on_loop()
            self.on_render()
            time.sleep(1/25)

        self.on_cleanup()

    def set_running_false(self):
        self._running = False

    def _render_gameover(self):
        font = pygame.font.Font(None, 250)
        text = font.render("Game Over", True, self.WHITE)
        text_rect = text.get_rect()
        text_x = int(self.windowWidth / 2 - text_rect.width / 2)
        text_y = int(self.windowHeight / 2 - text_rect.height / 2 - 200)
        pygame.draw.rect(self._display_surf, self.RED, (text_x - 20, text_y - 20, text_rect.width + 40, text_rect.height + 40 ), 0)
        self._display_surf.blit(text, [text_x, text_y])
        self._draw_button("Play Again", self.DARKTEAL, self.DARKTEALHOVER, self.on_reset, y=int(self.windowHeight / 2 + 100))
        self._draw_button("Exit", self.DARKRED, self.DARKREDHOVER, self.set_running_false, y=int(self.windowHeight / 2 + 200))

    def _draw_button(self, msg, init_color, hover_color, action, x=-1, y=-1, w=-1, h=-1):
        font = pygame.font.Font(None, 40)
        text = font.render(msg, True, self.WHITE) 
        text_rect = text.get_rect()
        
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        if w == -1: w = int(text_rect.width + 40)
        if h == -1: h = int(text_rect.height + 40)
        if x == -1: x = int(self.windowWidth / 2 - w / 2)
        if y == -1: y = int(self.windowHeight / 2 - h / 2)

        if x+w > mouse[0] > x and y+h > mouse[1] > y:
            pygame.draw.rect(self._display_surf, hover_color, (x, y, w, h), 0)
            if click[0] == 1: action()
        else: pygame.draw.rect(self._display_surf, init_color, (x, y, w, h), 0)
        
        self._display_surf.blit(text, [x + int((w - text_rect.width) / 2), y + int((h - text_rect.height) / 2)])

if __name__ == '__main__':
    theApp = App()
    theApp.on_execute()

