# menu.py
import pygame
import math
from .options import options_menu
from .settings import resol
# Import start_game conditionally to avoid circular import
# game will be imported when needed

# Colores de los tetrominós clásicos
COLORS = {
    'I': (0, 255, 255),    # Cian
    'O': (255, 255, 0),    # Amarillo
    'T': (160, 32, 240),   # Púrpura
    'S': (0, 255, 0),      # Verde
    'Z': (255, 0, 0),      # Rojo
    'J': (0, 100, 255),    # Azul
    'L': (255, 165, 0),    # Naranja
    'bg': (15, 15, 35),    # Fondo más oscuro
    'border': (100, 100, 100)
}

# Definimos el tamaño del sprite (usado en graphics.py)
SPRITE_SIZE = 30

def draw_pytris_logo_animated(surface, animation_progress, center_x, center_y):
    """
    Dibujar el logo PYTRIS animado centrado en las coordenadas especificadas usando sprites
    animation_progress: float de 0.0 a 1.0 indicando el progreso de la animación
    """
    # Importar el módulo de gráficos para usar los sprites
    from .graphics import TetrisRenderer
    
    # Crear un renderer temporal para usar los sprites
    # El tamaño del bloque debe ser el del sprite original en graphics.py (30px)
    SPRITE_SIZE = 30
    temp_renderer = TetrisRenderer(surface, block_size=SPRITE_SIZE)
    
    # Definir cada letra como una matriz de bloques con tipo de tetromino
    letters = {
        'P': {
            'blocks': [
                [1, 1, 1, 1],
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [1, 1, 1, 1],
                [1, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 0, 0, 0]
            ],
            'block_type': 6  # Tipo correspondiente a color púrpura (T)
        },
        'Y': {
            'blocks': [
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0]
            ],
            'block_type': 2  # Tipo correspondiente a color amarillo (O)
        },
        'T': {
            'blocks': [
                [1, 1, 1, 1, 1],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0]
            ],
            'block_type': 1  # Tipo correspondiente a color cian (I)
        },
        'R': {
            'blocks': [
                [1, 1, 1, 1],
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [1, 1, 1, 1],
                [1, 1, 0, 0],
                [1, 0, 1, 0],
                [1, 0, 0, 1],
                [1, 0, 0, 1]
            ],
            'block_type': 4  # Tipo correspondiente a color verde (S)
        },
        'I': {
            'blocks': [
                [1, 1, 1],
                [0, 1, 0],
                [0, 1, 0],
                [0, 1, 0],
                [0, 1, 0],
                [0, 1, 0],
                [0, 1, 0],
                [1, 1, 1]
            ],
            'block_type': 3  # Tipo correspondiente a color rojo (Z)
        },
        'S': {
            'blocks': [
                [1, 1, 1, 1],
                [1, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 1, 1, 0],
                [0, 0, 0, 1],
                [0, 0, 0, 1],
                [0, 0, 0, 1],
                [1, 1, 1, 1]
            ],
            'block_type': 7  # Tipo correspondiente a color naranja (L)
        }
    }
    
    # Calcular dimensiones totales del logo
    letter_widths = [4, 4, 5, 4, 3, 4]  # Ancho de cada letra en bloques
    letter_spacing = 1  # Espacio entre letras
    total_width = sum(letter_widths) + (len(letter_widths) - 1) * letter_spacing
    total_height = 8  # Altura máxima de las letras
    
    # Calcular posición inicial para centrar el logo
    start_x = center_x - (total_width * SPRITE_SIZE) // 2
    start_y = center_y - (total_height * SPRITE_SIZE) // 2
    
    # Definir el orden de las letras
    letter_order = ['P', 'Y', 'T', 'R', 'I', 'S']
    
    # Calcular cuántas letras mostrar basado en el progreso
    num_letters_to_show = int(animation_progress * len(letter_order))
    if animation_progress >= 1.0:
        num_letters_to_show = len(letter_order)
    
    # Dibujar las letras
    current_x = 0
    for i, letter_name in enumerate(letter_order):
        if i < num_letters_to_show:
            letter_data = letters[letter_name]
            
            # Efecto de aparición para la letra actual
            if i == num_letters_to_show - 1 and animation_progress < 1.0:
                # Calcular progreso de la letra actual
                letter_progress = (animation_progress * len(letter_order)) - i
                
                # Efecto de alpha para la letra que está apareciendo (50% a 100%)
                alpha = int(128 + 127 * letter_progress)
            else:
                alpha = 255
            
            # Dibujar la letra usando los sprites
            for row_idx, row in enumerate(letter_data['blocks']):
                for col_idx, cell in enumerate(row):
                    if cell == 1:
                        # Calcular posición en pantalla
                        screen_x = start_x + current_x + col_idx * SPRITE_SIZE
                        screen_y = start_y + row_idx * SPRITE_SIZE
                        
                        # Usar el sprite correspondiente a esta letra
                        block_type = letter_data['block_type']
                        
                        # Obtener el sprite
                        sprite = temp_renderer.block_sprites[block_type]
                        
                        # Si hay animación de aparición, aplicar alpha
                        if alpha < 255:
                            sprite_copy = sprite.copy()
                            sprite_copy.set_alpha(alpha)
                            sprite = sprite_copy
                        
                        # Dibujar el sprite
                        surface.blit(sprite, (screen_x, screen_y))
        
        # Mover a la siguiente posición
        current_x += (letter_widths[i] + letter_spacing) * SPRITE_SIZE

