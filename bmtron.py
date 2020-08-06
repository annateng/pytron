from collections import deque
from pygame.locals import *
import pygame
import time
import os
import numpy as np

from common import *
from player import Player

# LOG FILE
#  if os.path.exists("new_log.txt"):
  #  os.remove("new_log.txt")
#  f = open("new_log.txt", "a")

class App:

    PLAYER_COLORS = [P1COLOR, P2COLOR, P3COLOR, P4COLOR]
    PLAYER_HOVERS = [P1HOVER, P2HOVER, P3HOVER, P4HOVER] 

    class State(Enum):
        NEWGAME = auto()
        ROUNDOVER = auto()
        PLAYING = auto()
        ERROR = auto()

    windowHeight = 1600
    windowWidth = 3000
    n_players = 0
    players = []
    scores = []
    still_alive = []
    player_choices = ["ARROW KEYS", "WASD", "None", "None"]
    button_colors = [P1COLOR, P2COLOR, GREY, GREY]
    hover_colors = [P1HOVER, P2HOVER, GREYHOVER, GREYHOVER]
    controls = ["ARROW KEYS", "WASD", "GVBN", "OKL;"] 
    control_codes = [0, 1, 2, 3]
    player_colors = []
    player_isbots = []
    player_controlcodes = []
    board = None

    def __init__(self):
        pass

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.HWSURFACE)
        self._running = True
        self._ev = pygame.event.get()
        self.on_newgame()

    def on_loop(self):
        if self._state == self.State.PLAYING: 
            
            # update the board
            for player in self.players:
                self.board[ind(player.x, player.y)] = True

            # bots choose their next move
            for i in range(self.n_players):
                if self.players[i].alive:
                    self.players[i].update(self.board, self.players, self.windowWidth, self.windowHeight)
             
            # add next block for each player
            for i in range(self.n_players):
                if self.players[i].alive: 
                    self.players[i].addBlock()
                    
            for i in range(self.n_players):
                # collision detection: wall
                if self.players[i].alive:
                    if self.players[i].x < 0 or self.players[i].y < 0 or self.players[i].y + step_size > self.windowHeight or self.players[i].x + step_size > self.windowWidth:
                        self.players[i].alive = False
                # collision detection: other snakes
                # 1. check if player i's tail collides with any player's head
                for coord in zip(self.players[i].xs, self.players[i].ys):
                    for j in range(self.n_players):
                        if self.players[j].alive:
                            if coord == (self.players[j].x, self.players[j].y): 
                                self.players[j].alive = False
                # 2: check if any players heads collide with eachother
                for j in range(self.n_players):
                    if self.players[j].alive:
                        if i != j and self.players[i].x == self.players[j].x and self.players[i].y == self.players[j].y:
                            self.players[i].alive = False
                            self.players[j].alive = False

            # calculate whether there's a winner yet
            alive_count = self.n_players 
            for i in range(self.n_players):
                if not self.players[i].alive: alive_count -= 1
                if alive_count < 2: self._state = self.State.ROUNDOVER
            # add one point to the winning player
            if self._state == self.State.ROUNDOVER: 
                for i in range(self.n_players):
                    if self.players[i].alive: self.scores[i] += 1

    def on_render(self):
        self._display_surf.fill(BLACK)
        
        if self._state == self.State.NEWGAME:  
            self._draw_newgame()
        elif self._state == self.State.ERROR:
            self._draw_error()
        else:
            for player in self.players:
                # draw tail
                for coord in zip(player.xs, player.ys):
                    pygame.draw.rect(self._display_surf, player.color, (coord[0], coord[1], step_size, step_size), 0)
                # draw head
                pygame.draw.rect(self._display_surf, player.color, (player.x, player.y, step_size, step_size), 0)

        if self._state == self.State.ROUNDOVER: self._draw_gameover()
        pygame.display.flip()

    def on_cleanup(self): 
        f.close()
        pygame.quit()

    # sequence for starting a new round
    def on_new_round(self):
        self.players = []
        self.board = np.full((int(self.windowWidth/step_size), int(self.windowHeight/step_size)), False)
        
        if self.n_players < 2: 
            self._state = self.State.ERROR
            self._error_message = "Please Choose At Least 2 Players"
        else:
            if self.n_players == 2: 
                self.set_twoplayer()
            elif self.n_players == 3: 
                self.set_threeplayer()
            elif self.n_players == 4: 
                self.set_fourplayer()
            if len(self.scores) == 0: self.scores = [0] * self.n_players
            self._state = self.State.PLAYING

    # sequence for starting new game, after player clicks start
    def on_start_newgame(self):
        for i in range(len(self.player_choices)):
            if self.player_choices[i] == self.controls[i]:
                self.n_players += 1
                self.player_colors.append(self.button_colors[i])
                self.player_isbots.append(False)
                self.player_controlcodes.append(self.control_codes[i])
            elif self.player_choices[i] == "BOT":
                self.n_players += 1
                self.player_colors.append(self.button_colors[i])
                self.player_isbots.append(True)
                self.player_controlcodes.append(-1)
        self.on_new_round()

    # Sequence for setting up a new game, before the initial options screen
    def on_newgame(self):
        self._state = self.State.NEWGAME
        self.n_players = 0
        self.players = []
        self.scores = []
        self.player_choices = ["ARROW KEYS", "WASD", "None", "None"]
        self.button_colors = [P1COLOR, P2COLOR, GREY, GREY]
        self.hover_colors = [P1HOVER, P2HOVER, GREYHOVER, GREYHOVER]
        self.player_colors = []
        self.player_isbots = []
        self.player_controlcodes = []

    def on_execute(self):
        if self.on_init() == False:
            self._running == False

        # MAIN GAME LOOP
        while self._running:
            start = time.time()
            self._ev = pygame.event.get()
            for event in self._ev:
                if event.type == QUIT:
                    self._running = False
            
            keys = pygame.key.get_pressed()
            if keys[K_ESCAPE]: self._running = False

            # PLAYER 1: ARROW KEYS
            if self._state == self.State.PLAYING:
                for i in range(self.n_players):
                    if self.player_controlcodes[i] == 0:
                        if keys[K_RIGHT]: self.players[i].moveRight()
                        if keys[K_LEFT]: self.players[i].moveLeft()
                        if keys[K_UP]: self.players[i].moveUp()
                        if keys[K_DOWN]: self.players[i].moveDown()
                    # PLAYER 2: WASD
                    if self.player_controlcodes[i] == 1:
                        if keys[K_d]: self.players[i].moveRight()
                        if keys[K_a]: self.players[i].moveLeft()
                        if keys[K_w]: self.players[i].moveUp()
                        if keys[K_s]: self.players[i].moveDown()
                    # PLAYER 3: GVBN
                    if self.player_controlcodes[i] == 2:
                        if keys[K_n]: self.players[i].moveRight()
                        if keys[K_v]: self.players[i].moveLeft()
                        if keys[K_g]: self.players[i].moveUp()
                        if keys[K_b]: self.players[i].moveDown()
                    # PLAYER 4: OKL;
                    if self.player_controlcodes[i] == 3:
                        if keys[K_SEMICOLON]: self.players[i].moveRight()
                        if keys[K_k]: self.players[i].moveLeft()
                        if keys[K_o]: self.players[i].moveUp()
                        if keys[K_l]: self.players[i].moveDown()

            self.on_loop()
            self.on_render()
            end = time.time()
            # maintain constant frame rate
            if end - start < 1/15: time.sleep(1/15 - end + start)

        self.on_cleanup()

    def set_twoplayer(self): 
        player1 = Player(self.player_isbots[0], 200, int(self.windowHeight/2), Direction.RIGHT, self.player_colors[0])
        player2 = Player(self.player_isbots[1], self.windowWidth - 200, int(self.windowHeight/2), Direction.LEFT, self.player_colors[1])
        self.players = [player1, player2]
    def set_threeplayer(self): 
        self.n_players = 3
        player1 = Player(self.player_isbots[0], 200, 500, Direction.RIGHT, self.player_colors[0])
        player2 = Player(self.player_isbots[1], self.windowWidth - 200, 500, Direction.LEFT, self.player_colors[1])
        player3 = Player(self.player_isbots[2], int(self.windowWidth/2), self.windowHeight - 120, Direction.UP, self.player_colors[2])
        self.players = [player1, player2, player3]
    def set_fourplayer(self): 
        self.n_players = 4
        player1 = Player(self.player_isbots[0], 200, 500, Direction.RIGHT, self.player_colors[0])
        player2 = Player(self.player_isbots[1], self.windowWidth - 200, 500, Direction.LEFT, self.player_colors[1])
        player3 = Player(self.player_isbots[2], 200, 1100, Direction.RIGHT, self.player_colors[2])
        player4 = Player(self.player_isbots[3], self.windowWidth - 200, 1100, Direction.LEFT, self.player_colors[3])
        self.players = [player1, player2, player3, player4]
   
    def toggle_player(self, player_number):
        if self.player_choices[player_number] == self.controls[player_number]: 
            #  has_bot = False 
            #  for i in range(len(self.player_choices)):
                #  if self.player_choices[i] == "BOT": 
                    #  has_bot = True
                    #  break
            #  if not has_bot:
            self.player_choices[player_number] = "BOT"
            self.button_colors[player_number] = self.PLAYER_COLORS[player_number]
            self.hover_colors[player_number] = self.PLAYER_HOVERS[player_number]
            #  else:
                #  self.player_choices[player_number] = "None"
                #  self.button_colors[player_number] = GREY
                #  self.hover_colors[player_number] = GREYHOVER
        elif self.player_choices[player_number] == "BOT":
            self.player_choices[player_number] = "None"
            self.button_colors[player_number] = GREY
            self.hover_colors[player_number] = GREYHOVER
        elif self.player_choices[player_number] == "None":
            self.player_choices[player_number] = self.controls[player_number]
            self.button_colors[player_number] = self.PLAYER_COLORS[player_number]
            self.hover_colors[player_number] = self.PLAYER_HOVERS[player_number]

    def _draw_error(self):
        font = pygame.font.Font(None, 100)
        text = font.render(self._error_message, True, RED)
        text_rect = text.get_rect()
        self._display_surf.blit(text, [int(self.windowWidth / 2 - text_rect.width / 2), int(self.windowHeight / 2 - text_rect.height / 2)])
        pygame.display.flip()
        time.sleep(1)
        self.on_newgame()

    def _draw_newgame(self):
        font = pygame.font.Font(None, 100)
        text = font.render("New Game", True, LIMEGREEN)
        text_rect = text.get_rect()
        text_x = 20
        text_y = 20 
        self._display_surf.blit(text, [text_x, text_y])
        
        font = pygame.font.Font(None, 70)
        self._display_surf.blit(font.render("Player 1: ", True, WHITE), [20, 150])
        self._display_surf.blit(font.render("Player 2: ", True, WHITE), [20, 225])
        self._display_surf.blit(font.render("Player 3: ", True, WHITE), [20, 300])
        self._display_surf.blit(font.render("Player 4: ", True, WHITE), [20, 375])

        self._draw_button(self.player_choices[0], self.button_colors[0], self.hover_colors[0], lambda: self.toggle_player(0), 250, 150, 300, 70)
        self._draw_button(self.player_choices[1], self.button_colors[1], self.hover_colors[1], lambda: self.toggle_player(1), 250, 225, 300, 70)
        self._draw_button(self.player_choices[2], self.button_colors[2], self.hover_colors[2], lambda: self.toggle_player(2), 250, 300, 300, 70)
        self._draw_button(self.player_choices[3], self.button_colors[3], self.hover_colors[3], lambda: self.toggle_player(3), 250, 375, 300, 70)
        self._draw_button("START", LIMEGREEN, LIMEGREENHOVER, self.on_start_newgame, x=20, y=550, fontsize=100)

    def _draw_gameover(self):
        winner_str = "Winner: " 
        for i in range(self.n_players):
            if i in range(self.n_players): 
                if self.players[i].alive: winner_str += "Player " + str(i + 1)
        if len(winner_str) == 8: winner_str += "nobody"
        font = pygame.font.Font(None, 150)
        winner_text = font.render(winner_str, True, GREEN)
        winner_rect = winner_text.get_rect()
        pygame.draw.rect(self._display_surf, WHITE, (int(self.windowWidth / 2 - winner_rect.width / 2 - 120), int(100 - winner_rect.height / 2), winner_rect.width + 240, winner_rect.height + 100))
        self._display_surf.blit(winner_text, [int(self.windowWidth / 2 - winner_text.get_rect().width / 2), 100])

        score_str = ""
        font = pygame.font.Font(None, 75)
        for i in range(self.n_players):
            score_str += "Player " + str(i + 1) + ": " + str(self.scores[i]) + "      "
        score_text = font.render(score_str, True, PINK)
        score_rect = score_text.get_rect()
        pygame.draw.rect(self._display_surf, WHITE, (int(self.windowWidth / 2 - score_rect.width / 2 - 60), int(360 - score_rect.height / 2), score_rect.width + 120, score_rect.height + 40))
        self._display_surf.blit(score_text, [int(self.windowWidth / 2 - score_text.get_rect().width / 2), 360])
        
        self._draw_button("Play Again", LIMEGREEN, LIMEGREENHOVER, self.on_new_round, y=int(self.windowHeight / 2 + 100), fontsize=100)
        self._draw_button("Exit", DARKRED, DARKREDHOVER, self.on_newgame, y=int(self.windowHeight / 2 + 250), fontsize=100)

    def _draw_button(self, msg, init_color, hover_color, action, x=-1, y=-1, w=-1, h=-1, fontsize=40, fontcolor=(255,255,255)):
        font = pygame.font.Font(None, fontsize)
        text = font.render(msg, True, fontcolor) 
        text_rect = text.get_rect()
        
        mouse = pygame.mouse.get_pos()
        click = False
        for event in self._ev:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1: click = True
        
        if w == -1: w = int(text_rect.width + fontsize/2)
        if h == -1: h = int(text_rect.height + fontsize/3)
        if x == -1: x = int(self.windowWidth / 2 - w / 2)
        if y == -1: y = int(self.windowHeight / 2 - h / 2)

        if x+w > mouse[0] > x and y+h > mouse[1] > y:
            pygame.draw.rect(self._display_surf, hover_color, (x, y, w, h), 0)
            if click: action()
        else: pygame.draw.rect(self._display_surf, init_color, (x, y, w, h), 0)
        
        self._display_surf.blit(text, [x + int((w - text_rect.width) / 2), y + int((h - text_rect.height) / 2)])

if __name__ == '__main__':
    theApp = App()
    theApp.on_execute()

