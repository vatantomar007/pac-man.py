# game.py
"""
Main Game class that manages the game loop, state, and all game objects.
"""

import pygame
import sys
from settings import *
from maze import Maze
from pacman import Pacman
from ghost import Ghost


class Game:
    """
    Main game controller.
    
    Manages:
        - Game initialization and loop
        - All game objects (Pac-Man, ghosts, maze)
        - Game state (playing, paused, game over)
        - Score and lives display
        - Level progression
    """
    
    def __init__(self):
        """Initialize pygame and create game objects."""
        pygame.init()
        pygame.mixer.init()  # For sound effects
        
        # Create the game window
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pac-Man")
        
        # Game clock for consistent frame rate
        self.clock = pygame.time.Clock()
        
        # Load fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Initialize game state
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.game_state = 'ready'  # 'ready', 'playing', 'paused', 'game_over', 'level_complete'
        
        # Create game objects
        self._create_game_objects()
        
        # Load sounds (with error handling)
        self._load_sounds()
        
        # Power pellet animation timer
        self.power_pellet_timer = 0
    
    def _create_game_objects(self):
        """Create or reset all game objects."""
        # Create maze
        self.maze = Maze()
        
        # Create Pac-Man at starting position
        if self.maze.pacman_start:
            self.pacman = Pacman(self.maze.pacman_start)
        else:
            # Fallback position if not defined in maze
            self.pacman = Pacman((WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        
        # Create ghosts with different colors and AI types
        ghost_configs = [
            (RED, 'chase'),      # Blinky - direct chaser
            (PINK, 'patrol'),    # Pinky - patrol and ambush
            (CYAN, 'random'),    # Inky - unpredictable
            (ORANGE, 'random'),  # Clyde - random
        ]
        
        self.ghosts = []
        for i, (color, ai_type) in enumerate(ghost_configs):
            if i < len(self.maze.ghost_starts):
                ghost = Ghost(self.maze.ghost_starts[i], color, ai_type)
                self.ghosts.append(ghost)
    
    def _load_sounds(self):
        """Load sound effects with error handling."""
        self.sounds = {}
        
        sound_files = {
            'chomp': 'assets/chomp.wav',
            'death': 'assets/death.wav',
            'start': 'assets/start.wav',
            'power': 'assets/power.wav',
        }
        
        for name, path in sound_files.items():
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except:
                # Sound file not found - game will run without sounds
                self.sounds[name] = None
    
    def play_sound(self, sound_name):
        """Play a sound effect if available."""
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()
    
    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            # Handle events
            running = self._handle_events()
            
            # Update game state
            self._update()
            
            # Render everything
            self._draw()
            
            # Maintain consistent frame rate
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self):
        """
        Process pygame events.
        
        Returns:
            False if game should quit, True otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == 'playing':
                        self.game_state = 'paused'
                    elif self.game_state == 'paused':
                        self.game_state = 'playing'
                
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.game_state == 'ready':
                        self.game_state = 'playing'
                        self.play_sound('start')
                    elif self.game_state == 'game_over':
                        self._reset_game()
                    elif self.game_state == 'level_complete':
                        self._next_level()
                
                elif event.key == pygame.K_r:
                    # Quick restart
                    self._reset_game()
        
        return True
    
    def _update(self):
        """Update game logic."""
        if self.game_state != 'playing':
            return
        
        # Get keyboard state for Pac-Man movement
        keys = pygame.key.get_pressed()
        self.pacman.handle_input(keys)
        
        # Update Pac-Man
        self.pacman.update(self.maze)
        
        # Check pellet collection
        self._check_pellet_collection()
        
        # Update ghosts
        pacman_pos = self.pacman.get_position()
        for ghost in self.ghosts:
            ghost.update(self.maze, pacman_pos)
        
        # Check ghost collisions
        self._check_ghost_collisions()
        
        # Check level completion
        if self.maze.all_pellets_collected():
            self.game_state = 'level_complete'
        
        # Update power pellet animation
        self.power_pellet_timer = (self.power_pellet_timer + 1) % 30
    
    def _check_pellet_collection(self):
        """Check if Pac-Man collected any pellets."""
        pacman_pos = self.pacman.get_position()
        result = self.maze.remove_pellet(pacman_pos)
        
        if result == 'pellet':
            self.score += PELLET_SCORE
            self.play_sound('chomp')
        
        elif result == 'power':
            self.score += POWER_PELLET_SCORE
            self.play_sound('power')
            # Make all ghosts frightened
            for ghost in self.ghosts:
                ghost.set_frightened(300)  # 5 seconds at 60 FPS
    
    def _check_ghost_collisions(self):
        """Check collisions between Pac-Man and ghosts."""
        pacman_pos = self.pacman.get_position()
        
        for ghost in self.ghosts:
            if ghost.check_collision(pacman_pos, self.pacman.radius):
                if ghost.is_frightened:
                    # Eat the ghost!
                    self.score += 200
                    ghost.reset()
                else:
                    # Pac-Man dies
                    self._pacman_death()
                    return
    
    def _pacman_death(self):
        """Handle Pac-Man death."""
        self.play_sound('death')
        
        if self.pacman.lose_life():
            # Game over
            if self.score > self.high_score:
                self.high_score = self.score
            self.game_state = 'game_over'
        else:
            # Reset positions but continue game
            self.pacman.reset()
            for ghost in self.ghosts:
                ghost.reset()
    
    def _reset_game(self):
        """Reset the entire game."""
        self.score = 0
        self.level = 1
        self._create_game_objects()
        self.game_state = 'ready'
    
    def _next_level(self):
        """Progress to next level."""
        self.level += 1
        
        # Increase difficulty
        global GHOST_SPEED
        GHOST_SPEED = min(GHOST_SPEED + 0.3, PACMAN_SPEED)  # Cap at Pac-Man's speed
        
        # Reset maze and ghosts, keep Pac-Man's lives
        lives = self.pacman.lives
        self._create_game_objects()
        self.pacman.lives = lives
        
        self.game_state = 'playing'
    
    def _draw(self):
        """Render all game elements."""
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw maze
        self.maze.draw(self.screen)
        
        # Animated power pellets (pulsing effect)
        if self.power_pellet_timer < 15:
            for pos in self.maze.power_pellets:
                pygame.draw.circle(self.screen, BLACK, pos, 7)
                pygame.draw.circle(self.screen, WHITE, pos, 5)
        
        # Draw game objects
        self.pacman.draw(self.screen)
        for ghost in self.ghosts:
            ghost.draw(self.screen)
        
        # Draw UI
        self._draw_ui()
        
        # Draw overlay for different game states
        if self.game_state == 'ready':
            self._draw_ready_screen()
        elif self.game_state == 'paused':
            self._draw_paused_screen()
        elif self.game_state == 'game_over':
            self._draw_game_over_screen()
        elif self.game_state == 'level_complete':
            self._draw_level_complete_screen()
        
        # Update display
        pygame.display.flip()
    
    def _draw_ui(self):
        """Draw score, lives, and level information."""
        # Score (top left)
        score_text = self.font_small.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, WINDOW_HEIGHT - 25))
        
        # High score (top center)
        high_score_text = self.font_small.render(f"HIGH: {self.high_score}", True, WHITE)
        high_rect = high_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 15))
        self.screen.blit(high_score_text, high_rect)
        
        # Level (top right area)
        level_text = self.font_small.render(f"LEVEL: {self.level}", True, WHITE)
        self.screen.blit(level_text, (WINDOW_WIDTH - 100, WINDOW_HEIGHT - 25))
        
        # Lives (as Pac-Man icons)
        for i in range(self.pacman.lives):
            life_x = 10 + i * 25
            life_y = WINDOW_HEIGHT - 50
            pygame.draw.circle(self.screen, YELLOW, (life_x + 10, life_y), 8)
    
    def _draw_ready_screen(self):
        """Draw the ready/start screen overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_large.render("PAC-MAN", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        self.screen.blit(title, title_rect)
        
        # Instructions
        start_text = self.font_medium.render("Press SPACE or ENTER to Start", True, WHITE)
        start_rect = start_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(start_text, start_rect)
        
        # Controls
        controls = [
            "Arrow Keys or WASD to Move",
            "ESC to Pause",
            "R to Restart"
        ]
        for i, text in enumerate(controls):
            control_text = self.font_small.render(text, True, WHITE)
            control_rect = control_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50 + i * 25))
            self.screen.blit(control_text, control_rect)
    
    def _draw_paused_screen(self):
        """Draw the paused overlay."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("PAUSED", True, YELLOW)
        pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)
        
        resume_text = self.font_small.render("Press ESC to Resume", True, WHITE)
        resume_rect = resume_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(resume_text, resume_rect)
    
    def _draw_game_over_screen(self):
        """Draw the game over overlay."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        self.screen.blit(game_over_text, game_over_rect)
        
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        if self.score >= self.high_score and self.score > 0:
            new_high = self.font_medium.render("NEW HIGH SCORE!", True, YELLOW)
            new_high_rect = new_high.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
            self.screen.blit(new_high, new_high_rect)
        
        restart_text = self.font_small.render("Press SPACE or ENTER to Restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80))
        self.screen.blit(restart_text, restart_rect)
    
    def _draw_level_complete_screen(self):
        """Draw the level complete overlay."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        complete_text = self.font_large.render(f"LEVEL {self.level} COMPLETE!", True, YELLOW)
        complete_rect = complete_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        self.screen.blit(complete_text, complete_rect)
        
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        next_text = self.font_small.render("Press SPACE or ENTER for Next Level", True, WHITE)
        next_rect = next_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(next_text, next_rect)