def draw_text(surface, text, size, color, x, y):
    font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def main_menu(screen, settings):
    clock = pygame.time.Clock()
    
    # Importar el módulo de controles
    from .controls import handle_main_menu_controls
    
    # Comprobar si el audio está disponible
    audio_available = pygame.mixer.get_init() is not None
    
    # Configuración de audio solo si está disponible
    if audio_available:
        try:
            pygame.mixer.music.load("./assets/sounds/bgm/menu.mp3")
            
            # Aplicar los ajustes de volumen
            actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
            pygame.mixer.music.set_volume(actual_music_vol)
            
            if not settings['mute']:
                pygame.mixer.music.play(-1)
                
            # Cargar efectos de sonido
            sfx_cursor = pygame.mixer.Sound("assets/sounds/sfx/cursor.wav")
            sfx_enter = pygame.mixer.Sound("assets/sounds/sfx/enter.wav")
            sfx_back = pygame.mixer.Sound("assets/sounds/sfx/back.wav")
            
            # Ajustar volumen de efectos de sonido según la configuración
            sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
            sfx_cursor.set_volume(sfx_vol)
            sfx_enter.set_volume(sfx_vol)
            sfx_back.set_volume(sfx_vol)
        except (pygame.error, FileNotFoundError):
            audio_available = False
            settings['mute'] = True
    else:
        settings['mute'] = True
        
    # Crear objetos nulos para los efectos si no hay audio
    if not audio_available:
        class DummySound:
            def play(self): pass
            def set_volume(self, vol): pass
            
        sfx_cursor = DummySound()
        sfx_enter = DummySound()
        sfx_back = DummySound()

    menu_items = ["Modo Arcade", "Puntuaciones", "Opciones", "Salir"]
    selected = 0
    
    # Variables para la animación del logo
    logo_animation_start = pygame.time.get_ticks()
    logo_animation_duration = 2500  # 2.5 segundos para completar la animación
    logo_completed = False
    
    # Variables para el efecto de aparición del menú
    menu_start_time = 0
    
    # Variables para efectos visuales
    bg_animation = 0
    glow_timer = 0
    show_glow = False

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # Calcular progreso de la animación del logo
        if not logo_completed:
            elapsed_time = current_time - logo_animation_start
            logo_progress = min(1.0, elapsed_time / logo_animation_duration)
            if logo_progress >= 1.0 and not logo_completed:
                logo_completed = True
                menu_start_time = current_time  # Iniciar temporizador para la aparición del menú
        else:
            logo_progress = 1.0
            
        # Fondo animado
        bg_animation += 1
        bg_color = (
            10 + int(8 * abs(math.sin(bg_animation * 0.008))),
            10 + int(8 * abs(math.sin(bg_animation * 0.010))),
            50 + int(15 * abs(math.sin(bg_animation * 0.012)))
        )
        screen.fill(bg_color)
        
        # Dibujar el logo PYTRIS animado centrado horizontalmente
        center_x = screen.get_width() // 2
        center_y = 200  # Posición vertical del logo (ajustada para el tamaño más grande de los sprites)
        draw_pytris_logo_animated(screen, logo_progress, center_x, center_y)
        
        # Efecto de fondo estilo tetris: bloques cayendo lentamente
        current_time_ms = pygame.time.get_ticks()
        from .graphics import TetrisRenderer
        bg_renderer = TetrisRenderer(screen)
        block_size = 30  # Definimos el tamaño del bloque para los efectos de fondo
        
        # En vez de usar la franja de colores, generamos bloques aleatorios más dispersos
        # Esto creará un fondo más sutil y menos estructurado
        
        # Dibujar estrellas/bloques dispersos en el fondo para dar profundidad
        # Generamos posiciones aleatorias pero deterministas basadas en tiempo
        num_background_blocks = 25  # Menos bloques para un fondo más limpio
        
        # Usamos el tiempo para generar diferentes "semillas" para posiciones aleatorias
        # pero mantenemos cierta coherencia entre frames
        seed_time = int(current_time_ms / 10000)  # Cambia cada 10 segundos
        
        # Usar el tiempo para tener bloques que aparecen y desaparecen lentamente
        for i in range(num_background_blocks):
            # Crear un patrón pseudo-aleatorio pero determinista
            # Esto hace que los bloques aparezcan en posiciones que parecen aleatorias
            # pero son coherentes durante periodos de tiempo
            x_factor = math.sin(i * 0.3 + seed_time * 0.1) * 0.5 + 0.5
            y_factor = math.cos(i * 0.4 + seed_time * 0.2) * 0.5 + 0.5
            
            # Calcular posición basada en estos factores
            x_pos = int(x_factor * screen.get_width())
            y_pos = int(y_factor * screen.get_height())
            
            # Determinar si el bloque está visible basado en una función de tiempo
            visibility_factor = math.sin(i + current_time_ms / 3000)
            
            # Solo dibujar si la visibilidad es positiva
            if visibility_factor > 0:
                # Tipo de bloque basado en índice (1-7 para los diferentes tetrominos)
                block_type = (i % 7) + 1
                
                # Alpha basado en visibilidad para un efecto de pulso suave
                alpha = int(40 + 30 * visibility_factor)
                
                # Convertir a coordenadas de bloques
                block_col = int(x_pos / block_size)
                block_row = int(y_pos / block_size)
                
                # Dibujar el bloque con transparencia baja
                bg_renderer.draw_block(block_col, block_row, block_type, alpha=alpha)
        
        # Añadir algunos tetrominos completos cayendo para efecto visual
        # Definir formas de tetrominos similares a game.py
        tetromino_shapes = [
            [[1, 1, 1, 1]],  # I
            [[1, 1], [1, 1]],  # O
            [[0, 1, 0], [1, 1, 1]],  # T
            [[0, 1, 1], [1, 1, 0]],  # S
            [[1, 1, 0], [0, 1, 1]],  # Z
            [[1, 0, 0], [1, 1, 1]],  # J
            [[0, 0, 1], [1, 1, 1]]   # L
        ]
        
        # Dibujar algunos tetrominos cayendo
        for i in range(3):  # 3 piezas cayendo
            # Velocidad de caída basada en el tiempo
            speed = (current_time_ms / 10000) % 1  # 0 a 1
            
            # Posición X fija pero aleatoria por pieza
            x_pos = (screen.get_width() * (0.3 + i * 0.2)) % screen.get_width()
            
            # Posición Y basada en el tiempo (efecto de caída)
            y_pos = (speed * screen.get_height() * 2 + i * 200) % (screen.get_height() + 200) - 100
            
            # Elegir tipo de tetromino
            tetromino_type = (i + int(current_time_ms / 3000)) % 7
            shape = tetromino_shapes[tetromino_type]
            block_type = tetromino_type + 1
            
            # Dibujar la pieza
            for row_idx, row in enumerate(shape):
                for col_idx, cell in enumerate(row):
                    if cell == 1:
                        screen_x = int(x_pos + col_idx * block_size)
                        screen_y = int(y_pos + row_idx * block_size)
                        block_col = int(screen_x / block_size)
                        block_row = int(screen_y / block_size)
                        # Alpha variable para efecto de desvanecimiento
                        alpha = int(150 + 50 * math.sin(current_time_ms / 500 + i))
                        bg_renderer.draw_block(block_col, block_row, block_type, alpha=alpha)
        
        # Subtítulo en la parte inferior de la pantalla
        if logo_progress > 0.8:  # Mostrar subtítulo cuando el logo esté casi completo
            subtitle_alpha = int(255 * min(1.0, (logo_progress - 0.8) / 0.2))
            subtitle_color = (180, 180, 180)
            # Colocamos el subtítulo en la parte inferior de la pantalla
            footer_y = screen.get_height() - 30  # 30px desde el borde inferior
            
            if subtitle_alpha < 255:
                # Crear superficie temporal para el alpha
                temp_surface = pygame.Surface((screen.get_width(), 30))
                temp_surface.set_alpha(subtitle_alpha)
                temp_surface.fill(bg_color)
                font_small = pygame.font.Font(None, 24)
                subtitle_text = font_small.render("2025 Danew Malavita", True, subtitle_color)
                subtitle_rect = subtitle_text.get_rect(center=(screen.get_width() // 2, 15))
                temp_surface.blit(subtitle_text, subtitle_rect)
                screen.blit(temp_surface, (0, footer_y - 15))
            else:
                draw_text(screen, "2025 Danew Malavita", 24, subtitle_color, screen.get_width() // 2, footer_y)

        # Menú principal - sólo se muestra cuando la animación del logo termina
        menu_start_y = 390  # Posición inicial más alta
        menu_spacing = 50  # Menor espaciado entre opciones (antes era 80)
        menu_alpha = 0
        
        if logo_completed:
            # Calcular alpha para el menú (fadeIn)
            elapsed_since_completed = current_time - (logo_animation_start + logo_animation_duration)
            menu_fadein_duration = 1000  # 1 segundo para que aparezca el menú
            menu_alpha = min(255, int(255 * elapsed_since_completed / menu_fadein_duration))
            
            # Dibujar menú con transparencia
            for i, item in enumerate(menu_items):
                color = (255, 255, 255) if i == selected else (150, 150, 150)
                
                if menu_alpha < 255:
                    # Aplicar alpha al texto del menú
                    temp_surface = pygame.Surface((300, 60), pygame.SRCALPHA)
                    temp_surface.fill((0, 0, 0, 0))  # Superficie transparente
                    font = pygame.font.SysFont("Arial", 48)
                    text_surface = font.render(item, True, color)
                    text_rect = text_surface.get_rect(center=(150, 30))
                    temp_surface.blit(text_surface, text_rect)
                    temp_surface.set_alpha(menu_alpha)
                    screen_pos = (screen.get_width() // 2 - 150, menu_start_y + i * menu_spacing - 30)
                    screen.blit(temp_surface, screen_pos)
                else:
                    draw_text(screen, item, 48, color, screen.get_width() // 2, menu_start_y + i * menu_spacing)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Usar el módulo de controles unificado
            selected, action, exit_flag = handle_main_menu_controls(
                event, selected, menu_items, sfx_cursor, sfx_enter, sfx_back
            )
            
            if exit_flag:
                if pygame.mixer.get_init() is not None:
                    pygame.time.wait(100)  # Pequeña pausa para permitir que suene el efecto
                running = False
                
            if action:
                if pygame.mixer.get_init() is not None:
                    pygame.time.wait(100)  # Pequeña pausa para permitir que suene el efecto
                
                if action == "modo_arcade":
                    if pygame.mixer.get_init() is not None:
                        pygame.mixer.music.stop()
                    from .game import start_game
                    start_game(screen, settings)
                elif action == "puntuaciones":
                    # Import here to avoid circular import
                    from .highscore import show_high_scores
                    show_high_scores(screen, settings)
                elif action == "opciones":
                    options_menu(screen, settings)

        clock.tick(60)

    # Stop music only if mixer is available
    if pygame.mixer.get_init() is not None:
        pygame.mixer.music.stop()