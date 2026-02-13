# two_player_mode.py
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

def handle_two_player_menu_controls(event, selected, menu_items, gamepad=None):
    """
    Maneja los controles del menú de dos jugadores con soporte para gamepad.
    
    Args:
        event: Evento de pygame
        selected: Índice de la opción seleccionada
        menu_items: Lista de opciones del menú
        gamepad: Objeto gamepad opcional
    
    Returns:
        tuple: (selected, action)
    """
    action = None
    
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            selected = (selected - 1) % len(menu_items)
        elif event.key == pygame.K_DOWN:
            selected = (selected + 1) % len(menu_items)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            action = menu_items[selected].lower()
        elif event.key == pygame.K_ESCAPE:
            action = "volver"
    
    # Manejar controles de gamepad
    elif gamepad and gamepad.get_init():
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:  # Botón A (seleccionar)
                action = menu_items[selected].lower()
            elif event.button == 1:  # Botón B (volver)
                action = "volver"
        
        elif event.type == pygame.JOYHATMOTION:
            if event.value == (0, 1):  # Arriba
                selected = (selected - 1) % len(menu_items)
            elif event.value == (0, -1):  # Abajo
                selected = (selected + 1) % len(menu_items)
        
        elif event.type == pygame.JOYAXISMOTION:
            # Manejar stick analógico
            if event.axis == 1:  # Eje Y del stick izquierdo
                if event.value < -0.5:  # Arriba
                    selected = (selected - 1) % len(menu_items)
                    pygame.time.wait(150)  # Evitar repetición rápida
                elif event.value > 0.5:  # Abajo
                    selected = (selected + 1) % len(menu_items)
                    pygame.time.wait(150)  # Evitar repetición rápida
    
    return selected, action

def two_player_menu(screen, settings):
    """
    Menú para el modo de 2 jugadores.
    
    Args:
        screen (pygame.Surface): Superficie donde dibujar el menú
        settings (dict): Configuración del juego
    """
    clock = pygame.time.Clock()
    # Importar el módulo de controles
    from .controls import handle_controls_menu, check_gamepad_action, load_keybindings

    # Inicializar gamepad si está disponible
    gamepad = None
    if pygame.joystick.get_count() > 0:
        gamepad = pygame.joystick.Joystick(0)
        if not gamepad.get_init():
            gamepad.init()
        print(f"Gamepad detectado: {gamepad.get_name()}")
    

    
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

    # Opciones del menú de 2 jugadores
    menu_items = ["Versus", "Cooperativo", "Demo", "Volver"]
    selected = 0
    
    # Variables para efectos visuales (unificados con menu.py)
    bg_animation = 0
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # Fondo animado unificado
        bg_animation += 1
        draw_animated_background(screen, bg_animation)
        
        # Título con fuente unificada
        draw_text(screen, "MODO 2 JUGADORES", 56, (255, 255, 255), screen.get_width() // 2, 150, "assets/fonts/tetrisfont.ttf")
        
        # Menú de opciones con estilo unificado
        menu_start_y = 300
        menu_spacing = 60
        
        try:
            menu_font_48 = pygame.font.Font("assets/fonts/menufont.ttf", 48)
            menu_font_38 = pygame.font.Font("assets/fonts/menufont.ttf", 38)
        except:
            menu_font_48 = pygame.font.SysFont("Arial", 48)
            menu_font_38 = pygame.font.SysFont("Arial", 38)
        
        for i, item in enumerate(menu_items):
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
        
        # Mostrar descripción de la opción seleccionada
        descriptions = {
            "Versus": "Compite contra otro jugador",
            "Cooperativo": "Trabajen juntos para conseguir puntos",
            "Demo": "Observa una demostración del modo 2 jugadores",
            "Volver": ""
        }
        
        if menu_items[selected] in descriptions and descriptions[menu_items[selected]]:
            description_y = menu_start_y + (len(menu_items) + 1) * menu_spacing
            draw_text(screen, descriptions[menu_items[selected]], 24, (200, 200, 200), screen.get_width() // 2, description_y, "assets/fonts/menufont.ttf")
        
        # Mostrar información del gamepad si está conectado
        if gamepad:
            gamepad_info = f"Gamepad: {gamepad.get_name()}"
            draw_text(screen, gamepad_info, 18, (100, 200, 100), screen.get_width() // 2, screen.get_height() - 50, "assets/fonts/menufont.ttf")
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            # Usar la función de manejo de controles mejorada
            old_selected = selected
            selected, action = handle_two_player_menu_controls(event, selected, menu_items, gamepad)
            
            # Reproducir sonido si cambió la selección
            if selected != old_selected:
                sfx_cursor.play()
            
            if action:
                if action == "versus":
                    sfx_enter.play()
                    pygame.time.wait(100)
                    # Iniciar modo versus
                    try:
                        from .two_player_core import start_two_player_game
                        
                        start_two_player_game(screen, settings, mode="versus")
                    except ImportError:
                        print("Módulo two_player_core no encontrado. Implementando modo básico...")
                        # Implementación básica del modo versus
                        draw_text(screen, "Modo Versus en desarrollo", 32, (255, 255, 255), screen.get_width() // 2, screen.get_height() // 2)
                        pygame.display.flip()
                        pygame.time.wait(2000)
                        
                elif action == "cooperativo":
                    sfx_enter.play()
                    pygame.time.wait(100)
                    # Iniciar modo cooperativo
                    try:
                        from .two_player_core import start_two_player_game
                        start_two_player_game(screen, settings, mode="cooperative")
                    except ImportError:
                        print("Módulo two_player_core no encontrado. Implementando modo básico...")
                        # Implementación básica del modo cooperativo
                        draw_text(screen, "Modo Cooperativo en desarrollo", 32, (255, 255, 255), screen.get_width() // 2, screen.get_height() // 2)
                        pygame.display.flip()
                        pygame.time.wait(2000)
                        
                elif action == "demo":
                    sfx_enter.play()
                    pygame.time.wait(100)
                    # Mostrar demo
                    try:
                        from .two_playerdemo import start_two_player_demo
                        start_two_player_demo(screen, settings)
                    except ImportError:
                        print("Módulo two_playerdemo no encontrado. Mostrando demo básica...")
                        # Demo básica
                        draw_text(screen, "Demo del modo 2 jugadores", 32, (255, 255, 255), screen.get_width() // 2, screen.get_height() // 2)
                        draw_text(screen, "Presiona cualquier tecla para continuar", 24, (200, 200, 200), screen.get_width() // 2, screen.get_height() // 2 + 50)
                        pygame.display.flip()
                        
                        # Esperar input del usuario
                        waiting = True
                        while waiting:
                            for demo_event in pygame.event.get():
                                if demo_event.type == pygame.KEYDOWN or demo_event.type == pygame.JOYBUTTONDOWN:
                                    waiting = False
                                elif demo_event.type == pygame.QUIT:
                                    waiting = False
                                    
                elif action == "volver":
                    sfx_back.play()
                    pygame.time.wait(100)
                    return

        clock.tick(60)