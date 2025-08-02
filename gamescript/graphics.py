# graphics.py
# Módulo para funciones gráficas del juego Tetris

import pygame
import time
from .tetris_logic import SHAPES, COLORS
from .sprite_manager import sprite_manager
from .debug_utils import debugger

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

def draw_text(surface, text, size, color, x, y, font_name=None):
    """Dibuja texto en la superficie con el tamaño y color especificados, centrado en (x,y)"""
    try:
        if font_name:
            # Intenta cargar la fuente especificada
            font = pygame.font.Font(font_name, size)
        else:
            # Si no se especifica fuente, usar Arial como respaldo
            font = pygame.font.SysFont("Arial", size)
    except:
        # Si hay error al cargar la fuente, usar Arial como respaldo
        font = pygame.font.SysFont("Arial", size)
        
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

class TetrisRenderer:
    """Clase para renderizar elementos gráficos del juego Tetris"""
    def __init__(self, screen, block_size=30):
        self.screen = screen
        self.block_size = block_size
        
        # Asegurar que los sprites estén precargados
        if not sprite_manager.loaded:
            start_time = time.time()
            sprite_manager.preload_resources()
            elapsed = time.time() - start_time
            debugger.debug(f"Tiempo de carga de sprites: {elapsed:.3f} segundos")
        
        # Obtener los sprites necesarios del gestor
        self.sprite_sheet = sprite_manager.sprites.get("sprite_sheet")
        self.board_frame = sprite_manager.get_ui_element("board_frame")
        self.hold_frame = sprite_manager.get_ui_element("hold_frame")
        self.next_frame = sprite_manager.get_ui_element("next_frame")
        
        # Tamaño de cada sprite en la hoja de sprites
        self.sprite_size = 30  # Tamaño estándar de los sprites
        
        # Usar los sprites de bloques ya precargados
        self.block_sprites = sprite_manager.block_sprites
        
        # Crear un fondo para el campo de juego si no existe
        if not self.block_sprites:
            debugger.warning("No se encontraron sprites de bloques precargados. Cargando manualmente.")
            self.extract_sprites()
        else:
            debugger.debug(f"Usando {len(self.block_sprites)} sprites de bloques precargados.")
        
        # Crear el fondo para el campo de juego
        self.background = pygame.Surface((10 * self.block_size, 20 * self.block_size))
        self.background.fill((20, 20, 40))  # Color de fondo oscuro para el campo de juego
        
        # Calcular offset para centrar el campo de juego
        screen_width, screen_height = screen.get_size()
        game_width = 10 * block_size  # 10 columnas del campo de juego
        game_height = 20 * block_size  # 20 filas del campo de juego
        self.offset_x = (screen_width - game_width) // 2
        self.offset_y = (screen_height - game_height) // 2
    
    def extract_sprites(self):
        """Extrae los sprites individuales de la hoja de sprites (fallback)"""
        # Este método solo se usa si sprite_manager falla en cargar los sprites
        debugger.debug("Extrayendo sprites manualmente como respaldo...")
        
        if self.sprite_sheet is None:
            try:
                self.sprite_sheet = pygame.image.load("assets/img/sprites.png")
            except Exception as e:
                debugger.error(f"Error al cargar la hoja de sprites: {str(e)}")
                return
        
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
        
        # Dibujar el marco del tablero alrededor del campo de juego
        # Ajustar el tamaño del marco al tamaño del campo de juego
        frame_offset_x = self.offset_x + offset_x - 15  # Aumentar el margen para evitar invasión
        frame_offset_y = self.offset_y + offset_y - 15
        frame_width = game.width * self.block_size + 30  # Aumentar margen total
        frame_height = game.height * self.block_size + 30
        
        # Escalar el marco al tamaño adecuado
        scaled_frame = pygame.transform.scale(self.board_frame, (frame_width, frame_height))
        # Dibujar el marco primero, antes que los bloques, para que quede detrás
        self.screen.blit(scaled_frame, (frame_offset_x, frame_offset_y))
        
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
    
    def draw_next_piece(self, game, x, y, box_width, box_height, piece_index=0):
        """Dibuja la próxima pieza centrada en una caja específica"""
        # Si es la primera pieza (piece_index=0), usar next_piece_type
        # Si son las siguientes (piece_index>0), usar game.next_pieces si está disponible
        if piece_index == 0:
            if game.next_piece_type is None:
                return
            shape = game.next_piece_shape
            piece_type = game.next_piece_type + 1
        else:
            # Para piezas adicionales, buscarlas en next_pieces si está disponible
            if not hasattr(game, 'next_pieces') or len(game.next_pieces) <= piece_index:
                return
            piece_type = game.next_pieces[piece_index] + 1
            shape = SHAPES[game.next_pieces[piece_index]][0]  # Primera rotación

        # Calcular las dimensiones reales ocupadas por la pieza
        occupied_rows = []
        occupied_cols = []
        
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col] != 0:
                    occupied_rows.append(row)
                    occupied_cols.append(col)
        
        if not occupied_rows:
            return
            
        min_row = min(occupied_rows)
        max_row = max(occupied_rows)
        min_col = min(occupied_cols)
        max_col = max(occupied_cols)
        
        piece_width = (max_col - min_col + 1) * self.block_size
        piece_height = (max_row - min_row + 1) * self.block_size
        
        # Calcular offset para centrar la pieza en la caja
        center_offset_x = (box_width - piece_width) // 2
        center_offset_y = (box_height - piece_height) // 2
        
        # Dibujar la pieza centrada
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col] != 0:
                    screen_x = x + center_offset_x + (col - min_col) * self.block_size
                    screen_y = y + center_offset_y + (row - min_row) * self.block_size
                    self.screen.blit(self.block_sprites[piece_type], (screen_x, screen_y))
    
    def draw_hold_piece(self, game, x, y, box_width, box_height):
        """Dibuja la pieza en hold centrada en una caja específica"""
        if game.hold_piece_type is None:
            return
            
        shape = SHAPES[game.hold_piece_type][0]
        piece_type = game.hold_piece_type + 1

        # Calcular las dimensiones reales ocupadas por la pieza
        occupied_rows = []
        occupied_cols = []
        
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col] != 0:
                    occupied_rows.append(row)
                    occupied_cols.append(col)
        
        if not occupied_rows:
            return
            
        min_row = min(occupied_rows)
        max_row = max(occupied_rows)
        min_col = min(occupied_cols)
        max_col = max(occupied_cols)
        
        piece_width = (max_col - min_col + 1) * self.block_size
        piece_height = (max_row - min_row + 1) * self.block_size
        
        # Calcular offset para centrar la pieza en la caja
        center_offset_x = (box_width - piece_width) // 2
        center_offset_y = (box_height - piece_height) // 2
        
        # Dibujar la pieza centrada
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col] != 0:
                    screen_x = x + center_offset_x + (col - min_col) * self.block_size
                    screen_y = y + center_offset_y + (row - min_row) * self.block_size
                    self.screen.blit(self.block_sprites[piece_type], (screen_x, screen_y))
    
    def draw_game_info(self, game, next_piece_x, next_piece_y):
        """Dibuja la información del juego (puntuación, nivel, etc)"""
        # Dimensiones de las cajas para las piezas
        box_width = self.block_size * 5  # 150px para área de pieza
        box_height = self.block_size * 3  # 90px para área de pieza
        
        # Dimensiones del frame (incluyendo bordes de 20px)
        frame_width = box_width + 40  # 190px total
        frame_height = box_height + 40  # 130px total
        
        # Marco y posición para próxima pieza (next1)
        frame_x = next_piece_x - 20  # Offset del borde del frame
        frame_y = next_piece_y - 20
        
        # Escalamos el frame nextframe a 190x360px para cubrir el espacio vertical de los 3 next frames
        next_frame_total_height = 360  # Altura total que cubre next1+next2+next3
        scaled_next_frame = pygame.transform.scale(self.next_frame, (frame_width, next_frame_total_height))
        self.screen.blit(scaled_next_frame, (frame_x, frame_y))

        # Dibujar próxima pieza centrada en el área interior del frame
        self.draw_next_piece(game, next_piece_x, next_piece_y, box_width, box_height)
        
        # Definir dimensiones para Next2 y Next3 sin mostrar sus recuadros
        next_box_width = 160 - 40  # 160px (ancho total) - 40px (bordes) = 120px
        next_frame_width = 160
        
        # Calcular posiciones de next2 y next3 sin dibujar sus frames
        next2_frame_y = frame_y + frame_height - 20  # Eliminar el espaciado vertical entre cajas
        next3_frame_y = next2_frame_y + 130 - 20  # 130px es la altura del frame next2
        
        # Ya no dibujamos los marcos para next2 y next3
        # Solo el marco para next1 se mantiene visible
        
        # Dibujar Next2 y Next3 si están disponibles
        if hasattr(game, 'next_pieces') and len(game.next_pieces) >= 3:
            # Mover next2 y next3 15 pixels más a la izquierda
            next2_x = next_piece_x + (box_width - next_box_width) // 2 - 15
            next2_y = next_piece_y + frame_height - 20 # Eliminar espaciado vertical
            next3_x = next_piece_x + (box_width - next_box_width) // 2 - 15
            next3_y = next2_y + frame_height - 20 # Eliminar espaciado vertical
            
            # Dibujar las piezas
            if len(game.next_pieces) > 1:
                self.draw_next_piece(game, next2_x, next2_y, next_box_width, box_height, piece_index=1)
            if len(game.next_pieces) > 2:
                self.draw_next_piece(game, next3_x, next3_y, next_box_width, box_height, piece_index=2)

        # Marco y posición para Hold (con más separación del campo de juego)
        hold_x = self.offset_x - box_width - 55  # Más separación para evitar conflicto
        hold_y = self.offset_y + self.block_size * 2

        hold_frame_x = hold_x - 20  # Offset del borde del frame
        hold_frame_y = hold_y - 20
        scaled_hold_frame = pygame.transform.scale(self.hold_frame, (frame_width, frame_height))
        self.screen.blit(scaled_hold_frame, (hold_frame_x, hold_frame_y))

        # Dibujar pieza Hold centrada en el área interior del frame
        self.draw_hold_piece(game, hold_x, hold_y, box_width, box_height)
        
        # Panel de información alineado con el Hold box (misma posición X)
        info_x = hold_frame_x  # Usar la misma posición X que el hold frame
        info_y = hold_y + box_height + 40  # Posición vertical justo debajo del hold
        
        # Crear un recuadro transparente con borde blanco para la información del juego
        info_width = 190  # Ancho fijo de 190px como se solicita
        info_height = 320  # Altura fija de 320px como se solicita
        info_rect = pygame.Rect(info_x, info_y, info_width, info_height)
        
        # Crear superficie transparente
        info_surface = pygame.Surface((info_width, info_height), pygame.SRCALPHA)
        info_surface.fill((0, 0, 0, 150))  # Negro semi-transparente (alpha=150)
        
        # Dibujar superficie transparente con offset correcto
        self.screen.blit(info_surface, (info_x, info_y))
        
        # Dibujar borde blanco de 3px
        pygame.draw.rect(self.screen, (255, 255, 255), info_rect, 3)
        
        # Centro del panel de información para centrar el texto
        info_center_x = info_x + (info_width // 2)
        
        # Cargar la fuente correcta para los textos de información
        try:
            font = pygame.font.Font("assets/fonts/mainfont.ttf", 24)
        except:
            font = pygame.font.SysFont("Arial", 24)
            
        # Función para dibujar texto con la fuente cargada
        def draw_info_text(text, y_pos, color=WHITE):
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(info_center_x, y_pos))
            self.screen.blit(text_surface, text_rect)
        
        # Dibujar textos de información con offset adicional para evitar que se corte con la línea
        draw_info_text(f"Puntuación: {game.score}", info_y + 20)
        draw_info_text(f"Nivel: {game.level}", info_y + 50)
        draw_info_text(f"Líneas: {game.lines_cleared}", info_y + 80)
        
        # Mostrar información específica del modo de juego
        if hasattr(game, 'mode_name'):
            # Mostrar el nombre del modo
            mode_y = info_y + 110
            draw_info_text(f"Modo: {game.mode_name}", mode_y, (255, 255, 100))
            
            # Mostrar información específica del modo
            if hasattr(game, 'get_time_str') and game.mode_name in ["Contrarreloj", "Ultra"]:
                # Mostrar tiempo restante para modos de tiempo
                time_str = game.get_time_str()
                draw_info_text(f"Tiempo: {time_str}", mode_y + 30, (255, 200, 100))
            elif hasattr(game, 'get_progress_str') and game.mode_name == "Maratón":
                # Mostrar progreso para modo maratón
                progress_str = game.get_progress_str()
                draw_info_text(progress_str, mode_y + 30, (100, 255, 100))
        
        # Los controles ahora solo se muestran en el menú de pausa

    def draw_game_over(self, screen, game, settings):
        """Dibuja la pantalla de Game Over"""
        # Dibujar un panel semi-transparente
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        
        # Comprobar si es game over o victoria en modo maratón
        game_over_text = "¡GAME OVER!"
        text_color = WHITE
        
        # Si es un modo específico con mensaje personalizado
        if hasattr(game, 'game_over_reason'):
            game_over_text = game.game_over_reason
            
            # Color especial para mensaje de victoria
            if game_over_text == "¡COMPLETADO!":
                text_color = (100, 255, 100)  # Verde para victoria
        
        # Mostrar modo de juego si está disponible
        mode_text = ""
        if hasattr(game, 'mode_name'):
            mode_text = f"Modo: {game.mode_name}"
            draw_text(screen, mode_text, 36, (255, 255, 100), center_x, center_y - 90)
        
        draw_text(screen, game_over_text, 48, text_color, center_x, center_y - 50)
        draw_text(screen, f"Puntuación final: {game.score}", 30, WHITE, center_x, center_y)
        draw_text(screen, "ESC para volver al menú", 24, WHITE, center_x, center_y + 50)
        draw_text(screen, "ENTER para reintentar", 24, WHITE, center_x, center_y + 80)
        draw_text(screen, "H para ver Puntuaciones Altas", 24, WHITE, center_x, center_y + 110)

