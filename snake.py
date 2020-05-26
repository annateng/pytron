from collections import deque
from pygame.locals import *
import pygame
import time

class Player:
    x = 20
    y = 20 
    xs = deque()
    ys = deque()

    def __init__(self, x_start=20, y_start=20, start_direction="RIGHT"):
        self._X_START = x_start
        self._Y_START = y_start
        self._START_DIRECTION = start_direction
        self._direction = start_direction
        self._bSize = 20

        self.x = x_start
        self.y = y_start

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
        self.x = self._X_START
        self.y = self._Y_START
        self.xs = deque()
        self.ys = deque()
        self._direction = self._START_DIRECTION 

class App:

    windowHeight = 1600
    windowWidth = 3000
    n_players = 2
    players = 0

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

        player1 = Player(20, 20, "RIGHT")
        player2 = Player(self.windowWidth - 40, 20, "LEFT")
        self.players = [player1, player2]

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.HWSURFACE)
        self._running = True
        self._game_over = False

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False

    def on_loop(self):
        if not self._game_over: 
            for player in self.players: 
                player.addBlock()
                # collision detection: wall
                if player.x < 0 or player.y < 0 or player.y + 20 > self.windowHeight or player.x + 20 > self.windowWidth:
                    self._game_over = True
                # collision detection: self
                for coord in zip(player.xs, player.ys):
                    for inner_player in self.players: 
                        if coord == (inner_player.x, inner_player.y): self._game_over = True

    def on_render(self):
        self._display_surf.fill(self.BLACK)
        
        for player in self.players:
            for coord in zip(player.xs, player.ys):
                pygame.draw.rect(self._display_surf, self.YELLOW, (coord[0], coord[1], 20, 20), 0)
            pygame.draw.rect(self._display_surf, self.YELLOW, (player.x, player.y, 20, 20), 0)
        
        if self._game_over: self._draw_gameover()
        pygame.display.flip()

    def on_cleanup(self): 
        pygame.quit()

    def on_reset(self):
        for player in self.players:
            player.reset()
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

            if keys[K_RIGHT]: self.players[1].moveRight()
            if keys[K_LEFT]: self.players[1].moveLeft()
            if keys[K_UP]: self.players[1].moveUp()
            if keys[K_DOWN]: self.players[1].moveDown()

            self.on_loop()
            self.on_render()
            time.sleep(1/30)

        self.on_cleanup()

    def set_running_false(self):
        self._running = False

    def _draw_gameover(self):
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

