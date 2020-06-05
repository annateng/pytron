from collections import deque
from pygame.locals import *
from enum import Enum, auto
import pygame
import time
import numpy as np
import heapq
import os

# LOG FILE
if os.path.exists("new_log.txt"):
  os.remove("new_log.txt")
f = open("new_log.txt", "a")

class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()

step_size = 20
   
class Player:
    x = 20
    y = 20 
    xs = []
    ys = [] 
    color = (255,255,255)
    alive = True
    is_bot = False

    def __init__(self, is_bot, x_start=20, y_start=20, start_direction=Direction.RIGHT, color=(255,255,255)):
        self._X_START = x_start
        self._Y_START = y_start
        self._START_DIRECTION = start_direction
        self.direction = start_direction

        self.x = x_start
        self.y = y_start
        self.xs = []
        self.ys = []
        self.color = color
        self.is_bot = is_bot

    def moveRight(self):
        self.direction = Direction.RIGHT

    def moveLeft(self):
        self.direction = Direction.LEFT

    def moveUp(self):
        self.direction = Direction.UP

    def moveDown(self):
        self.direction = Direction.DOWN
        
    def _i(self, x, y):
        return (int(x/step_size), int(y/step_size))

    def _get_board(self, players, windowWidth, windowHeight):
        board = np.full((int(windowWidth/step_size), int(windowHeight/step_size)), False)
        for player in players:
            xs = player.xs + [player.x,]
            ys = player.ys + [player.y,]
            for coord in zip(xs, ys):
                board[self._i(coord[0], coord[1])] = True
        return board

    def _get_valid_directions(self, board, windowWidth, windowHeight):
        valid_directions = []
        if self.x != 0 and not board[self._i(self.x-step_size, self.y)]: 
            valid_directions.append(Direction.LEFT)
        if self.x+step_size != windowWidth and not board[self._i(self.x+step_size, self.y)]:
            valid_directions.append(Direction.RIGHT)
        if self.y != 0 and not board[self._i(self.x, self.y-step_size)]:
            valid_directions.append(Direction.UP)
        if self.y+step_size != windowHeight and not board[self._i(self.x, self.y+step_size)]:
            valid_directions.append(Direction.DOWN)
        return valid_directions

    def _dfs_score(self, start, board):
        visited = np.array(board, copy=True)
        distance = np.full(board.shape, float("inf"))
        heap = []
        
        score = 0
        node = (0, start)
        distance[start] = 0
        heapq.heappush(heap, node)
        while not len(heap) == 0 and node[0] < 30: 
            node = heapq.heappop(heap)
            block = node[1]
            left = (block[0]-1, block[1])
            right = (block[0]+1, block[1])
            up = (block[0], block[1]-1)
            down = (block[0], block[1]+1)
            if block[0] != 0 and not visited[left]:
                if distance[left] == float("inf"):
                    distance[left] = distance[block] + 1
                    heapq.heappush(heap, (distance[left], left))
                elif distance[left] > distance[block] + 1:
                    distance[left] = distance[block] + 1
                    for n in heap:
                        if n[1] == left: 
                            n[0] = distance[block] + 1 
                            heapq.heapify(heap)
            if block[0] != board.shape[0] - 1 and not visited[right]:
                if distance[right] == float("inf"):
                    distance[right] = distance[block] + 1
                    heapq.heappush(heap, (distance[right], right))
                elif distance[right] > distance[block] + 1:
                    distance[right] = distance[block] + 1
                    for n in heap:
                        if n[1] == right: 
                            n[0] = distance[block] + 1 
                            heapq.heapify(heap)
            if block[1] != 0 and not visited[up]:
                if distance[up] == float("inf"):
                    distance[up] = distance[block] + 1
                    heapq.heappush(heap, (distance[up], up))
                elif distance[up] > distance[up] + 1:
                    distance[up] = distance[up] + 1
                    for n in heap:
                        if n[1] == up: 
                            n[0] = distance[block] + 1 
                            heapq.heapify(heap)
            if block[1] != board.shape[1] - 1 and not visited[down]:
                if distance[down] == float("inf"):
                    distance[down] = distance[down] + 1
                    heapq.heappush(heap, (distance[down], down))
                elif distance[down] > distance[block] + 1:
                    distance[down] = distance[block] + 1
                    for n in heap:
                        if n[1] == down: 
                            n[0] = distance[block] + 1 
                            heapq.heapify(heap)
            visited[block] = True 
            score += 1

        return np.count_nonzero(visited==True) 

    def _get_score(self, board, start, players):
        
        self_score = self._dfs_score(start, board)
        f.write("self score: ")
        f.write(str(self_score)+"\n")

        player_scores = []
        for player in players:
            f.write("player: "+ str(player.x) + " " + str(player.y))
            f.write("self: " + str(self.x) + " " + str(self.y))
            if player.x != self.x:
                player_scores.append(self._dfs_score(self._i(player.x, player.y), board))

        final_score = 0
        for score in player_scores:
            f.write("player score: ")
            f.write(str(score) + "\n")
            final_score += self_score / score
        f.write("final score:") 
        f.write(str(final_score) + "\n")
        return final_score # SHOULD I ADD THE SELF_SCORE?

    def update(self, players, windowWidth, windowHeight):
        directions = {
            Direction.LEFT: -1000,
            Direction.RIGHT: -1000,
            Direction.UP: -1000,
            Direction.DOWN: -1000 
        }
        
        board = self._get_board(players, windowWidth, windowHeight)

        for direction in self._get_valid_directions(board, windowWidth, windowHeight):
            start = self._i(self.x, self.y)
            if direction == Direction.UP:
                start = self._i(self.x, self.y-step_size)
            elif direction == Direction.LEFT:
                start = self._i(self.x-step_size, self.y)
            elif direction == Direction.RIGHT:
                start = self._i(self.x+step_size, self.y)
            elif direction == Direction.DOWN:
                start = self._i(self.x, self.y+step_size)
            board[start] = True
            directions[direction] = self._get_score(board, start, players)
            board[start] = False

        # Try to cut other players off
        #  for i in range(len(players)):
            #  if players[i].direction == Direction.RIGHT and self.direction == Direction.RIGHT:
                #  if self.x - players[i].x > abs(self.y - players[i].y):
                    #  if self.y - players[i].y > 0: directions["up"] += 10000
                    #  else: directions["down"] += 10000
            #  if players[i].direction == Direction.LEFT and self.direction == Direction.LEFT:
                #  if players[i].x - self.x > abs(self.y - players[i].y):
                    #  if self.y - players[i].y > 0: directions["up"] += 10000
                    #  else: directions["down"] += 10000
            #  if players[i].direction == Direction.DOWN and self.direction == Direction.DOWN:
                #  if self.y - players[i].y > abs(self.x - players[i].x):
                    #  if self.x - players[i].x > 0: directions["left"] += 10000
                    #  else: directions["right"] += 10000
            #  if players[i].direction == Direction.UP and self.direction == Direction.UP:
                #  if players[i].y - self.y > abs(self.x - players[i].x):
                    #  if self.x - players[i].x > 0: directions["left"] += 10000
                    #  else: directions["right"] += 10000
            #  if self.direction == Direction.DOWN and players[i].direction == Direction.RIGHT and self.y - players[i].y < self.x - players[i].x and self.y - players[i].y > 0:
                #  directions["down"] += 10000
            #  if self.direction == Direction.DOWN and players[i].direction == Direction.LEFT and self.y - players[i].y < players[i].x - self.x and self.y - players[i].y > 0:
                #  directions["down"] += 10000
            #  if self.direction == Direction.RIGHT and players[i].direction == Direction.UP and players[i].x - self.x < self.y - players[i].y and players[i].x - self.x > 0:
                #  directions["right"] += 10000
            #  if self.direction == Direction.RIGHT and players[i].direction == Direction.DOWN and players[i].x - self.x < players[i].y - self.y and players[i].x - self.x > 0:
                #  directions["right"] += 10000
            #  if self.direction == Direction.UP and players[i].direction == Direction.RIGHT and players[i].y - self.y < players[i].x - self.x and players[i].y - self.y > 0:
                #  directions["up"] += 10000
            #  if self.direction == Direction.UP and players[i].direction == Direction.LEFT and players[i].y - self.y < self.x - players[i].x and players[i].y - self.y > 0:
                #  directions["up"] += 10000
            #  if self.direction == Direction.LEFT and players[i].direction == Direction.UP and self.x - players[i].x < players[i].y - self.y and self.x - players[i].x > 0:
                #  directions["left"] += 10000
            #  if self.direction == Direction.LEFT and players[i].direction == Direction.DOWN and self.x - players[i].x < self.y - players[i].y and self.x - players[i].x > 0:
                #  directions["left"] += 10000

        f.write(str(directions) + "\n")
        self.direction = max(directions, key=directions.get)
        f.write(str(self.direction) + "\n")

    def addBlock(self):
        self.xs.append(self.x)
        self.ys.append(self.y)
        if self.direction == Direction.RIGHT:
            self.x = self.x + step_size
        if self.direction == Direction.LEFT:
            self.x = self.x - step_size
        if self.direction == Direction.UP:
            self.y = self.y - step_size
        if self.direction == Direction.DOWN:
            self.y = self.y + step_size


