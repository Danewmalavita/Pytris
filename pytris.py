import curses
import random
import time
import threading
import winsound
import os
import sys

#Check the libraries
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not available. MIDI music will not work.")
    print("Install pygame with: pip install pygame")

#Define draw settings
class TetrisGame:
    def __init__(self):
        self.board_width = 10
        self.board_height = 20
        self.board = [[0 for _ in range(self.board_width)] for _ in range(self.board_height)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 0.5  # seconds
        self.window = None
        
        # Sound settings
        self.sound_enabled = True
        self.music_thread = None
        self.music_playing = False
        self.pygame_initialized = False
        self.midi_file = self.get_resource_path("tetris.mid")
        self.music_volume = 0.7
        self._music_lock = threading.Lock()
        
        # Current piece
        self.current_piece = None
        self.piece_x = 0
        self.piece_y = 0
        
        # Next piece
        self.next_piece = None
        
        # Tetris pieces (tetrominoes)
        self.pieces = {
            'I': [['.....',
                   '..#..',
                   '..#..',
                   '..#..',
                   '..#..'],
                  ['.....',
                   '.....',
                   '####.',
                   '.....',
                   '.....']],
            
            'O': [['.....',
                   '.....',
                   '.##..',
                   '.##..',
                   '.....']],
            
            'T': [['.....',
                   '.....',
                   '.#...',
                   '###..',
                   '.....'],
                  ['.....',
                   '.....',
                   '.#...',
                   '.##..',
                   '.#...'],
                  ['.....',
                   '.....',
                   '.....',
                   '###..',
                   '.#...'],
                  ['.....',
                   '.....',
                   '.#...',
                   '##...',
                   '.#...']],
            
            'S': [['.....',
                   '.....',
                   '.##..',
                   '##...',
                   '.....'],
                  ['.....',
                   '.#...',
                   '.##..',
                   '..#..',
                   '.....']],
            
            'Z': [['.....',
                   '.....',
                   '##...',
                   '.##..',
                   '.....'],
                  ['.....',
                   '..#..',
                   '.##..',
                   '.#...',
                   '.....']],
            
            'J': [['.....',
                   '.#...',
                   '.#...',
                   '##...',
                   '.....'],
                  ['.....',
                   '.....',
                   '#....',
                   '###..',
                   '.....'],
                  ['.....',
                   '.##..',
                   '.#...',
                   '.#...',
                   '.....'],
                  ['.....',
                   '.....',
                   '###..',
                   '..#..',
                   '.....']],
            
            'L': [['.....',
                   '..#..',
                   '..#..',
                   '.##..',
                   '.....'],
                  ['.....',
                   '.....',
                   '###..',
                   '#....',
                   '.....'],
                  ['.....',
                   '##...',
                   '.#...',
                   '.#...',
                   '.....'],
                  ['.....',
                   '.....',
                   '..#..',
                   '###..',
                   '.....']]}
        
        self.piece_colors = {
            'I': 1, 'O': 2, 'T': 3, 'S': 4, 'Z': 5, 'J': 6, 'L': 7
        }

    def get_resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except AttributeError:
            # Running in development mode
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

#Define BGM and SE
    def play_sound_effect(self, sound_type):
        """Play sound effects using Windows beeps"""
        if not self.sound_enabled:
            return
            
        def play_async():
            try:
                if sound_type == 'line_clear':
                    # Line clear sound - ascending notes
                    winsound.Beep(523, 100)  # C5
                    winsound.Beep(659, 100)  # E5
                    winsound.Beep(784, 100)  # G5
                    winsound.Beep(1047, 200) # C6
                elif sound_type == 'tetris':
                    # Tetris (4 lines) - special fanfare
                    winsound.Beep(1047, 150) # C6
                    winsound.Beep(784, 150)  # G5
                    winsound.Beep(659, 150)  # E5
                    winsound.Beep(523, 150)  # C5
                    winsound.Beep(659, 150)  # E5
                    winsound.Beep(784, 150)  # G5
                    winsound.Beep(1047, 300) # C6
                elif sound_type == 'rotate':
                    # Piece rotation - quick beep
                    winsound.Beep(880, 50)   # A5
                elif sound_type == 'move':
                    # Piece movement - subtle tick
                    winsound.Beep(440, 30)   # A4
                elif sound_type == 'drop':
                    # Piece drop - thud sound
                    winsound.Beep(220, 100)  # A3
                elif sound_type == 'game_over':
                    # Game over - descending notes
                    winsound.Beep(523, 200)  # C5
                    winsound.Beep(494, 200)  # B4
                    winsound.Beep(440, 200)  # A4
                    winsound.Beep(392, 400)  # G4
            except (OSError, RuntimeError, winsound.error):
                pass  # Ignore sound errors
                
        # Play sound in background thread to avoid blocking
        sound_thread = threading.Thread(target=play_async, daemon=True)
        sound_thread.start()

#PLay tetris MID (V_0.2) Doesn't sound on restart or compile (Pending check ;))        
    def init_pygame_mixer(self):
        """Initialize pygame mixer for MIDI playback"""
        if not PYGAME_AVAILABLE or self.pygame_initialized:
            return False
            
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self.pygame_initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize pygame mixer: {e}")
            return False
    
    def play_tetris_theme(self):
        """Play the Tetris theme using MIDI file or fallback to system beeps"""
        if not self.sound_enabled:
            return
            
        def theme_loop():
            if PYGAME_AVAILABLE and self.init_pygame_mixer():
                # Try to play MIDI file
                try:
                    if os.path.exists(self.midi_file):
                        # Stop any currently playing music first
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(self.midi_file)
                        pygame.mixer.music.set_volume(self.music_volume)
                        pygame.mixer.music.play(-1)  # Loop indefinitely
                        
                        # Wait while music is playing
                        while self.music_playing and not self.game_over:
                            if not pygame.mixer.music.get_busy():
                                # Music stopped, restart it
                                if self.music_playing and not self.game_over:
                                    pygame.mixer.music.load(self.midi_file)
                                    pygame.mixer.music.play(-1)
                            time.sleep(0.1)
                        return
                    else:
                        print(f"MIDI file not found: {self.midi_file}")
                except (OSError, RuntimeError, pygame.error) as e:
                    print(f"Error playing MIDI: {e}")

#Emergency beep sounds (don't work propertly on laptop, but works, LoL) Implemented on alpha 1.0         
            # Fallback to system beeps if MIDI fails
            print("Falling back to system beep music...")
            notes = [
                # Main melody - first part
                (659, 300), (494, 150), (523, 150), (587, 300), (523, 150), (494, 150),
                (440, 400), (440, 150), (523, 150), (659, 300), (587, 150), (523, 150),
                (494, 400), (494, 150), (523, 150), (587, 300), (659, 300),
                (523, 300), (440, 300), (440, 400),
                
                # Second part
                (587, 200), (698, 150), (880, 300), (784, 150), (698, 150),
                (659, 400), (523, 150), (659, 300), (587, 150), (523, 150),
                (494, 400), (494, 150), (523, 150), (587, 300), (659, 300),
                (523, 300), (440, 300), (440, 400),
            ]
            
            while self.music_playing and not self.game_over:
                try:
                    for freq, duration in notes:
                        if not self.music_playing or self.game_over:
                            break
                        winsound.Beep(freq, duration)
                        time.sleep(0.05)  # Small pause between notes
                    
                    # Pause before repeating
                    if self.music_playing and not self.game_over:
                        time.sleep(1)
                except (OSError, RuntimeError, winsound.error):
                    break  # Exit on any error
                    
        # Only start music if not already playing and sound is enabled
        with self._music_lock:
            # Check if we need to start music
            should_start = (self.sound_enabled and 
                          not self.music_playing and 
                          (self.music_thread is None or not self.music_thread.is_alive()))
            
            if should_start:
                self.music_playing = True
                self.music_thread = threading.Thread(target=theme_loop, daemon=True)
                self.music_thread.start()
            
    def stop_music(self):
        """Stop the background music with proper thread cleanup"""
        with self._music_lock:
            self.music_playing = False
            if PYGAME_AVAILABLE and self.pygame_initialized:
                try:
                    pygame.mixer.music.stop()
                except (OSError, RuntimeError, Exception):
                    pass
            
            # Wait for music thread to finish
            if self.music_thread and self.music_thread.is_alive():
                self.music_thread.join(timeout=0.5)
            
            # Reset thread reference after stopping
            self.music_thread = None
        
    def toggle_sound(self):
        """Toggle sound on/off"""
        self.sound_enabled = not self.sound_enabled
        if not self.sound_enabled:
            self.stop_music()
        else:
            # Ensure music is fully stopped before restarting
            self.stop_music()  # Stop any existing music first
            time.sleep(0.2)  # Wait longer for cleanup
            self.play_tetris_theme()

#Removes blinking on my AMD processor            
    def setup_game(self, stdscr):
        """Initialize the game window and settings"""
        self.window = stdscr
        curses.curs_set(0)
        curses.noecho()
        self.window.timeout(100)  # Increased timeout to 100ms for better responsiveness
        self.window.keypad(True)
        
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # I
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # O
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # T
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)   # S
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)     # Z
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)    # J
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)   # L
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_WHITE)   # Fixed blocks
        
        # Generate first pieces
        self.new_piece()
        self.next_piece = self.get_random_piece()
        
        # Start background music
        self.play_tetris_theme()

