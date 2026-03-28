# settings.py
"""
Game settings and constants.
All configurable values are stored here for easy modification.
"""

# Window dimensions
WINDOW_WIDTH = 560   # 28 cells * 20 pixels
WINDOW_HEIGHT = 620  # 31 cells * 20 pixels (extra for score display)

# Grid settings
CELL_SIZE = 20       # Size of each maze cell in pixels
GRID_WIDTH = 28      # Number of cells horizontally
GRID_HEIGHT = 31     # Number of cells vertically

# Colors (RGB format)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (33, 33, 222)
RED = (255, 0, 0)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)

# Game settings
FPS = 60                    # Frames per second
PACMAN_SPEED = 3            # Pixels per frame
GHOST_SPEED = 2             # Slightly slower than Pac-Man
STARTING_LIVES = 3

# Scoring
PELLET_SCORE = 10
POWER_PELLET_SCORE = 50

# Animation settings
PACMAN_ANIMATION_SPEED = 5  # Frames between animation updates
GHOST_ANIMATION_SPEED = 10
