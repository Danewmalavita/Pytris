# advanced_tetris_ai_fixed.py
# Fixed Advanced AI Controller for Tetris compatible with tetris_logic.py

import random
import copy
import time
from typing import Optional, Dict, List, Tuple, Any
from .tetris_logic import SHAPES, COLORS


class TetrisPiece:
    """
    Wrapper class to simulate a piece object that the AI expects
    """
    def __init__(self, piece_type, x, y, rotation):
        self.shape = piece_type
        self.x = x
        self.y = y
        self.rotation = rotation
        self.piece_type = piece_type
    
    def get_blocks(self):
        """Return the blocks of the current piece in relative coordinates"""
        shape = SHAPES[self.piece_type][self.rotation]
        blocks = []
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell != 0:
                    blocks.append((col_idx, row_idx))
        return blocks
    
    def rotate(self):
        """Rotate the piece clockwise"""
        self.rotation = (self.rotation + 1) % 4


class AdvancedAIController:
    """
    Advanced AI controller for Tetris with strategic planning and adaptive difficulty.
    Fixed to work with the actual tetris_logic.py structure.
    """
    
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty
        self.current_plan = None
        self.last_piece_type = None
        self.evaluation_cache = {}
        
        # Difficulty settings
        self.difficulty_settings = {
            'easy': {
                'think_time': 300,
                'lookahead_depth': 1,
                'mistake_chance': 0.20,
                'speed_multiplier': 1.8
            },
            'medium': {
                'think_time': 200,
                'lookahead_depth': 2,
                'mistake_chance': 0.12,
                'speed_multiplier': 1.4
            },
            'hard': {
                'think_time': 150,
                'lookahead_depth': 3,
                'mistake_chance': 0.06,
                'speed_multiplier': 1.1
            },
            'master': {
                'think_time': 100,
                'lookahead_depth': 4,
                'mistake_chance': 0.02,
                'speed_multiplier': 0.9
            }
        }
        
        self.settings = self.difficulty_settings.get(difficulty, self.difficulty_settings['medium'])
        
        # AI state
        self.last_action_time = 0
        self.current_target = None
        self.action_sequence = []
        self.thinking = False
        self.last_move_time = 0
        
        # Weights for board evaluation
        self.weights = {
            'height': -0.510066,
            'lines': 0.760666,
            'holes': -0.35663,
            'bumpiness': -0.184483,
            'aggregate_height': -0.5,
            'complete_lines': 1.0,
            'well_sums': -0.2,
            'pit_depth': -0.3
        }
    
    def get_next_action(self, game, current_time: int, player_num: int = 1) -> Optional[str]:
        """
        Get the next action for the AI to perform.
        
        Args:
            game: The Tetris game instance
            current_time: Current game time in milliseconds
            player_num: Player number (1 or 2)
            
        Returns:
            String representing the action to take, or None
        """
        # Check if enough time has passed since last action
        if current_time - self.last_move_time < self.settings['think_time']:
            return None
        
        # Check if game is over or paused
        if game.game_over or getattr(game, 'paused', False):
            return None
        
        # If animating line clear, don't move
        if getattr(game, 'animating_clear', False):
            return None
        
        # Check if there's a current piece
        if not hasattr(game, 'piece_type') or game.piece_type is None:
            return None
        
        # Get current piece info
        try:
            current_piece = self.get_current_piece(game)
            if not current_piece:
                return None
                
            # Find the best move for this piece
            best_move = self.find_best_move(game, current_piece)
            
            if best_move:
                # Execute the move step by step
                action = self.get_action_for_move(game, current_piece, best_move)
                
                if action:
                    self.last_move_time = current_time
                    
                    # Add some randomness based on difficulty
                    if random.random() < self.settings['mistake_chance']:
                        # Occasionally make a "mistake" for more realistic gameplay
                        mistake_actions = ['left', 'right', 'rotate']
                        return random.choice(mistake_actions)
                    
                    return action
                    
        except Exception as e:
            print(f"AI Error: {e}")
            pass
        
        # Fallback - simple random action
        self.last_move_time = current_time
        return random.choice(['left', 'right', 'rotate', 'down'])
    
    def get_current_piece(self, game):
        """Create a piece object from game state"""
        if hasattr(game, 'piece_type') and game.piece_type is not None:
            return TetrisPiece(
                game.piece_type,
                game.piece_x,
                game.piece_y,
                game.rotation
            )
        return None
    
    def get_action_for_move(self, game, current_piece, target_move):
        """Determine what action to take to reach the target move"""
        # Check if we need to rotate
        rotations_needed = (target_move['rotation'] - current_piece.rotation) % 4
        if rotations_needed > 0:
            return 'rotate'
        
        # Check if we need to move horizontally
        target_x = target_move['x']
        current_x = current_piece.x
        
        if target_x < current_x:
            return 'left'
        elif target_x > current_x:
            return 'right'
        
        # If we're in the right position, drop it
        return 'hard_drop'
    
    def find_best_move(self, game, current_piece) -> Optional[Dict[str, Any]]:
        """Find the best move for the current piece."""
        best_score = float('-inf')
        best_move = None
        
        # Get all possible positions for the current piece
        possible_moves = self.get_all_possible_moves(game, current_piece)
        
        for move in possible_moves:
            # Evaluate this move
            score = self.evaluate_move(game, current_piece, move)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def get_all_possible_moves(self, game, current_piece) -> List[Dict[str, Any]]:
        """Get all possible moves for the current piece."""
        moves = []
        
        # Try all rotations
        for rotation in range(4):
            # Try all horizontal positions
            for x in range(-2, game.width + 2):
                # Create test piece
                test_piece = TetrisPiece(
                    current_piece.piece_type,
                    x,
                    0,  # Start from top
                    rotation
                )
                
                # Drop the piece to find landing position
                landing_y = self.find_landing_position(game, test_piece)
                
                if landing_y is not None:
                    # This is a valid position
                    move = {
                        'x': x,
                        'y': landing_y,
                        'rotation': rotation
                    }
                    moves.append(move)
        
        return moves
    
    def find_landing_position(self, game, piece):
        """Find where a piece would land"""
        piece.y = 0
        
        # Check if piece can even be placed at the top
        if not self.is_valid_position(game, piece):
            return None
        
        # Drop until it can't go further
        while self.is_valid_position(game, piece, dy=1):
            piece.y += 1
        
        return piece.y
    
    def is_valid_position(self, game, piece, dx=0, dy=0):
        """Check if piece position is valid"""
        for block_x, block_y in piece.get_blocks():
            new_x = piece.x + block_x + dx
            new_y = piece.y + block_y + dy
            
            # Check boundaries
            if new_x < 0 or new_x >= game.width or new_y >= game.height:
                return False
            
            # Check collision with existing blocks (only if y >= 0)
            if new_y >= 0 and game.field[new_y][new_x] != 0:
                return False
        
        return True
    
    def evaluate_move(self, game, piece, move):
        """Evaluate how good a move is"""
        # Create a copy of the game state
        temp_field = [row[:] for row in game.field]
        
        # Place the piece in the target position
        test_piece = TetrisPiece(
            piece.piece_type,
            move['x'],
            move['y'],
            move['rotation']
        )
        
        # Place piece on temporary board
        for block_x, block_y in test_piece.get_blocks():
            board_x = test_piece.x + block_x
            board_y = test_piece.y + block_y
            
            if 0 <= board_x < game.width and 0 <= board_y < game.height:
                temp_field[board_y][board_x] = piece.piece_type + 1
        
        # Calculate score for this board state
        lines_cleared = self.count_complete_lines(temp_field)
        
        # Remove completed lines for evaluation
        if lines_cleared > 0:
            temp_field = self.remove_complete_lines(temp_field)
        
        # Evaluate the resulting board
        score = self.evaluate_board(temp_field)
        
        # Add bonus for line clears
        line_clear_bonus = {0: 0, 1: 40, 2: 100, 3: 300, 4: 1200}
        score += line_clear_bonus.get(lines_cleared, 0) * 10
        
        return score
    
    def count_complete_lines(self, field):
        """Count how many complete lines there are"""
        complete_lines = 0
        for row in field:
            if all(cell != 0 for cell in row):
                complete_lines += 1
        return complete_lines
    
    def remove_complete_lines(self, field):
        """Remove complete lines and add empty ones at top"""
        height = len(field)
        width = len(field[0]) if field else 0
        
        # Filter out complete lines
        new_field = [row for row in field if not all(cell != 0 for cell in row)]
        
        # Add empty lines at the top
        lines_removed = height - len(new_field)
        for _ in range(lines_removed):
            new_field.insert(0, [0] * width)
        
        return new_field
    
    def evaluate_board(self, field) -> float:
        """Evaluate the board state and return a score."""
        if not field:
            return 0
        
        height = len(field)
        width = len(field[0]) if field else 0
        
        # Calculate metrics
        aggregate_height = 0
        holes = 0
        bumpiness = 0
        
        # Column heights
        column_heights = []
        for x in range(width):
            col_height = 0
            for y in range(height):
                if field[y][x] != 0:
                    col_height = height - y
                    break
            column_heights.append(col_height)
            aggregate_height += col_height
        
        # Calculate bumpiness (difference between adjacent column heights)
        for i in range(len(column_heights) - 1):
            bumpiness += abs(column_heights[i] - column_heights[i + 1])
        
        # Count holes (empty cells with filled cells above them)
        for x in range(width):
            found_block = False
            for y in range(height):
                if field[y][x] != 0:
                    found_block = True
                elif found_block and field[y][x] == 0:
                    holes += 1
        
        # Calculate final score
        score = (
            self.weights['aggregate_height'] * aggregate_height +
            self.weights['holes'] * holes +
            self.weights['bumpiness'] * bumpiness
        )
        
        return score


def create_ai_controller(difficulty='medium') -> AdvancedAIController:
    """Factory function to create an AI controller."""
    return AdvancedAIController(difficulty)