class App:

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
    P1COLOR = (185,201,103)
    P1HOVER = (P1COLOR[0]-20, P1COLOR[1]-20, P1COLOR[2]-20)
    P2COLOR = (139,121,173)
    P2HOVER = (P2COLOR[0]-20, P2COLOR[1]-20, P2COLOR[2]-20)
    P3COLOR = (214,149,103)
    P3HOVER = (P3COLOR[0]-20, P3COLOR[1]-20, P3COLOR[2]-20)
    P4COLOR = (217,121,160)
    P4HOVER = (P4COLOR[0]-20, P4COLOR[1]-20, P4COLOR[2]-20)
    GREEN = (69,111,298)
    LIGHTGREY = (150,150,150)
    LIGHTGREYHOVER = (LIGHTGREY[0]-20, LIGHTGREY[1]-20, LIGHTGREY[2]-20)
    GREY = (80,80,80)
    GREYHOVER = (60,60,60)
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

    def __init__(self):
        pass

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.HWSURFACE)
        self._running = True
        self.ev = pygame.event.get()
        self.on_newgame()

    def on_loop(self):
        if self._state == self.State.PLAYING: 
            
            for i in range(self.n_players):
                if self.players[i].is_bot: self.players[i].update(self.players, self.windowWidth, self.windowHeight)
             
            for i in range(self.n_players):
                if self.players[i].alive: 
                    self.players[i].addBlock()
                    
            for i in range(self.n_players):
                # collision detection: wall
                if self.players[i].alive:
                    if self.players[i].x < 0 or self.players[i].y < 0 or self.players[i].y + step_size > self.windowHeight or self.players[i].x + step_size > self.windowWidth:
                        self.players[i].alive = False
                        self.still_alive[i] = False
                # collision detection: other snakes
                for coord in zip(self.players[i].xs, self.players[i].ys):
                    for j in range(self.n_players):
                        if self.players[j].alive:
                            if coord == (self.players[j].x, self.players[j].y): 
                                self.players[j].alive = False
                                self.still_alive[j] = False

            alive_count = self.n_players 
            for i in range(self.n_players):
                if not self.still_alive[i]: alive_count -= 1
                if alive_count < 2: self._state = self.State.ROUNDOVER
            if self._state == self.State.ROUNDOVER: 
                for i in range(self.n_players):
                    if self.still_alive[i]: self.scores[i] += 1

    def on_render(self):
        self._display_surf.fill(self.BLACK)
        
        if self._state == self.State.NEWGAME:  
            self._draw_newgame()
        elif self._state == self.State.ERROR:
            self._draw_error()
        else:
            for player in self.players:
                for coord in zip(player.xs, player.ys):
                    pygame.draw.rect(self._display_surf, player.color, (coord[0], coord[1], step_size, step_size), 0)
                pygame.draw.rect(self._display_surf, player.color, (player.x, player.y, step_size, step_size), 0)

        if self._state == self.State.ROUNDOVER: self._draw_gameover()
        pygame.display.flip()

    def on_cleanup(self): 
        f.close()
        pygame.quit()

    def on_reset(self):
        self.players = []
        self.still_alive = []
        
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
            self.still_alive = [True] * self.n_players
            self._state = self.State.PLAYING

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
        self.on_reset()

    def on_newgame(self):
        self._state = self.State.NEWGAME
        self.n_players = 0
        self.players = []
        self.scores = []
        self.still_alive = []
        self.player_choices = ["ARROW KEYS", "WASD", "None", "None"]
        self.button_colors = [self.P1COLOR, self.P2COLOR, self.GREY, self.GREY]
        self.hover_colors = [self.P1HOVER, self.P2HOVER, self.GREYHOVER, self.GREYHOVER]
        self.player_colors = []
        self.player_isbots = []
        self.player_controlcodes = []

    def on_execute(self):
        if self.on_init() == False:
            self._running == False

        while self._running:
            self.ev = pygame.event.get()
            for event in self.ev:
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
            time.sleep(1/80)

        self.on_cleanup()

    def set_twoplayer(self): 
        player1 = Player(self.player_isbots[0], 100, int(self.windowHeight/2), Direction.RIGHT, self.player_colors[0])
        player2 = Player(self.player_isbots[1], self.windowWidth - 120, int(self.windowHeight/2), Direction.LEFT, self.player_colors[1])
        self.players = [player1, player2]
    def set_threeplayer(self): 
        self.n_players = 3
        player1 = Player(self.player_isbots[0], 100, 500, Direction.RIGHT, self.player_colors[0])
        player2 = Player(self.player_isbots[1], self.windowWidth - 120, 500, Direction.LEFT, self.player_colors[1])
        player3 = Player(self.player_isbots[2], int(self.windowWidth/2), self.windowHeight - 120, Direction.UP, self.player_colors[2])
        self.players = [player1, player2, player3]
    def set_fourplayer(self): 
        self.n_players = 4
        player1 = Player(self.player_isbots[0], 100, 500, Direction.RIGHT, self.player_colors[0])
        player2 = Player(self.player_isbots[1], self.windowWidth - 120, 500, Direction.LEFT, self.player_colors[1])
        player3 = Player(self.player_isbots[2], 100, 1100, Direction.RIGHT, self.player_colors[2])
        player4 = Player(self.player_isbots[3], self.windowWidth - 120, 1100, Direction.LEFT, self.player_colors[3])
        self.players = [player1, player2, player3, player4]
   
    def toggle_player(self, player_number):
        if self.player_choices[player_number] == self.controls[player_number]: 
            self.player_choices[player_number] = "BOT"
            self.button_colors[player_number] = self.LIGHTGREY
            self.hover_colors[player_number] = self.LIGHTGREYHOVER
        elif self.player_choices[player_number] == "BOT":
            self.player_choices[player_number] = "None"
            self.button_colors[player_number] = self.GREY
            self.hover_colors[player_number] = self.GREYHOVER
        elif self.player_choices[player_number] == "None":
            self.player_choices[player_number] = self.controls[player_number]
            self.button_colors[player_number] = self.PLAYER_COLORS[player_number]
            self.hover_colors[player_number] = self.PLAYER_HOVERS[player_number]

    def _draw_error(self):
        font = pygame.font.Font(None, 250)
        text = font.render(self._error_message, True, self.RED)
        text_rect = text.get_rect()
        self._display_surf.blit(text, [int(self.windowWidth / 2 - text_rect.width / 2), int(self.windowHeight / 2 - text_rect.height / 2)])
        pygame.display.flip()
        time.sleep(1)
        self.on_newgame()

    def _draw_newgame(self):
        font = pygame.font.Font(None, 300)
        text = font.render("New Game", True, self.LIMEGREEN)
        text_rect = text.get_rect()
        text_x = int(self.windowWidth / 2 - text_rect.width / 2)
        text_y = int(self.windowHeight / 2 - text_rect.height / 2 - 500)
        self._display_surf.blit(text, [text_x, text_y])
        
        font = pygame.font.Font(None, 100)
        self._display_surf.blit(font.render("Player 1: ", True, self.YELLOW), [int(self.windowWidth / 2 - 500), 600])
        self._display_surf.blit(font.render("Player 2: ", True, self.YELLOW), [int(self.windowWidth / 2 - 500), 750])
        self._display_surf.blit(font.render("Player 3: ", True, self.YELLOW), [int(self.windowWidth / 2 - 500), 900])
        self._display_surf.blit(font.render("Player 4: ", True, self.YELLOW), [int(self.windowWidth / 2 - 500), 1050])

        self._draw_button(self.player_choices[0], self.button_colors[0], self.hover_colors[0], lambda: self.toggle_player(0), int(self.windowWidth/2), 600, 400, 100)
        self._draw_button(self.player_choices[1], self.button_colors[1], self.hover_colors[1], lambda: self.toggle_player(1), int(self.windowWidth/2), 750, 400, 100)
        self._draw_button(self.player_choices[2], self.button_colors[2], self.hover_colors[2], lambda: self.toggle_player(2), int(self.windowWidth/2), 900, 400, 100)
        self._draw_button(self.player_choices[3], self.button_colors[3], self.hover_colors[3], lambda: self.toggle_player(3), int(self.windowWidth/2), 1050, 400, 100)
        self._draw_button("START", self.DARKTEAL, self.DARKTEALHOVER, self.on_start_newgame, y=1300, fontsize=200)

    def _draw_gameover(self):
        winner_str = "Winner: " 
        for i in range(self.n_players):
            if i in range(self.n_players): 
                if self.still_alive[i]: winner_str += "Player " + str(i + 1)
        if len(winner_str) == 8: winner_str += "nobody"
        font = pygame.font.Font(None, 300)
        winner_text = font.render(winner_str, True, self.LIMEGREEN)
        winner_rect = winner_text.get_rect()
        pygame.draw.rect(self._display_surf, self.BLACK, (int(self.windowWidth / 2 - winner_rect.width / 2 - 120), int(100 - winner_rect.height / 2), winner_rect.width + 240, winner_rect.height + 100))
        self._display_surf.blit(winner_text, [int(self.windowWidth / 2 - winner_text.get_rect().width / 2), 100])

        score_str = ""
        font = pygame.font.Font(None, 75)
        for i in range(self.n_players):
            score_str += "Player " + str(i + 1) + ": " + str(self.scores[i]) + "      "
        score_text = font.render(score_str, True, self.WHITE)
        score_rect = score_text.get_rect()
        pygame.draw.rect(self._display_surf, self.BLACK, (int(self.windowWidth / 2 - score_rect.width / 2 - 60), int(360 - score_rect.height / 2), score_rect.width + 120, score_rect.height + 40))
        self._display_surf.blit(score_text, [int(self.windowWidth / 2 - score_text.get_rect().width / 2), 360])
        
        self._draw_button("Play Again", self.DARKTEAL, self.DARKTEALHOVER, self.on_reset, y=int(self.windowHeight / 2 + 100), fontsize=100)
        self._draw_button("Exit", self.DARKRED, self.DARKREDHOVER, self.on_newgame, y=int(self.windowHeight / 2 + 250), fontsize=100)

    def _draw_button(self, msg, init_color, hover_color, action, x=-1, y=-1, w=-1, h=-1, fontsize=40, fontcolor=(255,255,255)):
        font = pygame.font.Font(None, fontsize)
        text = font.render(msg, True, fontcolor) 
        text_rect = text.get_rect()
        
        mouse = pygame.mouse.get_pos()
        click = False
        for event in self.ev:
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

