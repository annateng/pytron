from constants import *
import numpy as np
from collections import deque

class Player:
    def __init__(self, is_bot, x_start=20, y_start=20, start_direction=Direction.RIGHT, color=(255,255,255)):
        self._X_START = x_start
        self._Y_START = y_start
        self._START_DIRECTION = start_direction
        
        self.alive = True
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
    
    def addBlock(self):
        self.xs.append(self.x)
        self.ys.append(self.y)
        if self.direction == Direction.RIGHT:
            self.x = self.x + step_size
        elif self.direction == Direction.LEFT:
            self.x = self.x - step_size
        elif self.direction == Direction.UP:
            self.y = self.y - step_size
        else: # self.direction == Direction.DOWN:
            self.y = self.y + step_size

    ## Start BOT methods
    def _i(self, x, y):
        return (int(x/step_size), int(y/step_size))

    # create matrix representing current game - true means space is occupied
    def _get_board(self, players, windowWidth, windowHeight):
        board = np.full((int(windowWidth/step_size), int(windowHeight/step_size)), False)
        for player in players:
            # assume player (except self) continues one step in the same direction. this will prevent head-on collisions and ties
            xNext = player.x
            yNext = player.y
            if player.x != self.x:
                if player.direction == Direction.RIGHT:
                    xNext = min(player.x + step_size, windowWidth - step_size)
                    yNext = player.y
                elif player.direction == Direction.LEFT:
                    xNext = max(player.x - step_size, 0)
                    yNext = player.y
                elif player.direction == Direction.UP:
                    xNext = player.x
                    yNext = max(player.y - step_size, 0)
                else: # player.direction == Direction.DOWN
                    xNext = player.x
                    yNext = min(player.y + step_size, windowHeight - step_size)
            xs = player.xs + [player.x, xNext]
            ys = player.ys + [player.y, yNext]
            for coord in zip(xs, ys):
                board[self._i(coord[0], coord[1])] = True
        return board

    # return each direction bot can go in without killing himself immediately
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
        visited = np.full(board.shape, False)
        #  distance = np.full(board.shape, float("inf"))
        #  heap = []
        stack = deque()
        
        score = 0
        #  node = (0, start)
        #  distance[start] = 0
        #  heapq.heappush(heap, node)
        stack.append(start)
        while stack: # not len(heap) == 0 and node[0] < 50: 
            #  node = heapq.heappop(heap)
            #  block = node[1]
            block = stack.pop()
            left = (block[0]-1, block[1])
            right = (block[0]+1, block[1])
            up = (block[0], block[1]-1)
            down = (block[0], block[1]+1)
            if block[0] != 0 and not visited[left] and not board[left]:
                visited[left] = True
                score += 1
                stack.append(left)
                
                #  if distance[left] == float("inf"):
                    #  distance[left] = distance[block] + 1
                    #  heapq.heappush(heap, (distance[left], left))
                #  elif distance[left] > distance[block] + 1:
                    #  distance[left] = distance[block] + 1
                    #  for n in heap:
                        #  if n[1] == left: 
                            #  n[0] = distance[block] + 1 
                            #  heapq.heapify(heap)
            if block[0] != board.shape[0] - 1 and not visited[right] and not board[right]:
                visited[right] = True
                score += 1
                stack.append(right)
                #  if distance[right] == float("inf"):
                    #  distance[right] = distance[block] + 1
                    #  heapq.heappush(heap, (distance[right], right))
                #  elif distance[right] > distance[block] + 1:
                    #  distance[right] = distance[block] + 1
                    #  for n in heap:
                        #  if n[1] == right: 
                            #  n[0] = distance[block] + 1 
                            #  heapq.heapify(heap)
            if block[1] != 0 and not visited[up] and not board[up]:
                visited[up] = True
                score += 1
                stack.append(up)
                #  if distance[up] == float("inf"):
                    #  distance[up] = distance[block] + 1
                    #  heapq.heappush(heap, (distance[up], up))
                #  elif distance[up] > distance[up] + 1:
                    #  distance[up] = distance[up] + 1
                    #  for n in heap:
                        #  if n[1] == up: 
                            #  n[0] = distance[block] + 1 
                            #  heapq.heapify(heap)
            if block[1] != board.shape[1] - 1 and not visited[down] and not board[down]:
                visited[down] = True
                score += 1
                stack.append(down)
                #  if distance[down] == float("inf"):
                    #  distance[down] = distance[down] + 1
                    #  heapq.heappush(heap, (distance[down], down))
                #  elif distance[down] > distance[block] + 1:
                    #  distance[down] = distance[block] + 1
                    #  for n in heap:
                        #  if n[1] == down: 
                            #  n[0] = distance[block] + 1 
                            #  heapq.heapify(heap)

        return score 

    def _get_score(self, board, start, players):
        
        self_score = self._dfs_score(start, board)
        #  f.write("self score: ")
        #  f.write(str(self_score)+"\n")

        #  player_scores = []
        #  for player in players:
            #  #  f.write("player: "+ str(player.x) + " " + str(player.y))
            #  #  f.write("self: " + str(self.x) + " " + str(self.y) + "\n")
            #  if player.x != self.x:
                #  player_scores.append(self._dfs_score(self._i(player.x, player.y), board))

        #  final_score = 0
        #  for score in player_scores:
            #  #  f.write("player score: ")
            #  #  f.write(str(score) + "\n")
            #  if score > 0:
                #  final_score += self_score / score
            #  if score == 0:
                #  final_score += 1000
        #  #  f.write("final score:") 
        #  #  f.write(str(final_score) + "\n")
        return self_score 

    def update(self, players, windowWidth, windowHeight):
        # do nothing if player is human
        if not self.is_bot:
            return 

        # initialize preferences to -1000
        directions = {
            Direction.LEFT: -1000,
            Direction.RIGHT: -1000,
            Direction.UP: -1000,
            Direction.DOWN: -1000 
        }
        
        board = self._get_board(players, windowWidth, windowHeight)

        for direction in self._get_valid_directions(board, windowWidth, windowHeight):
            start = None
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
        
        #  f.write(str(directions) + "\n")
        self.direction = max(directions, key=directions.get)
        #  f.write(str(self.direction) + "\n")

