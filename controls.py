# controls.py
# Módulo unificado para gestionar todos los controles del juego
import pygame
import json
import os

# Ruta al archivo de configuración de teclas
KEYBINDINGS_FILE = "keybindings.json"

# Variables para joystick/gamepad
gamepads = []
gamepad_deadzone = 0.2  # Zona muerta para evitar inputs no intencionados

# Función para cargar las configuraciones de teclas
def load_keybindings():
    """
    Carga la configuración de teclas desde el archivo JSON.
    Si el archivo no existe, crea uno con la configuración por defecto.
    
    Returns:
        dict: Diccionario con las configuraciones de teclas
    """
    if not os.path.exists(KEYBINDINGS_FILE):
        # Si el archivo no existe, usar configuración por defecto
        print(f"Archivo de configuración {KEYBINDINGS_FILE} no encontrado. Usando valores por defecto.")
        return get_default_keybindings()
    
    try:
        with open(KEYBINDINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error al leer el archivo de configuración: {e}")
        return get_default_keybindings()

def save_keybindings(config):
    """
    Guarda la configuración de teclas en el archivo JSON.
    
    Args:
        config (dict): Diccionario con las configuraciones a guardar
    """
    try:
        with open(KEYBINDINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, OSError) as e:
        print(f"Error al guardar la configuración: {e}")
        return False

def get_default_keybindings():
    """
    Devuelve la configuración de teclas por defecto.
    
    Returns:
        dict: Diccionario con la configuración por defecto
    """
    return {
        "keyboard": {
            "move_left": [
                {"key": "K_LEFT", "description": "Flecha izquierda"},
                {"key": "K_a", "description": "Tecla A"}
            ],
            "move_right": [
                {"key": "K_RIGHT", "description": "Flecha derecha"},
                {"key": "K_d", "description": "Tecla D"}
            ],
            "rotate": [
                {"key": "K_UP", "description": "Flecha arriba"},
                {"key": "K_w", "description": "Tecla W"}
            ],
            "soft_drop": [
                {"key": "K_DOWN", "description": "Flecha abajo"},
                {"key": "K_s", "description": "Tecla S"}
            ],
            "hard_drop": [
                {"key": "K_SPACE", "description": "Espacio"}
            ],
            "hold": [
                {"key": "K_c", "description": "Tecla C"}
            ],
            "pause": [
                {"key": "K_ESCAPE", "description": "Escape"}
            ],
            "confirm": [
                {"key": "K_RETURN", "description": "Enter"}
            ],
            "cancel": [
                {"key": "K_ESCAPE", "description": "Escape"}
            ],
            "menu_up": [
                {"key": "K_UP", "description": "Flecha arriba"}
            ],
            "menu_down": [
                {"key": "K_DOWN", "description": "Flecha abajo"}
            ],
            "menu_left": [
                {"key": "K_LEFT", "description": "Flecha izquierda"}
            ],
            "menu_right": [
                {"key": "K_RIGHT", "description": "Flecha derecha"}
            ],
            "view_highscores": [
                {"key": "K_h", "description": "Tecla H"}
            ]
        },
        "gamepad": {
            "move_left": [
                {"button_type": "axis", "axis": 0, "value": -0.5, "description": "Joystick/D-pad izquierda"}
            ],
            "move_right": [
                {"button_type": "axis", "axis": 0, "value": 0.5, "description": "Joystick/D-pad derecha"}
            ],
            "rotate": [
                {"button_type": "button", "button": 0, "description": "Botón A/Cruz"},
                {"button_type": "button", "button": 3, "description": "Botón Y/Triángulo"}
            ],
            "soft_drop": [
                {"button_type": "axis", "axis": 1, "value": 0.5, "description": "Joystick/D-pad abajo"}
            ],
            "hard_drop": [
                {"button_type": "button", "button": 1, "description": "Botón B/Círculo"}
            ],
            "hold": [
                {"button_type": "button", "button": 2, "description": "Botón X/Cuadrado"}
            ],
            "pause": [
                {"button_type": "button", "button": 7, "description": "Start/Options"}
            ],
            "confirm": [
                {"button_type": "button", "button": 0, "description": "Botón A/Cruz"}
            ],
            "cancel": [
                {"button_type": "button", "button": 1, "description": "Botón B/Círculo"}
            ],
            "menu_up": [
                {"button_type": "axis", "axis": 1, "value": -0.5, "description": "Joystick/D-pad arriba"}
            ],
            "menu_down": [
                {"button_type": "axis", "axis": 1, "value": 0.5, "description": "Joystick/D-pad abajo"}
            ],
            "menu_left": [
                {"button_type": "axis", "axis": 0, "value": -0.5, "description": "Joystick/D-pad izquierda"}
            ],
            "menu_right": [
                {"button_type": "axis", "axis": 0, "value": 0.5, "description": "Joystick/D-pad derecha"}
            ],
            "view_highscores": [
                {"button_type": "button", "button": 3, "description": "Botón Y/Triángulo"}
            ]
        }
    }

# Inicializar los controles
def initialize_controls():
    """
    Inicializa los controles, incluyendo joysticks/gamepads.
    Debe ser llamada antes de usar cualquier función de control.
    """
    global gamepads
    
    # Inicializar el módulo joystick si aún no está inicializado
    if not pygame.joystick.get_init():
        pygame.joystick.init()
    
    # Detectar todos los joysticks/gamepads conectados
    gamepads = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    for gamepad in gamepads:
        gamepad.init()
        print(f"Gamepad detectado: {gamepad.get_name()}")

# Convertir string de tecla a constante de pygame
def key_string_to_pygame_key(key_str):
    """
    Convierte una cadena con el nombre de una tecla a su código pygame.
    
    Args:
        key_str (str): Nombre de la tecla como string (ej: "K_LEFT")
    
    Returns:
        int: Código de tecla pygame correspondiente
    """
    return getattr(pygame, key_str, None)

# Verificar si una tecla específica está presionada
def is_key_action(event, action, keybindings=None):
    """
    Verifica si un evento corresponde a una acción específica según la configuración.
    
    Args:
        event: Evento de pygame
        action (str): Nombre de la acción a verificar
        keybindings (dict, optional): Configuración de teclas personalizada
        
    Returns:
        bool: True si el evento corresponde a la acción
    """
    if keybindings is None:
        keybindings = load_keybindings()
        
    # Verificar teclas de teclado
    if event.type == pygame.KEYDOWN and action in keybindings["keyboard"]:
        for binding in keybindings["keyboard"][action]:
            pygame_key = key_string_to_pygame_key(binding["key"])
            if pygame_key and event.key == pygame_key:
                return True
    
    return False

# Verificar si algún gamepad/joystick está ejecutando una acción específica
def check_gamepad_action(action, keybindings=None):
    """
    Verifica si algún gamepad/joystick está ejecutando una acción específica.
    
    Args:
        action (str): Nombre de la acción a verificar
        keybindings (dict, optional): Configuración de teclas personalizada
        
    Returns:
        bool: True si algún gamepad está ejecutando la acción
    """
    if keybindings is None:
        keybindings = load_keybindings()
    
    if not gamepads or action not in keybindings["gamepad"]:
        return False
    
    for gamepad in gamepads:
        # Verificar acciones del D-pad directamente (para mandos Xbox One genéricos)
        # Esta parte maneja el D-pad específicamente para compatibilidad
        if action == "move_left" or action == "menu_left":
            # Comprobar botón D-pad izquierda (índice típico: 13)
            for i in range(13, 16):  # Prueba algunos índices comunes
                if i < gamepad.get_numbuttons() and gamepad.get_button(i):
                    # Imprimir para debug: qué botón se presionó
                    print(f"Botón D-pad detectado: {i}")
                    if i == 13 or i == 14:  # Izquierda en varios controladores
                        return True
            
            # D-pad como hat (sombrero) - común en varios mandos
            for i in range(gamepad.get_numhats()):
                hat = gamepad.get_hat(i)
                if hat[0] == -1:  # -1 en X significa izquierda
                    return True
        
        elif action == "move_right" or action == "menu_right":
            # Comprobar botón D-pad derecha (índice típico: 14)
            for i in range(13, 16):
                if i < gamepad.get_numbuttons() and gamepad.get_button(i):
                    print(f"Botón D-pad detectado: {i}")
                    if i == 14 or i == 15:  # Derecha en varios controladores
                        return True
            
            # D-pad como hat
            for i in range(gamepad.get_numhats()):
                hat = gamepad.get_hat(i)
                if hat[0] == 1:  # 1 en X significa derecha
                    return True
        
        elif action == "soft_drop" or action == "menu_down":
            # Comprobar botón D-pad abajo (índice típico: 12)
            for i in range(11, 14):
                if i < gamepad.get_numbuttons() and gamepad.get_button(i):
                    print(f"Botón D-pad detectado: {i}")
                    if i == 12 or i == 11:  # Abajo en varios controladores
                        return True
            
            # D-pad como hat
            for i in range(gamepad.get_numhats()):
                hat = gamepad.get_hat(i)
                if hat[1] == -1:  # -1 en Y significa abajo
                    return True
        
        elif action == "menu_up":
            # Comprobar botón D-pad arriba (índice típico: 11)
            for i in range(10, 13):
                if i < gamepad.get_numbuttons() and gamepad.get_button(i):
                    print(f"Botón D-pad detectado: {i}")
                    if i == 11 or i == 10:  # Arriba en varios controladores
                        return True
            
            # D-pad como hat
            for i in range(gamepad.get_numhats()):
                hat = gamepad.get_hat(i)
                if hat[1] == 1:  # 1 en Y significa arriba
                    return True
        
        # Hard drop (botón B - normalmente índice 1, o D-pad arriba)
        elif action == "hard_drop":
            # Check for button-based hard_drop (usually B button)
            for binding in keybindings.get("gamepad", {}).get(action, []):
                # Button type (standard button press)
                if binding.get("button_type") == "button":
                    button_idx = binding.get("button")
                    if button_idx is not None and 0 <= button_idx < gamepad.get_numbuttons():
                        if gamepad.get_button(button_idx):
                            print(f"Hard drop con botón {button_idx}")
                            return True
                
                # Axis type (for D-pad on some controllers)
                elif binding.get("button_type") == "axis" and binding.get("axis") == 1:
                    # Check for D-pad up (negative value on axis 1)
                    axis_val = gamepad.get_axis(1)
                    if binding.get("value", 0) < 0 and axis_val < -0.5:
                        print(f"Hard drop con D-pad arriba (axis 1)")
                        return True
                
                # Hat type (for D-pad on other controllers)
                elif binding.get("button_type") == "hat":
                    hat_idx = binding.get("hat", 0)
                    if hat_idx < gamepad.get_numhats():
                        hat_val = gamepad.get_hat(hat_idx)
                        # Check if it matches the up direction (0, 1)
                        if hat_val[1] == 1:
                            print(f"Hard drop con D-pad hat up")
                            return True
            
            # Also check D-pad explicitly for compatibility
            for i in range(gamepad.get_numhats()):
                hat = gamepad.get_hat(i)
                if hat[1] == 1:  # Up direction
                    print(f"Hard drop con D-pad hat {i} (universal)")
                    return True


        
        # Verificar configuración normal de botones y ejes
        for binding in keybindings["gamepad"][action]:
            # Comprobar botones directos
            if binding["button_type"] == "button" and "button" in binding:
                button_idx = binding["button"]
                if button_idx < gamepad.get_numbuttons() and gamepad.get_button(button_idx):
                    return True
            
            # Comprobar ejes analógicos
            elif binding["button_type"] == "axis" and "axis" in binding and "value" in binding:
                axis_idx = binding["axis"]
                target_value = binding["value"]
                if axis_idx < gamepad.get_numaxes():
                    axis_value = gamepad.get_axis(axis_idx)
                    # Para valores negativos (como izquierda/arriba)
                    if target_value < 0 and axis_value < target_value:
                        return True
                    # Para valores positivos (como derecha/abajo)
                    elif target_value > 0 and axis_value > target_value:
                        return True
    
    return False
# Obtener estado de un botón/axis específico de un gamepad
def get_gamepad_input_state(gamepad_idx, input_type, input_idx):
    """
    Obtiene el estado actual de un botón o axis específico de un gamepad.
    
    Args:
        gamepad_idx (int): Índice del gamepad
        input_type (str): Tipo de entrada ('button' o 'axis')
        input_idx (int): Índice del botón o axis
        
    Returns:
        bool o float: Estado del botón (bool) o valor del axis (float)
    """
    if not gamepads or gamepad_idx >= len(gamepads):
        return False if input_type == 'button' else 0.0
        
    gamepad = gamepads[gamepad_idx]
    
    if input_type == 'button' and input_idx < gamepad.get_numbuttons():
        return gamepad.get_button(input_idx)
    elif input_type == 'axis' and input_idx < gamepad.get_numaxes():
        return gamepad.get_axis(input_idx)
    
    return False if input_type == 'button' else 0.0

# Funciones auxiliares para el menú de opciones
def handle_options_left_input(selected, options, current_res_index, resolution_keys, settings, sfx_cursor):
    """
    Maneja la entrada hacia la izquierda en el menú de opciones.
    
    Returns:
        int: Nuevo índice de resolución
    """
    if options[selected] == "Volumen General":
        settings['volume_general'] = max(0.0, settings['volume_general'] - 0.05)
        # Actualizar volumen de los SFX
        sfx_cursor.set_volume(settings['volume_general'] * settings['volume_sfx'])
        sfx_cursor.play()
    elif options[selected] == "Volumen BGM":
        settings['volume_bgm'] = max(0.0, settings['volume_bgm'] - 0.05)
        sfx_cursor.play()
    elif options[selected] == "Volumen SFX":
        settings['volume_sfx'] = max(0.0, settings['volume_sfx'] - 0.05)
        # Actualizar volumen de los SFX
        sfx_cursor.set_volume(settings['volume_general'] * settings['volume_sfx'])
        sfx_cursor.play()
    elif options[selected] == "Resolución":
        current_res_index = (current_res_index - 1) % len(resolution_keys)
        sfx_cursor.play()
    return current_res_index

def handle_options_right_input(selected, options, current_res_index, resolution_keys, settings, sfx_cursor):
    """
    Maneja la entrada hacia la derecha en el menú de opciones.
    
    Returns:
        int: Nuevo índice de resolución
    """
    if options[selected] == "Volumen General":
        settings['volume_general'] = min(1.0, settings['volume_general'] + 0.05)
        # Actualizar volumen de los SFX
        sfx_cursor.set_volume(settings['volume_general'] * settings['volume_sfx'])
        sfx_cursor.play()
    elif options[selected] == "Volumen BGM":
        settings['volume_bgm'] = min(1.0, settings['volume_bgm'] + 0.05)
        sfx_cursor.play()
    elif options[selected] == "Volumen SFX":
        settings['volume_sfx'] = min(1.0, settings['volume_sfx'] + 0.05)
        # Actualizar volumen de los SFX
        sfx_cursor.set_volume(settings['volume_general'] * settings['volume_sfx'])
        sfx_cursor.play()
    elif options[selected] == "Resolución":
        current_res_index = (current_res_index + 1) % len(resolution_keys)
        sfx_cursor.play()
    return current_res_index

def handle_options_confirm(selected, options, settings, sfx_enter, sfx_back):
    """
    Maneja la confirmación en el menú de opciones.
    """
    if options[selected] == "Mute":
        sfx_enter.play()
        settings['mute'] = not settings['mute']
        # Actualizar inmediatamente el volumen de los SFX
        sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
        sfx_enter.set_volume(sfx_vol)
    elif options[selected] == "Controles":
        sfx_enter.play()
        # El menú de controles se maneja en options.py ahora
        return "controles"
    elif options[selected] == "Volver":
        sfx_back.play()
    else:
        sfx_enter.play()
    
    return None

# Pause Menu Controls
def handle_pause_menu_controls(event, selected, options, sfx_cursor, sfx_enter):
    """
    Maneja los controles para el menú de pausa.
    
    Args:
        event: Evento de pygame
        selected: Índice de la opción seleccionada actualmente
        options: Lista de opciones del menú
        sfx_cursor: Efecto de sonido para navegación
        sfx_enter: Efecto de sonido para selección
    
    Returns:
        tuple: (nuevo_indice_seleccionado, accion)
    """
    action = None
    keybindings = load_keybindings()
    
    # Manejar controles de teclado
    if event.type == pygame.KEYDOWN:
        if is_key_action(event, "menu_up", keybindings):
            selected = (selected - 1) % len(options)
            sfx_cursor.play()
        elif is_key_action(event, "menu_down", keybindings):
            selected = (selected + 1) % len(options)
            sfx_cursor.play()
        elif is_key_action(event, "confirm", keybindings):
            sfx_enter.play()
            action = options[selected].lower().replace(" ", "_")
    
    # Manejar controles de gamepad (se verifica en cada frame del juego)
    if check_gamepad_action("menu_up", keybindings):
        selected = (selected - 1) % len(options)
        sfx_cursor.play()
    elif check_gamepad_action("menu_down", keybindings):
        selected = (selected + 1) % len(options)
        sfx_cursor.play()
    elif check_gamepad_action("confirm", keybindings):
        sfx_enter.play()
        action = options[selected].lower().replace(" ", "_")
            
    return selected, action

# Main Menu Controls
def handle_main_menu_controls(event, selected, menu_items, sfx_cursor, sfx_enter, sfx_back):
    """
    Maneja los controles para el menú principal.
    
    Args:
        event: Evento de pygame
        selected: Índice de la opción seleccionada actualmente
        menu_items: Lista de opciones del menú
        sfx_cursor: Efecto de sonido para navegación
        sfx_enter: Efecto de sonido para selección
        sfx_back: Efecto de sonido para retroceso/salida
    
    Returns:
        tuple: (nuevo_indice_seleccionado, accion, salir)
    """
    action = None
    exit_flag = False
    keybindings = load_keybindings()
    
    # Manejar controles de teclado
    if event.type == pygame.KEYDOWN:
        if is_key_action(event, "menu_up", keybindings):
            selected = (selected - 1) % len(menu_items)
            sfx_cursor.play()
        elif is_key_action(event, "menu_down", keybindings):
            selected = (selected + 1) % len(menu_items)
            sfx_cursor.play()
        elif is_key_action(event, "confirm", keybindings):
            if menu_items[selected] == "Salir":
                sfx_back.play()
                exit_flag = True
            else:
                sfx_enter.play()
                action = menu_items[selected].lower().replace(" ", "_")
        elif is_key_action(event, "cancel", keybindings):
            sfx_back.play()
            exit_flag = True
    
    # Manejar controles de gamepad
    if check_gamepad_action("menu_up", keybindings):
        selected = (selected - 1) % len(menu_items)
        sfx_cursor.play()
    elif check_gamepad_action("menu_down", keybindings):
        selected = (selected + 1) % len(menu_items)
        sfx_cursor.play()
    elif check_gamepad_action("confirm", keybindings):
        if menu_items[selected] == "Salir":
            sfx_back.play()
            exit_flag = True
        else:
            sfx_enter.play()
            action = menu_items[selected].lower().replace(" ", "_")
    elif check_gamepad_action("cancel", keybindings):
        sfx_back.play()
        exit_flag = True
            
    return selected, action, exit_flag

# Options Menu Controls
def handle_options_menu_controls(event, selected, options, current_res_index, resolution_keys, settings, sfx_cursor, sfx_enter, sfx_back):
    """
    Maneja los controles para el menú de opciones.
    
    Args:
        event: Evento de pygame
        selected: Índice de la opción seleccionada actualmente
        options: Lista de opciones del menú
        current_res_index: Índice de la resolución actual
        resolution_keys: Lista de claves de resolución disponibles
        settings: Diccionario con los ajustes del juego
        sfx_cursor: Efecto de sonido para navegación
        sfx_enter: Efecto de sonido para selección
        sfx_back: Efecto de sonido para retroceso
    
    Returns:
        tuple: (nuevo_indice_seleccionado, nuevo_indice_resolucion, aplicar_cambios, salir)
    """
    apply_changes = False
    exit_menu = False
    open_controls_menu = False
    keybindings = load_keybindings()
    
    # Manejar controles de teclado
    if event.type == pygame.KEYDOWN:
        if is_key_action(event, "menu_up", keybindings):
            selected = (selected - 1) % len(options)
            sfx_cursor.play()
        elif is_key_action(event, "menu_down", keybindings):
            selected = (selected + 1) % len(options)
            sfx_cursor.play()
        elif is_key_action(event, "menu_left", keybindings):
            current_res_index = handle_options_left_input(selected, options, current_res_index, resolution_keys, settings, sfx_cursor)
        elif is_key_action(event, "menu_right", keybindings):
            current_res_index = handle_options_right_input(selected, options, current_res_index, resolution_keys, settings, sfx_cursor)
        elif is_key_action(event, "confirm", keybindings):
            action = handle_options_confirm(selected, options, settings, sfx_enter, sfx_back)
            if options[selected] == "Volver":
                apply_changes = True
                exit_menu = True
            elif options[selected] == "Controles" or action == "controles":
                open_controls_menu = True
        elif is_key_action(event, "cancel", keybindings):
            sfx_back.play()
            apply_changes = True
            exit_menu = True
    
    # Manejar controles de gamepad
    if check_gamepad_action("menu_up", keybindings):
        selected = (selected - 1) % len(options)
        sfx_cursor.play()
    elif check_gamepad_action("menu_down", keybindings):
        selected = (selected + 1) % len(options)
        sfx_cursor.play()
    elif check_gamepad_action("menu_left", keybindings):
        current_res_index = handle_options_left_input(selected, options, current_res_index, resolution_keys, settings, sfx_cursor)
    elif check_gamepad_action("menu_right", keybindings):
        current_res_index = handle_options_right_input(selected, options, current_res_index, resolution_keys, settings, sfx_cursor)
    elif check_gamepad_action("confirm", keybindings):
        action = handle_options_confirm(selected, options, settings, sfx_enter, sfx_back)
        if options[selected] == "Volver":
            apply_changes = True
            exit_menu = True
        elif options[selected] == "Controles" or action == "controles":
            open_controls_menu = True
    elif check_gamepad_action("cancel", keybindings):
        sfx_back.play()
        apply_changes = True
        exit_menu = True
            
    return selected, current_res_index, apply_changes, exit_menu, open_controls_menu

# Game Controls
def handle_game_controls(event, game, das_left_pressed, das_right_pressed, das_down_pressed, 
                       das_left_start, das_right_start, das_down_start, sfx_move, 
                       sfx_rotate, sfx_soft_drop, sfx_hold, paused):
    """
    Maneja los controles durante el juego.
    
    Args:
        event: Evento de pygame
        game: Objeto del juego Tetris
        das_*: Variables para el sistema de auto-repetición retardada (DAS)
        sfx_*: Efectos de sonido para acciones del juego
        paused: Bandera que indica si el juego está pausado
        
    Returns:
        tuple: (das_left_pressed, das_right_pressed, das_down_pressed, das_left_start, 
               das_right_start, das_down_start, paused)
    """
    # No procesar controles si el juego está terminado
    if game.game_over:
        return das_left_pressed, das_right_pressed, das_down_pressed, das_left_start, das_right_start, das_down_start, paused
    
    keybindings = load_keybindings()
    
    # Manejar controles de teclado
    if event.type == pygame.KEYDOWN:
        # Tecla para pausar el juego
        if is_key_action(event, "pause", keybindings):
            paused = True
            return das_left_pressed, das_right_pressed, das_down_pressed, das_left_start, das_right_start, das_down_start, paused
            
        # Solo procesar controles de movimiento si el juego no está pausado
        if not paused:
            # Movimiento izquierdo
            if is_key_action(event, "move_left", keybindings):
                if game.move_left():
                    sfx_move.play()
                das_left_pressed = True
                das_left_start = pygame.time.get_ticks()
                
            # Movimiento derecho
            elif is_key_action(event, "move_right", keybindings):
                if game.move_right():
                    sfx_move.play()
                das_right_pressed = True
                das_right_start = pygame.time.get_ticks()
                
            # Rotación
            elif is_key_action(event, "rotate", keybindings):
                if game.rotate():
                    sfx_rotate.play()
                    
            # Movimiento hacia abajo
            elif is_key_action(event, "soft_drop", keybindings):
                if game.move_down():
                    sfx_soft_drop.play()
                das_down_pressed = True
                das_down_start = pygame.time.get_ticks()
                
            # Hold piece
            elif is_key_action(event, "hold", keybindings):
                game.hold_piece()
                sfx_hold.play()
                
            # Hard drop (la lógica principal se maneja en game.py)
            elif is_key_action(event, "hard_drop", keybindings):
                pass
    
    # Detectar cuando se sueltan las teclas
    elif event.type == pygame.KEYUP:
        # Verificar si las teclas soltadas son las de movimiento
        for key_action in ["soft_drop", "move_left", "move_right"]:
            if is_key_action(event, key_action, keybindings):
                if key_action == "soft_drop":
                    das_down_pressed = False
                elif key_action == "move_left":
                    das_left_pressed = False
                elif key_action == "move_right":
                    das_right_pressed = False
            
    # Manejar controles de gamepad
    if not paused:
        if check_gamepad_action("pause", keybindings):
            paused = True
        
        if check_gamepad_action("move_left", keybindings) and not das_left_pressed:
            if game.move_left():
                sfx_move.play()
            das_left_pressed = True
            das_left_start = pygame.time.get_ticks()
        else:
            das_left_pressed = check_gamepad_action("move_left", keybindings)
            
        if check_gamepad_action("move_right", keybindings) and not das_right_pressed:
            if game.move_right():
                sfx_move.play()
            das_right_pressed = True
            das_right_start = pygame.time.get_ticks()
        else:
            das_right_pressed = check_gamepad_action("move_right", keybindings)
            
        if check_gamepad_action("rotate", keybindings):
            if game.rotate():
                sfx_rotate.play()
                
        if check_gamepad_action("soft_drop", keybindings) and not das_down_pressed:
            if game.move_down():
                sfx_soft_drop.play()
            das_down_pressed = True
            das_down_start = pygame.time.get_ticks()
        else:
            das_down_pressed = check_gamepad_action("soft_drop", keybindings)
            
        if check_gamepad_action("hold", keybindings):
            game.hold_piece()
            sfx_hold.play()
            
        if check_gamepad_action("hard_drop", keybindings):
            # La lógica de hard drop se maneja en game.py
            pass
    
    return das_left_pressed, das_right_pressed, das_down_pressed, das_left_start, das_right_start, das_down_start, paused

# Game Over Controls
def handle_game_over_controls(event):
    """
    Maneja los controles en la pantalla de fin de juego.
    
    Args:
        event: Evento de pygame
        
    Returns:
        str o None: Acción a realizar (reiniciar, volver_a_inicio, mostrar_puntuaciones, None)
    """
    keybindings = load_keybindings()
    
    # Manejar controles de teclado
    if event.type == pygame.KEYDOWN:
        if is_key_action(event, "cancel", keybindings):
            return "volver_a_inicio"
        elif is_key_action(event, "confirm", keybindings):
            return "reiniciar"
        elif is_key_action(event, "view_highscores", keybindings):
            return "mostrar_puntuaciones"
    
    # Manejar controles de gamepad
    if check_gamepad_action("cancel", keybindings):
        return "volver_a_inicio"
    elif check_gamepad_action("confirm", keybindings):
        return "reiniciar"
    elif check_gamepad_action("view_highscores", keybindings):
        return "mostrar_puntuaciones"
    
    return None

# High Score Input Controls
def handle_highscore_input_controls(event, name, sfx_key, sfx_enter):
    """
    Maneja los controles para la entrada de nombres en la tabla de puntuaciones.
    
    Args:
        event: Evento de pygame
        name: Nombre actual ingresado
        sfx_key: Efecto de sonido para teclas
        sfx_enter: Efecto de sonido para confirmar
        
    Returns:
        tuple: (nuevo_nombre, confirmar, cancelar)
    """
    confirm = False
    cancel = False
    keybindings = load_keybindings()
    
    if event.type == pygame.KEYDOWN:
        if is_key_action(event, "confirm", keybindings) and name.strip():
            sfx_enter.play()
            confirm = True
        elif is_key_action(event, "cancel", keybindings):
            cancel = True
        elif event.key == pygame.K_BACKSPACE:
            name = name[:-1]
            sfx_key.play()
        # Limitar el tamaño del nombre a 10 caracteres
        elif len(name) < 10 and event.unicode.isprintable():
            name += event.unicode
            sfx_key.play()
    
    # Manejar controles de gamepad para la confirmación/cancelación
    if check_gamepad_action("confirm", keybindings) and name.strip():
        sfx_enter.play()
        confirm = True
    elif check_gamepad_action("cancel", keybindings):
        cancel = True
            
    return name, confirm, cancel

# High Score Viewing Controls
def handle_highscore_view_controls(event, sfx_sound=None):
    """
    Maneja los controles para ver la tabla de puntuaciones.
    
    Args:
        event: Evento de pygame
        sfx_sound: Efecto de sonido opcional para reproducir al salir
        
    Returns:
        bool: True si se debe salir de la vista de puntuaciones
    """
    keybindings = load_keybindings()
    
    # Manejar controles de teclado
    if event.type == pygame.KEYDOWN:
        if is_key_action(event, "cancel", keybindings) or is_key_action(event, "confirm", keybindings):
            if sfx_sound:
                sfx_sound.play()
            return True
    
    # Manejar controles de gamepad
    if check_gamepad_action("cancel", keybindings) or check_gamepad_action("confirm", keybindings):
        if sfx_sound:
            sfx_sound.play()
        return True
    
    return False

# Función para el menú de configuración de controles
def handle_controls_menu(screen, settings):
    """
    Maneja el menú de configuración de controles.
    
    Args:
        screen: Superficie de pygame donde dibujar
        settings: Configuración del juego
        
    Returns:
        bool: True si se han aplicado cambios
    """
    # Esta función se implementará en el futuro para permitir configurar controles
    # desde dentro del juego
    pass