#Game main functions to work (Moves, colliders, etc)       
    def get_random_piece(self):
        """Get a random piece type"""
        return random.choice(list(self.pieces.keys()))
        
    def new_piece(self):
        """Create a new falling piece"""
        if self.next_piece:
            piece_type = self.next_piece
            self.next_piece = self.get_random_piece()
        else:
            piece_type = self.get_random_piece()
            
        self.current_piece = {
            'type': piece_type,
            'rotation': 0,
            'shape': self.pieces[piece_type][0]
        }
        
        self.piece_x = self.board_width // 2 - 2
        self.piece_y = 0
        
        # Check if game over
        if not self.is_valid_position(self.piece_x, self.piece_y, self.current_piece['shape']):
            self.game_over = True
            self.stop_music()
            self.play_sound_effect('game_over')
            
    def is_valid_position(self, x, y, shape):
        """Check if piece position is valid"""
        for py, row in enumerate(shape):
            for px, cell in enumerate(row):
                if cell == '#':
                    new_x = x + px
                    new_y = y + py
                    
                    # Check boundaries
                    if (new_x < 0 or new_x >= self.board_width or 
                        new_y >= self.board_height):
                        return False
                        
                    # Check collision with existing blocks
                    if new_y >= 0 and self.board[new_y][new_x]:
                        return False
                        
        return True
        
    def place_piece(self):
        """Place the current piece on the board"""
        piece_type = self.current_piece['type']
        color = self.piece_colors[piece_type]
        
        for py, row in enumerate(self.current_piece['shape']):
            for px, cell in enumerate(row):
                if cell == '#':
                    board_x = self.piece_x + px
                    board_y = self.piece_y + py
                    if 0 <= board_y < self.board_height and 0 <= board_x < self.board_width:
                        self.board[board_y][board_x] = color
                        
    def clear_lines(self):
        """Clear completed lines and return number cleared"""
        lines_to_clear = []
        
        for y in range(self.board_height):
            if all(self.board[y]):
                lines_to_clear.append(y)
                
        # Remove completed lines in reverse order to avoid index shifting
        for y in reversed(lines_to_clear):
            del self.board[y]
            self.board.insert(0, [0 for _ in range(self.board_width)])
            
        return len(lines_to_clear)

