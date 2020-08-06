from enum import Enum, auto
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

step_size = 50

# function for indexing positions
def ind(x, y):
    return (int(x/step_size), int(y/step_size))
   
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
LIMEGREENHOVER = (173,255,10)
GREEN = (0,141,0)
PINK = (242,136,164)
P1COLOR = (250,234,52)
P1HOVER = (P1COLOR[0]-20, P1COLOR[1]-20, P1COLOR[2]-20)
P2COLOR = (139,121,173)
P2HOVER = (P2COLOR[0]-20, P2COLOR[1]-20, P2COLOR[2]-20)
P3COLOR = (214,149,103)
P3HOVER = (P3COLOR[0]-20, P3COLOR[1]-20, P3COLOR[2]-20)
P4COLOR = (217,121,160)
P4HOVER = (P4COLOR[0]-20, P4COLOR[1]-20, P4COLOR[2]-20)
LIGHTGREY = (150,150,150)
LIGHTGREYHOVER = (LIGHTGREY[0]-20, LIGHTGREY[1]-20, LIGHTGREY[2]-20)
GREY = (80,80,80)
GREYHOVER = (60,60,60)
