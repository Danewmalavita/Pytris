# options.py
import pygame
import math
from .settings import resol

# Colores de los tetrominós clásicos (unificados con menu.py)
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

def draw_text(surface, text, size, color, x, y, font_name=None):
    try:
        if font_name:
            # Intentar cargar la fuente específica
            font = pygame.font.Font(font_name, size)
        else:
            # Usar menufont.ttf como fuente predeterminada
            font = pygame.font.Font("assets/fonts/menufont.ttf", size)
    except Exception:
        # Usar Arial como respaldo si hay error
        font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def draw_pulse_text(screen, font, text, time_counter, x, y):
    """Efecto de pulsación - ideal para opciones seleccionadas"""
    pulse = abs(math.sin(time_counter * 0.1)) * 0.5 + 0.5
    color_intensity = int(255 * pulse)
    color = (color_intensity, color_intensity // 2, 255)
    
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def draw_animated_background(screen, bg_animation):
    """Dibuja el fondo animado unificado"""
    bg_color = (
        10 + int(8 * abs(math.sin(bg_animation * 0.008))),
        10 + int(8 * abs(math.sin(bg_animation * 0.010))),
        50 + int(15 * abs(math.sin(bg_animation * 0.012)))
    )
    screen.fill(bg_color)
    
    # Efecto de fondo estilo tetris: bloques cayendo lentamente
    current_time_ms = pygame.time.get_ticks()
    from .graphics import TetrisRenderer
    bg_renderer = TetrisRenderer(screen)
    block_size = 30
    
    # Dibujar estrellas/bloques dispersos en el fondo para dar profundidad
    num_background_blocks = 25
    seed_time = int(current_time_ms / 10000)
    
    for i in range(num_background_blocks):
        x_factor = math.sin(i * 0.3 + seed_time * 0.1) * 0.5 + 0.5
        y_factor = math.cos(i * 0.4 + seed_time * 0.2) * 0.5 + 0.5
        
        x_pos = int(x_factor * screen.get_width())
        y_pos = int(y_factor * screen.get_height())
        
        visibility_factor = math.sin(i + current_time_ms / 3000)
        
        if visibility_factor > 0:
            block_type = (i % 7) + 1
            alpha = int(40 + 30 * visibility_factor)
            
            block_col = int(x_pos / block_size)
            block_row = int(y_pos / block_size)
            
            bg_renderer.draw_block(block_col, block_row, block_type, alpha=alpha)

def options_menu(screen, settings):
    clock = pygame.time.Clock()
    
    # Importar el módulo de controles
    from .controls import handle_options_menu_controls
    
    # Importar y usar el audio_manager para los efectos de sonido (unificado con menu.py)
    from .audio_manager import audio_manager
    from .debug_utils import debugger
    
    # Configurar el gestor de audio con los ajustes actuales
    audio_manager.set_master_volume(settings['volume_general'])
    audio_manager.set_music_volume(settings['volume_bgm'])
    audio_manager.set_sfx_volume(settings['volume_sfx'])
    audio_manager.set_mute(settings['mute'])
    
    # Crear objetos de sonido que usarán el audio_manager (unificado con menu.py)
    class DummySound:
        def __init__(self, sound_name=None):
            self.sound_name = sound_name
            
        def play(self):
            if self.sound_name and audio_manager.audio_available:
                audio_manager.play_sound(self.sound_name)
                
        def set_volume(self, vol):
            pass  # El volumen se maneja a través del audio_manager
            
    # Crear objetos para cada efecto de sonido
    sfx_cursor = DummySound("cursor")
    sfx_enter = DummySound("enter")
    sfx_back = DummySound("back")

    # Opciones del menú
    options = [
        "Volumen General",
        "Volumen Música",
        "Volumen Efectos",
        "Resolución",
        "Silenciar",
        "Controles",
        "Volver"
    ]
    
    selected = 0
    
    # Variables para efectos visuales (unificados con menu.py)
    bg_animation = 0
    current_time = pygame.time.get_ticks()

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # Fondo animado unificado
        bg_animation += 1
        draw_animated_background(screen, bg_animation)
        
        # Título con fuente unificada
        try:
            title_font = pygame.font.Font("assets/fonts/tetrisfont.ttf", 56)
        except:
            title_font = pygame.font.SysFont("Arial", 56)
        
        draw_text(screen, "OPCIONES", 56, (255, 255, 255), screen.get_width() // 2, 150, "assets/fonts/tetrisfont.ttf")
        
        # Menú de opciones con estilo unificado
        menu_start_y = 300
        menu_spacing = 60
        
        try:
            menu_font_48 = pygame.font.Font("assets/fonts/menufont.ttf", 48)
            menu_font_38 = pygame.font.Font("assets/fonts/menufont.ttf", 38)
        except:
            menu_font_48 = pygame.font.SysFont("Arial", 48)
            menu_font_38 = pygame.font.SysFont("Arial", 38)
        
        for i, option in enumerate(options):
            y_pos = menu_start_y + i * menu_spacing
            
            if i == selected:
                # Dibujar fondo resaltado para opción seleccionada
                pygame.draw.rect(
                    screen, 
                    (40, 40, 80), 
                    (screen.get_width() // 2 - 200, y_pos - 30, 400, 60),
                    border_radius=10
                )
                # Usar efecto de pulso para opción seleccionada
                draw_pulse_text(screen, menu_font_48, option, current_time, screen.get_width() // 2, y_pos)
            else:
                color = (150, 150, 150)
                draw_text(screen, option, 38, color, screen.get_width() // 2, y_pos, "assets/fonts/menufont.ttf")
            
            # Mostrar valores actuales de configuración
            if option == "Volumen General":
                value = f"{int(settings['volume_general'] * 100)}%"
                draw_text(screen, value, 32, (200, 200, 200), screen.get_width() // 2 + 250, y_pos)
            elif option == "Volumen Música":
                value = f"{int(settings['volume_bgm'] * 100)}%"
                draw_text(screen, value, 32, (200, 200, 200), screen.get_width() // 2 + 250, y_pos)
            elif option == "Volumen Efectos":
                value = f"{int(settings['volume_sfx'] * 100)}%"
                draw_text(screen, value, 32, (200, 200, 200), screen.get_width() // 2 + 250, y_pos)
            elif option == "Resolución":
                value = f"{settings['resolution'][0]}x{settings['resolution'][1]}"
                draw_text(screen, value, 32, (200, 200, 200), screen.get_width() // 2 + 250, y_pos)
            elif option == "Silenciar":
                value = "SÍ" if settings['mute'] else "NO"
                draw_text(screen, value, 32, (200, 200, 200), screen.get_width() // 2 + 250, y_pos)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Usar el módulo de controles unificado
            selected, action, exit_flag = handle_options_menu_controls(
                event, selected, options, settings, sfx_cursor, sfx_enter, sfx_back
            )
            
            if exit_flag:
                # Pequeña pausa para permitir que suene el efecto
                pygame.time.wait(100)
                running = False
                
            if action:
                # Pequeña pausa para permitir que suene el efecto
                pygame.time.wait(100)
                
                if action == "volumen_general":
                    # Ajustar volumen general
                    pass  # Manejado en handle_options_menu_controls
                elif action == "volumen_musica":
                    # Ajustar volumen música
                    pass  # Manejado en handle_options_menu_controls
                elif action == "volumen_efectos":
                    # Ajustar volumen efectos
                    pass  # Manejado en handle_options_menu_controls
                elif action == "resolucion":
                    # Cambiar resolución
                    pass  # Manejado en handle_options_menu_controls
                elif action == "silenciar":
                    # Toggle mute
                    settings['mute'] = not settings['mute']
                    audio_manager.set_mute(settings['mute'])
                elif action == "controles":
                    # Abrir menú de controles
                    from .controls import handle_controls_menu
                    handle_controls_menu(screen, settings)
                elif action == "volver":
                    running = False

        clock.tick(60)