#the rotation magic        
    def rotate_piece(self):
        """Rotate the current piece"""
        piece_type = self.current_piece['type']
        rotations = self.pieces[piece_type]
        
        # Try next rotation
        new_rotation = (self.current_piece['rotation'] + 1) % len(rotations)
        new_shape = rotations[new_rotation]
        
        # Check if rotation is valid
        if self.is_valid_position(self.piece_x, self.piece_y, new_shape):
            self.current_piece['rotation'] = new_rotation
            self.current_piece['shape'] = new_shape
            return True
            
        # Try wall kicks (move left/right to make rotation fit)
        for dx in [-1, 1, -2, 2]:
            if self.is_valid_position(self.piece_x + dx, self.piece_y, new_shape):
                self.current_piece['rotation'] = new_rotation
                self.current_piece['shape'] = new_shape
                self.piece_x += dx
                return True
                
        return False
        
    def move_piece(self, dx, dy):
        """Move the current piece"""
        new_x = self.piece_x + dx
        new_y = self.piece_y + dy
        
        if self.is_valid_position(new_x, new_y, self.current_piece['shape']):
            self.piece_x = new_x
            self.piece_y = new_y
            return True
        return False
        
    def drop_piece(self):
        """Drop piece to bottom"""
        while self.move_piece(0, 1):
            pass
            
    def update_game(self, dt):
        """Update game state"""
        if self.game_over:
            return
            
        # Handle falling
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            if not self.move_piece(0, 1):
                # Piece has landed
                self.place_piece()
                
                # Clear lines
                cleared = self.clear_lines()
                if cleared > 0:
                    # Play sound effects for line clears
                    if cleared == 4:
                        self.play_sound_effect('tetris')  # Special sound for Tetris
                    else:
                        self.play_sound_effect('line_clear')
                        
                    # Score calculation (classic Tetris scoring)
                    line_scores = {1: 40, 2: 100, 3: 300, 4: 1200}
                    self.score += line_scores.get(cleared, 0) * (self.level + 1)
                    self.lines_cleared += cleared
                    
                    # Level up every 10 lines
                    self.level = min(self.lines_cleared // 10 + 1, 20)
                    self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.02)
                    
                # Get new piece
                self.new_piece()
                self.play_sound_effect('drop')  # Play drop sound when piece lands
                
            self.fall_time = 0
            
    def get_input(self):
        """Handle player input"""
        key = self.window.getch()
        
        if key == ord('q') or key == ord('Q'):
            self.stop_music()
            self.game_over = True
            return
        elif key == ord('m') or key == ord('M'):
            # Toggle music
            self.toggle_sound()
            return
            
        if not self.current_piece or self.game_over:
            return
            
        if key == curses.KEY_LEFT or key == ord('a') or key == ord('A'):
            if self.move_piece(-1, 0):
                self.play_sound_effect('move')
        elif key == curses.KEY_RIGHT or key == ord('d') or key == ord('D'):
            if self.move_piece(1, 0):
                self.play_sound_effect('move')
        elif key == curses.KEY_DOWN or key == ord('s') or key == ord('S'):
            if self.move_piece(0, 1):
                self.score += 1  # Bonus for soft drop
                self.play_sound_effect('move')
        elif key == curses.KEY_UP or key == ord('w') or key == ord('W'):
            if self.rotate_piece():
                self.play_sound_effect('rotate')
        elif key == ord(' '):
            # Hard drop
            original_y = self.piece_y
            # Calculate distance before dropping to fix scoring bug
            distance = 0
            temp_y = self.piece_y
            while self.is_valid_position(self.piece_x, temp_y + 1, self.current_piece['shape']):
                temp_y += 1
                distance += 1
            
            self.drop_piece()
            self.score += distance * 2  # Bonus for hard drop
            self.play_sound_effect('drop')
            
            
    def draw_board(self):
        """Draw the game board with all pieces (no blinking)"""
        start_x = 2
        start_y = 2
        
        # Draw border
        for y in range(self.board_height + 2):
            self.window.addch(start_y + y, start_x - 1, '|')
            self.window.addch(start_y + y, start_x + self.board_width * 2, '|')
            
        for x in range(self.board_width * 2 + 2):
            self.window.addch(start_y - 1, start_x - 1 + x, '-')
            self.window.addch(start_y + self.board_height, start_x - 1 + x, '-')
            
        # Create a composite view with both fixed pieces and current piece
        for y in range(self.board_height):
            for x in range(self.board_width):
                screen_x = start_x + x * 2
                screen_y = start_y + y
                
                # Check if current piece occupies this position
                piece_here = False
                piece_color = None
                
                if self.current_piece:
                    for py, row in enumerate(self.current_piece['shape']):
                        for px, cell in enumerate(row):
                            if (cell == '#' and 
                                self.piece_x + px == x and 
                                self.piece_y + py == y):
                                piece_here = True
                                piece_color = self.piece_colors[self.current_piece['type']]
                                break
                        if piece_here:
                            break
                
                # Draw fixed piece, current piece, or empty space
                if self.board[y][x]:  # Fixed piece
                    color = self.board[y][x]
                    self.window.addstr(screen_y, screen_x, '██', curses.color_pair(color))
                elif piece_here:  # Current falling piece
                    self.window.addstr(screen_y, screen_x, '██', curses.color_pair(piece_color))
                else:  # Empty space
                    self.window.addstr(screen_y, screen_x, '  ')
                    
                        
    def draw_next_piece(self):
        """Draw the next piece preview (fixed)"""
        if not self.next_piece:
            return
            
        start_x = 26
        start_y = 4
        
        self.window.addstr(start_y - 1, start_x, "Next:")
        
        # Get terminal dimensions for bounds checking
        max_y, max_x = self.window.getmaxyx()
        
        # Clear the next piece area (5x5 grid to accommodate I-piece)
        for y in range(5):
            for x in range(10):  # 5 blocks * 2 chars each
                draw_y = start_y + y
                draw_x = start_x + x
                # Ensure we don't draw outside terminal bounds
                if draw_y < max_y - 1 and draw_x < max_x - 1:
                    try:
                        self.window.addstr(draw_y, draw_x, ' ')
                    except curses.error:
                        pass
        
        # Draw the next piece
        if self.next_piece in self.pieces:
            shape = self.pieces[self.next_piece][0]
            color = self.piece_colors[self.next_piece]
            
            # Calculate offset to center the piece in the preview area
            offset_x = 0
            offset_y = 0
            
            # Special positioning for different pieces
            if self.next_piece == 'I':
                offset_x = 0  # I-piece looks better flush left
                offset_y = 1  # Move down a bit to center vertically
            elif self.next_piece == 'O':
                offset_x = 1  # Center the O-piece
                offset_y = 1
            else:
                offset_x = 0  # Other pieces
                offset_y = 0
            
            for py, row in enumerate(shape):
                for px, cell in enumerate(row):
                    if cell == '#':
                        draw_x = start_x + (px + offset_x) * 2
                        draw_y = start_y + py + offset_y
                        
                        # Make sure we don't draw outside the preview area
                        if (draw_y >= start_y and draw_y < start_y + 5 and 
                            draw_x >= start_x and draw_x < start_x + 10):
                            try:
                                self.window.addstr(draw_y, draw_x, '██', curses.color_pair(color))
                            except curses.error:
                                pass
                    
    def draw_ui(self):
        """Draw the user interface"""
        start_x = 26
        start_y = 2
        
        # Game info
        self.window.addstr(start_y, start_x, f"Score: {self.score}")
        self.window.addstr(start_y + 1, start_x, f"Level: {self.level}")
        self.window.addstr(start_y + 2, start_x, f"Lines: {self.lines_cleared}")
        
        # Controls (moved down to accommodate larger next piece area)
        controls_y = 13
        self.window.addstr(controls_y, start_x, "Controls:")
        self.window.addstr(controls_y + 1, start_x, "A/D: Move")
        self.window.addstr(controls_y + 2, start_x, "S: Soft drop")
        self.window.addstr(controls_y + 3, start_x, "W: Rotate")
        self.window.addstr(controls_y + 4, start_x, "Space: Hard drop")
        self.window.addstr(controls_y + 5, start_x, "M: Toggle music (Beta)")
        self.window.addstr(controls_y + 6, start_x, "Q: Quit")
        
        # Sound status
        sound_status = "ON" if self.sound_enabled else "OFF"
        self.window.addstr(controls_y + 8, start_x, f"Sound: {sound_status}")
        
    def draw_game_over(self):
        """Draw game over screen"""
        self.window.addstr(10, 8, "GAME OVER!")
        self.window.addstr(11, 6, f"Final Score: {self.score}")
        self.window.addstr(12, 5, "Press 'r' to restart")
        self.window.addstr(13, 7, "or 'q' to quit")
        
    def reset_game(self):
        """Reset the game to initial state"""
        # Stop current music first
        self.stop_music()
        
        # Reset game state
        self.board = [[0 for _ in range(self.board_width)] for _ in range(self.board_height)]
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 0.5
        self.new_piece()
        self.next_piece = self.get_random_piece()
        
        # Wait a moment for music to fully stop, then restart
        if self.sound_enabled:
            time.sleep(0.1)  # Brief pause
            self.play_tetris_theme()
    
    def run(self, stdscr):
        """Main game loop"""
        self.setup_game(stdscr)
        last_time = time.time()
        
        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Draw everything in one pass to prevent blinking
            self.draw_board()
            
            if not self.game_over:
                self.get_input()
                self.update_game(dt)
                
                # Draw UI elements that need updating
                self.draw_next_piece()
                self.draw_ui()
                
            else:
                # Game over state
                self.draw_board()
                self.draw_game_over()
                
                key = self.window.getch()
                if key == ord('r') or key == ord('R'):
                    self.reset_game()
                elif key == ord('q') or key == ord('Q'):
                    break
                    
            self.window.refresh()
            time.sleep(0.016)  # ~60 FPS

def main():
    """Main function to start the game"""
    try:
        game = TetrisGame()
        curses.wrapper(game.run)
    except KeyboardInterrupt:
        print("\nGame interrupted. Thanks for playing!")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Make sure your terminal supports colors and is large enough.")
    finally:
        # Make sure to stop music when exiting
        try:
            if 'game' in locals():
                game.stop_music()
            if PYGAME_AVAILABLE:
                pygame.mixer.quit()
        except:
            pass


if __name__ == "__main__":
    print("====================")
    print("")
    print("🧩 Python Tetris 🧩")
    print("")
    print("Ver. Beta 1.0")
    print("")
    print("2025 (c) Danew")
    print("")
    print("====================")
    print("Controls:")
    print("  A/D or Left/Right: Move piece")
    print("  S or Down: Soft drop")
    print("  W or Up: Rotate piece")
    print("  Space: Hard drop")
    print("  M: Toggle music on/off (Beta)")
    print("  Q: Quit game")
    print("  R: Restart (when game over)")
    print("")
    print("🎵 Features classic Tetris theme music from MIDI file! 🎵")
    print("Score points by clearing lines!")
    print("Game gets faster every 10 lines cleared.")
    print("")
    print("Press Enter to start...")
    input()
    main()

