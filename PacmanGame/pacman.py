      # pacman.py
"""
Pac-Man player character class.
Handles movement, animation, and collision detection with walls.
"""

import pygame
import math
from settings import *

class Pacman:
    """
    The player-controlled Pac-Man character.
    """
    
    def __init__(self, start_pos):
        """Initialize Pac-Man at the starting position."""
        self.start_pos = start_pos
        self.x, self.y = start_pos
        
        # Direction vectors: (dx, dy)
        self.direction = (0, 0)       
        self.next_direction = (0, 0)  
        
        self.speed = PACMAN_SPEED
        self.lives = STARTING_LIVES
        
        # Animation state
        self.animation_timer = 0
        self.mouth_open = True 
        
        # Size for collision detection
        self.radius = CELL_SIZE // 2 - 2
    
    def handle_input(self, keys):
        """Process keyboard input and queue the next direction."""
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.next_direction = (0, -1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.next_direction = (0, 1)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.next_direction = (-1, 0)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.next_direction = (1, 0)

    def update(self, maze):
        """Update Pac-Man's position and animation."""
        # 1. Try to change to the queued direction
        if self.next_direction != (0, 0):
            if self._can_move(self.next_direction, maze):
                if self.direction != self.next_direction:
                    self._align_to_grid()
                    self.direction = self.next_direction
        
        # 2. Move in the current direction
        if self.direction != (0, 0):
            new_x = self.x + self.direction[0] * self.speed
            new_y = self.y + self.direction[1] * self.speed
            
            if not self._check_wall_collision(new_x, new_y, maze):
                self.x = new_x
                self.y = new_y
            else:
                self.direction = (0, 0)
                self._align_to_grid()
        
        self._handle_tunnel()
        self._update_animation()

    def _can_move(self, direction, maze):
        """Check if a tile-based move is possible."""
        current_col = int(self.x // CELL_SIZE)
        current_row = int(self.y // CELL_SIZE)
        
        next_col = current_col + direction[0]
        next_row = current_row + direction[1]
        
        return not maze.is_wall(next_col * CELL_SIZE + CELL_SIZE // 2, 
                                next_row * CELL_SIZE + CELL_SIZE // 2)

    def _check_wall_collision(self, x, y, maze):
        """Check if specific pixel coordinates hit a wall."""
        check_points = [
            (x - self.radius + 2, y - self.radius + 2),
            (x + self.radius - 2, y - self.radius + 2),
            (x - self.radius + 2, y + self.radius - 2),
            (x + self.radius - 2, y + self.radius - 2),
        ]
        for point in check_points:
            if maze.is_wall(point[0], point[1]):
                return True
        return False

    def _align_to_grid(self):
        """Snap Pac-Man to the nearest grid cell center."""
        self.x = (self.x // CELL_SIZE) * CELL_SIZE + CELL_SIZE // 2
        self.y = (self.y // CELL_SIZE) * CELL_SIZE + CELL_SIZE // 2

    def _handle_tunnel(self):
        """Handle wrapping through tunnels."""
        if self.x < 0:
            self.x = WINDOW_WIDTH
        elif self.x > WINDOW_WIDTH:
            self.x = 0

    def _update_animation(self):
        """Update the mouth animation."""
        if self.direction != (0, 0):
            self.animation_timer += 1
            if self.animation_timer >= PACMAN_ANIMATION_SPEED:
                self.animation_timer = 0
                self.mouth_open = not self.mouth_open

    def draw(self, screen):
        """Render Pac-Man on the screen."""
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
        if self.mouth_open and self.direction != (0, 0):
            self._draw_mouth(screen)

    def _draw_mouth(self, screen):
        """Draw Pac-Man's mouth as a triangle."""
        mouth_len = self.radius + 2
        mw = 8 # mouth width
        
        if self.direction == (1, 0):    # Right
            pts = [(self.x, self.y), (self.x + mouth_len, self.y - mw), (self.x + mouth_len, self.y + mw)]
        elif self.direction == (-1, 0):  # Left
            pts = [(self.x, self.y), (self.x - mouth_len, self.y - mw), (self.x - mouth_len, self.y + mw)]
        elif self.direction == (0, -1):  # Up
            pts = [(self.x, self.y), (self.x - mw, self.y - mouth_len), (self.x + mw, self.y - mouth_len)]
        elif self.direction == (0, 1):   # Down
            pts = [(self.x, self.y), (self.x - mw, self.y + mouth_len), (self.x + mw, self.y + mouth_len)]
        else:
            pts = [(self.x, self.y), (self.x + mouth_len, self.y - mw), (self.x + mouth_len, self.y + mw)]
        
        pygame.draw.polygon(screen, BLACK, pts)

    def get_position(self):
        return (self.x, self.y)

    def reset(self):
        self.x, self.y = self.start_pos
        self.direction = (0, 0)
        self.next_direction = (0, 0)

    def lose_life(self):
        self.lives -= 1
        return self.lives <= 0