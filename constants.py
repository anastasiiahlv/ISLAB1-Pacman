from enum import Enum

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 480
CELL_SIZE = 20
MAZE_WIDTH = WINDOW_WIDTH // CELL_SIZE
MAZE_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PINK = (255, 192, 203)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class DifficultyLevel(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
