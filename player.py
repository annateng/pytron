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
    def _get_next(self, player, windowWidth, windowHeight):
        # assume player (except self) continues a step in each direction, to prevent head on collisions and ties
        ns = []
        if player.x != self.x:
            #  if player.direction == Direction.RIGHT:
            ns.append([min(player.x + step_size, windowWidth - step_size), player.y])
            #  yNext.append(player.y)
            #  elif player.direction == Direction.LEFT:
            ns.append([max(player.x - step_size, 0), player.y])
            #  yNext.append(player.y)
            #  elif player.direction == Direction.UP:
            ns.append([player.x, max(player.y - step_size, 0)])
            #  yNext.append(max(player.y - step_size, 0))
            #  else: # player.direction == Direction.DOWN
            #  xNext.append(player.x)
            ns.append([player.x, min(player.y + step_size, windowHeight - step_size)])
        return ns
        
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
            #  f.write(",".join(map(str, block)) + "\n")
            #  f.write(str(board.shape) + "\n")
            
            left = (block[0]-1, block[1])
            right = (block[0]+1, block[1])
            up = (block[0], block[1]-1)
            down = (block[0], block[1]+1)

            #  f.write(",".join(map(str, left)) + " ")
            #  f.write(",".join(map(str, right)) + " ")
            #  f.write(",".join(map(str, up)) + " ")
            #  f.write(",".join(map(str, down)) + "\n")
            numChoices = 0
            if block[0] != 0 and not board[left]:
                numChoices += 1
                #  f.write("left ok\n")
                if not visited[left]:
                    visited[left] = True
                    score += 1
                    stack.append((dist+1, left))
                
            if block[0] != board.shape[0] - 1 and not board[right]:
                numChoices += 1
                #  f.write("right ok\n")
                if not visited[right]:
                    visited[right] = True
                    score += 1
                    stack.append((dist+1, right))
            
            if block[1] != 0 and not board[up]:
                numChoices += 1
                #  f.write("up ok\n")
                if not visited[up]:
                    visited[up] = True
                    score += 1
                    stack.append((dist+1, up))

            if block[1] != board.shape[1] - 1 and not board[down]:
                numChoices += 1
                #  f.write("down ok\n")
                if not visited[down]:
                    visited[down] = True
                    score += 1
                    stack.append((dist+1, down))
            # discourage going down one lane paths (no escape)
            if numChoices < 2: 
                score -= 5
            f.write(str(numChoices) + "\n")

        return score 

    def _get_score(self, board, start, players):
        
        self_score = self._dfs_score(start, board)
        return self_score 

    def update(self, board, players, windowWidth, windowHeight):
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

        # assume all players (except self) continue one step in each direction to avoid head-on collisions
        coords = []
        old = []
        for player in players:
            ns = self._get_next(player, windowWidth, windowHeight)
            for n in ns:
                i = ind(n[0], n[1])
                old.append(board[i]) # keep track of what board used to be so we can set it back
                coords.append(i)
        for coord in coords:
            board[coord] = True
        
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
        
        # set board back
        for j in range(len(coords)):
            board[coords[j]] = old[j]

        #  f.write(str(directions) + "\n")
        #  print(str(directions))
        self.direction = max(directions, key=directions.get)


