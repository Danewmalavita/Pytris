# debug_utils.py
import traceback
import sys
import time
import os

class GameDebugger:
    def __init__(self, log_file="game_debug.log"):
        self.log_file = log_file
        # Create or clear the log file
        with open(self.log_file, 'w') as f:
            f.write(f"=== PyTris Debug Log ===\nStarted at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Set up exception hook to catch unhandled exceptions
        self.original_hook = sys.excepthook
        sys.excepthook = self.exception_hook
    
    def log(self, message, level="INFO"):
        """Log a message with timestamp"""
        timestamp = time.strftime('%H:%M:%S')
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {level}: {message}\n")
    
    def debug(self, message):
        self.log(message, "DEBUG")
    
    def warning(self, message):
        self.log(message, "WARNING")
    
    def error(self, message):
        self.log(message, "ERROR")
    
    def exception_hook(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions and log them"""
        self.error(f"Uncaught {exc_type.__name__}: {exc_value}")
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_text = ''.join(tb_lines)
        self.log(f"Traceback:\n{tb_text}", "ERROR")
        
        # Call the original exception hook
        self.original_hook(exc_type, exc_value, exc_traceback)
    
    def log_game_state(self, game):
        """Log the current game state to help debug issues"""
        self.debug(f"Game Level: {game.level}, Score: {game.score}, Lines: {game.lines_cleared}")
        self.debug(f"Game Speed: {game.game_speed}ms, Animating: {game.animating_clear}")
        if hasattr(game, 'lines_to_clear') and game.lines_to_clear:
            self.debug(f"Lines to clear: {game.lines_to_clear}")
    
    def log_performance(self, function_name, start_time):
        """Log performance of a function"""
        elapsed = time.time() - start_time
        if elapsed > 0.1:  # Only log if it took more than 100ms
            self.warning(f"Performance: {function_name} took {elapsed:.4f} seconds")

# Create a global debugger instance
debugger = GameDebugger()