def draw_pause_menu(screen, settings, selected, options):
    """Dibuja el menú de pausa"""
    # Overlay semi-transparente
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(200)
    overlay.fill((20, 20, 40))
    screen.blit(overlay, (0, 0))

    # Usar la fuente mainfont.ttf para el título "Pausa"
    draw_text(screen, "Pausa", 64, (255, 255, 255), screen.get_width() // 2, 80, "assets/fonts/mainfont.ttf")

    # Usar mainfont.ttf para las opciones del menú
    for i, option in enumerate(options):
        color = (255, 255, 255) if i == selected else (180, 180, 180)
        label = option
        
        if option == "Volumen General":
            label += f": {int(settings['volume_general'] * 100)}%"
        elif option == "Volumen BGM":
            label += f": {int(settings['volume_bgm'] * 100)}%"
        elif option == "Volumen SFX":
            label += f": {int(settings['volume_sfx'] * 100)}%"
            
        draw_text(screen, label, 40, color, screen.get_width() // 2, 150 + i * 60, "assets/fonts/mainfont.ttf")
    
    # Solo mostrar controles si la opción seleccionada es "Información"
    if options[selected] == "Información":
        # Posicionar los controles en el lado derecho de la pantalla
        controls_x = screen.get_width() * 3 / 4  # 75% del ancho de la pantalla
        controls_y = 150  # Misma altura que las opciones del menú
        
        # Título de los controles
        draw_text(screen, "Controles:", 30, (220, 220, 220), controls_x, controls_y, None)
        
        # Controles alineados a la derecha usando Arial (None significa que usará SysFont Arial)
        arial_font = pygame.font.SysFont("Arial", 20)
        controls_list = [
            "← → : Mover izquierda/derecha",
            "↑ Z : Rotar sentido horario",
            "X : Rotar sentido anti-horario",
            "↓ : Caída suave",
            "ESPACIO : Caída dura",
            "C : Guardar pieza (Hold)",
            "ESC : Pausar juego"
        ]
        
        for i, control_text in enumerate(controls_list):
            text_surface = arial_font.render(control_text, True, (200, 200, 200))
            text_rect = text_surface.get_rect(center=(controls_x, controls_y + 40 + i*30))
            screen.blit(text_surface, text_rect)

    pygame.display.flip()