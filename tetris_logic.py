# tetris_logic.py
# Módulo que contiene la lógica del juego Tetris
import pygame
import random

# Colores de los tetraminos (correspondientes a los sprites)
COLORS = [
    (0, 0, 0),        # Negro (para espacios vacíos)
    (255, 0, 0),      # Rojo - Z piece
    (0, 255, 0),      # Verde - S piece
    (0, 0, 255),      # Azul - J piece
    (255, 255, 0),    # Amarillo - O piece
    (0, 255, 255),    # Cian - I piece
    (255, 0, 255),    # Magenta - T piece
    (255, 128, 0),    # Naranja - L piece
]

# Definición de las piezas (tetraminos) - cada una con sus 4 rotaciones posibles
SHAPES = [
    # Z-shape (rojo)
    [
        [[1, 1, 0],
         [0, 1, 1],
         [0, 0, 0]],
        
        [[0, 0, 1],
         [0, 1, 1],
         [0, 1, 0]],
        
        [[0, 0, 0],
         [1, 1, 0],
         [0, 1, 1]],
        
        [[0, 1, 0],
         [1, 1, 0],
         [1, 0, 0]]
    ],
    # S-shape (verde)
    [
        [[0, 2, 2],
         [2, 2, 0],
         [0, 0, 0]],
        
        [[0, 2, 0],
         [0, 2, 2],
         [0, 0, 2]],
        
        [[0, 0, 0],
         [0, 2, 2],
         [2, 2, 0]],
        
        [[2, 0, 0],
         [2, 2, 0],
         [0, 2, 0]]
    ],
    # J-shape (azul)
    [
        [[3, 0, 0],
         [3, 3, 3],
         [0, 0, 0]],
        
        [[0, 3, 3],
         [0, 3, 0],
         [0, 3, 0]],
        
        [[0, 0, 0],
         [3, 3, 3],
         [0, 0, 3]],
        
        [[0, 3, 0],
         [0, 3, 0],
         [3, 3, 0]]
    ],
    # O-shape (amarillo)
    [
        [[0, 4, 4, 0],
         [0, 4, 4, 0],
         [0, 0, 0, 0]],
        
        [[0, 4, 4, 0],
         [0, 4, 4, 0],
         [0, 0, 0, 0]],
        
        [[0, 4, 4, 0],
         [0, 4, 4, 0],
         [0, 0, 0, 0]],
        
        [[0, 4, 4, 0],
         [0, 4, 4, 0],
         [0, 0, 0, 0]]
    ],
    # I-shape (cian)
    [
        [[0, 0, 0, 0],
         [5, 5, 5, 5],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],
        
        [[0, 0, 5, 0],
         [0, 0, 5, 0],
         [0, 0, 5, 0],
         [0, 0, 5, 0]],
        
        [[0, 0, 0, 0],
         [0, 0, 0, 0],
         [5, 5, 5, 5],
         [0, 0, 0, 0]],
        
        [[0, 5, 0, 0],
         [0, 5, 0, 0],
         [0, 5, 0, 0],
         [0, 5, 0, 0]]
    ],
    # T-shape (magenta)
    [
        [[0, 6, 0],
         [6, 6, 6],
         [0, 0, 0]],
        
        [[0, 6, 0],
         [0, 6, 6],
         [0, 6, 0]],
        
        [[0, 0, 0],
         [6, 6, 6],
         [0, 6, 0]],
        
        [[0, 6, 0],
         [6, 6, 0],
         [0, 6, 0]]
    ],
    # L-shape (naranja)
    [
        [[0, 0, 7],
         [7, 7, 7],
         [0, 0, 0]],
        
        [[0, 7, 0],
         [0, 7, 0],
         [0, 7, 7]],
        
        [[0, 0, 0],
         [7, 7, 7],
         [7, 0, 0]],
        
        [[7, 7, 0],
         [0, 7, 0],
         [0, 7, 0]]
    ]
]

# tetris_logic.py (actualizado: corrección completa del bug al eliminar múltiples líneas con animación)
import pygame
import random
import time
from debug_utils import debugger

# Colores y SHAPES definidos como antes (sin cambios)

