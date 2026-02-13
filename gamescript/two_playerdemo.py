# two_playerdemo.py
# Updated two-player demo using advanced AI and shared core configuration

import pygame
import time
import random
from .tetris_logic import TetrisGame
from .tetris_ai import AdvancedAIController
from .two_player_core import TwoPlayerCore
from .visual_effects import DynamicBackground
from .graphics import draw_text

class FallbackEffect:
    """Fallback class for visual effects when core components fail"""
    def update(self): pass
    def draw(self, screen, x=0, y=0): pass
    def get_offset(self): return (0, 0)

class FallbackRenderer:
    """Fallback renderer for when sprite system fails"""
    def draw_current_piece(self, game, offset_x=0, offset_y=0):
        pass

class TwoPlayerDemo:
    """
    Two-player Tetris demo with advanced AI and optimized shared configuration.
    Uses the new two_player_core for all graphics and shared functionality.
    """
    
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.clock = pygame.time.Clock()
        
        # Initialize shared core configuration
        try:
            self.core = TwoPlayerCore(screen, settings)
        except Exception as e:
            # Fallback if TwoPlayerCore fails
            print(f"Warning: TwoPlayerCore failed to initialize: {e}")
            self.core = None
        
        # Initialize two Tetris games
        self.game_p1 = TetrisGame(width=10, height=20)
        self.game_p2 = TetrisGame(width=10, height=20)
        
        # Create player components using shared core
        if self.core:
            try:
                self.p1_components = self.core.create_player_components(1)
                self.p2_components = self.core.create_player_components(2)
                
                # Setup renderer offsets
                self.core.setup_player_renderer(self.p1_components, 1)
                self.core.setup_player_renderer(self.p2_components, 2)
            except Exception as e:
                print(f"Warning: Failed to create player components: {e}")
                self.p1_components = self.create_fallback_components()
                self.p2_components = self.create_fallback_components()
        else:
            self.p1_components = self.create_fallback_components()
            self.p2_components = self.create_fallback_components()
        
        # Initialize dynamic background
        self.dynamic_background = DynamicBackground(screen.get_width(), screen.get_height())
        
        # Game state
        self.running = True
        
        # Initialize advanced AI controllers with different difficulties for variety
        self.p1_ai = AdvancedAIController(difficulty='master')
        self.p2_ai = AdvancedAIController(difficulty='hard')
        
        # Initialize game speeds - slightly different for each player
        self.game_p1.game_speed = 500  # milliseconds
        self.game_p2.game_speed = 550  # milliseconds
        
        # Demo timing
        self.demo_start_time = pygame.time.get_ticks()
    
    def create_fallback_components(self):
        """Create fallback components when core fails"""
        return {
            'last_move_down_time': time.time(),
            'next_move_time': pygame.time.get_ticks(),
            'screen_shake': FallbackEffect(),
            'combo_animator': FallbackEffect(),
            'particle_system': FallbackEffect(),
            'renderer': FallbackRenderer()
        }
    
    def run(self):
        """Run the two-player demo"""
        while self.running:
            current_time = pygame.time.get_ticks()
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Clear the screen
            self.screen.fill((0, 0, 0))
            
            # Update dynamic background
            max_level = max(self.game_p1.level, self.game_p2.level)
            self.dynamic_background.update(max_level)
            self.dynamic_background.draw(self.screen)
            
            # Update player games
            elapsed = current_time - self.demo_start_time
            
            # Start player 1 immediately
            if elapsed > 1000:  # 1 second delay
                self.update_player_game(self.game_p1, self.p1_components, 
                                       self.p1_ai, 1, current_time)
            
            # Start player 2 with delay
            if elapsed > 2000:  # 2 second delay
                self.update_player_game(self.game_p2, self.p2_components,
                                       self.p2_ai, 2, current_time)
            
            # Draw all game elements
            self.draw_all_elements(current_time)
            
            # Draw title and instructions
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()
            
            draw_text(self.screen, "VERSUS", 48, (255, 255, 100), 
                     screen_width // 2, 650, "assets/fonts/tetrisfont.ttf")
            
            draw_text(self.screen, "Presiona ESC para volver", 20, (200, 200, 200), 
                     screen_width // 2, screen_height - 40)
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        # Cleanup
        if self.core:
            self.core.cleanup()
    
    def update_player_game(self, game, components, ai_controller, player_num, current_time):
        """Update the game state for a player using advanced AI"""
        
        # Reset game if over
        if game.game_over:
            game.reset()
            ai_controller.current_plan = None
            ai_controller.last_piece_type = None
            return
        
        # Handle line clear animation
        if hasattr(game, 'animating_clear') and game.animating_clear:
            if self.core:
                self.core.update_line_clear_animation(game, components, player_num)
            return
        
        # Auto-drop based on game speed
        last_move_down_time = components['last_move_down_time']
        move_delay = game.game_speed / 1000.0
        
        if time.time() - last_move_down_time > move_delay:
            try:
                if hasattr(game, 'move_down') and not game.move_down():
                    # Play landing sound
                    if self.core:
                        self.core.play_sound_for_player('landing', player_num)
                    
                    # Fix piece and handle line clears
                    if hasattr(game, 'fix_piece'):
                        line_clear_result = game.fix_piece()
                        
                        if line_clear_result and self.core:
                            self.core.handle_line_clear_effects(game, line_clear_result, 
                                                               components, player_num)
            except Exception as e:
                print(f"Error in game update: {e}")
            
            # Update last move time
            components['last_move_down_time'] = time.time()
        
        # Ensure game has a current piece
        if not hasattr(game, 'piece_type') or game.piece_type is None:
            try:
                game.new_piece()
            except:
                return
        
        # Use advanced AI for moves
        if current_time > components['next_move_time']:
            action = ai_controller.get_next_action(game, current_time, player_num)
            
            if action:
                action_executed = self.execute_ai_action(game, action, player_num)
                
                # Play sound effects
                if action_executed and self.core:
                    self.play_action_sound(action, player_num)
                
                # Set next move time with variation for natural gameplay
                base_delay = 120  # Slightly slower for better visibility
                if action == 'hard_drop':
                    base_delay = 200  # Longer delay after drops
                elif action in ['left', 'right']:
                    base_delay = 80   # Faster for movement
                
                delay_variation = 40
                delay = random.uniform(base_delay, base_delay + delay_variation)
                
                if player_num == 2:
                    delay *= 1.2  # Player 2 slightly slower
                
                components['next_move_time'] = current_time + delay
            else:
                # If no action, set shorter delay to try again soon
                components['next_move_time'] = current_time + 50
    
    def execute_ai_action(self, game, action, player_num):
        """Execute AI action and return success status"""
        try:
            if action == 'left':
                return game.move_left()
            elif action == 'right':
                return game.move_right()
            elif action == 'rotate':
                return game.rotate()
            elif action == 'rotate_inv':
                return game.rotate_inv()
            elif action == 'down':
                return game.move_down(is_soft_drop=True)
            elif action == 'hard_drop':
                drop_result = game.drop()
                # Handle piece fixing and line clears
                line_clear_result = game.fix_piece()
                if line_clear_result and self.core:
                    components = self.p1_components if player_num == 1 else self.p2_components
                    self.core.handle_line_clear_effects(game, line_clear_result, 
                                                       components, player_num)
                return True
            elif action == 'hold':
                return game.hold_piece()
        except Exception as e:
            print(f"Error executing AI action {action}: {e}")
            pass
        return False
    
    def play_action_sound(self, action, player_num):
        """Play sound for AI action"""
        sound_map = {
            'left': 'move',
            'right': 'move',
            'rotate': 'rotate',
            'rotate_inv': 'rotate',
            'down': 'soft_drop',
            'hard_drop': 'hard_drop',
            'hold': 'hold'
        }
        
        sound_name = sound_map.get(action)
        if sound_name:
            self.core.play_sound_for_player(sound_name, player_num)
    
    def draw_all_elements(self, current_time):
        """Draw all game elements for both players"""
        
        # Update visual effects
        for components in [self.p1_components, self.p2_components]:
            components['screen_shake'].update()
            components['combo_animator'].update()
            components['particle_system'].update()
        
        # Draw player 1 elements
        shake_x_p1, shake_y_p1 = self.p1_components['screen_shake'].get_offset()
        
        # Draw board frame for player 1
        frame_x = self.core.p1_offset_x - 17
        frame_y = self.core.offset_y - 17
        frame_width = self.game_p1.width * self.core.block_size + 34
        frame_height = self.game_p1.height * self.core.block_size + 34
        
        scaled_frame_p1 = pygame.transform.scale(self.core.p1_board_frame, (frame_width, frame_height))
        self.screen.blit(scaled_frame_p1, (frame_x + shake_x_p1, frame_y + shake_y_p1))
        
        # Draw game field for player 1
        self.core.draw_field_without_frame(self.game_p1, self.p1_components['renderer'], 
                                          shake_x_p1, shake_y_p1)
        self.p1_components['renderer'].draw_current_piece(self.game_p1, 
                                                         offset_x=shake_x_p1, offset_y=shake_y_p1)
        
        # Draw particle effects for player 1
        self.p1_components['particle_system'].draw(self.screen, self.core.p1_offset_x, self.core.offset_y)
        
        # Draw combo animations for player 1
        combo_center_x_p1 = self.core.p1_offset_x + (self.game_p1.width * self.core.block_size) // 2
        combo_center_y_p1 = self.core.offset_y + (self.game_p1.height * self.core.block_size) // 2
        self.p1_components['combo_animator'].draw(self.screen, combo_center_x_p1, combo_center_y_p1)
        
        # Draw hold and next pieces for player 1
        self.core.draw_hold_piece(self.game_p1, 1, self.p1_components)
        self.core.draw_next_pieces(self.game_p1, 1, self.p1_components)
        
        # Draw player 2 elements
        shake_x_p2, shake_y_p2 = self.p2_components['screen_shake'].get_offset()
        
        # Draw board frame for player 2
        frame_x = self.core.p2_offset_x - 17
        frame_y = self.core.offset_y - 17
        
        scaled_frame_p2 = pygame.transform.scale(self.core.p2_board_frame, (frame_width, frame_height))
        self.screen.blit(scaled_frame_p2, (frame_x + shake_x_p2, frame_y + shake_y_p2))
        
        # Draw game field for player 2
        self.core.draw_field_without_frame(self.game_p2, self.p2_components['renderer'], 
                                          shake_x_p2, shake_y_p2)
        self.p2_components['renderer'].draw_current_piece(self.game_p2, 
                                                         offset_x=shake_x_p2, offset_y=shake_y_p2)
        
        # Draw particle effects for player 2
        self.p2_components['particle_system'].draw(self.screen, self.core.p2_offset_x, self.core.offset_y)
        
        # Draw combo animations for player 2
        combo_center_x_p2 = self.core.p2_offset_x + (self.game_p2.width * self.core.block_size) // 2
        combo_center_y_p2 = self.core.offset_y + (self.game_p2.height * self.core.block_size) // 2
        self.p2_components['combo_animator'].draw(self.screen, combo_center_x_p2, combo_center_y_p2)
        
        # Draw hold and next pieces for player 2
        self.core.draw_hold_piece(self.game_p2, 2, self.p2_components)
        self.core.draw_next_pieces(self.game_p2, 2, self.p2_components)
        
        # Draw player info
        self.core.draw_player_info(self.game_p1, 1)
        self.core.draw_player_info(self.game_p2, 2)


def start_two_player_demo(screen, settings):
    """Entry point for the two-player demo mode"""
    demo = TwoPlayerDemo(screen, settings)
    demo.run()