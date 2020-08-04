from common import *
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

    ## Start BOT methods #####################################################################################################
    # create matrix representing current game - true means space is occupied
    def _get_board(self, players, windowWidth, windowHeight):
        board = np.full((int(windowWidth/step_size), int(windowHeight/step_size)), False)
        for player in players:
            (xNext, yNext) = self._get_next(player, windowWidth, windowHeight) 
            xs = player.xs + xNext
            ys = player.ys + yNext
            for coord in zip(xs, ys):
                board[ind(coord[0], coord[1])] = True
        return board

    def _get_next(self, player, windowWidth, windowHeight):
        # assume player (except self) continues a step in the same direction, to prevent head on collisions and ties
        xNext = [player.x,]
        yNext = [player.y,]
        if player.x != self.x:
            if player.direction == Direction.RIGHT:
                xNext.append(min(player.x + step_size, windowWidth - step_size))
                yNext.append(player.y)
            elif player.direction == Direction.LEFT:
                xNext.append(max(player.x - step_size, 0))
                yNext.append(player.y)
            elif player.direction == Direction.UP:
                xNext.append(player.x)
                yNext.append(max(player.y - step_size, 0))
            else: # player.direction == Direction.DOWN
                xNext.append(player.x)
                yNext.append(min(player.y + step_size, windowHeight - step_size))
        return (xNext, yNext)
        
    # return each direction bot can go in without killing himself immediately
    def _get_valid_directions(self, board, windowWidth, windowHeight):
        valid_directions = []
        if self.x != 0 and not board[ind(self.x-step_size, self.y)]: 
            valid_directions.append(Direction.LEFT)
        if self.x+step_size != windowWidth and not board[ind(self.x+step_size, self.y)]:
            valid_directions.append(Direction.RIGHT)
        if self.y != 0 and not board[ind(self.x, self.y-step_size)]:
            valid_directions.append(Direction.UP)
        if self.y+step_size != windowHeight and not board[ind(self.x, self.y+step_size)]:
            valid_directions.append(Direction.DOWN)
        return valid_directions

    def _dfs_score(self, start, board):
        visited = np.full(board.shape, False)
        stack = deque()
        
        score = 0
        # Append nodes of the form (distance, coordinate)
        dist = 0
        stack.append((dist, start))
        while stack and dist < 101: # not len(heap) == 0 and node[0] < 50: 
            #  node = heapq.heappop(heap)
            #  block = node[1]
            node = stack.popleft()
            dist = node[0]
            block = node[1]
            
            left = (block[0]-1, block[1])
            right = (block[0]+1, block[1])
            up = (block[0], block[1]-1)
            down = (block[0], block[1]+1)

            numChoices = 0
            if block[0] != 0 and not visited[left] and not board[left]:
                visited[left] = True
                numChoices += 1
                score += 1
                stack.append((dist+1, left))
                
            if block[0] != board.shape[0] - 1 and not visited[right] and not board[right]:
                visited[right] = True
                numChoices += 1
                score += 1
                stack.append((dist+1, right))
            
            if block[1] != 0 and not visited[up] and not board[up]:
                visited[up] = True
                numChoices += 1
                score += 1
                stack.append((dist+1, up))

            if block[1] != board.shape[1] - 1 and not visited[down] and not board[down]:
                visited[down] = True
                numChoices += 1
                score += 1
                stack.append((dist+1, down))
            score += numChoices - 1

        return score 

    def _get_score(self, board, start, players):
        
        self_score = self._dfs_score(start, board)
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
                start = ind(self.x, self.y-step_size)
            elif direction == Direction.LEFT:
                start = ind(self.x-step_size, self.y)
            elif direction == Direction.RIGHT:
                start = ind(self.x+step_size, self.y)
            elif direction == Direction.DOWN:
                start = ind(self.x, self.y+step_size)
            board[start] = True
            selfScore = self._get_score(board, start, players)
            #  otherScore = 0
            #  for player in players:
                #  otherScore += self._get_score(board, ind(player.x, player.y), players)
            #  directions[direction] = selfScore / max(otherScore, 1)
            directions[direction] = selfScore
            board[start] = False
        
        self.direction = max(directions, key=directions.get)

