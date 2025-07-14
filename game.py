# game.py
import pygame
import time
import random
from options import options_menu
from tetris_logic import TetrisGame, SHAPES, COLORS
from visual_effects import ParticleSystem, ScreenShake, ComboAnimator, DynamicBackground
from graphics import TetrisRenderer, draw_text, draw_pause_menu, BLACK, WHITE, GRAY
from debug_utils import debugger

def pause_menu(screen, settings, current_song="tetris.mp3"):
    clock = pygame.time.Clock()
    options = ["Reanudar Juego", "Reintentar", "Cambiar Música", "Opciones", "Volver a inicio"]
    selected = 0
    
    # Track current music
    if 'current_song' not in settings:
        settings['current_song'] = current_song
    
    # Cargar efectos de sonido
    audio_available = pygame.mixer.get_init() is not None
    
    if audio_available:
        try:
            sfx_cursor = pygame.mixer.Sound("assets/bgm/sfx/cursor.wav")
            sfx_enter = pygame.mixer.Sound("assets/bgm/sfx/enter.wav")
            
            # Ajustar volumen de efectos de sonido según la configuración
            sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
            sfx_cursor.set_volume(sfx_vol)
            sfx_enter.set_volume(sfx_vol)
        except (pygame.error, FileNotFoundError):
            audio_available = False
    
    # Crear objetos nulos para los efectos si no hay audio
    if not audio_available:
        class DummySound:
            def play(self): pass
            def set_volume(self, vol): pass
            
        sfx_cursor = DummySound()
        sfx_enter = DummySound()

    # Importar el módulo de controles unificado
    from controls import handle_pause_menu_controls

    while True:
        # Usar la función de dibujo del menú de pausa desde graphics.py
        draw_pause_menu(screen, settings, selected, options)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            # Usar el módulo de controles unificado
            new_selected, action = handle_pause_menu_controls(event, selected, options, sfx_cursor, sfx_enter)
            selected = new_selected
            
            if action:
                return action

        clock.tick(60)

# La clase TetrisRenderer ahora se encuentra en graphics.py


