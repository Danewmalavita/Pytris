# graphics.py
# Módulo para funciones gráficas del juego Tetris

import pygame
from tetris_logic import SHAPES, COLORS

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

def draw_text(surface, text, size, color, x, y):
    """Dibuja texto en la superficie con el tamaño y color especificados, centrado en (x,y)"""
    font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

class TetrisRenderer:
    """Clase para renderizar elementos gráficos del juego Tetris"""
    def __init__(self, screen, block_size=30):
        self.screen = screen
        self.block_size = block_size
        
        # Cargar sprites
        self.sprite_sheet = pygame.image.load("assets/img/sprites.png")
        
        # Tamaño de cada sprite en la hoja de sprites
        self.sprite_size = 30  # Tamaño estándar de los sprites
        
        # Crear diccionario de sprites de bloques
        self.block_sprites = {}
        self.background = None
        self.extract_sprites()
        
        # Calcular offset para centrar el campo de juego
        screen_width, screen_height = screen.get_size()
        game_width = 10 * block_size  # 10 columnas del campo de juego
        game_height = 20 * block_size  # 20 filas del campo de juego
        self.offset_x = (screen_width - game_width) // 2
        self.offset_y = (screen_height - game_height) // 2
    
    def extract_sprites(self):
        """Extrae los sprites individuales de la hoja de sprites"""
        # Extraer los sprites de bloques (suponiendo que están en la primera fila)
        for i in range(8):  # 0 (vacío) + 7 colores de tetraminos
            # Obtener el rectángulo del sprite en la hoja
            sprite_rect = pygame.Rect(i * self.sprite_size, 0, self.sprite_size, self.sprite_size)
            
            # Crear una nueva superficie para el sprite
            block_sprite = pygame.Surface((self.sprite_size, self.sprite_size), pygame.SRCALPHA)
            
            # Copiar el sprite de la hoja a la nueva superficie
            block_sprite.blit(self.sprite_sheet, (0, 0), sprite_rect)
            
            # Guardar el sprite en el diccionario
            self.block_sprites[i] = block_sprite
        
        # También extraer el fondo del nivel (suponiendo que está en otra parte del sprite sheet)
        # Por ahora, simplemente crear un fondo negro
        self.background = pygame.Surface((10 * self.block_size, 20 * self.block_size))
        self.background.fill((20, 20, 40))  # Color de fondo oscuro para el campo de juego
    
    def draw_block(self, x, y, block_type, alpha=255, offset_x=0, offset_y=0):
        """Dibuja un bloque del tipo especificado en la posición (x,y) del campo"""
        if block_type >= 0 and block_type < len(self.block_sprites):
            # Obtener el sprite del bloque
            sprite = self.block_sprites[block_type]
            
            # Si se requiere transparencia
            if alpha < 255:
                sprite_copy = sprite.copy()
                sprite_copy.set_alpha(alpha)
                sprite = sprite_copy
            
            # Calcular la posición real en pantalla (incluyendo offset de efectos visuales)
            screen_x = self.offset_x + x * self.block_size + offset_x
            screen_y = self.offset_y + y * self.block_size + offset_y
            
            # Dibujar el sprite
            self.screen.blit(sprite, (screen_x, screen_y))
    
    def draw_field(self, game, highlight_lines=None, offset_x=0, offset_y=0):
        """Dibuja el campo de juego completo, resaltando líneas si se anima"""
        self.screen.blit(self.background, (self.offset_x + offset_x, self.offset_y + offset_y))
        
        # Dibujar la rejilla del tablero de juego
        grid_color = (50, 50, 70)  # Color sutil para la rejilla
        
        # Líneas horizontales
        for y in range(game.height + 1):
            pygame.draw.line(
                self.screen, 
                grid_color,
                (self.offset_x + offset_x, self.offset_y + y * self.block_size + offset_y),
                (self.offset_x + game.width * self.block_size + offset_x, self.offset_y + y * self.block_size + offset_y),
                1  # grosor de la línea
            )
        
        # Líneas verticales
        for x in range(game.width + 1):
            pygame.draw.line(
                self.screen,
                grid_color,
                (self.offset_x + x * self.block_size + offset_x, self.offset_y + offset_y),
                (self.offset_x + x * self.block_size + offset_x, self.offset_y + game.height * self.block_size + offset_y),
                1  # grosor de la línea
            )
        
        for y in range(game.height):
            for x in range(game.width):
                block = game.field[y][x]
                if block != 0:
                    if highlight_lines and y in highlight_lines:
                        self.draw_block(x, y, block, alpha=120, offset_x=offset_x, offset_y=offset_y)  # Efecto visual tenue
                    else:
                        self.draw_block(x, y, block, offset_x=offset_x, offset_y=offset_y)
    
    def draw_current_piece(self, game, offset_x=0, offset_y=0):
        """Dibuja la pieza activa"""
        if game.game_over:
            return
            
        # Obtener la forma de la pieza activa
        shape = game.get_piece_shape()
        piece_type = game.get_piece_type()
        
        # Dibujar la posición fantasma (donde caería la pieza)
        ghost_y = game.get_ghost_position()
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col] != 0:
                    self.draw_block(game.piece_x + col, ghost_y + row, piece_type, alpha=80, offset_x=offset_x, offset_y=offset_y)  # Semi-transparente
        
        # Dibujar la pieza activa
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col] != 0:
                    self.draw_block(game.piece_x + col, game.piece_y + row, piece_type, offset_x=offset_x, offset_y=offset_y)
    
    def draw_next_piece(self, game, x, y):
        """Dibuja la próxima pieza centrada en una posición específica (4x4)"""
        if game.next_piece_type is None:
            return

        shape = game.next_piece_shape
        piece_type = game.next_piece_type + 1

        # Calcular dimensiones reales de la pieza
        rows = len(shape)
        cols = len(shape[0])
        min_x, min_y = 4, 4
        max_x, max_y = 0, 0

        for row in range(rows):
            for col in range(cols):
                if shape[row][col] != 0:
                    min_x = min(min_x, col)
                    max_x = max(max_x, col)
                    min_y = min(min_y, row)
                    max_y = max(max_y, row)

        width = max_x - min_x + 1
        height = max_y - min_y + 1

        # Centrar la pieza dentro del recuadro de 4x4
        offset_x = (4 - width) // 2
        offset_y = (4 - height) // 2

        for row in range(rows):
            for col in range(cols):
                if shape[row][col] != 0:
                    screen_x = x + (col - min_x + offset_x) * self.block_size
                    screen_y = y + (row - min_y + offset_y) * self.block_size
                    self.screen.blit(self.block_sprites[piece_type], (screen_x, screen_y))
    
    def draw_hold_piece(self, game, x, y):
        """Dibuja la pieza en hold"""
        if game.hold_piece_type is None:
            return
            
        shape = SHAPES[game.hold_piece_type][0]
        piece_type = game.hold_piece_type + 1

        rows = len(shape)
        cols = len(shape[0])
        min_x, min_y = 4, 4
        max_x, max_y = 0, 0

        for row in range(rows):
            for col in range(cols):
                if shape[row][col] != 0:
                    min_x = min(min_x, col)
                    max_x = max(max_x, col)
                    min_y = min(min_y, row)
                    max_y = max(max_y, row)

        width = max_x - min_x + 1
        height = max_y - min_y + 1

        offset_x = (4 - width) // 2
        offset_y = (4 - height) // 2

        for row in range(rows):
            for col in range(cols):
                if shape[row][col] != 0:
                    screen_x = x + (col - min_x + offset_x) * self.block_size
                    screen_y = y + (row - min_y + offset_y) * self.block_size
                    self.screen.blit(self.block_sprites[piece_type], (screen_x, screen_y))
    
    def draw_game_info(self, game, next_piece_x, next_piece_y):
        """Dibuja la información del juego (puntuación, nivel, etc)"""
        # Recuadro de próxima pieza (4x4)
        pygame.draw.rect(self.screen, (80, 80, 80),
            (next_piece_x - 5, next_piece_y - 5, self.block_size * 4 + 10, self.block_size * 4 + 10),
            2)
        draw_text(self.screen, "Next", 20, WHITE, next_piece_x + self.block_size * 2, next_piece_y - 20)

        # Dibujar próxima pieza
        self.draw_next_piece(game, next_piece_x, next_piece_y)

        # Recuadro de Hold (máximo 4x4)
        hold_x = self.offset_x - self.block_size * 5  # Ajustar para que no toque el área de juego
        hold_y = self.offset_y + self.block_size * 2

        pygame.draw.rect(self.screen, (80, 80, 80),
            (hold_x - 5, hold_y - 5, self.block_size * 4 + 10, self.block_size * 4 + 10),
            2)
        draw_text(self.screen, "Hold", 20, WHITE, hold_x + self.block_size * 2, hold_y - 20)

        # Dibujar pieza Hold si existe
        self.draw_hold_piece(game, hold_x, hold_y)
        
        # Dibujar puntuación, nivel y líneas
        score_y = next_piece_y + self.block_size * 6
        draw_text(self.screen, f"Puntuación: {game.score}", 24, WHITE, next_piece_x + self.block_size * 3, score_y)
        draw_text(self.screen, f"Nivel: {game.level}", 24, WHITE, next_piece_x + self.block_size * 3, score_y + 30)
        draw_text(self.screen, f"Líneas: {game.lines_cleared}", 24, WHITE, next_piece_x + self.block_size * 3, score_y + 60)
        
        # Dibujar controles
        controls_y = score_y + 120
        draw_text(self.screen, "Controles:", 20, WHITE, next_piece_x + self.block_size * 3, controls_y)
        draw_text(self.screen, "←/→: Mover", 18, GRAY, next_piece_x + self.block_size * 3, controls_y + 25)
        draw_text(self.screen, "↑: Rotar", 18, GRAY, next_piece_x + self.block_size * 3, controls_y + 45)
        draw_text(self.screen, "↓: Caída rápida", 18, GRAY, next_piece_x + self.block_size * 3, controls_y + 65)
        draw_text(self.screen, "Espacio: Soltar", 18, GRAY, next_piece_x + self.block_size * 3, controls_y + 85)
        draw_text(self.screen, "ESC: Pausar", 18, GRAY, next_piece_x + self.block_size * 3, controls_y + 105)
    
    def draw_game_over(self, screen, game, settings):
        """Dibuja la pantalla de Game Over"""
        # Dibujar un panel semi-transparente
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        
        draw_text(screen, "¡GAME OVER!", 48, WHITE, center_x, center_y - 50)
        draw_text(screen, f"Puntuación final: {game.score}", 30, WHITE, center_x, center_y)
        draw_text(screen, "ESC para volver al menú", 24, WHITE, center_x, center_y + 50)
        draw_text(screen, "ENTER para reintentar", 24, WHITE, center_x, center_y + 80)
        draw_text(screen, "H para ver Puntuaciones Altas", 24, WHITE, center_x, center_y + 110)

def draw_pause_menu(screen, settings, selected, options):
    """Dibuja el menú de pausa"""
    screen.fill((50, 20, 20))

    draw_text(screen, "Pausa", 64, (255, 255, 255), screen.get_width() // 2, 80)

    for i, option in enumerate(options):
        color = (255, 255, 255) if i == selected else (180, 180, 180)
        label = option
        
        if option == "Volumen General":
            label += f": {int(settings['volume_general'] * 100)}%"
        elif option == "Volumen BGM":
            label += f": {int(settings['volume_bgm'] * 100)}%"
        elif option == "Volumen SFX":
            label += f": {int(settings['volume_sfx'] * 100)}%"
            
        draw_text(screen, label, 40, color, screen.get_width() // 2, 150 + i * 60)

    pygame.display.flip()