class TetrisGame:
    def __init__(self, width=10, height=20):
        self.width = width
        self.height = height
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_speed = 500
        self.next_piece_type = None
        self.next_piece_shape = None
        self.bag = []
        self.combo_count = 0  # Contador de combos consecutivos
        self.last_clear_time = 0  # Para el temporizador de combo
        self.combo_timeout = 5000  # Tiempo en ms para resetear combo (5 segundos)
        self.level_up_event = False  # Flag to signal a level up event
        self.reset()

    def reset(self):
        self.field = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.new_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.lock_timer = 0
        self.on_ground = False
        self.lock_delay_ms = 500
        self.hold_piece_type = None
        self.hold_used = False
        self.bag = []
        self.lines_to_clear = []
        self.clear_animation_time = 0
        self.animating_clear = False
        self.combo_count = 0
        self.level_up_event = False

    def refill_bag(self):
        self.bag = list(range(7))
        random.shuffle(self.bag)

    def new_piece(self):
        if self.next_piece_type is not None:
            self.piece_type = self.next_piece_type
            self.rotation = 0
        else:
            if not self.bag:
                self.refill_bag()
            self.piece_type = self.bag.pop(0)
            self.rotation = 0

        if not self.bag:
            self.refill_bag()
        self.next_piece_type = self.bag.pop(0)
        self.next_piece_shape = SHAPES[self.next_piece_type][0]

        shape = SHAPES[self.piece_type][self.rotation]
        width = len(shape[0])
        self.piece_x = (self.width // 2) - (width // 2)
        self.piece_y = 0

        if not self.is_valid_position():
            self.game_over = True

    def is_valid_position(self, x=None, y=None, rotation=None):
        if x is None:
            x = self.piece_x
        if y is None:
            y = self.piece_y
        if rotation is None:
            rotation = self.rotation

        shape = SHAPES[self.piece_type][rotation]

        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col] == 0:
                    continue
                field_x = x + col
                field_y = y + row
                if field_x < 0 or field_x >= self.width or field_y >= self.height:
                    return False
                if field_y >= 0 and self.field[field_y][field_x] != 0:
                    return False

        return True

    def rotate(self):
        new_rotation = (self.rotation + 1) % 4
        kicks = [(0, 0), (-1, 0), (1, 0), (0, -1), (-2, 0), (2, 0)]
        for dx, dy in kicks:
            new_x = self.piece_x + dx
            new_y = self.piece_y + dy
            if self.is_valid_position(x=new_x, y=new_y, rotation=new_rotation):
                self.piece_x = new_x
                self.piece_y = new_y
                self.rotation = new_rotation
                return True
        return False

    def move_left(self):
        if self.is_valid_position(x=self.piece_x - 1):
            self.piece_x -= 1
            return True
        return False

    def move_right(self):
        if self.is_valid_position(x=self.piece_x + 1):
            self.piece_x += 1
            return True
        return False

    def move_down(self):
        if self.is_valid_position(y=self.piece_y + 1):
            self.piece_y += 1
            self.on_ground = False
            self.lock_timer = 0
            return True
        else:
            if not self.on_ground:
                self.on_ground = True
                self.lock_timer = pygame.time.get_ticks()
            return False

    def drop(self):
        drop_y = self.piece_y
        while self.is_valid_position(y=drop_y + 1):
            drop_y += 1
        self.piece_y = drop_y

    def hold_piece(self):
        if self.hold_used or self.game_over:
            return
        current = self.piece_type
        if self.hold_piece_type is None:
            self.piece_type = self.next_piece_type
            # Usar el sistema de bolsa para el siguiente tetromino
            if not self.bag:
                self.refill_bag()
            self.next_piece_type = self.bag.pop(0)
        else:
            self.piece_type, self.hold_piece_type = self.hold_piece_type, current
        self.hold_piece_type = current
        self.rotation = 0
        self.piece_x = (self.width // 2) - (len(SHAPES[self.piece_type][0][0]) // 2)
        self.piece_y = 0
        self.hold_used = True
        if not self.is_valid_position():
            self.game_over = True

    def should_lock(self):
        if self.on_ground:
            elapsed = pygame.time.get_ticks() - self.lock_timer
            return elapsed >= self.lock_delay_ms
        return False

    def fix_piece(self):
        shape = SHAPES[self.piece_type][self.rotation]
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col] != 0:
                    field_y = self.piece_y + row
                    if 0 <= field_y < self.height:
                        self.field[field_y][self.piece_x + col] = shape[row][col]

        line_clear_result = self.clear_lines()
        self.hold_used = False

        # Solo crear nueva pieza si no hay animación pendiente
        if not self.animating_clear:
            self.new_piece()

        return line_clear_result

    def clear_lines(self):
        self.lines_to_clear = [i for i in range(self.height) if all(cell != 0 for cell in self.field[i])]
        if self.lines_to_clear:
            now = pygame.time.get_ticks()
            
            # Verificar combo (líneas consecutivas en un periodo de tiempo)
            if now - self.last_clear_time < self.combo_timeout:
                self.combo_count += 1
            else:
                self.combo_count = 1
                
            self.last_clear_time = now
            self.animating_clear = True
            self.clear_animation_time = now
            
            return {
                "count": len(self.lines_to_clear),
                "is_tetris": (len(self.lines_to_clear) == 4),
                "combo": self.combo_count
            }
        else:
            # Resetear combo si ha pasado demasiado tiempo desde la última limpieza
            now = pygame.time.get_ticks()
            if now - self.last_clear_time > self.combo_timeout:
                self.combo_count = 0
                
        return None

    def finish_clear_animation(self):
        try:
            start_time = time.time()
            debugger.debug(f"Starting clear animation finish, lines to clear: {self.lines_to_clear}")
            
            # Safety check: ensure lines_to_clear isn't empty
            if not self.lines_to_clear:
                debugger.warning("finish_clear_animation called with empty lines_to_clear")
                self.animating_clear = False
                return
            
            # Ordenar las líneas a eliminar de mayor a menor (bottom to top)
            sorted_lines = sorted(self.lines_to_clear, reverse=True)
            debugger.debug(f"Sorted lines: {sorted_lines}")
            
            # Complete rewrite of the line clearing algorithm
            # 1. Create a temporary field without the cleared lines
            temp_field = []
            for y in range(self.height):
                if y not in self.lines_to_clear:
                    temp_field.append(self.field[y].copy())
                    
            # 2. Create new empty rows to replace the cleared lines
            empty_rows = [[0 for _ in range(self.width)] for _ in range(len(self.lines_to_clear))]
            
            # 3. Construct new field with empty rows at top
            new_field = empty_rows + temp_field
            
            # 4. Make sure we have exactly the right number of rows
            if len(new_field) > self.height:
                # Too many rows, trim from the bottom (shouldn't normally happen)
                new_field = new_field[:self.height]
            elif len(new_field) < self.height:
                # Too few rows, add more empty rows at the top (shouldn't normally happen)
                missing = self.height - len(new_field)
                new_field = [[0 for _ in range(self.width)] for _ in range(missing)] + new_field
                
            # Ensure we have the exact height needed
            assert len(new_field) == self.height, f"Field height mismatch: {len(new_field)} != {self.height}"
            
            # Replace the entire field with the new version
            self.field = new_field
            
            debugger.debug(f"Field reconstruction completed with {len(self.lines_to_clear)} lines cleared")

            lines_count = len(self.lines_to_clear)
            self.lines_cleared += lines_count
            points = {1: 40, 2: 100, 3: 300, 4: 1200}
            self.score += points.get(lines_count, 0) * self.level

            new_level = 1 + (self.lines_cleared // 10)
            if new_level > self.level:
                # Store old level for comparison
                old_level = self.level
                
                # Update level
                self.level = new_level
                
                # Improved speed calculation with better curve
                # - Levels 1-9: Gradual decrease from 500ms to 200ms
                # - Levels 10+: Slower decrease from 200ms to 150ms minimum
                if self.level <= 9:
                    # Levels 1-9: 500ms to 200ms
                    self.game_speed = 500 - (self.level - 1) * 35
                else:
                    # Levels 10+: Slower progression with a minimum of 150ms
                    high_level_speed = 200 - ((self.level - 9) * 5)
                    self.game_speed = max(150, high_level_speed)
                
                debugger.debug(f"Updated game speed for level {self.level}: {self.game_speed}ms")
                
                # Signal level up for particle clearing
                self.level_up_event = True
                
                debugger.debug(f"Level up! From {old_level} to {self.level} with game speed {self.game_speed}ms")
                print(f"Level up! From {old_level} to {self.level} with game speed {self.game_speed}ms")

            self.lines_to_clear = []
            self.animating_clear = False
            
            debugger.log_performance("finish_clear_animation", start_time)
            
        except Exception as e:
            debugger.error(f"Error in finish_clear_animation: {str(e)}")
            # Ensure we reset animation state even if there's an error
            self.lines_to_clear = []
            self.animating_clear = False
            raise  # Re-raise the exception to be caught by the global handler

    def get_piece_shape(self):
        return SHAPES[self.piece_type][self.rotation]

    def get_piece_type(self):
        return self.piece_type + 1

    def get_ghost_position(self):
        ghost_y = self.piece_y
        while self.is_valid_position(y=ghost_y + 1):
            ghost_y += 1
        return ghost_y
