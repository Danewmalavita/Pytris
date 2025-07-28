# tetris_logic.py
import pygame
import random

# Tetromino colors
COLORS = [
    (0, 0, 0),        # Black (empty)
    (255, 0, 0),      # Red - Z
    (0, 255, 0),      # Green - S
    (0, 0, 255),      # Blue - J
    (255, 255, 0),    # Yellow - O
    (0, 255, 255),    # Cyan - I
    (255, 0, 255),    # Magenta - T
    (255, 128, 0),    # Orange - L
]

# Tetrominos with their 4 rotations
SHAPES = [
    # Z-shape
    [
        [[1, 1, 0], [0, 1, 1], [0, 0, 0]],
        [[0, 0, 1], [0, 1, 1], [0, 1, 0]],
        [[0, 0, 0], [1, 1, 0], [0, 1, 1]],
        [[0, 1, 0], [1, 1, 0], [1, 0, 0]]
    ],
    # S-shape
    [
        [[0, 2, 2], [2, 2, 0], [0, 0, 0]],
        [[0, 2, 0], [0, 2, 2], [0, 0, 2]],
        [[0, 0, 0], [0, 2, 2], [2, 2, 0]],
        [[2, 0, 0], [2, 2, 0], [0, 2, 0]]
    ],
    # J-shape
    [
        [[3, 0, 0], [3, 3, 3], [0, 0, 0]],
        [[0, 3, 3], [0, 3, 0], [0, 3, 0]],
        [[0, 0, 0], [3, 3, 3], [0, 0, 3]],
        [[0, 3, 0], [0, 3, 0], [3, 3, 0]]
    ],
    # O-shape
    [
        [[0, 4, 4, 0], [0, 4, 4, 0], [0, 0, 0, 0]],
        [[0, 4, 4, 0], [0, 4, 4, 0], [0, 0, 0, 0]],
        [[0, 4, 4, 0], [0, 4, 4, 0], [0, 0, 0, 0]],
        [[0, 4, 4, 0], [0, 4, 4, 0], [0, 0, 0, 0]]
    ],
    # I-shape
    [
        [[0, 0, 0, 0], [5, 5, 5, 5], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 0, 5, 0], [0, 0, 5, 0], [0, 0, 5, 0], [0, 0, 5, 0]],
        [[0, 0, 0, 0], [0, 0, 0, 0], [5, 5, 5, 5], [0, 0, 0, 0]],
        [[0, 5, 0, 0], [0, 5, 0, 0], [0, 5, 0, 0], [0, 5, 0, 0]]
    ],
    # T-shape
    [
        [[0, 6, 0], [6, 6, 6], [0, 0, 0]],
        [[0, 6, 0], [0, 6, 6], [0, 6, 0]],
        [[0, 0, 0], [6, 6, 6], [0, 6, 0]],
        [[0, 6, 0], [6, 6, 0], [0, 6, 0]]
    ],
    # L-shape
    [
        [[0, 0, 7], [7, 7, 7], [0, 0, 0]],
        [[0, 7, 0], [0, 7, 0], [0, 7, 7]],
        [[0, 0, 0], [7, 7, 7], [7, 0, 0]],
        [[7, 7, 0], [0, 7, 0], [0, 7, 0]]
    ]
]

