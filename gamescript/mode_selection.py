# mode_selection.py
import pygame
import math
from .debug_utils import debugger

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

def draw_mode_description(surface, mode_name, center_y):
    """
    Dibuja la descripción del modo de juego seleccionado.
    """
    descriptions = {
        "Clásico": "Modo tradicional de Tetris. ¡Aguanta lo máximo posible!",
        "Contrarreloj": "Consigue la mayor puntuación en 3 minutos.",
        "Maratón": "Completa 150 líneas con dificultad creciente.",
        "Ultra": "Logra la mayor puntuación posible en 2 minutos."
    }
    
    if mode_name in descriptions:
        description = descriptions[mode_name]
        try:
            font = pygame.font.Font("assets/fonts/menufont.ttf", 24)
        except:
            font = pygame.font.SysFont("Arial", 24)
        text_surface = font.render(description, True, (200, 200, 200))
        text_rect = text_surface.get_rect(center=(surface.get_width() // 2, center_y))
        surface.blit(text_surface, text_rect)

def mode_selection(screen, settings):
    """
    Menú de selección de modo de juego.
    
    Args:
        screen (pygame.Surface): Superficie donde dibujar el menú
        settings (dict): Configuración del juego
        
    Returns:
        str: El modo de juego seleccionado ('classic', 'time_attack', 'marathon', 'ultra' o None si se cancela)
    """
    clock = pygame.time.Clock()
    
    # Importar el módulo de controles
    from .controls import handle_menu_controls, check_gamepad_action, load_keybindings
    
    # Importar y usar el audio_manager para los efectos de sonido (unificado con menu.py)
    from .audio_manager import audio_manager
    
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

    # Opciones de modo de juego
    mode_items = ["Clásico", "Contrarreloj", "Maratón", "Ultra", "Volver"]
    selected = 0
    
    # Mapeo de nombres visuales a identificadores de código
    mode_mapping = {
        "Clásico": "classic",
        "Contrarreloj": "time_attack",
        "Maratón": "marathon",
        "Ultra": "ultra",
        "Volver": None
    }
    
    # Variables para efectos visuales (unificados con menu.py)
    bg_animation = 0
    
    # Variables para control de navegación con gamepad
    last_gamepad_check = pygame.time.get_ticks()
    gamepad_delay = 200  # Tiempo mínimo entre cambios de selección (ms)
    
    # Cargar configuración de teclas
    keybindings = load_keybindings()
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # Fondo animado unificado
        bg_animation += 1
        draw_animated_background(screen, bg_animation)
        
        # Título con fuente unificada
        draw_text(screen, "SELECCIONA MODO DE JUEGO", 56, (255, 255, 255), screen.get_width() // 2, 150, "assets/fonts/tetrisfont.ttf")
        
        # Menú de modos con estilo unificado
        menu_start_y = 300
        menu_spacing = 60
        
        try:
            menu_font_48 = pygame.font.Font("assets/fonts/menufont.ttf", 48)
            menu_font_38 = pygame.font.Font("assets/fonts/menufont.ttf", 38)
        except:
            menu_font_48 = pygame.font.SysFont("Arial", 48)
            menu_font_38 = pygame.font.SysFont("Arial", 38)
        
        for i, item in enumerate(mode_items):
            y_pos = menu_start_y + i * menu_spacing
            
            if i == selected:
                # Dibujar fondo resaltado para opción seleccionada
                pygame.draw.rect(
                    screen, 
                    (40, 40, 80), 
                    (screen.get_width() // 2 - 150, y_pos - 30, 300, 60),
                    border_radius=10
                )
                # Usar efecto de pulso para opción seleccionada
                draw_pulse_text(screen, menu_font_48, item, current_time, screen.get_width() // 2, y_pos)
            else:
                color = (150, 150, 150)
                draw_text(screen, item, 38, color, screen.get_width() // 2, y_pos, "assets/fonts/menufont.ttf")
        
        # Mostrar descripción del modo seleccionado
        if selected < len(mode_items) - 1:  # No mostrar para la opción "Volver"
            description_y = menu_start_y + (len(mode_items) + 1) * menu_spacing
            draw_mode_description(screen, mode_items[selected], description_y)
        
        pygame.display.flip()

        action = None
        # Control de gamepad con limitación de frecuencia
        current_time = pygame.time.get_ticks()
        if current_time - last_gamepad_check > gamepad_delay:
            if check_gamepad_action("menu_up", keybindings):
                selected = (selected - 1) % len(mode_items)
                sfx_cursor.play()
                last_gamepad_check = current_time
            elif check_gamepad_action("menu_down", keybindings):
                selected = (selected + 1) % len(mode_items)
                sfx_cursor.play()
                last_gamepad_check = current_time
            elif check_gamepad_action("confirm", keybindings):
                action = mode_items[selected]
                sfx_enter.play()
                last_gamepad_check = current_time
            elif check_gamepad_action("cancel", keybindings):
                sfx_back.play()
                return None
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            
            # Manejar controles del menú con teclado
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(mode_items)
                    sfx_cursor.play()
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(mode_items)
                    sfx_cursor.play()
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    action = mode_items[selected]
                    sfx_enter.play()
                elif event.key == pygame.K_ESCAPE:
                    sfx_back.play()
                    return None
        
        if action:
            # Pequeña pausa para permitir que suene el efecto
            pygame.time.wait(100)
            return mode_mapping[action]
                
        clock.tick(60)
    
    return None