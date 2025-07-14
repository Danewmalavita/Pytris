# options.py
import pygame
import time
from settings import resol
from controls import load_keybindings, save_keybindings, key_string_to_pygame_key, initialize_controls, gamepads

def draw_text(surface, text, size, color, x, y):
    font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def options_menu(screen, settings):
    clock = pygame.time.Clock()
    
    # Importar el módulo de controles
    from controls import handle_options_menu_controls
    
    # Cargar efectos de sonido
    sfx_cursor = pygame.mixer.Sound("assets/bgm/sfx/cursor.wav")
    sfx_enter = pygame.mixer.Sound("assets/bgm/sfx/enter.wav")
    sfx_back = pygame.mixer.Sound("assets/bgm/sfx/back.wav")
    
    # Ajustar volumen de efectos de sonido según la configuración
    sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
    sfx_cursor.set_volume(sfx_vol)
    sfx_enter.set_volume(sfx_vol)
    sfx_back.set_volume(sfx_vol)

    options = ["Volumen General", "Volumen BGM", "Volumen SFX", "Mute", "Resolución", "Controles", "Volver"]
    selected = 0

    resolution_keys = list(resol.keys())
    current_res_index = resolution_keys.index(settings['resolution_label'])

    running = True
    while running:
        screen.fill((30, 30, 30))

        for i, option in enumerate(options):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            label = option

            if option == "Volumen General":
                label += f": {int(settings['volume_general'] * 100)}%"
            elif option == "Volumen BGM":
                label += f": {int(settings['volume_bgm'] * 100)}%"
            elif option == "Volumen SFX":
                label += f": {int(settings['volume_sfx'] * 100)}%"
            elif option == "Mute":
                label += f": {'ON' if settings['mute'] else 'OFF'}"
            elif option == "Resolución":
                label += f": {resolution_keys[current_res_index]}"

            draw_text(screen, label, 36, color, screen.get_width() // 2, 150 + i * 60)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Usar el módulo de controles unificado
            selected, current_res_index, apply_changes, exit_menu, open_controls = handle_options_menu_controls(
                event, selected, options, current_res_index, resolution_keys, 
                settings, sfx_cursor, sfx_enter, sfx_back
            )
            
            # Si se deben aplicar cambios de resolución
            if apply_changes:
                # Aplicar la resolución seleccionada
                settings['resolution_label'] = resolution_keys[current_res_index]
                settings['resolution'] = resol[settings['resolution_label']]
                screen = pygame.display.set_mode(settings['resolution'])
            
            # Si se seleccionó la opción de Controles o se activó desde el controlador
            if open_controls:
                # Mostrar menú de configuración de controles
                controls_menu(screen, settings)
                
            # Si se debe salir del menú
            if exit_menu:
                pygame.time.wait(100)  # Pequeña pausa para permitir que suene el efecto
                return

        # Aplicar los ajustes de volumen a la música
        actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
        pygame.mixer.music.set_volume(actual_music_vol)
        clock.tick(60)

def controls_menu(screen, settings):
    """
    Menú para configurar los controles del juego y probar los gamepads.
    Incorpora funcionalidades de depuración y configuración avanzada.
    """
    clock = pygame.time.Clock()
    
    # Cargar configuraciones actuales
    keybindings = load_keybindings()
    
    # Cargar efectos de sonido
    sfx_cursor = pygame.mixer.Sound("assets/bgm/sfx/cursor.wav")
    sfx_enter = pygame.mixer.Sound("assets/bgm/sfx/enter.wav")
    sfx_back = pygame.mixer.Sound("assets/bgm/sfx/back.wav")
    
    # Ajustar volumen
    sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
    sfx_cursor.set_volume(sfx_vol)
    sfx_enter.set_volume(sfx_vol)
    sfx_back.set_volume(sfx_vol)
    
    # Asegurarse que el módulo joystick esté inicializado
    if not pygame.joystick.get_init():
        pygame.joystick.init()
    
    # Reinicializar los gamepads para asegurarse de detectar todos los conectados
    global gamepads
    gamepads = []
    for i in range(pygame.joystick.get_count()):
        try:
            gamepad = pygame.joystick.Joystick(i)
            gamepad.init()
            gamepads.append(gamepad)
            print(f"Gamepad inicializado: {gamepad.get_name()}")
        except pygame.error as e:
            print(f"Error al inicializar gamepad {i}: {e}")
    
    # Opciones principales del menú de controles
    options = ["Configurar Teclado", "Configurar Gamepad", "Depurar Gamepad"]
    
    # Añadir opción de vibrar gamepads si hay alguno conectado
    if gamepads:
        for i, gamepad in enumerate(gamepads):
            options.append(f"Gamepad {i+1}: {gamepad.get_name()}")
    
    options.append("Volver")
    
    selected = 0
    waiting_for_key = False
    current_action = ""
    current_device = ""
    waiting_for_gamepad = False
    
    # Variables para control de navegación con gamepad
    last_axis_values = {0: 0, 1: 0}  # Para ejes principales (0=horizontal, 1=vertical)
    axis_threshold = 0.5
    button_delay = 200  # ms entre lecturas de botones para evitar múltiples activaciones
    last_button_time = 0
    
    running = True
    while running:
        screen.fill((30, 30, 30))
        
        # Dibujar título
        draw_text(screen, "Configuración de Controles", 40, (255, 255, 255), screen.get_width() // 2, 70)
        
        if waiting_for_key:
            # Modo de espera para asignar una tecla
            draw_text(screen, f"Presiona una tecla para '{current_action}'", 36, (255, 255, 0), 
                     screen.get_width() // 2, screen.get_height() // 2 - 30)
        elif waiting_for_gamepad:
            # Modo de espera para asignar un botón de gamepad
            draw_text(screen, f"Presiona un botón para '{current_action}'", 36, (255, 255, 0),
                     screen.get_width() // 2, screen.get_height() // 2 - 30)
        else:
            # Mostrar las opciones del menú
            for i, option in enumerate(options):
                color = (255, 255, 0) if i == selected else (200, 200, 200)
                
                # Si es una opción de gamepad, cambiar el color para indicar que puede probarse
                if option.startswith("Gamepad") and i == selected:
                    color = (0, 255, 255)
                    
                draw_text(screen, option, 36, color, screen.get_width() // 2, 150 + i * 50)
                
            # Mostrar instrucciones adicionales
            if selected < len(options) - 1 and options[selected].startswith("Gamepad"):
                draw_text(screen, "Presiona ENTER para probar la vibración", 24, (150, 150, 150),
                         screen.get_width() // 2, screen.get_height() - 80)
        
        pygame.display.flip()
        
        # Control con gamepad para la navegación del menú
        current_time = pygame.time.get_ticks()
        if not waiting_for_key and not waiting_for_gamepad and gamepads and (current_time - last_button_time) > button_delay:
            for gamepad in gamepads:
                # Control de navegación vertical con ejes
                axis_y = gamepad.get_axis(1)  # Eje vertical
                if abs(axis_y) > axis_threshold:
                    if abs(last_axis_values[1]) <= axis_threshold:  # Solo si antes no estaba presionado
                        if axis_y < 0:  # Arriba
                            selected = (selected - 1) % len(options)
                            sfx_cursor.play()
                        elif axis_y > 0:  # Abajo
                            selected = (selected + 1) % len(options)
                            sfx_cursor.play()
                        last_button_time = current_time + 200  # Aumentar el retraso para una navegación más lenta
                last_axis_values[1] = axis_y
                
                # Control de navegación con D-pad (hats)
                for i in range(gamepad.get_numhats()):
                    hat = gamepad.get_hat(i)
                    # Solo procesar si hay un cambio en el D-pad y ha pasado suficiente tiempo
                    if hat[1] != 0 and (current_time - last_button_time) > button_delay:
                        if hat[1] > 0:  # Arriba
                            selected = (selected - 1) % len(options)
                            sfx_cursor.play()
                            last_button_time = current_time + 200  # Más retraso para controlar la velocidad
                        elif hat[1] < 0:  # Abajo
                            selected = (selected + 1) % len(options)
                            sfx_cursor.play()
                            last_button_time = current_time + 200  # Más retraso para controlar la velocidad
                
                # Botones para confirmar selección (típicamente A/X/Botón 0)
                if gamepad.get_button(0):  # A/Cruz en mayoría de controles
                    if (current_time - last_button_time) > button_delay:
                        sfx_enter.play()
                        last_button_time = current_time
                        
                        if selected == 0:  # Configurar Teclado
                            try:
                                keyboard_config_menu(screen, settings, keybindings)
                            except Exception as e:
                                print(f"Error en keyboard_config_menu: {e}")
                        elif selected == 1:  # Configurar Gamepad
                            try:
                                gamepad_config_menu(screen, settings, keybindings)
                            except Exception as e:
                                print(f"Error en gamepad_config_menu: {e}")
                        elif selected == 2:  # Depurar Gamepad
                            try:
                                show_gamepad_debug(screen)
                            except Exception as e:
                                print(f"Error en show_gamepad_debug: {e}")
                        elif options[selected] == "Volver":
                            # Evitar crasheos al volver
                            try:
                                sfx_back.play()
                                # Establecer running en False de manera segura
                                running = False
                            except Exception as e:
                                print(f"Error al salir del menú: {e}")
                                running = False
                        elif options[selected].startswith("Gamepad"):
                            # Probar vibración del gamepad seleccionado
                            try:
                                gamepad_idx = int(options[selected].split(":")[0].strip()[-1]) - 1
                                if gamepad_idx < len(gamepads):
                                    try:
                                        gamepads[gamepad_idx].rumble(0.7, 0.7, 500)
                                        draw_text(screen, "¡Vibrando!", 24, (0, 255, 0), 
                                                 screen.get_width() // 2, screen.get_height() - 40)
                                        pygame.display.flip()
                                    except Exception as e:
                                        print(f"Error en rumble: {e}")
                                        draw_text(screen, "Este gamepad no soporta vibración", 24, (255, 0, 0), 
                                                 screen.get_width() // 2, screen.get_height() - 40)
                                        pygame.display.flip()
                                    time.sleep(0.5)
                            except Exception as e:
                                print(f"Error al procesar gamepad: {e}")
                
                # Botón para volver (típicamente B/O/Botón 1 o botón de menú/start)
                if gamepad.get_button(1) or (gamepad.get_numbuttons() > 7 and gamepad.get_button(7)):  # B/Círculo o Start/Options
                    if (current_time - last_button_time) > button_delay:
                        try:
                            sfx_back.play()
                            pygame.time.wait(100)  # Pequeña pausa para que suene el efecto
                            last_button_time = current_time
                            running = False
                        except Exception as e:
                            print(f"Error al procesar botón de volver en controls_menu: {e}")
                            running = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if waiting_for_key:
                # Modo de captura de teclas para configurar el teclado
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Cancelar la asignación
                        waiting_for_key = False
                    else:
                        # Obtener el nombre de la tecla y guardarlo
                        key_name = pygame.key.name(event.key).upper()
                        key_constant = f"K_{key_name}"
                        
                        # Actualizar keybindings
                        keybindings["keyboard"][current_action][0] = {
                            "key": key_constant, 
                            "description": f"Tecla {key_name}"
                        }
                        
                        # Guardar cambios
                        save_keybindings(keybindings)
                        waiting_for_key = False
                        sfx_enter.play()
                        
            elif waiting_for_gamepad:
                # Modo de captura de botones para configurar gamepad
                for i, gamepad in enumerate(gamepads):
                    # Verificar botones
                    for btn_idx in range(gamepad.get_numbuttons()):
                        if gamepad.get_button(btn_idx):
                            print(f"Botón de gamepad detectado: {btn_idx}")
                            # Actualizar keybindings para botones
                            keybindings["gamepad"][current_action][0] = {
                                "button_type": "button",
                                "button": btn_idx,
                                "description": f"Botón {btn_idx}"
                            }
                            save_keybindings(keybindings)
                            waiting_for_gamepad = False
                            sfx_enter.play()
                            time.sleep(0.3)  # Evitar múltiples capturas
                            
                    # Verificar ejes
                    for axis_idx in range(gamepad.get_numaxes()):
                        axis_val = gamepad.get_axis(axis_idx)
                        if abs(axis_val) > 0.7:  # Umbral para detectar movimiento de eje
                            print(f"Eje de gamepad detectado: {axis_idx} (valor: {axis_val:.2f})")
                            # Actualizar keybindings para ejes
                            keybindings["gamepad"][current_action][0] = {
                                "button_type": "axis",
                                "axis": axis_idx,
                                "value": 0.5 if axis_val > 0 else -0.5,
                                "description": f"Axis {axis_idx} {'positivo' if axis_val > 0 else 'negativo'}"
                            }
                            save_keybindings(keybindings)
                            waiting_for_gamepad = False
                            sfx_enter.play()
                            time.sleep(0.3)  # Evitar múltiples capturas
                
                # Opción para cancelar con teclado
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    waiting_for_gamepad = False
            
            else:
                # Navegación normal del menú
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                        sfx_cursor.play()
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                        sfx_cursor.play()
                    elif event.key == pygame.K_RETURN:
                        sfx_enter.play()
                        
                        if selected == 0:  # Configurar Teclado
                            keyboard_config_menu(screen, settings, keybindings)
                        elif selected == 1:  # Configurar Gamepad
                            gamepad_config_menu(screen, settings, keybindings)
                        elif selected == 2:  # Depurar Gamepad
                            # Mostrar el depurador de gamepad
                            show_gamepad_debug(screen)
                        elif options[selected] == "Volver":
                            running = False
                        elif options[selected].startswith("Gamepad"):
                            # Probar vibración del gamepad seleccionado
                            gamepad_idx = int(options[selected].split(":")[0].strip()[-1]) - 1
                            if gamepad_idx < len(gamepads):
                                try:
                                    # Intentar hacer vibrar el gamepad (si soporta vibración)
                                    gamepads[gamepad_idx].rumble(0.7, 0.7, 500)  # Intensidad, duración en ms
                                    draw_text(screen, "¡Vibrando!", 24, (0, 255, 0), 
                                             screen.get_width() // 2, screen.get_height() - 40)
                                    pygame.display.flip()
                                except:
                                    draw_text(screen, "Este gamepad no soporta vibración", 24, (255, 0, 0), 
                                             screen.get_width() // 2, screen.get_height() - 40)
                                    pygame.display.flip()
                                time.sleep(0.5)
                    
                    elif event.key == pygame.K_ESCAPE:
                        sfx_back.play()
                        running = False
        
        clock.tick(60)

def keyboard_config_menu(screen, settings, keybindings):
    """
    Menú para configurar las teclas del teclado.
    """
    clock = pygame.time.Clock()
    
    # Cargar efectos de sonido
    sfx_cursor = pygame.mixer.Sound("assets/bgm/sfx/cursor.wav")
    sfx_enter = pygame.mixer.Sound("assets/bgm/sfx/enter.wav")
    sfx_back = pygame.mixer.Sound("assets/bgm/sfx/back.wav")
    
    # Ajustar volumen
    sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
    sfx_cursor.set_volume(sfx_vol)
    sfx_enter.set_volume(sfx_vol)
    sfx_back.set_volume(sfx_vol)
    
    # Lista de acciones configurables
    actions = [
        ("move_left", "Mover Izquierda"),
        ("move_right", "Mover Derecha"),
        ("rotate", "Rotar Pieza"),
        ("soft_drop", "Caída Suave"),
        ("hard_drop", "Caída Dura"),
        ("hold", "Guardar Pieza"),
        ("pause", "Pausar"),
        ("confirm", "Confirmar"),
        ("cancel", "Cancelar"),
        ("view_highscores", "Ver Puntuaciones")
    ]
    
    selected = 0
    waiting_for_key = False
    current_action = ""
    
    running = True
    while running:
        screen.fill((30, 30, 30))
        
        # Título
        draw_text(screen, "Configurar Teclado", 40, (255, 255, 255), screen.get_width() // 2, 70)
        
        if waiting_for_key:
            # Modo de espera para asignar una tecla
            draw_text(screen, f"Presiona una tecla para '{current_action}'", 36, (255, 255, 0), 
                     screen.get_width() // 2, screen.get_height() // 2 - 30)
        else:
            # Mostrar las acciones y sus teclas asignadas
            y_offset = 140
            for i, (action_key, action_name) in enumerate(actions):
                color = (255, 255, 0) if i == selected else (200, 200, 200)
                
                # Obtener la tecla asignada actualmente
                key_binding = keybindings["keyboard"][action_key][0]["description"]
                
                draw_text(screen, f"{action_name}: {key_binding}", 30, color, 
                         screen.get_width() // 2, y_offset + i * 40)
            
            # Opción para volver
            back_option_y = y_offset + len(actions) * 40
            color = (255, 255, 0) if selected == len(actions) else (200, 200, 200)
            draw_text(screen, "Volver", 30, color, screen.get_width() // 2, back_option_y)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if waiting_for_key:
                # Modo de captura de teclas
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Cancelar la asignación
                        waiting_for_key = False
                    else:
                        # Obtener el nombre de la tecla y guardarlo
                        key_name = pygame.key.name(event.key).upper()
                        key_constant = f"K_{key_name}"
                        
                        # Actualizar keybindings
                        action_key = actions[selected][0]
                        keybindings["keyboard"][action_key][0] = {
                            "key": key_constant, 
                            "description": f"Tecla {key_name}"
                        }
                        
                        # Guardar cambios
                        save_keybindings(keybindings)
                        waiting_for_key = False
                        sfx_enter.play()
            else:
                # Navegación normal del menú
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % (len(actions) + 1)
                        sfx_cursor.play()
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % (len(actions) + 1)
                        sfx_cursor.play()
                    elif event.key == pygame.K_RETURN:
                        if selected < len(actions):
                            # Iniciar modo de asignación de teclas
                            current_action = actions[selected][1]
                            waiting_for_key = True
                            sfx_enter.play()
                        else:
                            # Volver al menú anterior
                            sfx_back.play()
                            running = False
                    elif event.key == pygame.K_ESCAPE:
                        sfx_back.play()
                        running = False
        
        clock.tick(60)

def gamepad_config_menu(screen, settings, keybindings):
    """
    Menú para configurar los botones del gamepad.
    Incluye la funcionalidad de depuración y configuración avanzada.
    """
    clock = pygame.time.Clock()
    
    # Cargar efectos de sonido
    sfx_cursor = pygame.mixer.Sound("assets/bgm/sfx/cursor.wav")
    sfx_enter = pygame.mixer.Sound("assets/bgm/sfx/enter.wav")
    sfx_back = pygame.mixer.Sound("assets/bgm/sfx/back.wav")
    
    # Ajustar volumen
    sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
    sfx_cursor.set_volume(sfx_vol)
    sfx_enter.set_volume(sfx_vol)
    sfx_back.set_volume(sfx_vol)
    
    # Asegurarse que el módulo joystick esté inicializado
    if not pygame.joystick.get_init():
        pygame.joystick.init()
    
    # Reinicializar los gamepads para asegurarse de detectar todos los conectados
    global gamepads
    gamepads = []
    for i in range(pygame.joystick.get_count()):
        try:
            gamepad = pygame.joystick.Joystick(i)
            gamepad.init()
            gamepads.append(gamepad)
            print(f"Gamepad inicializado: {gamepad.get_name()}")
        except pygame.error as e:
            print(f"Error al inicializar gamepad {i}: {e}")
    
    # Verificar si hay gamepads conectados
    if not gamepads:
        # Mostrar mensaje si no hay gamepads
        running = True
        while running:
            screen.fill((30, 30, 30))
            draw_text(screen, "No hay gamepads conectados", 40, (255, 255, 255), 
                     screen.get_width() // 2, screen.get_height() // 2 - 60)
            draw_text(screen, "Conecta un gamepad y reinicia la configuración", 30, (200, 200, 200),
                     screen.get_width() // 2, screen.get_height() // 2)
            draw_text(screen, "Presiona cualquier tecla para volver", 24, (150, 150, 150),
                     screen.get_width() // 2, screen.get_height() // 2 + 60)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    running = False
                    
            clock.tick(60)
        return
    
    # Lista de acciones configurables
    actions = [
        ("move_left", "Mover Izquierda"),
        ("move_right", "Mover Derecha"),
        ("rotate", "Rotar Pieza"),
        ("soft_drop", "Caída Suave"),
        ("hard_drop", "Caída Dura"),
        ("hold", "Guardar Pieza"),
        ("pause", "Pausar"),
        ("confirm", "Confirmar"),
        ("cancel", "Cancelar"),
        ("view_highscores", "Ver Puntuaciones")
    ]
    
    selected = 0
    waiting_for_gamepad = False
    current_action = ""
    current_action_key = ""
    
    # Variables para control de navegación con gamepad
    last_axis_values = {0: 0, 1: 0}  # Para ejes principales (0=horizontal, 1=vertical)
    axis_threshold = 0.5
    button_delay = 200  # ms entre lecturas de botones para evitar múltiples activaciones
    last_button_time = 0
    
    running = True
    while running:
        screen.fill((30, 30, 30))
        
        # Título
        draw_text(screen, "Configurar Gamepad", 40, (255, 255, 255), screen.get_width() // 2, 70)
        
        if waiting_for_gamepad:
            # Modo de espera para asignar un botón/eje
            draw_text(screen, f"Presiona un botón/stick para '{current_action}'", 36, (255, 255, 0), 
                     screen.get_width() // 2, screen.get_height() // 2 - 30)
            draw_text(screen, "Presiona ESC para cancelar", 24, (150, 150, 150),
                     screen.get_width() // 2, screen.get_height() // 2 + 20)
        else:
            # Mostrar las acciones y sus asignaciones actuales
            y_offset = 140
            for i, (action_key, action_name) in enumerate(actions):
                color = (255, 255, 0) if i == selected else (200, 200, 200)
                
                # Obtener la descripción del botón/eje asignado actualmente
                binding_desc = keybindings["gamepad"][action_key][0]["description"]
                
                draw_text(screen, f"{action_name}: {binding_desc}", 30, color, 
                         screen.get_width() // 2, y_offset + i * 40)
            
            # Opción para volver
            back_option_y = y_offset + len(actions) * 40
            color = (255, 255, 0) if selected == len(actions) else (200, 200, 200)
            draw_text(screen, "Volver", 30, color, screen.get_width() // 2, back_option_y)
        
        pygame.display.flip()
        
        # Control con gamepad para la navegación del menú cuando no estamos esperando input
        current_time = pygame.time.get_ticks()
        if not waiting_for_gamepad and gamepads and (current_time - last_button_time) > button_delay:
            for gamepad in gamepads:
                # Control de navegación vertical con ejes
                axis_y = gamepad.get_axis(1)  # Eje vertical
                if abs(axis_y) > axis_threshold:
                    if abs(last_axis_values[1]) <= axis_threshold:  # Solo si antes no estaba presionado
                        if axis_y < 0:  # Arriba
                            selected = (selected - 1) % (len(actions) + 1)
                            sfx_cursor.play()
                        elif axis_y > 0:  # Abajo
                            selected = (selected + 1) % (len(actions) + 1)
                            sfx_cursor.play()
                        last_button_time = current_time + 300  # Aumentar el retraso para una navegación más lenta
                last_axis_values[1] = axis_y
                
                # Control de navegación con D-pad (hats)
                for i in range(gamepad.get_numhats()):
                    hat = gamepad.get_hat(i)
                    # Solo procesar si hay un cambio en el D-pad y ha pasado suficiente tiempo
                    if hat[1] != 0 and (current_time - last_button_time) > button_delay:
                        if hat[1] > 0:  # Arriba
                            selected = (selected - 1) % (len(actions) + 1)
                            sfx_cursor.play()
                            last_button_time = current_time + 300  # Más retraso para controlar la velocidad
                        elif hat[1] < 0:  # Abajo
                            selected = (selected + 1) % (len(actions) + 1)
                            sfx_cursor.play()
                            last_button_time = current_time + 300  # Más retraso para controlar la velocidad
                
                # Botones para confirmar selección (típicamente A/X/Botón 0)
                if gamepad.get_button(0):  # A/Cruz en mayoría de controles
                    if (current_time - last_button_time) > button_delay:
                        sfx_enter.play()
                        last_button_time = current_time
                        
                        if selected < len(actions):
                            # Iniciar modo de asignación de botones/ejes
                            current_action_key = actions[selected][0]
                            current_action = actions[selected][1]
                            waiting_for_gamepad = True
                        else:
                            # Volver al menú anterior
                            try:
                                sfx_back.play()
                                pygame.time.wait(300)  # Mayor pausa para asegurar que suene el efecto
                                running = False
                            except Exception as e:
                                print(f"Error al salir del menú en gamepad_config_menu: {e}")
                                running = False
                
                # Botón para volver (típicamente B/O/Botón 1 o botón de menú/start)
                if gamepad.get_button(1) or (gamepad.get_numbuttons() > 7 and gamepad.get_button(7)):  # B/Círculo o Start/Options
                    if (current_time - last_button_time) > button_delay:
                        try:
                            sfx_back.play()
                            pygame.time.wait(100)  # Pequeña pausa para que suene el efecto
                            last_button_time = current_time
                            running = False
                        except Exception as e:
                            print(f"Error al procesar botón de volver en gamepad_config_menu: {e}")
                            running = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if waiting_for_gamepad:
                # Modo de captura de botones/ejes de gamepad
                for gamepad in gamepads:
                    # Verificar botones
                    for btn_idx in range(gamepad.get_numbuttons()):
                        if gamepad.get_button(btn_idx):
                            print(f"Botón de gamepad detectado en config: {btn_idx}")
                            # Actualizar keybindings para botones
                            keybindings["gamepad"][current_action_key][0] = {
                                "button_type": "button",
                                "button": btn_idx,
                                "description": f"Botón {btn_idx}"
                            }
                            save_keybindings(keybindings)
                            waiting_for_gamepad = False
                            sfx_enter.play()
                            time.sleep(0.3)  # Evitar múltiples capturas
                            
                    # Verificar ejes
                    stored_axis_values = {}
                    for axis_idx in range(gamepad.get_numaxes()):
                        axis_val = gamepad.get_axis(axis_idx)
                        # Store the axis value for debugging
                        stored_axis_values[axis_idx] = axis_val
                        
                        # Skip axis 5 negative values which are often false triggers
                        if axis_idx == 5 and axis_val < -0.5:
                            continue
                            
                        # Only detect strong axis movements with a higher threshold
                        if abs(axis_val) > 0.85:
                            print(f"Eje de gamepad detectado en config: {axis_idx} (valor: {axis_val:.2f})")
                            
                            # Only update if this is an intentional axis movement
                            if not (axis_idx >= 2 and abs(axis_val) > 0.95):  # Triggers and some other axes can have false positives
                                # Actualizar keybindings para ejes
                                keybindings["gamepad"][current_action_key][0] = {
                                    "button_type": "axis",
                                    "axis": axis_idx,
                                    "value": 0.5 if axis_val > 0 else -0.5,
                                    "description": f"Axis {axis_idx} {'positivo' if axis_val > 0 else 'negativo'}"
                                }
                                save_keybindings(keybindings)
                                waiting_for_gamepad = False
                                sfx_enter.play()
                                time.sleep(0.5)  # Longer delay to avoid multiple triggers
                                break
                    
                    # Print axis values for debugging
                    if waiting_for_gamepad and any(abs(v) > 0.3 for v in stored_axis_values.values()):
                        print("Current axis values:", stored_axis_values)
                
                # Opción para cancelar con teclado
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    waiting_for_gamepad = False
            else:
                # Navegación normal del menú con teclado
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % (len(actions) + 1)
                        sfx_cursor.play()
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % (len(actions) + 1)
                        sfx_cursor.play()
                    elif event.key == pygame.K_RETURN:
                        if selected < len(actions):
                            # Iniciar modo de asignación de botones/ejes
                            current_action_key = actions[selected][0]
                            current_action = actions[selected][1]
                            waiting_for_gamepad = True
                            sfx_enter.play()
                        else:
                            # Volver al menú anterior
                            sfx_back.play()
                            running = False
                    elif event.key == pygame.K_ESCAPE:
                        sfx_back.play()
                        running = False
        
        clock.tick(60)
# Integrated gamepad debugger functionality from gamepad_debugger.py
def show_gamepad_debug(screen):
    """
    Muestra una pantalla de depuración con la información de todos los gamepads conectados.
    Útil para identificar índices de botones, ejes y hats.
    
    Args:
        screen: Superficie de pygame donde dibujar
    """
    pygame.joystick.init()
    clock = pygame.time.Clock()
    
    running = True
    while running:
        screen.fill((20, 20, 40))
        
        # Título
        draw_text(screen, "Depurador de Gamepad", 40, (255, 255, 255), screen.get_width() // 2, 30)
        draw_text(screen, "Presiona ESC para salir", 20, (200, 200, 200), screen.get_width() // 2, 70)
        
        # Contar y mostrar gamepads detectados
        num_gamepads = pygame.joystick.get_count()
        draw_text(screen, f"Gamepads detectados: {num_gamepads}", 30, (255, 255, 0), screen.get_width() // 2, 110)
        
        y_offset = 150
        
        # Si no hay gamepads
        if num_gamepads == 0:
            draw_text(screen, "No se detectaron gamepads", 30, (255, 100, 100), 
                     screen.get_width() // 2, screen.get_height() // 2)
        
        # Mostrar información de cada gamepad
        for i in range(num_gamepads):
            gamepad = pygame.joystick.Joystick(i)
            gamepad.init()
            
            # Nombre e índice del gamepad
            draw_text(screen, f"Gamepad {i}: {gamepad.get_name()}", 25, (100, 255, 255), 
                     screen.get_width() // 2, y_offset)
            y_offset += 40
            
            # Información de botones
            buttons_text = "Botones: "
            for b in range(gamepad.get_numbuttons()):
                state = gamepad.get_button(b)
                color = (0, 255, 0) if state else (150, 150, 150)
                draw_text(screen, f"{b}:{1 if state else 0}", 20, color, 
                         100 + (b * 40), y_offset, "left")
            
            y_offset += 30
            
            # Información de ejes
            axes_text = "Ejes: "
            for a in range(gamepad.get_numaxes()):
                value = gamepad.get_axis(a)
                color = (255, 255, 0) if abs(value) > 0.5 else (150, 150, 150)
                draw_text(screen, f"{a}:{value:.2f}", 20, color, 
                         100 + (a * 100), y_offset, "left")
            
            y_offset += 30
            
            # Información de hats (d-pads en algunos controladores)
            for h in range(gamepad.get_numhats()):
                hat = gamepad.get_hat(h)
                draw_text(screen, f"Hat {h}: {hat}", 20, (255, 200, 100), 
                         100, y_offset, "left")
            
            y_offset += 50
        
        # Gestión de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        pygame.display.flip()
        clock.tick(60)

# Integrated controller configuration functionality
class ControllerConfigPatch:
    """
    A class that adds the functionality to configure gamepad controllers.
    This should be instantiated within the options.py file.
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
    
    def init_gamepad(self):
        """Initialize gamepad if available."""
        # Close and reinitialize joystick subsystem to ensure fresh detection
        pygame.joystick.quit()
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()
            print(f"Gamepad detectado: {self.gamepad.get_name()}")
            return True
        print("No se detectó ningún gamepad")
        return False
    
    def handle_controller_config(self):
        """Configure controller buttons."""
        # Get color constants from the global scope
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        YELLOW = (255, 255, 0)
        GREEN = (0, 255, 0)
        RED = (255, 0, 0)
        
        import sys
        
        font = pygame.font.Font(None, 36)
        buttons = ["A (Rotar)", "B (Hard Drop)", "X (Hold)", "D-Pad Down (Soft Drop)"]
        button_keys = ["rotate", "harddrop", "hold", "softdrop"]
        button_values = [0, 1, 2, 13]  # Valores predeterminados para Xbox
        
        current_button = 0
        waiting_for_input = False
        
        # Reinitialize gamepad to ensure fresh detection
        self.init_gamepad()
        
        # Track previous button states to detect new presses
        previous_buttons = [0] * 16 if hasattr(self, 'gamepad') and self.gamepad else []
        
        while True:
            self.screen.fill(BLACK)
            
            # Render title
            title = font.render("Configuración de Controles", True, WHITE)
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))
            
            # Display gamepad status
            if hasattr(self, 'gamepad') and self.gamepad:
                status_text = f"Gamepad conectado: {self.gamepad.get_name()}"
                color = GREEN
            else:
                status_text = "No se detectó ningún gamepad"
                color = RED
                
            status = font.render(status_text, True, color)
            self.screen.blit(status, (self.width // 2 - status.get_width() // 2, 90))
            
            # Instructions
            instruction = font.render("Presiona ESC para guardar y salir", True, WHITE)
            self.screen.blit(instruction, (self.width // 2 - instruction.get_width() // 2, 120))
            
            if waiting_for_input:
                wait_text = font.render(f"Presiona un botón para '{buttons[current_button]}'", True, YELLOW)
                self.screen.blit(wait_text, (self.width // 2 - wait_text.get_width() // 2, 150))
            
            # Button settings
            y_pos = 180
            for i, button_text in enumerate(buttons):
                color = YELLOW if i == current_button else WHITE
                text = font.render(f"{button_text}: Botón {button_values[i]}", True, color)
                self.screen.blit(text, (self.width // 2 - text.get_width() // 2, y_pos))
                y_pos += 50
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Guardar configuración
                        config = {}
                        for i, key in enumerate(button_keys):
                            config[key] = button_values[i]
                        self.save_controller_config(config)
                        return
                    elif event.key == pygame.K_UP:
                        current_button = (current_button - 1) % len(buttons)
                    elif event.key == pygame.K_DOWN:
                        current_button = (current_button + 1) % len(buttons)
                    elif event.key == pygame.K_RETURN:
                        waiting_for_input = not waiting_for_input
            
            # Check gamepad buttons
            if hasattr(self, 'gamepad') and self.gamepad:
                # Get current button states
                current_buttons = []
                for i in range(self.gamepad.get_numbuttons()):
                    current_buttons.append(self.gamepad.get_button(i))
                
                # Ensure we have enough entries in our previous state array
                while len(previous_buttons) < len(current_buttons):
                    previous_buttons.append(0)
                
                # If waiting for input, detect any new button press
                if waiting_for_input:
                    for i, (prev, curr) in enumerate(zip(previous_buttons, current_buttons)):
                        if curr == 1 and prev == 0:  # Button was just pressed
                            print(f"Button {i} pressed for {buttons[current_button]}")
                            button_values[current_button] = i
                            waiting_for_input = False
                            break
                
                # Update previous button states
                previous_buttons = current_buttons.copy()
                
            # Small delay to prevent CPU overuse
            pygame.time.delay(50)
    
    def save_controller_config(self, config):
        """
        Guarda la configuración de botones del gamepad.
        Actualiza el archivo keybindings.json con la nueva configuración.
        """
        import json
        try:
            # Cargar configuración actual
            with open("keybindings.json", "r") as f:
                keybindings = json.load(f)
                
            # Actualizar la configuración con los nuevos valores
            if "rotate" in config and isinstance(config["rotate"], int):
                keybindings["gamepad"]["rotate"][0]["button"] = config["rotate"]
                keybindings["gamepad"]["rotate"][0]["description"] = f"Botón {config['rotate']}"
                
            if "harddrop" in config and isinstance(config["harddrop"], int):
                keybindings["gamepad"]["hard_drop"][0]["button"] = config["harddrop"]
                keybindings["gamepad"]["hard_drop"][0]["description"] = f"Botón {config['harddrop']}"
                
            if "hold" in config and isinstance(config["hold"], int):
                keybindings["gamepad"]["hold"][0]["button"] = config["hold"]
                keybindings["gamepad"]["hold"][0]["description"] = f"Botón {config['hold']}"
                
            if "softdrop" in config and isinstance(config["softdrop"], int):
                # Softdrop might be an axis, need to handle specially
                keybindings["gamepad"]["soft_drop"][0]["button_type"] = "button"
                keybindings["gamepad"]["soft_drop"][0]["button"] = config["softdrop"]
                keybindings["gamepad"]["soft_drop"][0]["description"] = f"Botón {config['softdrop']}"
                if "axis" in keybindings["gamepad"]["soft_drop"][0]:
                    del keybindings["gamepad"]["soft_drop"][0]["axis"]
                if "value" in keybindings["gamepad"]["soft_drop"][0]:
                    del keybindings["gamepad"]["soft_drop"][0]["value"]
                
            # Guardar la configuración actualizada
            with open("keybindings.json", "w") as f:
                json.dump(keybindings, f, indent=2)
            
            print("Configuración del controlador guardada correctamente")
            return True
        except Exception as e:
            print(f"Error al guardar la configuración: {e}")
            return False

# Add advanced controller configuration to the controls menu
def advanced_controller_config(screen, settings):
    """
    Menú avanzado para configurar controles de gamepad.
    Utiliza la clase ControllerConfigPatch.
    """
    controller_config = ControllerConfigPatch(screen)
    controller_config.handle_controller_config()
