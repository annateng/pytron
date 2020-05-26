from collections import deque
from pygame.locals import *
import pygame
import time

class Player:
    x = 20
    y = 20 
    xs = deque()
    ys = deque()
    color = (255,255,255)

    def __init__(self, x_start=20, y_start=20, start_direction="RIGHT", color=(255,255,255)):
        self._X_START = x_start
        self._Y_START = y_start
        self._START_DIRECTION = start_direction
        self._direction = start_direction
        self._bSize = 20

        self.x = x_start
        self.y = y_start
        self.xs = deque()
        self.ys = deque()
        self.color = color

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

class App:

    windowHeight = 1600
    windowWidth = 3000
    players = []
    n_players = 1

    # COLOR CONSTANTS
    BLACK = (0,0,0)
    YELLOW = (255,255,0)
    WHITE = (255,255,255)
    DARKRED = (153,0,76)
    DARKREDHOVER = (169,0,102)
    RED = (255,0,0)
    DARKTEAL = (27,70,65)
    DARKTEALHOVER = (55,84,76)
    LIMEGREEN = (143,250,0)
    MAUVE = (216,203,207)
    PINK = (49,181,252)

    def __init__(self):
        self._running = True
        self._game_over = False
        self._display_surf = True

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.HWSURFACE)
        self._running = True
        self._game_over = False
        self._newgame = True

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False

    def on_loop(self):
        if not self._newgame and not self._game_over: 
            for player in self.players: 
                player.addBlock()
                # collision detection: wall
                if player.x < 0 or player.y < 0 or player.y + 20 > self.windowHeight or player.x + 20 > self.windowWidth:
                    self._game_over = True
                # collision detection: other snakes
                for coord in zip(player.xs, player.ys):
                    for inner_player in self.players: 
                        if coord == (inner_player.x, inner_player.y): self._game_over = True

    def on_render(self):
        self._display_surf.fill(self.BLACK)
        
        if self._newgame:  
            self._draw_newgame()
        else:
            for player in self.players:
                for coord in zip(player.xs, player.ys):
                    pygame.draw.rect(self._display_surf, player.color, (coord[0], coord[1], 20, 20), 0)
                pygame.draw.rect(self._display_surf, player.color, (player.x, player.y, 20, 20), 0)
        
        if self._game_over: self._draw_gameover()
        pygame.display.flip()

    def on_cleanup(self): 
        pygame.quit()

    def on_reset(self):
        self.players = []
        self._game_over = False
        self._newgame = True

    def on_execute(self):
        if self.on_init() == False:
            self._running == False

        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
            
            keys = pygame.key.get_pressed()
            if keys[K_ESCAPE]: self._running = False

            # PLAYER 1: ARROW KEYS
            if keys[K_RIGHT]: self.players[0].moveRight()
            if keys[K_LEFT]: self.players[0].moveLeft()
            if keys[K_UP]: self.players[0].moveUp()
            if keys[K_DOWN]: self.players[0].moveDown()
            # PLAYER 2: WASD
            if self.n_players > 1:
                if keys[K_d]: self.players[1].moveRight()
                if keys[K_a]: self.players[1].moveLeft()
                if keys[K_w]: self.players[1].moveUp()
                if keys[K_s]: self.players[1].moveDown()
            # PLAYER 3: GVBN
            if self.n_players > 2:
                if keys[K_n]: self.players[2].moveRight()
                if keys[K_v]: self.players[2].moveLeft()
                if keys[K_g]: self.players[2].moveUp()
                if keys[K_b]: self.players[2].moveDown()
            # PLAYER 4: OKL;
            if self.n_players > 3:
                if keys[K_SEMICOLON]: self.players[3].moveRight()
                if keys[K_k]: self.players[3].moveLeft()
                if keys[K_o]: self.players[3].moveUp()
                if keys[K_l]: self.players[3].moveDown()

            self.on_loop()
            self.on_render()
            time.sleep(1/30)

        self.on_cleanup()

    def set_running_false(self): 
        self._running = False

    def set_oneplayer(self): 
        self.n_players = 1
        player1 = Player(int(self.windowWidth/2), int(self.windowHeight/2), "RIGHT", self.YELLOW)
        self.players = [player1,]
        self._newgame = False
    def set_twoplayer(self): 
        self.n_players = 2
        player1 = Player(20, int(self.windowHeight/2), "RIGHT", self.YELLOW)
        player2 = Player(self.windowWidth - 40, int(self.windowHeight/2), "LEFT", self.MAUVE)
        self.players = [player1, player2]
        self._newgame = False
    def set_threeplayer(self): 
        self.n_players = 3
        player1 = Player(20, 500, "RIGHT", self.YELLOW)
        player2 = Player(self.windowWidth - 40, 500, "LEFT", self.MAUVE)
        player3 = Player(int(self.windowWidth/2), 1100, "UP", self.PINK)
        self.players = [player1, player2, player3]
        self._newgame = False
    def set_fourplayer(self): 
        self.n_players = 4
        player1 = Player(20, 500, "RIGHT", self.YELLOW)
        player2 = Player(self.windowWidth - 40, 500, "LEFT", self.MAUVE)
        player3 = Player(20, 1100, "RIGHT", self.PINK)
        player4 = Player(self.windowWidth - 40, 1100, "LEFT", self.WHITE)
        self.players = [player1, player2, player3, player4]
        self._newgame = False
    
    def _draw_newgame(self):
        font = pygame.font.Font(None, 250)
        text = font.render("New Game", True, self.LIMEGREEN)
        text_rect = text.get_rect()
        text_x = int(self.windowWidth / 2 - text_rect.width / 2)
        text_y = int(self.windowHeight / 2 - text_rect.height / 2 - 200)
        self._display_surf.blit(text, [text_x, text_y])
        self._draw_button("Play One Player", self.DARKTEAL, self.DARKTEALHOVER, self.set_oneplayer, 100, 1200, 400, 100)
        self._draw_button("Play Two Player", self.DARKTEAL, self.DARKTEALHOVER, self.set_twoplayer, 100, 1400, 400, 100)
        self._draw_button("Play Three Player", self.DARKTEAL, self.DARKTEALHOVER, self.set_threeplayer, self.windowWidth - 500, 1200, 400, 100)
        self._draw_button("Play Four Player", self.DARKTEAL, self.DARKTEALHOVER, self.set_fourplayer, self.windowWidth - 500, 1400, 400, 100)

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

