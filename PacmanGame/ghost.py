# ghost.py
"""
Ghost enemy class with basic AI behaviors.
Different ghosts have different personalities (chase, random, patrol).
"""

import pygame
import random
import math
from settings import *


class Ghost:
    """
    Enemy ghost character with AI movement.
    
    Different AI types:
        'chase': Directly pursues Pac-Man
        'random': Moves randomly at intersections
        'patrol': Moves in a pattern, occasionally chases
    """
    
    def __init__(self, start_pos, color, ai_type='random'):
        """
        Initialize a ghost.
        
        Args:
            start_pos: Tuple of (x, y) starting coordinates
            color: RGB color tuple for this ghost
            ai_type: AI behavior type ('chase', 'random', or 'patrol')
        """
        self.start_pos = start_pos
        self.x, self.y = start_pos
        self.color = color
        self.ai_type = ai_type
        
        # Movement
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.speed = GHOST_SPEED
        
        # AI state
        self.is_frightened = False  # True when Pac-Man eats power pellet
        self.frightened_timer = 0
        
        # Animation
        self.animation_frame = 0
        self.animation_timer = 0
        self.wave_offset = random.randint(0, 100)  # For wavy bottom animation
        
        # Size
        self.radius = CELL_SIZE // 2 - 2
        
        # For patrol AI: store patrol points
        self.patrol_index = 0
        self.direction_timer = 0  # For random direction changes
    
    def update(self, maze, pacman_pos):
        """
        Update ghost position and AI decisions.
        
        Args:
            maze: Maze object for collision and pathfinding
            pacman_pos: Tuple of Pac-Man's (x, y) position
        """
        # Update frightened state
        if self.is_frightened:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.is_frightened = False
        
        # Determine movement based on AI type
        if self.is_frightened:
            self._frightened_ai(maze, pacman_pos)
        elif self.ai_type == 'chase':
            self._chase_ai(maze, pacman_pos)
        elif self.ai_type == 'random':
            self._random_ai(maze)
        else:  # patrol
            self._patrol_ai(maze, pacman_pos)
        
        # Apply movement
        self._move(maze)
        
        # Handle tunnel
        self._handle_tunnel()
        
        # Update animation
        self._update_animation()
    
    def _chase_ai(self, maze, pacman_pos):
        """
        AI that directly chases Pac-Man.
        At intersections, chooses the direction closest to Pac-Man.
        """
        # Check if at an intersection (can turn)
        if self._at_intersection(maze):
            possible_directions = self._get_valid_directions(maze)
            
            if possible_directions:
                # Choose direction that gets closest to Pac-Man
                best_direction = min(
                    possible_directions,
                    key=lambda d: self._distance_after_move(d, pacman_pos)
                )
                self.direction = best_direction
    
    def _random_ai(self, maze):
        """
        AI that chooses random directions at intersections.
        """
        # Increment timer for occasional random turns
        self.direction_timer += 1
        
        if self._at_intersection(maze) or self.direction_timer > 60:
            possible_directions = self._get_valid_directions(maze)
            
            if possible_directions:
                # Prefer not reversing unless it's the only option
                non_reverse = [d for d in possible_directions 
                              if d != self._reverse_direction()]
                
                if non_reverse:
                    self.direction = random.choice(non_reverse)
                else:
                    self.direction = random.choice(possible_directions)
                
                self.direction_timer = 0
    
    def _patrol_ai(self, maze, pacman_pos):
        """
        AI that patrols an area but will chase if Pac-Man is close.
        """
        # Calculate distance to Pac-Man
        dist_to_pacman = math.sqrt(
            (self.x - pacman_pos[0])**2 + (self.y - pacman_pos[1])**2
        )
        
        # If Pac-Man is close, chase
        if dist_to_pacman < 100:
            self._chase_ai(maze, pacman_pos)
        else:
            # Otherwise move randomly
            self._random_ai(maze)
    
    def _frightened_ai(self, maze, pacman_pos):
        """
        AI when ghost is frightened (runs away from Pac-Man).
        """
        if self._at_intersection(maze):
            possible_directions = self._get_valid_directions(maze)
            
            if possible_directions:
                # Choose direction that gets furthest from Pac-Man
                best_direction = max(
                    possible_directions,
                    key=lambda d: self._distance_after_move(d, pacman_pos)
                )
                self.direction = best_direction
    
    def _get_valid_directions(self, maze):
        """
        Get list of directions that don't lead into walls.
        
        Returns:
            List of valid direction tuples
        """
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        valid = []
        
        for d in directions:
            test_x = self.x + d[0] * CELL_SIZE
            test_y = self.y + d[1] * CELL_SIZE
            
            if not self._check_wall_collision(test_x, test_y, maze):
                valid.append(d)
        
        return valid
    
    def _at_intersection(self, maze):
        """
        Check if ghost is at an intersection (more than 2 valid directions).
        Also returns True if current direction is blocked.
        
        Returns:
            True if at intersection or blocked, False otherwise
        """
        # Check if roughly centered in a cell
        cell_center_x = (self.x // CELL_SIZE) * CELL_SIZE + CELL_SIZE // 2
        cell_center_y = (self.y // CELL_SIZE) * CELL_SIZE + CELL_SIZE // 2
        
        if abs(self.x - cell_center_x) > 3 or abs(self.y - cell_center_y) > 3:
            return False  # Not centered enough
        
        valid_directions = self._get_valid_directions(maze)
        
        # At intersection if 3+ options, or if current path is blocked
        if len(valid_directions) >= 3:
            return True
        if self.direction not in valid_directions and self._reverse_direction() not in valid_directions:
            return True
        if self.direction not in valid_directions:
            return True
            
        return False
    
    def _distance_after_move(self, direction, target_pos):
        """
        Calculate distance to target if ghost moves in given direction.
        
        Args:
            direction: Direction tuple to test
            target_pos: Position to measure distance to
            
        Returns:
            Distance as a float
        """
        test_x = self.x + direction[0] * CELL_SIZE
        test_y = self.y + direction[1] * CELL_SIZE
        
        return math.sqrt((test_x - target_pos[0])**2 + (test_y - target_pos[1])**2)
    
    def _reverse_direction(self):
        """Get the opposite of current direction."""
        return (-self.direction[0], -self.direction[1])
    
    def _move(self, maze):
        """
        Move ghost in current direction if possible.
        """
        speed = self.speed if not self.is_frightened else self.speed * 0.5
        
        new_x = self.x + self.direction[0] * speed
        new_y = self.y + self.direction[1] * speed
        
        if not self._check_wall_collision(new_x, new_y, maze):
            self.x = new_x
            self.y = new_y
        else:
            # Align to grid and find new direction
            self._align_to_grid()
    
    def _check_wall_collision(self, x, y, maze):
        """Check if position collides with walls."""
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
        """Snap to nearest grid cell center."""
        self.x = round(self.x / CELL_SIZE) * CELL_SIZE + CELL_SIZE // 2
        self.y = round(self.y / CELL_SIZE) * CELL_SIZE + CELL_SIZE // 2
    
    def _handle_tunnel(self):
        """Handle screen edge wrapping."""
        if self.x < 0:
            self.x = WINDOW_WIDTH
        elif self.x > WINDOW_WIDTH:
            self.x = 0
    
    def _update_animation(self):
        """Update animation state."""
        self.animation_timer += 1
        if self.animation_timer >= GHOST_ANIMATION_SPEED:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 2
    
    def draw(self, screen):
        """
        Render the ghost on screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Choose color based on state
        if self.is_frightened:
            # Flash white when almost done being frightened
            if self.frightened_timer < 60 and self.animation_frame == 1:
                color = WHITE
            else:
                color = BLUE
        else:
            color = self.color
        
        # Draw ghost body (rounded top, wavy bottom)
        # Main body circle
        pygame.draw.circle(
            screen, color,
            (int(self.x), int(self.y - 2)),
            self.radius
        )
        
        # Body rectangle
        body_rect = pygame.Rect(
            self.x - self.radius,
            self.y - 2,
            self.radius * 2,
            self.radius + 4
        )
        pygame.draw.rect(screen, color, body_rect)
        
        # Wavy bottom (3 bumps)
        wave_y = self.y + self.radius
        bump_width = (self.radius * 2) // 3
        
        for i in range(3):
            bump_x = self.x - self.radius + bump_width * i + bump_width // 2
            # Alternate bump direction based on animation
            bump_offset = 3 if (i + self.animation_frame) % 2 == 0 else -1
            pygame.draw.circle(
                screen, color,
                (int(bump_x), int(wave_y + bump_offset)),
                bump_width // 2
            )
        
        # Draw eyes
        eye_offset_x = 4
        eye_y = self.y - 4
        
        # White of eyes
        pygame.draw.circle(screen, WHITE, (int(self.x - eye_offset_x), int(eye_y)), 4)
        pygame.draw.circle(screen, WHITE, (int(self.x + eye_offset_x), int(eye_y)), 4)
        
        # Pupils (look in movement direction)
        pupil_offset_x = self.direction[0] * 2
        pupil_offset_y = self.direction[1] * 2
        
        if not self.is_frightened:
            pygame.draw.circle(
                screen, BLUE,
                (int(self.x - eye_offset_x + pupil_offset_x), int(eye_y + pupil_offset_y)),
                2
            )
            pygame.draw.circle(
                screen, BLUE,
                (int(self.x + eye_offset_x + pupil_offset_x), int(eye_y + pupil_offset_y)),
                2
            )
    
    def set_frightened(self, duration=300):
        """
        Set ghost to frightened mode.
        
        Args:
            duration: How many frames to stay frightened
        """
        self.is_frightened = True
        self.frightened_timer = duration
        # Reverse direction when frightened
        self.direction = self._reverse_direction()
    
    def get_position(self):
        """Return current position as tuple."""
        return (self.x, self.y)
    
    def reset(self):
        """Reset ghost to starting position."""
        self.x, self.y = self.start_pos
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.is_frightened = False
        self.frightened_timer = 0
    
    def check_collision(self, pacman_pos, pacman_radius):
        """
        Check if ghost collides with Pac-Man.
        
        Args:
            pacman_pos: Pac-Man's (x, y) position
            pacman_radius: Pac-Man's collision radius
            
        Returns:
            True if collision detected, False otherwise
        """
        dist = math.sqrt(
            (self.x - pacman_pos[0])**2 + (self.y - pacman_pos[1])**2
        )
        
        return dist < (self.radius + pacman_radius - 4)
