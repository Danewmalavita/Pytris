# mode_selection.py
import pygame
from .debug_utils import debugger

def draw_text(surface, text, size, color, x, y, font_name=None):
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
            font = pygame.font.Font("assets/fonts/mainfont.ttf", 24)
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
    
    # Importar y usar el audio_manager para los efectos de sonido
    from .audio_manager import audio_manager
    
    # Crear objetos de sonido que usarán el audio_manager
    class DummySound:
        def __init__(self, sound_name=None):
            self.sound_name = sound_name
            
        def play(self):
            if self.sound_name and audio_manager.audio_available and not settings['mute']:
                audio_manager.play_sound(self.sound_name)
                
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
    
    # Variables para efectos visuales
    bg_animation = 0
    
    # Variables para control de navegación con gamepad
    last_gamepad_check = pygame.time.get_ticks()
    gamepad_delay = 200  # Tiempo mínimo entre cambios de selección (ms)
    
    # Cargar configuración de teclas
    keybindings = load_keybindings()
    
    running = True
    while running:
        screen.fill((15, 15, 35))  # Color de fondo
        
        # Fondo animado simple
        bg_animation += 1
        
        # Título con tetrisfont
        title_y = 150
        draw_text(screen, "SELECCIONA MODO DE JUEGO", 56, (255, 255, 255), screen.get_width() // 2, title_y, "assets/fonts/tetrisfont.ttf")
        
        # Menú de modos
        menu_start_y = 300
        menu_spacing = 60
        
        for i, item in enumerate(mode_items):
            color = (255, 255, 255) if i == selected else (150, 150, 150)
            font_size = 48 if i == selected else 38
            
            # Si es el elemento seleccionado, dibujar un indicador
            if i == selected:
                # Dibujar el indicador (flecha o efecto de resaltado)
                pygame.draw.rect(
                    screen, 
                    (40, 40, 80), 
                    (screen.get_width() // 2 - 150, menu_start_y + i * menu_spacing - 30, 300, 60),
                    border_radius=10
                )
            
            draw_text(screen, item, font_size, color, screen.get_width() // 2, menu_start_y + i * menu_spacing, "assets/fonts/mainfont.ttf")
        
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