def start_game(screen, settings):
    clock = pygame.time.Clock()
    
    # Check if audio is available
    audio_available = pygame.mixer.get_init() is not None
    
    # Set up dummy sound class for when audio isn't available
    class DummySound:
        def play(self): pass
        def set_volume(self, vol): pass
    
    # Initialize sound effects
    if audio_available:
        try:
            # Usar la canción seleccionada o predeterminada
            current_song = settings.get('current_song', 'tetris.mp3')
            pygame.mixer.music.load(f"assets/bgm/{current_song}")
            
            # Aplicar los ajustes de volumen
            actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
            pygame.mixer.music.set_volume(actual_music_vol)
            
            if not settings['mute']:
                pygame.mixer.music.play(-1)
    
            # Cargar efecto de pausa y otros efectos de sonido
            sfx_pause = pygame.mixer.Sound("assets/bgm/sfx/pause.wav")
            sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
            sfx_pause.set_volume(sfx_vol)
            
            # Cargar efectos de sonido del juego
            sfx_move = pygame.mixer.Sound("assets/bgm/sfx/move.wav")  # Movimiento de pieza
            sfx_rotate = pygame.mixer.Sound("assets/bgm/sfx/rotate.wav")  # Rotación de pieza
            sfx_hard_drop = pygame.mixer.Sound("assets/bgm/sfx/harddrop.wav")  # Aterrizaje con espacio (hard drop)
            sfx_soft_drop = pygame.mixer.Sound("assets/bgm/sfx/softdrop.wav")  # Aterrizaje sin espacio (soft drop)
            sfx_landing = pygame.mixer.Sound("assets/bgm/sfx/landing.wav")  # Sonido al aterrizar la pieza
            sfx_single = pygame.mixer.Sound("assets/bgm/sfx/single.wav")  # Sonido al hacer una línea
            sfx_tetris = pygame.mixer.Sound("assets/bgm/sfx/tetris.wav")  # Sonido al hacer una linea de 4 (tetris)
            sfx_hold = pygame.mixer.Sound("assets/bgm/sfx/hold.wav")  # Sonido al hacer hold de una pieza
            sfx_drop = sfx_landing  # Mantener compatibilidad con código existente
            
            # Ajustar volumen de todos los efectos
            sfx_move.set_volume(sfx_vol)
            sfx_rotate.set_volume(sfx_vol)
            sfx_hard_drop.set_volume(sfx_vol)
            sfx_soft_drop.set_volume(sfx_vol)
            sfx_landing.set_volume(sfx_vol)
            sfx_single.set_volume(sfx_vol)
            sfx_tetris.set_volume(sfx_vol)
            sfx_hold.set_volume(sfx_vol)
            sfx_drop.set_volume(sfx_vol)  # Para compatibilidad con código existente
        except (pygame.error, FileNotFoundError):
            audio_available = False
            settings['mute'] = True
    
    # If audio isn't available, use dummy sound objects
    if not audio_available:
        settings['mute'] = True
        sfx_pause = DummySound()
        sfx_move = DummySound()
        sfx_rotate = DummySound()
        sfx_hard_drop = DummySound()
        sfx_soft_drop = DummySound()
        sfx_landing = DummySound()
        sfx_single = DummySound()
        sfx_tetris = DummySound()
        sfx_hold = DummySound()
        sfx_drop = DummySound()
    
    # Crear juego y renderizador
    game = TetrisGame()
    renderer = TetrisRenderer(screen)
    
    # Inicializar efectos visuales
    particle_system = ParticleSystem()
    screen_shake = ScreenShake()
    combo_animator = ComboAnimator()
    dynamic_background = DynamicBackground(screen.get_width(), screen.get_height())
    
    # Variables de tiempo
    last_move_down_time = time.time()

    
    running = True
    paused = False

    # Controles de DAS/ARR
    das_left_pressed = False
    das_right_pressed = False
    das_down_pressed = False
    das_left_start = 0
    das_right_start = 0
    das_down_start = 0
    DAS_DELAY = 170
    ARR_INTERVAL = 40
    
    while running:
        current_time = time.time()
        screen.fill((0, 0, 0))  # Limpiar pantalla
        
        # Importar el módulo de controles unificado
        from controls import handle_game_controls

        # Manejar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Si el juego ha terminado, usar controles de game over
            if game.game_over:
                continue  # Los controles de game over se manejan en la sección de game over
                
            # Manejar los controles del juego usando el módulo de controles unificado
            if not paused:
                das_left_pressed, das_right_pressed, das_down_pressed, das_left_start, \
                das_right_start, das_down_start, new_paused = handle_game_controls(
                    event, game, das_left_pressed, das_right_pressed, das_down_pressed,
                    das_left_start, das_right_start, das_down_start, 
                    sfx_move, sfx_rotate, sfx_soft_drop, sfx_hold, paused
                )
                
                # Si se presiona Escape, mostrar menú de pausa
                if new_paused and not paused:
                    sfx_pause.play()
                    paused = True
                    choice = pause_menu(screen, settings, settings.get('current_song', 'tetris.mp3'))
                    paused = False
                    
                    # Procesar la elección del menú de pausa
                    if choice == "reanudar_juego":
                        pass
                    elif choice == "reintentar":
                        # Reiniciar juego
                        game = TetrisGame()
                        start_game(screen, settings)
                        return
                    elif choice == "cambiar_música":
                        # Cambiar entre las músicas
                        if audio_available:
                            pygame.mixer.music.stop()
                            if settings.get('current_song') == 'tetris.mp3':
                                settings['current_song'] = 'tetrisB.mp3'
                            elif settings.get('current_song') == 'tetrisB.mp3':
                                settings['current_song'] = 'song3.mp3'
                            else:
                                settings['current_song'] = 'tetris.mp3'
                            
                            # Cargar y reproducir la nueva música
                            try:
                                pygame.mixer.music.load(f"assets/bgm/{settings['current_song']}")
                                if not settings['mute']:
                                    actual_music_vol = settings['volume_general'] * settings['volume_bgm']
                                    pygame.mixer.music.set_volume(actual_music_vol)
                                    pygame.mixer.music.play(-1)
                            except (pygame.error, FileNotFoundError):
                                pass
                    elif choice == "opciones":
                        options_menu(screen, settings)
                        screen = pygame.display.set_mode(settings['resolution'])
                        # Actualizar volumen
                        actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
                        pygame.mixer.music.set_volume(actual_music_vol)
                        sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
                        sfx_pause.set_volume(sfx_vol)
                        sfx_move.set_volume(sfx_vol)
                        sfx_rotate.set_volume(sfx_vol)
                        sfx_hard_drop.set_volume(sfx_vol)
                        sfx_soft_drop.set_volume(sfx_vol)
                        sfx_single.set_volume(sfx_vol)
                        sfx_tetris.set_volume(sfx_vol)
                        sfx_drop.set_volume(sfx_vol)
                    elif choice == "volver_a_inicio":
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("assets/bgm/menu.mp3")
                        actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
                        pygame.mixer.music.set_volume(actual_music_vol)
                        if not settings['mute']:
                            pygame.mixer.music.play(-1)
                        return
                    elif choice == "quit":
                        running = False
                
                # Manejar el hard drop (se maneja por separado debido a su complejidad)
                # Verificar tanto teclado como gamepad para hard drop
                hard_drop_key = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not paused and not game.game_over
                
                # Importar el módulo de controles unificado para verificar gamepad
                from controls import check_gamepad_action
                hard_drop_gamepad = check_gamepad_action("hard_drop") and not paused and not game.game_over
                
                if hard_drop_key or hard_drop_gamepad:
                    # Mostrar mensaje de depuración para confirmar que el hard drop del gamepad funciona
                    if hard_drop_gamepad:
                        print("Hard drop ejecutado mediante gamepad")
                    
                    game.drop()
                    # Usar el sonido de hard drop previamente cargado
                    sfx_hard_drop.play()
                    
                    # No reproducir sonido de aterrizaje aquí ya que hardrop tiene su propio sonido
                    
                    # Fijar pieza y comprobar líneas
                    line_clear_result = game.fix_piece()
                    
                    # Reproducir sonido de eliminación de líneas si corresponde
                    if line_clear_result:
                        if line_clear_result["is_tetris"]:
                            sfx_tetris.play()
                        elif line_clear_result["count"] > 0:
                            sfx_single.play()
                            
                    last_move_down_time = current_time  # Resetear tiempo tras hard drop
        
        if not paused and not game.game_over:
            # Movimiento automático hacia abajo
            move_delay = game.game_speed
            if current_time - last_move_down_time > move_delay / 1000.0:  # Convertir a segundos
                if not game.move_down():
                    if game.should_lock():
                        sfx_soft_drop.play()
                        
                        # Reproducir sonido de aterrizaje de pieza (ya cargado previamente)
                        sfx_landing.play()
                        
                        # Fijar pieza y verificar líneas eliminadas
                        line_clear_result = game.fix_piece()
                        
                        # Reproducir sonido de eliminación de líneas si corresponde
                        if line_clear_result:
                            if line_clear_result["is_tetris"]:
                                sfx_tetris.play()
                            elif line_clear_result["count"] > 0:
                                sfx_single.play()


                last_move_down_time = current_time

        now = pygame.time.get_ticks()
        # Animación de limpieza de líneas
        if game.animating_clear:
            # Improved animation duration calculation with better high-level performance
            # Set a fixed animation duration for all levels to ensure consistency
            # This prevents timing issues at higher levels while maintaining visual quality
            base_duration = 250  # Base duration ms for low levels
            min_duration = 150   # Absolute minimum duration ms
            
            # For high levels (10+), use a more aggressive minimum to prevent slowdowns
            if game.level >= 10:
                min_duration = 100
                
            # Calculate appropriate duration based on level - more aggressive scaling
            anim_duration = max(min_duration, base_duration - (game.level * 15))
            
            # Track elapsed time with safety overflow prevention
            current_time = now
            elapsed = current_time - game.clear_animation_time
            
            # Safety check - if animation time is invalid, fix it
            if elapsed < 0 or elapsed > 2000:  # If negative or excessive time elapsed
                debugger.warning(f"Invalid animation time: {elapsed}ms, resetting")
                game.clear_animation_time = current_time - anim_duration  # Force animation to complete
                elapsed = anim_duration

            # Dibujar el fondo dinámico
            dynamic_background.draw(screen)
            
            # Dibujar el campo con líneas atenuadas
            renderer.draw_field(game, highlight_lines=game.lines_to_clear)
            renderer.draw_current_piece(game)  # para que no desaparezca
            
            # Crear partículas para las líneas que se eliminarán - ajustar timing según nivel
            particle_time = min(80, 40 + (game.level * 2))  # Adjusts with game level
            if elapsed < particle_time:  # Solo añadir partículas en la primera parte de la animación
                block_size = renderer.block_size
                for line in game.lines_to_clear:
                    for x in range(game.width):
                        block_type = game.field[line][x]
                        if block_type != 0:
                            # Obtener color del bloque
                            color = COLORS[block_type]
                            # Añadir partículas en la posición del bloque
                            particle_count = min(5, max(3, 6 - game.level//3))  # Fewer particles at high levels
                            particle_system.add_particles_for_line_clear(
                                x * block_size, 
                                line * block_size, 
                                block_size,
                                color,
                                count=particle_count
                            )
            
            # Actualizar y dibujar partículas
            particle_system.update()
            particle_system.draw(screen, renderer.offset_x, renderer.offset_y)
            
            # Guarantee animation completes after duration
            if elapsed >= anim_duration:
                # Log to debug
                debugger.debug(f"Completing line clear animation at level {game.level}, duration: {anim_duration}ms")
                
                # Si se hizo un tetris, aplicar efecto de temblor de pantalla
                if len(game.lines_to_clear) == 4:
                    shake_intensity = min(5, 3 + game.level//3)  # Scale with level but cap at 5
                    screen_shake.start_shake(shake_intensity, 20)  # Intensidad, duración 20 frames
                    
                # Actualizar animador de combo si hubo líneas eliminadas
                combo_animator.add_combo(len(game.lines_to_clear))
                
                try:
                    # Try-except to catch any errors in the clear animation
                    game.finish_clear_animation()
                    game.new_piece()
                except Exception as e:
                    debugger.error(f"Error completing line clear animation: {str(e)}")
                    # Force reset animation state to prevent game from getting stuck
                    game.lines_to_clear = []
                    game.animating_clear = False
                    game.new_piece()

            # Mostrar frame y limitar a 60fps, pero permitir que se salte del loop en caso de error
            pygame.display.flip()
            
            # Límite de tiempo para animación para evitar congelamiento
            if elapsed > 1000:  # 1 segundo de seguridad máximo
                debugger.warning(f"Animation taking too long ({elapsed}ms), forcing completion")
                try:
                    game.finish_clear_animation()
                    game.new_piece()
                except Exception as e:
                    debugger.error(f"Error in forced animation completion: {str(e)}")
                    # Reset state to prevent freeze
                    game.lines_to_clear = []
                    game.animating_clear = False
                    game.new_piece()
            
            clock.tick(60)
            continue

        # DAS movimiento continuo con timing mejorado
        if das_left_pressed:
            elapsed = now - das_left_start
            # Verificar si ha pasado el tiempo inicial de DAS
            if elapsed >= DAS_DELAY:
                # Calcular cuántos movimientos deberían haberse producido desde el inicio del ARR
                arr_elapsed = elapsed - DAS_DELAY
                arr_steps = arr_elapsed // ARR_INTERVAL
                
                # Si estamos en un nuevo paso de ARR, mover la pieza
                if arr_steps > 0 and arr_elapsed % ARR_INTERVAL < clock.get_time():
                    if game.move_left():
                        sfx_move.play()

        if das_right_pressed:
            elapsed = now - das_right_start
            # Verificar si ha pasado el tiempo inicial de DAS
            if elapsed >= DAS_DELAY:
                # Calcular cuántos movimientos deberían haberse producido desde el inicio del ARR
                arr_elapsed = elapsed - DAS_DELAY
                arr_steps = arr_elapsed // ARR_INTERVAL
                
                # Si estamos en un nuevo paso de ARR, mover la pieza
                if arr_steps > 0 and arr_elapsed % ARR_INTERVAL < clock.get_time():
                    if game.move_right():
                        sfx_move.play()

        if das_down_pressed:
            elapsed = now - das_down_start
            # Verificar si ha pasado el tiempo inicial de DAS
            if elapsed >= DAS_DELAY:
                # Calcular cuántos movimientos deberían haberse producido desde el inicio del ARR
                arr_elapsed = elapsed - DAS_DELAY
                arr_steps = arr_elapsed // ARR_INTERVAL
                
                # Si estamos en un nuevo paso de ARR, mover la pieza
                if arr_steps > 0 and arr_elapsed % ARR_INTERVAL < clock.get_time():
                    if game.move_down():
                        # Usar el sonido de soft drop previamente cargado
                        sfx_soft_drop.play()

        # Actualizar el fondo dinámico según el nivel
        dynamic_background.update(game.level)
        
        # Check if there was a level up and clear particles if needed
        if hasattr(game, 'level_up_event') and game.level_up_event:
            debugger.debug(f"Level up detected! Clearing particles...")
            particle_system.particles = []  # Clear all particles on level up
            game.level_up_event = False
        
        # Dibujar el fondo dinámico
        dynamic_background.draw(screen)
        
        # Actualizar y dibujar efectos visuales
        screen_shake.update()
        shake_offset_x, shake_offset_y = screen_shake.get_offset()
        
        # Actualizar animador de combo
        combo_animator.update()
        
        # Actualizar sistema de partículas
        particle_system.update()
        
        # Dibujar el juego con efecto de temblor si está activo
        renderer.draw_field(game, offset_x=shake_offset_x, offset_y=shake_offset_y)
        renderer.draw_current_piece(game, offset_x=shake_offset_x, offset_y=shake_offset_y)
        
        # Dibujar partículas
        particle_system.draw(screen, renderer.offset_x, renderer.offset_y)
        
        # Dibujar animación de combo en el centro del área de juego
        combo_center_x = renderer.offset_x + (game.width * renderer.block_size) // 2
        combo_center_y = renderer.offset_y + (game.height * renderer.block_size) // 2
        combo_animator.draw(screen, combo_center_x, combo_center_y)
        
        # Dibujar próxima pieza e información del juego
        next_piece_x = renderer.offset_x + renderer.block_size * 12
        next_piece_y = renderer.offset_y + renderer.block_size * 2
        
        # Dibujar información del juego usando la función de graphics.py
        renderer.draw_game_info(game, next_piece_x, next_piece_y)
        


        # Si el juego ha terminado, mostrar pantalla de Game Over
        if game.game_over:
            # Reproducir sonido de Game Over si no se ha reproducido ya
            if not hasattr(game, "gameover_sound_played"):
                sfx_gameover = pygame.mixer.Sound("assets/bgm/sfx/gameover.wav")
                sfx_gameover.set_volume(sfx_vol)
                sfx_gameover.play()
                game.gameover_sound_played = True
                
                # Import here to avoid circular imports
                from highscore import is_high_score, add_high_score, get_player_name, show_high_scores
                
                # Check if this is a new high score
                if is_high_score(game.score):
                    # Get player name
                    player_name = get_player_name(screen, game.score)
                    if player_name:
                        # Add to high scores
                        position = add_high_score(player_name, game.score, game.level, game.lines_cleared)
                        # Show high scores with current score highlighted
                        show_high_scores(screen, settings, game.score)
            
            # Usar función de dibujo de game over desde graphics.py
            renderer.draw_game_over(screen, game, settings)
            
            # Importar el módulo de controles para game over
            from controls import handle_game_over_controls
            
            # Esperar a que el jugador decida qué hacer
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                    
                # Usar el módulo de controles unificado para el game over
                action = handle_game_over_controls(event)
                
                if action == "volver_a_inicio":
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("assets/bgm/menu.mp3")
                    actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
                    pygame.mixer.music.set_volume(actual_music_vol)
                    if not settings['mute']:
                        pygame.mixer.music.play(-1)
                    return
                elif action == "reiniciar":
                    start_game(screen, settings)
                    return
                elif action == "mostrar_puntuaciones":
                    # Import here to avoid circular import
                    from highscore import show_high_scores
                    show_high_scores(screen, settings)
                    # Need to redraw the game over screen after returning from high scores
                    # Use the draw_game_over function from renderer
                    renderer.draw_game_over(screen, game, settings)
        


        pygame.display.flip()
        clock.tick(60)

    pygame.mixer.music.stop()