import time
from .debug_utils import debugger

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
        self.soft_drop_score = 0  # Puntuación acumulada por soft drop
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
        self.soft_drop_score = 0

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
        """
        Clockwise rotation (X key)
        Follows the pattern: shapes = 1->2->3->4->1
        """
        # Clockwise rotation: increment rotation index
        new_rotation = (self.rotation + 1) % 4
        
        # Use appropriate wall kicks for clockwise rotation
        kicks = [(0, 0), (-1, 0), (1, 0), (0, -1), (-2, 0), (2, 0)]
        
        # Special kicks for I-piece (long piece)
        if self.piece_type == 4:  # Index 4 is the I-piece
            kicks = [(0, 0), (-2, 0), (2, 0), (-1, 0), (1, 0), (0, 1)]
        
        for dx, dy in kicks:
            new_x = self.piece_x + dx
            new_y = self.piece_y + dy
            if self.is_valid_position(x=new_x, y=new_y, rotation=new_rotation):
                self.piece_x = new_x
                self.piece_y = new_y
                self.rotation = new_rotation
                return True
        return False
        
    def rotate_inv(self):
        """Counter-clockwise rotation"""
        # Counter-clockwise rotation: equivalent to -1 mod 4, but always positive
        new_rotation = (self.rotation + 3) % 4
        
        # Wall kicks for counter-clockwise rotation
        kicks = [(0, 0), (-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1), (0, 2), (1, 2), (-1, 2)]
        
        # Special kicks for I-piece
        if self.piece_type == 4:  # I-piece
            if self.rotation == 0 and new_rotation == 3:
                kicks = [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)]
            elif self.rotation == 1 and new_rotation == 0:
                kicks = [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)]
            elif self.rotation == 2 and new_rotation == 1:
                kicks = [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)]
            elif self.rotation == 3 and new_rotation == 2:
                kicks = [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)]
            
        # Try each possible position with wall kicks
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

    def move_down(self, is_soft_drop=False):
        """
        Mueve la pieza hacia abajo.
        
        Args:
            is_soft_drop (bool): True si el movimiento es iniciado por el jugador (tecla abajo)
        
        Returns:
            bool: True si la pieza se movió exitosamente
        """
        if self.is_valid_position(y=self.piece_y + 1):
            self.piece_y += 1
            self.on_ground = False
            self.lock_timer = 0
            
            # Solo incrementar puntuación si es soft drop manual
            if is_soft_drop:
                self.soft_drop_score += 1
                # Actualizar la puntuación total en tiempo real
                self.score += 1
                
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

    def is_tspin(self):
        """
        Detecta si la última rotación resultó en un T-spin.
        Un T-spin ocurre cuando una pieza T es rotada y tiene 3 de sus 4 esquinas bloqueadas.
        """
        # Solo aplica a la pieza T (índice 5 en SHAPES)
        if self.piece_type != 5:
            return False
        
        # Verificar las 4 esquinas alrededor de la pieza T
        # Las coordenadas de las esquinas dependen de la posición del centro de la T
        corners_blocked = 0
        corners = [
            (self.piece_x, self.piece_y),               # Superior izquierda
            (self.piece_x + 2, self.piece_y),           # Superior derecha
            (self.piece_x, self.piece_y + 2),           # Inferior izquierda
            (self.piece_x + 2, self.piece_y + 2)        # Inferior derecha
        ]
        
        for x, y in corners:
            # Verificar si la esquina está bloqueada (fuera del campo o con un bloque)
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                corners_blocked += 1
            elif self.field[y][x] != 0:
                corners_blocked += 1
        
        # Un T-spin requiere al menos 3 esquinas bloqueadas
        return corners_blocked >= 3

    def fix_piece(self):
        # Verificar T-spin antes de fijar la pieza
        is_tspin = self.is_tspin()
        
        shape = SHAPES[self.piece_type][self.rotation]
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col] != 0:
                    field_y = self.piece_y + row
                    if 0 <= field_y < self.height:
                        self.field[field_y][self.piece_x + col] = shape[row][col]

        # No necesitamos añadir la puntuación de soft drop aquí porque ya se agregó en tiempo real
        # Solo reseteamos el contador para la siguiente pieza
        self.soft_drop_score = 0

        line_clear_result = self.clear_lines()
        self.hold_used = False
        
        # Agregar información de T-spin al resultado si es aplicable
        if line_clear_result and is_tspin:
            line_clear_result["is_tspin"] = True
            # Puntos base para líneas eliminadas
            points_table = {1: 40, 2: 100, 3: 300, 4: 1200}
            # Duplicar la puntuación por T-spin
            self.score += points_table.get(line_clear_result["count"], 0) * self.level
            debugger.debug(f"¡T-SPIN detectado! Puntuación adicional otorgada.")
        elif is_tspin:
            # T-spin sin líneas, dar puntos adicionales
            self.score += 400 * self.level
            debugger.debug(f"¡T-SPIN sin líneas detectado! 400 puntos × nivel {self.level}")

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
                "combo": self.combo_count,
                "combo_active": True  # Indica que el combo sigue activo
            }
        else:
            # Resetear combo si ha pasado demasiado tiempo desde la última limpieza
            now = pygame.time.get_ticks()
            if now - self.last_clear_time > self.combo_timeout:
                self.combo_count = 0
                # Si necesitamos indicar que el combo terminó (sin líneas eliminadas)
                # podemos devolver un resultado vacío pero con el combo_active=False
                if self.combo_count > 0:  # Solo si había un combo activo
                    return {
                        "count": 0,
                        "combo": self.combo_count,
                        "combo_active": False  # Indica que el combo ha terminado
                    }
                
        return None

    def finish_clear_animation(self):
        try:
            start_time = time.time()
            
            # Safety check: ensure lines_to_clear isn't empty
            if not self.lines_to_clear:
                self.animating_clear = False
                return
            
            # Sort lines to clear from bottom to top
            sorted_lines = sorted(self.lines_to_clear, reverse=True)
            
            # Optimized line clearing algorithm
            # 1. Create a temporary field without the cleared lines
            temp_field = [self.field[y].copy() for y in range(self.height) if y not in self.lines_to_clear]
                
            # 2. Create new empty rows and construct new field with empty rows at top
            empty_rows = [[0 for _ in range(self.width)] for _ in range(len(self.lines_to_clear))]
            new_field = empty_rows + temp_field
            
            # 3. Ensure the field has the correct height
            if len(new_field) != self.height:
                if len(new_field) > self.height:
                    new_field = new_field[:self.height]
                else:
                    missing = self.height - len(new_field)
                    new_field = [[0 for _ in range(self.width)] for _ in range(missing)] + new_field
            
            # Replace the entire field
            self.field = new_field

            # Update score and level
            lines_count = len(self.lines_to_clear)
            self.lines_cleared += lines_count
            points = {1: 40, 2: 100, 3: 300, 4: 1200}
            
            # Apply combo multiplier (max 5x)
            combo_multiplier = min(5, self.combo_count)
            base_points = points.get(lines_count, 0) * self.level
            combo_points = base_points * combo_multiplier
            self.score += combo_points

            # Check for level up
            new_level = 1 + (self.lines_cleared // 10)
            if new_level > self.level:
                old_level = self.level
                self.level = new_level
                
                # Calculate new game speed based on level
                if self.level <= 9:
                    # Levels 1-9: 500ms to 200ms
                    self.game_speed = 500 - (self.level - 1) * 35
                else:
                    # Levels 10+: Slower decrease to minimum 150ms
                    high_level_speed = 200 - ((self.level - 9) * 5)
                    self.game_speed = max(150, high_level_speed)
                
                # Signal level up for effects
                self.level_up_event = True
                print(f"Level up! from {old_level} to {self.level} with game speed {self.game_speed}ms")

            # Reset animation state
            self.lines_to_clear = []
            self.animating_clear = False
            
        except Exception as e:
            debugger.error(f"Error in finish_clear_animation: {str(e)}")
            # Reset animation state even on error
            self.lines_to_clear = []
            self.animating_clear = False
            raise

    def get_piece_shape(self):
        return SHAPES[self.piece_type][self.rotation]

    def get_piece_type(self):
        return self.piece_type + 1

    def get_ghost_position(self):
        ghost_y = self.piece_y
        while self.is_valid_position(y=ghost_y + 1):
            ghost_y += 1
        return ghost_y