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
        self.next_piece_type = None  # Para compatibilidad con código antiguo
        self.next_piece_shape = None  # Para compatibilidad con código antiguo
        self.next_pieces = []  # Lista para las siguientes 3 piezas
        self.bag = []
        self.combo_count = 0  # Contador de combos consecutivos
        self.last_clear_time = 0  # Para el temporizador de combo
        self.combo_timeout = 5000  # Tiempo en ms para resetear combo (5 segundos)
        self.level_up_event = False  # Flag to signal a level up event
        self.soft_drop_score = 0  # Puntuación acumulada por soft drop
        self.reset()

    def reset(self):
        self.field = [[0 for _ in range(self.width)] for _ in range(self.height)]
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
        self.next_pieces = []  # Inicializar lista vacía para las próximas piezas
        self.lines_to_clear = []
        self.clear_animation_time = 0
        self.animating_clear = False
        self.combo_count = 0
        self.level_up_event = False
        self.soft_drop_score = 0
        
        # Variables para el sistema SRS y detección de T-spin
        self.last_move_was_rotation = False
        self.last_rotation_kick = (0, 0)
        self.back_to_back = 0  # Contador para técnicas consecutivas (Tetris y T-spin)
        
        # Inicializar la bolsa con el algoritmo 7-bag shuffle
        self.refill_bag()
        
        # Inicializar la pieza actual y las próximas piezas
        self.prepare_first_piece()

    def refill_bag(self):
        """
        Implementa el sistema 7-bag shuffle: todas las 7 piezas aparecen exactamente
        una vez antes de que cualquiera se repita, asegurando una distribución justa.
        """
        self.bag = list(range(7))
        random.shuffle(self.bag)

    def prepare_first_piece(self):
        """
        Inicializa la primera pieza del juego y las 3 piezas siguientes.
        """
        # Asegurar que la bolsa esté llena
        if len(self.bag) < 4:  # Necesitamos al menos 4 piezas (1 actual + 3 siguientes)
            self.refill_bag()
            
        # Obtener la pieza actual
        self.piece_type = self.bag.pop(0)
        self.rotation = 0
        
        # Generar las 3 piezas siguientes
        self.next_pieces = []
        for _ in range(3):
            if not self.bag:
                self.refill_bag()
            self.next_pieces.append(self.bag.pop(0))
            
        # Mantener compatibilidad con el código existente
        self.next_piece_type = self.next_pieces[0]
        self.next_piece_shape = SHAPES[self.next_piece_type][0]
        
        # Posicionar la pieza en el tablero
        shape = SHAPES[self.piece_type][self.rotation]
        width = len(shape[0])
        self.piece_x = (self.width // 2) - (width // 2)
        self.piece_y = 0
        
        # Verificar game over
        if not self.is_valid_position():
            self.game_over = True
    
    def new_piece(self):
        """
        Genera una nueva pieza para el jugador tomando la primera de la cola de piezas siguientes,
        y añade una nueva pieza al final de la cola para mantener 3 piezas visibles.
        """
        # Tomar la primera pieza de la cola como la pieza actual
        self.piece_type = self.next_pieces[0]
        
        # Eliminar la primera pieza de la cola y desplazar las demás
        self.next_pieces = self.next_pieces[1:]
        
        # Añadir una nueva pieza al final de la cola
        if not self.bag:
            self.refill_bag()
        self.next_pieces.append(self.bag.pop(0))
        
        # Actualizar next_piece_type para mantener compatibilidad
        self.next_piece_type = self.next_pieces[0]
        self.next_piece_shape = SHAPES[self.next_piece_type][0]
        
        # Resetear la rotación
        self.rotation = 0
        
        # Posicionar la pieza en el tablero
        shape = SHAPES[self.piece_type][self.rotation]
        width = len(shape[0])
        self.piece_x = (self.width // 2) - (width // 2)
        self.piece_y = 0
        
        # Verificar game over
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

    def get_wall_kicks(self, piece_type, rotation_from, rotation_to):
        """
        Implementa el sistema oficial de SRS (Super Rotation System) para wall kicks
        según la especificación de los Tetris modernos.
        
        Referencia: https://harddrop.com/wiki/SRS
        """
        # Definir tablas de kick para piezas JLSTZ (todas excepto I y O)
        JLSTZ_WALL_KICKS = {
            # (rotación_inicial, rotación_destino): [(test_1_x, test_1_y), (test_2_x, test_2_y), ...]
            (0, 1): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],  # 0->R
            (1, 0): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],    # R->0
            (1, 2): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],    # R->2
            (2, 1): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],  # 2->R
            (2, 3): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],     # 2->L
            (3, 2): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)], # L->2
            (3, 0): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)], # L->0
            (0, 3): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)]      # 0->L
        }
        
        # Definir tabla de kick específica para la pieza I
        I_WALL_KICKS = {
            (0, 1): [(0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)],   # 0->R
            (1, 0): [(0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)],   # R->0
            (1, 2): [(0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)],   # R->2
            (2, 1): [(0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)],   # 2->R
            (2, 3): [(0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)],   # 2->L
            (3, 2): [(0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)],   # L->2
            (3, 0): [(0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)],   # L->0
            (0, 3): [(0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)]    # 0->L
        }
        
        # La pieza O no tiene kicks (no rota visiblemente)
        O_WALL_KICKS = {
            (0, 1): [(0, 0)],
            (1, 0): [(0, 0)],
            (1, 2): [(0, 0)],
            (2, 1): [(0, 0)],
            (2, 3): [(0, 0)],
            (3, 2): [(0, 0)],
            (3, 0): [(0, 0)],
            (0, 3): [(0, 0)]
        }
        
        # Seleccionar la tabla correcta según el tipo de pieza
        if piece_type == 4:  # I-piece (index 4)
            return I_WALL_KICKS.get((rotation_from, rotation_to), [(0, 0)])
        elif piece_type == 3:  # O-piece (index 3)
            return O_WALL_KICKS.get((rotation_from, rotation_to), [(0, 0)])
        else:  # JLSTZ pieces (todas las demás)
            return JLSTZ_WALL_KICKS.get((rotation_from, rotation_to), [(0, 0)])
    
    def rotate(self):
        """
        Clockwise rotation (X key)
        Implementa SRS (Super Rotation System) para la rotación en sentido horario.
        """
        # No rotar si es game over
        if self.game_over:
            return False
            
        # Calcular nueva rotación (sentido horario)
        new_rotation = (self.rotation + 1) % 4
        
        # Obtener kicks según SRS para esta pieza y rotación
        kicks = self.get_wall_kicks(self.piece_type, self.rotation, new_rotation)
        
        # Registrar último estado para detección de T-spin
        last_x, last_y, last_rot = self.piece_x, self.piece_y, self.rotation
        
        # Intentar cada posible kick
        for dx, dy in kicks:
            new_x = self.piece_x + dx
            new_y = self.piece_y + dy
            if self.is_valid_position(x=new_x, y=new_y, rotation=new_rotation):
                self.piece_x = new_x
                self.piece_y = new_y
                self.rotation = new_rotation
                
                # Si es pieza T, registrar que hubo rotación para detección de T-spin
                if self.piece_type == 5:  # T-piece
                    self.last_move_was_rotation = True
                    # Guardar el tipo de kick para distinguir entre T-spin normal y mini
                    self.last_rotation_kick = (dx, dy)
                else:
                    self.last_move_was_rotation = False
                
                return True
                
        return False
        
    def rotate_inv(self):
        """
        Counter-clockwise rotation (Z key)
        Implementa SRS (Super Rotation System) para la rotación en sentido antihorario.
        """
        # No rotar si es game over
        if self.game_over:
            return False
            
        # Calcular nueva rotación (sentido antihorario)
        new_rotation = (self.rotation + 3) % 4
        
        # Obtener kicks según SRS para esta pieza y rotación
        kicks = self.get_wall_kicks(self.piece_type, self.rotation, new_rotation)
        
        # Registrar último estado para detección de T-spin
        last_x, last_y, last_rot = self.piece_x, self.piece_y, self.rotation
        
        # Intentar cada posible kick
        for dx, dy in kicks:
            new_x = self.piece_x + dx
            new_y = self.piece_y + dy
            if self.is_valid_position(x=new_x, y=new_y, rotation=new_rotation):
                self.piece_x = new_x
                self.piece_y = new_y
                self.rotation = new_rotation
                
                # Si es pieza T, registrar que hubo rotación para detección de T-spin
                if self.piece_type == 5:  # T-piece
                    self.last_move_was_rotation = True
                    # Guardar el tipo de kick para distinguir entre T-spin normal y mini
                    self.last_rotation_kick = (dx, dy)
                else:
                    self.last_move_was_rotation = False
                
                return True
                
        return False

    def move_left(self):
        if self.is_valid_position(x=self.piece_x - 1):
            self.piece_x -= 1
            # Resetear el flag de rotación para T-spin (un movimiento horizontal invalida el T-spin)
            if self.piece_type == 5:  # T-piece
                self.last_move_was_rotation = False
            return True
        return False

    def move_right(self):
        if self.is_valid_position(x=self.piece_x + 1):
            self.piece_x += 1
            # Resetear el flag de rotación para T-spin (un movimiento horizontal invalida el T-spin)
            if self.piece_type == 5:  # T-piece
                self.last_move_was_rotation = False
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
            
            # Resetear el flag de rotación para T-spin (un movimiento vertical invalida el T-spin)
            if self.piece_type == 5:  # T-piece
                self.last_move_was_rotation = False
            
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
        drop_distance = 0
        
        # Calcular la distancia del hard drop y la posición final
        while self.is_valid_position(y=drop_y + 1):
            drop_y += 1
            drop_distance += 1
        
        self.piece_y = drop_y
        
        # Añadir puntuación por hard drop (2 puntos por cada celda que cae)
        hard_drop_score = drop_distance * 2
        self.score += hard_drop_score
        
        # Resetear el flag de rotación para T-spin (hard drop invalida el T-spin)
        if self.piece_type == 5:  # T-piece
            self.last_move_was_rotation = False
            
        # Devolver la distancia caída para posibles efectos visuales
        return drop_distance

    def hold_piece(self):
        """
        Intercambia la pieza actual con la pieza en hold, o toma la primera pieza de next_pieces
        si es la primera vez que se usa el hold.
        """
        # No se puede usar hold si ya se usó o si el juego terminó
        if self.hold_used or self.game_over:
            return
            
        # Guardar la pieza actual temporalmente
        current = self.piece_type
        
        if self.hold_piece_type is None:
            # Primera vez que se usa hold: tomar la primera pieza de next_pieces
            # La nueva pieza actual será la primera de la cola
            self.piece_type = self.next_pieces[0]
            
            # Reorganizar la cola de piezas siguientes
            self.next_pieces = self.next_pieces[1:]
            
            # Añadir una nueva pieza al final para mantener 3 piezas en la cola
            if not self.bag:
                self.refill_bag()
            self.next_pieces.append(self.bag.pop(0))
        else:
            # Intercambiar la pieza actual con la pieza en hold
            self.piece_type, self.hold_piece_type = self.hold_piece_type, current
        
        # Guardar la pieza actual en hold
        self.hold_piece_type = current
        
        # Actualizar next_piece_type para compatibilidad
        self.next_piece_type = self.next_pieces[0]
        self.next_piece_shape = SHAPES[self.next_piece_type][0]
        
        # Resetear la posición y rotación de la pieza
        self.rotation = 0
        shape = SHAPES[self.piece_type][0]
        width = len(shape[0])
        self.piece_x = (self.width // 2) - (width // 2)
        self.piece_y = 0
        
        # Marcar que hold ya fue usado
        self.hold_used = True
        
        # Verificar si la posición es válida (game over si no lo es)
        if not self.is_valid_position():
            self.game_over = True

    def should_lock(self):
        if self.on_ground:
            elapsed = pygame.time.get_ticks() - self.lock_timer
            return elapsed >= self.lock_delay_ms
        return False

    def is_tspin(self):
        """
        Detecta si la última rotación resultó en un T-spin según las reglas modernas de SRS.
        
        En el sistema moderno:
        - Un T-spin ocurre cuando la última acción fue una rotación de la pieza T
          Y al menos 3 de las 4 esquinas alrededor del centro de la T están ocupadas
        - Se distingue entre T-spin normal y T-spin mini según el tipo de rotación
          y la posición final de los bloques
          
        Referencia: https://harddrop.com/wiki/List_of_twists#Twists_with_T_.28or_T-Spin.29
        """
        # Solo aplica a la pieza T (índice 5 en SHAPES)
        if self.piece_type != 5:
            return False
        
        # Verificar si la última acción fue una rotación (requisito de SRS moderno)
        if not hasattr(self, 'last_move_was_rotation') or not self.last_move_was_rotation:
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
        
        front_corners = []
        
        # Determinar cuáles son las esquinas frontales según la rotación actual
        if self.rotation == 0:  # T apuntando hacia arriba
            front_corners = [corners[0], corners[1]]  # Esquinas superiores
        elif self.rotation == 1:  # T apuntando hacia la derecha
            front_corners = [corners[1], corners[3]]  # Esquinas derechas
        elif self.rotation == 2:  # T apuntando hacia abajo
            front_corners = [corners[2], corners[3]]  # Esquinas inferiores
        elif self.rotation == 3:  # T apuntando hacia la izquierda
            front_corners = [corners[0], corners[2]]  # Esquinas izquierdas
        
        # Contar esquinas bloqueadas y esquinas frontales bloqueadas
        front_blocked = 0
        for i, (x, y) in enumerate(corners):
            is_blocked = False
            
            # Verificar si la esquina está bloqueada (fuera del campo o con un bloque)
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                corners_blocked += 1
                is_blocked = True
            elif self.field[y][x] != 0:
                corners_blocked += 1
                is_blocked = True
            
            # Verificar si es una esquina frontal bloqueada
            if is_blocked and (x, y) in front_corners:
                front_blocked += 1
        
        # Determinar el tipo de T-spin
        # Según SRS moderno:
        # - T-spin normal: 3 o 4 esquinas bloqueadas con al menos 2 frontales bloqueadas
        # - T-spin mini: 3 esquinas bloqueadas pero menos de 2 frontales bloqueadas
        if corners_blocked >= 3:
            # Verificar si el último kick fue un test 4 o 5 (típicamente kicks especiales)
            # que pueden convertir un mini T-spin en un T-spin completo
            if hasattr(self, 'last_rotation_kick') and self.last_rotation_kick != (0, 0):
                # Si el kick no fue (0,0) y es el último test, considerarlo T-spin completo
                kick_index = 0
                if hasattr(self, 'last_rotation_kick'):
                    kicks = self.get_wall_kicks(5, (self.rotation-1)%4, self.rotation)
                    if self.last_rotation_kick in kicks:
                        kick_index = kicks.index(self.last_rotation_kick)
                
                # Verificar si es un T-spin mini o completo
                if front_blocked >= 2 or kick_index >= 3:
                    return "T-spin"
                else:
                    return "T-spin mini"
            else:
                # Sin kick especial, usar la regla estándar de esquinas frontales
                if front_blocked >= 2:
                    return "T-spin"
                else:
                    return "T-spin mini"
        
        return False

    def fix_piece(self):
        # Verificar T-spin antes de fijar la pieza
        tspin_result = self.is_tspin()
        
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
        if line_clear_result and tspin_result:
            # Determinar el tipo exacto de T-spin para calcular la puntuación
            tspin_type = tspin_result  # "T-spin" o "T-spin mini"
            line_clear_result["is_tspin"] = True
            line_clear_result["tspin_type"] = tspin_type
            
            # Puntuación para T-spins según el sistema moderno
            if tspin_type == "T-spin":
                # T-spin normal
                points_table = {
                    0: 400,    # T-spin sin líneas
                    1: 800,    # T-spin Single
                    2: 1200,   # T-spin Double
                    3: 1600    # T-spin Triple
                }
            else:
                # T-spin mini
                points_table = {
                    0: 200,    # T-spin mini sin líneas
                    1: 200,    # T-spin mini Single
                    2: 400,    # T-spin mini Double
                    3: 400     # T-spin mini Triple (raro, pero posible)
                }
            
            # Aplicar puntuación según el tipo de T-spin y líneas eliminadas
            points = points_table.get(line_clear_result.get("count", 0), 0) * self.level
            self.score += points
            
            # Registrar en el log el tipo específico de T-spin
            lines_str = f"{line_clear_result.get('count', 0)} línea(s)" if line_clear_result.get("count", 0) > 0 else "sin líneas"
            debugger.debug(f"¡{tspin_type} {lines_str} detectado! {points} puntos otorgados (nivel {self.level}).")
        elif tspin_result:
            # T-spin sin líneas
            if tspin_result == "T-spin":
                points = 400 * self.level
            else:  # T-spin mini
                points = 200 * self.level
                
            self.score += points
            debugger.debug(f"¡{tspin_result} sin líneas detectado! {points} puntos × nivel {self.level}")

        # Resetear flag de rotación después de fijar la pieza
        self.last_move_was_rotation = False
        
        # Generar nueva pieza solo cuando no hay animación de eliminación de líneas
        if not self.lines_to_clear:  # Si no hay líneas para eliminar, generamos una nueva pieza inmediatamente
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
            
            # Verificar si es un Perfect Clear (todos los bloques eliminados)
            is_perfect = all(all(cell == 0 for cell in row) for row in self.field)
            
            # Calcular líneas después de la eliminación
            temp_field = [self.field[y].copy() for y in range(self.height) if y not in self.lines_to_clear]
            is_perfect = len(temp_field) == 0 or all(all(cell == 0 for cell in row) for row in temp_field)
            
            return {
                "count": len(self.lines_to_clear),
                "is_tetris": (len(self.lines_to_clear) == 4),
                "is_perfect": is_perfect,  # Nuevo flag para Perfect Clear
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
            
            # Ya no es necesario generar una nueva pieza aquí, ya que se genera en el método fix_piece()
            # cuando animating_clear se establece a False
            
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