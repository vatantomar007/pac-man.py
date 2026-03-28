# maze.py
"""
Maze class handles the level layout, walls, and pellet positions.
Uses a text-based grid where each character represents a tile type.
"""

import pygame
from settings import *


class Maze:
    """
    Represents the game maze/level.
    
    Tile legend:
        '#' = Wall
        '.' = Pellet (small dot)
        'o' = Power pellet (big dot)
        ' ' = Empty space
        'P' = Pac-Man starting position
        'G' = Ghost starting position
    """
    
    def __init__(self):
        # Classic Pac-Man inspired layout
        # 28 characters wide, 31 rows tall
        self.layout = [
            "############################",
            "#............##............#",
            "#.####.#####.##.#####.####.#",
            "#o####.#####.##.#####.####o#",
            "#.####.#####.##.#####.####.#",
            "#..........................#",
            "#.####.##.########.##.####.#",
            "#.####.##.########.##.####.#",
            "#......##....##....##......#",
            "######.##### ## #####.######",
            "     #.##### ## #####.#     ",
            "     #.##    G     ##.#     ",
            "     #.## ######## ##.#     ",
            "######.## #      # ##.######",
            "      .   #  GG  #   .      ",
            "######.## #      # ##.######",
            "     #.## ######## ##.#     ",
            "     #.##          ##.#     ",
            "     #.## ######## ##.#     ",
            "######.## ######## ##.######",
            "#............##............#",
            "#.####.#####.##.#####.####.#",
            "#.####.#####.##.#####.####.#",
            "#o..##.......P .......##..o#",
            "###.##.##.########.##.##.###",
            "###.##.##.########.##.##.###",
            "#......##....##....##......#",
            "#.##########.##.##########.#",
            "#.##########.##.##########.#",
            "#..........................#",
            "############################",
        ]
        
        # Parse the layout to find positions and count pellets
        self.walls = []           # List of wall rectangles
        self.pellets = []         # List of pellet positions
        self.power_pellets = []   # List of power pellet positions
        self.pacman_start = None  # Pac-Man's starting position
        self.ghost_starts = []    # Ghost starting positions
        
        self._parse_layout()
    
    def _parse_layout(self):
        """
        Convert the text layout into game objects.
        Creates rectangles for walls and stores positions for other elements.
        """
        for row_index, row in enumerate(self.layout):
            for col_index, cell in enumerate(row):
                # Calculate pixel position (center of cell)
                x = col_index * CELL_SIZE + CELL_SIZE // 2
                y = row_index * CELL_SIZE + CELL_SIZE // 2
                
                if cell == '#':
                    # Create a wall rectangle
                    wall_rect = pygame.Rect(
                        col_index * CELL_SIZE,
                        row_index * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                    self.walls.append(wall_rect)
                
                elif cell == '.':
                    # Regular pellet position
                    self.pellets.append((x, y))
                
                elif cell == 'o':
                    # Power pellet position
                    self.power_pellets.append((x, y))
                
                elif cell == 'P':
                    # Pac-Man starting position
                    self.pacman_start = (x, y)
                
                elif cell == 'G':
                    # Ghost starting position
                    self.ghost_starts.append((x, y))
    
    def draw(self, screen):
        """
        Render the maze walls and pellets.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw walls as blue rectangles
        for wall in self.walls:
            pygame.draw.rect(screen, BLUE, wall)
            # Add a slight border effect
            pygame.draw.rect(screen, (50, 50, 255), wall, 1)
        
        # Draw regular pellets as small circles
        for pellet_pos in self.pellets:
            pygame.draw.circle(screen, WHITE, pellet_pos, 3)
        
        # Draw power pellets as larger, pulsing circles
        # (pulsing effect handled by animation in Game class)
        for power_pos in self.power_pellets:
            pygame.draw.circle(screen, WHITE, power_pos, 7)
    
    def is_wall(self, x, y):
        """
        Check if a pixel position collides with any wall.
        
        Args:
            x, y: Pixel coordinates to check
            
        Returns:
            True if position is inside a wall, False otherwise
        """
        # Create a small rect at the position to check collision
        check_rect = pygame.Rect(x - 5, y - 5, 10, 10)
        
        for wall in self.walls:
            if wall.colliderect(check_rect):
                return True
        return False
    
    def get_cell(self, x, y):
        """
        Convert pixel coordinates to grid cell coordinates.
        
        Args:
            x, y: Pixel coordinates
            
        Returns:
            Tuple of (column, row) in grid coordinates
        """
        col = int(x // CELL_SIZE)
        row = int(y // CELL_SIZE)
        return (col, row)
    
    def get_cell_center(self, col, row):
        """
        Get the pixel coordinates of a cell's center.
        
        Args:
            col, row: Grid cell coordinates
            
        Returns:
            Tuple of (x, y) pixel coordinates
        """
        x = col * CELL_SIZE + CELL_SIZE // 2
        y = row * CELL_SIZE + CELL_SIZE // 2
        return (x, y)
    
    def remove_pellet(self, position):
        """
        Remove a pellet at the given position if it exists.
        
        Args:
            position: Tuple of (x, y) coordinates
            
        Returns:
            'pellet' if regular pellet removed,
            'power' if power pellet removed,
            None if no pellet at position
        """
        # Check regular pellets (with some tolerance)
        for pellet in self.pellets[:]:  # Copy list to allow removal
            if abs(pellet[0] - position[0]) < 10 and abs(pellet[1] - position[1]) < 10:
                self.pellets.remove(pellet)
                return 'pellet'
        
        # Check power pellets
        for power in self.power_pellets[:]:
            if abs(power[0] - position[0]) < 10 and abs(power[1] - position[1]) < 10:
                self.power_pellets.remove(power)
                return 'power'
        
        return None
    
    def all_pellets_collected(self):
        """Check if all pellets have been collected (level complete)."""
        return len(self.pellets) == 0 and len(self.power_pellets) == 0
    
    def reset_pellets(self):
        """Reset all pellets for a new level/game."""
        self.pellets = []
        self.power_pellets = []
        self._parse_layout()
