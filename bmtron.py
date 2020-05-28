from collections import deque
from pygame.locals import *
from enum import Enum, auto
import pygame
import time

class Player:
    x = 20
    y = 20 
    xs = deque()
    ys = deque()
    color = (255,255,255)
    alive = True

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

    class State(Enum):
        NEWGAME = auto()
        ROUNDOVER = auto()
        PLAYING = auto()

    windowHeight = 1600
    windowWidth = 3000
    players = []
    n_players = 0
    scores = []
    winners = []

    # COLOR CONSTANTS
    BLACK = (0,0,0)
    YELLOW = (255,255,150)
    WHITE = (255,255,255)
    DARKRED = (153,0,76)
    DARKREDHOVER = (169,0,102)
    RED = (255,0,0)
    DARKTEAL = (27,70,65)
    DARKTEALHOVER = (55,84,76)
    LIMEGREEN = (143,250,0)
    MAUVE = (216,176,186)
    PINK = (249,181,252)
    LIGHTBLUE = (87,178,220)
    SAND = (231,174,121)
    GREEN = (69,111,28)

    def __init__(self):
        self._display_surf = True

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.HWSURFACE)
        self._running = True
        self._state = self.State.NEWGAME

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False

    def on_loop(self):
        if self._state == self.State.PLAYING: 
            for i in range(self.n_players):
                if self.players[i].alive: 
                    self.players[i].addBlock()
                    # collision detection: wall
                    if self.players[i].x < 0 or self.players[i].y < 0 or self.players[i].y + 20 > self.windowHeight or self.players[i].x + 20 > self.windowWidth:
                        self.players[i].alive = False
                        self.winners[i] = 0
                    # collision detection: other snakes
                for coord in zip(self.players[i].xs, self.players[i].ys):
                    for j in range(self.n_players):
                        if coord == (self.players[j].x, self.players[j].y): 
                            self.players[j].alive = False
                            self.winners[j] = 0
            winner_count = self.n_players 
            for i in range(self.n_players):
                if self.winners[i] == 0: winner_count -= 1
                if winner_count < 2: self._state = self.State.ROUNDOVER
            if self._state == self.State.ROUNDOVER: 
                for i in range(self.n_players):
                    if self.winners[i] == 1: self.scores[i] += 1

    def on_render(self):
        self._display_surf.fill(self.BLACK)
        
        if self._state == self.State.NEWGAME:  
            self._draw_newgame()
        else:
            for player in self.players:
                for coord in zip(player.xs, player.ys):
                    pygame.draw.rect(self._display_surf, player.color, (coord[0], coord[1], 20, 20), 0)
                pygame.draw.rect(self._display_surf, player.color, (player.x, player.y, 20, 20), 0)
        
        if self._state == self.State.ROUNDOVER: self._draw_gameover()
        pygame.display.flip()

    def on_cleanup(self): 
        pygame.quit()

    def on_reset(self):
        self.players = []
        self.losers = []
        if self.n_players == 1: self.set_oneplayer()
        elif self.n_players == 2: self.set_twoplayer()
        elif self.n_players == 3: self.set_threeplayer()
        elif self.n_players == 4: self.set_fourplayer()
        self._state = self.State.PLAYING

    def on_newgame(self):
        self._state = self.State.NEWGAME
        self.scores = []

    def on_execute(self):
        if self.on_init() == False:
            self._running == False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            
            keys = pygame.key.get_pressed()
            if keys[K_ESCAPE]: self._running = False

            # PLAYER 1: ARROW KEYS
            if self.n_players > 0:
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
            time.sleep(1/60)

        self.on_cleanup()

    def set_oneplayer(self): 
        self.n_players = 1
        player1 = Player(int(self.windowWidth/2), int(self.windowHeight/2), "RIGHT", self.YELLOW)
        self.players = [player1,]
        if len(self.scores) == 0: self.scores = [0,]
        self.winners = [1,]
        self._state = self.State.PLAYING
    def set_twoplayer(self): 
        self.n_players = 2
        player1 = Player(20, int(self.windowHeight/2), "RIGHT", self.YELLOW)
        player2 = Player(self.windowWidth - 40, int(self.windowHeight/2), "LEFT", self.MAUVE)
        self.players = [player1, player2]
        if len(self.scores) == 0: self.scores = [0,0]
        self.winners = [1,1]
        self._state = self.State.PLAYING
    def set_threeplayer(self): 
        self.n_players = 3
        player1 = Player(20, 500, "RIGHT", self.YELLOW)
        player2 = Player(self.windowWidth - 40, 500, "LEFT", self.MAUVE)
        player3 = Player(int(self.windowWidth/2), 1100, "UP", self.SAND)
        self.players = [player1, player2, player3]
        if len(self.scores) == 0: self.scores = [0,0,0]
        self.winners = [1,1,1]
        self._state = self.State.PLAYING
    def set_fourplayer(self): 
        self.n_players = 4
        player1 = Player(20, 500, "RIGHT", self.YELLOW)
        player2 = Player(self.windowWidth - 40, 500, "LEFT", self.MAUVE)
        player3 = Player(20, 1100, "RIGHT", self.SAND)
        player4 = Player(self.windowWidth - 40, 1100, "LEFT", self.WHITE)
        self.players = [player1, player2, player3, player4]
        if len(self.scores) == 0: self.scores = [0,0,0,0]
        self.winners = [1,1,1,1]
        self._state = self.State.PLAYING
    
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
        winner_str = "Winner: " 
        for i in range(self.n_players):
            if i in range(self.n_players): 
                if self.winners[i] == 1: winner_str += "Player " + str(i + 1)
        font = pygame.font.Font(None, 300)
        winner_text = font.render(winner_str, True, self.LIMEGREEN)
        self._display_surf.blit(winner_text, [int(self.windowWidth / 2 - winner_text.get_rect().width / 2), int(self.windowHeight / 2 - winner_text.get_rect().height / 2 - 100)])

        score_str = ""
        font = pygame.font.Font(None, 75)
        for i in range(self.n_players):
            score_str += "Player " + str(i + 1) + ": " + str(self.scores[i]) + "      "
        score_text = font.render(score_str, True, self.PINK)
        self._display_surf.blit(score_text, [int(self.windowWidth / 2 - score_text.get_rect().width / 2), 200])
        
        self._draw_button("Play Again", self.DARKTEAL, self.DARKTEALHOVER, self.on_reset, y=int(self.windowHeight / 2 + 100))
        self._draw_button("Exit", self.DARKRED, self.DARKREDHOVER, self.on_newgame, y=int(self.windowHeight / 2 + 200))

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

