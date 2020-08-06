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

    def _bfs_score(self, start, board, direc, numSteps, nextFive=None):
        visited = np.full(board.shape, False)
        q = deque()
        
        score = 0
        # Append nodes of the form (distance, coordinate)
        dist = 0
        q.append((dist, start))
        while q and dist < numSteps: 
            node = q.popleft()
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
                if not visited[left]:
                    visited[left] = True
                    score += 1
                    q.append((dist+1, left))
                
            if block[0] != board.shape[0] - 1 and not board[right]:
                numChoices += 1
                if not visited[right]:
                    visited[right] = True
                    score += 1
                    q.append((dist+1, right))
            
            if block[1] != 0 and not board[up]:
                numChoices += 1
                if not visited[up]:
                    visited[up] = True
                    score += 1
                    q.append((dist+1, up))

            if block[1] != board.shape[1] - 1 and not board[down]:
                numChoices += 1
                if not visited[down]:
                    visited[down] = True
                    score += 1
                    q.append((dist+1, down))
            # discourage going down one lane paths (no escape)
            if numChoices < 2: 
                score -= 5

        # encourage cutting players off
        if nextFive:
            snf = []
            if direc == Direction.LEFT:
                for i in range(0, 5):
                    if start[0] - i < 0: 
                        break
                    n = (start[0] - i, start[1]) 
                    if i == 0 or not board[n]: snf.append(n)
                    else: break
            elif direc == Direction.RIGHT:
                for i in range(0, 5):
                    if start[0] + i > board.shape[0] - 1: 
                        break
                    n = (start[0] + i, start[1])
                    if i == 0 or not board[n]: snf.append(n) 
                    else: break
            elif direc == Direction.UP:
                for i in range(0, 5):
                    if start[1] - i < 0: 
                        break
                    n = (start[0], start[1] - i)
                    if i == 0 or not board[n]: snf.append(n)
                    else: break
            else:
                for i in range(0,5):
                    if start[1] + i > board.shape[1] - 1: 
                        break
                    n = (start[0], start[1] + i)
                    if i == 0 or not board[n]: snf.append(n)
                    else: break
            #  print("dir " + str(direc) + " snf:")
            #  print(snf) # DEBUG
            #  print("nf")
            #  print(nextFive)
            for nf in nextFive:
                for i in range(len(nf)):
                    pos = nf[i]
                    if pos in snf and snf.index(pos) <= i: 
                        score += 1000
                        #  print('cutoff')
        
        return score 

    def _get_next_five(self, board, players, windowWidth, windowHeight):
        nfs = []
        for player in players:
            nf = []
            if player.x == self.x and player.y == self.y: 
                continue
            if player.direction == Direction.LEFT:
                for i in range(2, 6):
                    if player.x - (step_size * i) < 0: 
                        break
                    n = ind(max(player.x - (step_size * i), 0), player.y)
                    if not board[n]: nf.append(n)
                    else: 
                        break
            elif player.direction == Direction.RIGHT:
                for i in range(2, 6):
                    if player.x + (step_size * i) > windowWidth - step_size: 
                        break
                    n = ind(min(player.x + (step_size * i), windowWidth - step_size), player.y)
                    if not board[n]: nf.append(n)
                    else: 
                        break
            elif player.direction == Direction.UP:
                for i in range(2, 6):
                    if player.y - (step_size * i) < 0: 
                        break
                    n = ind(player.x, max(player.y - (step_size * i), 0))
                    if not board[n]: nf.append(n)
                    else: 
                        break
            else: 
                for i in range(2, 6):
                    if player.y + (step_size * i) > windowHeight - step_size: 
                        break
                    n = ind(player.x, min(player.y + (step_size * i), windowHeight - step_size))
                    if not board[n]: nf.append(n)
                    else: 
                        break
            nfs.append(nf)
        return nfs

    def _get_score(self, board, start, players, nextFive, direc):
        self_score = self._bfs_score(start, board, direc, 101, nextFive)
        return self_score 

    def update(self, board, players, windowWidth, windowHeight):
        # do nothing if player is human
        if not self.is_bot:
            return 

        # initialize preferences to -1000
        directions = {
            Direction.LEFT: float('-inf'),
            Direction.RIGHT: float('-inf'),
            Direction.UP: float('-inf'),
            Direction.DOWN: float('-inf') 
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
        
        # get next five straight moves for all players (except self)
        nextFive = self._get_next_five(board, players, windowWidth, windowHeight) 
        #  print(nextFive) # DEBUG 

        validDirections = self._get_valid_directions(board, windowWidth, windowHeight)
        for direction in validDirections:
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
            directions[direction] = self._get_score(board, start, players, nextFive, direction)
            board[start] = False
        
        # set board back
        for j in range(len(coords)):
            board[coords[j]] = old[j]

        # if the best direction is "splitting" ie it will divide the board into two halves, discourage it
        if directions[Direction.UP] > 0 and (self.y <= step_size or board[ind(self.x, self.y-step_size*2)]) \
                and Direction.LEFT in validDirections and Direction.RIGHT in validDirections:
            #  print('up split') # debug
            directions[Direction.UP] /= 2
        if directions[Direction.LEFT] > 0 and (self.x <= step_size or board[ind(self.x-step_size*2, self.y)]) \
                and Direction.UP in validDirections and Direction.DOWN in validDirections:
            #  print('left split') # debug
            directions[Direction.LEFT] /= 2
        if directions[Direction.RIGHT] > 0 and (self.x >= windowWidth - step_size*2 or \
                board[ind(self.x+step_size*2, self.y)]) and Direction.UP in validDirections \
                and Direction.DOWN in validDirections:
            #  print('right split') # debug
            directions[Direction.RIGHT] /= 2
        if directions[Direction.DOWN] > 0 and (self.y >= windowHeight - step_size*2 or \
                board[ind(self.x, self.y+step_size*2)]) and Direction.LEFT in validDirections and \
                Direction.RIGHT in validDirections:
            directions[Direction.DOWN] /= 2
            #  print('down split') # debug
            
        # encourage going in the same direction
        directions[self.direction] *= 1.05

        self.direction = max(directions, key=directions.get)
        #  print(str(directions)) # DEBUG


