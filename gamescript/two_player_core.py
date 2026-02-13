# two_player_core.py
# Core configuration and shared utilities for all two-player modes

import pygame
import time
import random
import os
from .tetris_logic import TetrisGame, SHAPES, COLORS
from .visual_effects import ParticleSystem, ScreenShake, ComboAnimator, DynamicBackground
from .graphics import TetrisRenderer, draw_text, BLACK, WHITE, GRAY
from .debug_utils import debugger

class TwoPlayerCore:
    """
    Core configuration and shared functionality for all two-player Tetris modes.
    Contains all graphics settings, visual effects, and common game logic.
    """
    
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.clock = pygame.time.Clock()
        
        # Screen dimensions
        self.screen_width, self.screen_height = screen.get_size()
        
        # Block size for rendering - optimized for two-player layout
        self.block_size = 30
        
        # Calculate offsets for both game boards - centered layout
        board_width = 10 * self.block_size
        self.separation = 240  # Space between boards
        self.p1_offset_x = (self.screen_width // 2) - board_width - self.separation
        self.p2_offset_x = (self.screen_width // 2) + self.separation
        self.offset_y = (self.screen_height - 20 * self.block_size) // 2
        
        # Initialize graphics assets
        self._load_graphics_assets()
        
        # Initialize audio with shared settings
        self._setup_audio()
        
        # Game timing configuration
        self.timing_config = {
            'p1_spawn_delay': 0,
            'p2_spawn_delay': 1500,  # 1.5 second stagger
            'base_move_delay': 80,
            'ai_delay_variation': 100,
            'animation_duration_base': 250,
            'animation_duration_min': 100
        }
    
    def _load_graphics_assets(self):
        """Load all graphics assets with fallback handling"""
        # Define frame dimensions
        frame_width = 10 * self.block_size + 34
        frame_height = 20 * self.block_size + 34
        
        # Load board frames
        self.p1_board_frame = self._load_asset_with_fallback(
            'assets/img/boardframe.png', 
            (frame_width, frame_height), 
            (100, 100, 255)
        )
        
        self.p2_board_frame = self._load_asset_with_fallback(
            'assets/img/boardframe2.png', 
            (frame_width, frame_height), 
            (255, 100, 100)
        )
        
        # Load UI frames
        self.hold_frame = self._load_asset_with_fallback(
            'assets/img/holdframe.png', 
            (100, 80), 
            (80, 80, 100)
        )
        
        self.p1_next_frame = self._load_asset_with_fallback(
            'assets/img/nextframe.png', 
            (100, 200), 
            (100, 80, 100)
        )
        
        self.p2_next_frame = self._load_asset_with_fallback(
            'assets/img/nextframe2p.png', 
            (100, 200), 
            (100, 80, 100)
        )
    
    def _load_asset_with_fallback(self, path, size, color):
        """Load an asset with fallback surface creation"""
        try:
            return pygame.image.load(path)
        except Exception as e:
            debugger.error(f"Could not load {path}: {e}")
            surface = pygame.Surface(size)
            surface.fill(color)
            return surface
    
    def _setup_audio(self):
        """Setup audio with shared settings"""
        from .audio_manager import audio_manager
        self.audio_manager = audio_manager
        
        # Create shared sound effect wrapper
        class SoundEffect:
            def __init__(self, sound_name, audio_manager, probability=1.0):
                self.sound_name = sound_name
                self.audio_manager = audio_manager
                self.probability = probability
            
            def play(self, force=False):
                if force or random.random() < self.probability:
                    if self.sound_name and self.audio_manager.audio_available:
                        self.audio_manager.play_sound(self.sound_name)
            
            def set_volume(self, vol):
                pass
        
        # Initialize sound effects with reduced probability for player 2
        self.sounds = {
            'move': SoundEffect("move", audio_manager, 0.3),
            'rotate': SoundEffect("rotate", audio_manager, 0.3),
            'hard_drop': SoundEffect("harddrop", audio_manager, 0.3),
            'soft_drop': SoundEffect("softdrop", audio_manager, 0.3),
            'landing': SoundEffect("landing", audio_manager, 0.3),
            'single': SoundEffect("single", audio_manager, 0.3),
            'double': SoundEffect("double", audio_manager, 0.3),
            'triple': SoundEffect("triple", audio_manager, 0.3),
            'tetris': SoundEffect("tetris", audio_manager, 0.3),
            'tspin': SoundEffect("tspin", audio_manager, 0.3),
            'hold': SoundEffect("hold", audio_manager, 0.3),
            'perfect': SoundEffect("perfect", audio_manager, 1.0)
        }
        
        # Setup music
        current_song = self.settings.get('current_song', 'tetris.mp3')
        audio_manager.play_music(os.path.splitext(current_song)[0], -1)
        audio_manager.set_master_volume(self.settings.get('volume_general', 1.0))
        audio_manager.set_music_volume(self.settings.get('volume_bgm', 1.0))
        audio_manager.set_sfx_volume(self.settings.get('volume_sfx', 1.0))
        audio_manager.set_mute(self.settings.get('mute', False))
    
    def restore_main_menu_music(self):
        """
        Restore main menu music when exiting two-player modes.
        This function should be called when returning to the main menu from any two-player game mode.
        """
        try:
            # Stop current music
            self.audio_manager.stop_music()
            
            # Play main menu music
            self.audio_manager.play_music("menu", -1)
            
            debugger.debug("Música del menú principal restaurada desde modo de dos jugadores")
            
        except Exception as e:
            debugger.error(f"Error al restaurar música del menú principal: {e}")
    
    def create_player_components(self, player_num):
        """Create visual effect components for a player"""
        return {
            'renderer': TetrisRenderer(self.screen, block_size=self.block_size),
            'particle_system': ParticleSystem(),
            'screen_shake': ScreenShake(),
            'combo_animator': ComboAnimator(),
            'last_move_down_time': time.time(),
            'next_move_time': 0
        }
    
    def setup_player_renderer(self, components, player_num):
        """Configure renderer offset for a player"""
        if player_num == 1:
            components['renderer'].offset_x = self.p1_offset_x
        else:
            components['renderer'].offset_x = self.p2_offset_x
        components['renderer'].offset_y = self.offset_y
    
    def play_sound_for_player(self, sound_name, player_num, force=False):
        """Play sound effect for a specific player"""
        if player_num == 1:
            force = True  # Always play sounds for player 1
        self.sounds[sound_name].play(force)
    
    def handle_line_clear_effects(self, game, line_clear_result, components, player_num):
        """Shared line clear effect handling"""
        screen_shake = components['screen_shake']
        combo_animator = components['combo_animator']
        
        # Handle T-spin effects
        is_tspin = line_clear_result.get("is_tspin", False)
        if is_tspin:
            self.play_sound_for_player('tspin', player_num)
            shake_intensity = 8 if game.level_up_event else 6
            shake_duration = 30 if game.level_up_event else 25
            screen_shake.start_shake(shake_intensity, shake_duration)
            
            # Add T-spin animation
            mini_suffix = ""
            if "tspin_type" in line_clear_result and line_clear_result["tspin_type"] == "T-spin mini":
                mini_suffix = " Mini"
            
            tspin_type = "Single"
            if line_clear_result['count'] == 2:
                tspin_type = "Double"
            elif line_clear_result['count'] == 3:
                tspin_type = "Triple"
            combo_animator.add_tspin_animation(f"{tspin_type}{mini_suffix}")
        
        # Handle perfect clear
        is_perfect = line_clear_result.get("is_perfect", False)
        if is_perfect:
            self.play_sound_for_player('perfect', player_num, force=True)
            combo_animator.add_perfect_animation()
            screen_shake.start_shake(10, 35)
        
        # Handle line clear sounds and animations
        if line_clear_result["is_tetris"]:
            self.play_sound_for_player('tetris', player_num)
            combo_animator.add_tetris_animation()
            if not is_tspin and not is_perfect:
                screen_shake.start_shake(7, 25)
        elif line_clear_result["count"] == 3:
            self.play_sound_for_player('triple', player_num)
        elif line_clear_result["count"] == 2:
            self.play_sound_for_player('double', player_num)
        elif line_clear_result["count"] == 1:
            self.play_sound_for_player('single', player_num)
    
    def update_line_clear_animation(self, game, components, player_num):
        """Shared line clear animation update"""
        now = pygame.time.get_ticks()
        
        # Calculate animation duration
        base_duration = self.timing_config['animation_duration_base']
        min_duration = self.timing_config['animation_duration_min'] if game.level >= 10 else 150
        anim_duration = max(min_duration, base_duration - (game.level * 15))
        
        # Track elapsed time
        current_time = now
        elapsed = current_time - game.clear_animation_time
        
        # Fix invalid animation time
        if elapsed < 0 or elapsed > 2000:
            game.clear_animation_time = current_time - anim_duration
            elapsed = anim_duration
        
        # Create particles for cleared lines
        if elapsed < 80:
            particle_system = components['particle_system']
            for line in game.lines_to_clear:
                for x in range(game.width):
                    block_type = game.field[line][x]
                    if block_type != 0:
                        color = COLORS[block_type]
                        particle_count = min(5, max(3, 6 - game.level//3))
                        particle_system.add_particles_for_line_clear(
                            x * self.block_size,
                            line * self.block_size,
                            self.block_size,
                            color,
                            count=particle_count
                        )
        
        # Complete animation
        if elapsed >= anim_duration:
            screen_shake = components['screen_shake']
            combo_animator = components['combo_animator']
            
            if len(game.lines_to_clear) == 4:
                shake_intensity = min(5, 3 + game.level//3)
                screen_shake.start_shake(shake_intensity, 20)
            
            combo_animator.add_combo(len(game.lines_to_clear))
            
            try:
                game.finish_clear_animation()
                game.new_piece()
            except Exception:
                game.lines_to_clear = []
                game.animating_clear = False
                game.new_piece()
        
        # Safety timeout
        if elapsed > 1000:
            try:
                game.finish_clear_animation() 
                game.new_piece()
            except Exception:
                game.lines_to_clear = []
                game.animating_clear = False
                game.new_piece()
    
    def draw_field_without_frame(self, game, renderer, offset_x=0, offset_y=0):
        """Draw game field without frame (shared implementation)"""
        background_width = game.width * renderer.block_size
        background_height = game.height * renderer.block_size
        
        # Create background
        background_surface = pygame.Surface((background_width, background_height))
        background_surface.fill((20, 20, 30))
        renderer.screen.blit(background_surface, (renderer.offset_x + offset_x, renderer.offset_y + offset_y))
        
        # Draw grid
        grid_color = (50, 50, 70)
        
        # Horizontal lines
        for y in range(game.height + 1):
            start_x = renderer.offset_x + offset_x
            end_x = renderer.offset_x + game.width * renderer.block_size + offset_x
            line_y = renderer.offset_y + y * renderer.block_size + offset_y
            pygame.draw.line(renderer.screen, grid_color, (start_x, line_y), (end_x, line_y), 1)
        
        # Vertical lines
        for x in range(game.width + 1):
            line_x = renderer.offset_x + x * renderer.block_size + offset_x
            start_y = renderer.offset_y + offset_y
            end_y = renderer.offset_y + game.height * renderer.block_size + offset_y
            pygame.draw.line(renderer.screen, grid_color, (line_x, start_y), (line_x, end_y), 1)
        
        # Draw blocks
        for y in range(game.height):
            for x in range(game.width):
                block = game.field[y][x]
                if block != 0:
                    renderer.draw_block(x, y, block, offset_x=offset_x, offset_y=offset_y)
    
    def draw_hold_piece(self, game, player_num, components):
        """Draw hold piece with shared positioning"""
        box_width = self.block_size * 5
        box_height = self.block_size * 3
        frame_width = box_width + 40
        frame_height = box_height + 40
        
        screen_center_x = self.screen_width // 2
        
        if player_num == 1:
            hold_frame_x = screen_center_x - frame_width - 20
        else:
            hold_frame_x = screen_center_x + 20
        
        hold_frame_y = self.offset_y - 15
        
        # Draw frame
        hold_frame_scaled = pygame.transform.scale(self.hold_frame, (frame_width, frame_height))
        self.screen.blit(hold_frame_scaled, (hold_frame_x, hold_frame_y))
        
        # Draw piece
        if game.hold_piece_type is not None:
            hold_x = hold_frame_x + 20
            hold_y = hold_frame_y + 20
            renderer = components['renderer']
            renderer.draw_hold_piece(game, hold_x, hold_y, box_width, box_height)
    
    def draw_next_pieces(self, game, player_num, components):
        """Draw next pieces with shared positioning"""
        box_width = self.block_size * 5
        box_height = self.block_size * 3
        frame_width = box_width + 40
        frame_height = box_height + 40
        
        screen_center_x = self.screen_width // 2
        
        if player_num == 1:
            next_x = screen_center_x - frame_width - 20
            next_frame = self.p1_next_frame
        else:
            next_x = screen_center_x + 20
            next_frame = self.p2_next_frame
        
        hold_frame_y = self.offset_y - 15
        next_y = hold_frame_y + frame_height + 10
        
        # Draw frame
        next_frame_total_height = 360
        next_frame_scaled = pygame.transform.scale(next_frame, (frame_width, next_frame_total_height))
        self.screen.blit(next_frame_scaled, (next_x, next_y))
        
        # Draw pieces
        if hasattr(game, 'next_pieces') and game.next_pieces:
            next_piece_x = next_x + 20
            next_piece_y = next_y + 20
            renderer = components['renderer']
            
            renderer.draw_next_piece(game, next_piece_x, next_piece_y, box_width, box_height, piece_index=0)
            
            if len(game.next_pieces) >= 3:
                next_box_width = 120
                
                if player_num == 1:
                    next2_x = next_piece_x + (box_width - next_box_width) // 2 - 15
                    next3_x = next_piece_x + (box_width - next_box_width) // 2 - 15
                else:
                    next2_x = next_piece_x + (box_width - next_box_width) // 2 + 15
                    next3_x = next_piece_x + (box_width - next_box_width) // 2 + 15
                
                next2_y = next_piece_y + frame_height - 20
                next3_y = next2_y + frame_height - 20
                
                if len(game.next_pieces) > 1:
                    renderer.draw_next_piece(game, next2_x, next2_y, next_box_width, box_height, piece_index=1)
                if len(game.next_pieces) > 2:
                    renderer.draw_next_piece(game, next3_x, next3_y, next_box_width, box_height, piece_index=2)
    
    def draw_player_info(self, game, player_num):
        """Draw player info with shared positioning"""
        screen_center_x = self.screen_width // 2
        
        if player_num == 1:
            info_x = screen_center_x - 120
            player_name = "PLAYER 1"
        else:
            info_x = screen_center_x + 120
            player_name = "PLAYER 2"
        
        info_y = self.offset_y + 500
        
        draw_text(self.screen, player_name, 24, (255, 255, 100), info_x, info_y, "assets/fonts/tetrisfont.ttf")
        draw_text(self.screen, f"Puntuación: {game.score}", 18, WHITE, info_x, info_y + 25, "assets/fonts/mainfont.ttf")
        draw_text(self.screen, f"Líneas: {game.lines_cleared}", 18, WHITE, info_x, info_y + 45, "assets/fonts/mainfont.ttf")
    
    def cleanup(self):
        """Cleanup resources"""
        self.audio_manager.stop_music()


def start_two_player_game(screen, settings, mode="versus"):
    """
    Start a two-player game with the specified mode.
    This is a wrapper function that should be called from two_player_mode.py
    """
    # Create core instance
    core = TwoPlayerCore(screen, settings)
    
    try:
        # Import the specific game mode implementation
        if mode == "versus":
            from .two_player_versus import run_versus_mode
            run_versus_mode(screen, settings, core)
        elif mode == "cooperative":
            from .two_player_coop import run_cooperative_mode
            run_cooperative_mode(screen, settings, core)
        else:
            debugger.warning(f"Modo de juego desconocido: {mode}")
            
    except ImportError as e:
        debugger.error(f"No se pudo importar el módulo del modo {mode}: {e}")
        # Fallback implementation or error message
        draw_text(screen, f"Modo {mode} no implementado", 32, (255, 255, 255), 
                 screen.get_width() // 2, screen.get_height() // 2)
        pygame.display.flip()
        pygame.time.wait(2000)
    
    finally:
        # Always restore main menu music when exiting any two-player mode
        core.restore_main_menu_music()
        core.cleanup()