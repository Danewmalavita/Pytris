# game.py
import pygame
import time
import random
import os
from .options import options_menu
from .tetris_logic import TetrisGame, SHAPES, COLORS
from .visual_effects import ParticleSystem, ScreenShake, ComboAnimator, DynamicBackground
from .graphics import TetrisRenderer, draw_text, draw_pause_menu, BLACK, WHITE, GRAY
from .debug_utils import debugger

def pause_menu(screen, settings, current_song="tetris.mp3"):
    from .audio_manager import audio_manager
    
    clock = pygame.time.Clock()
    options = ["Reanudar Juego", "Reintentar", "Cambiar Música", "Información", "Opciones", "Volver a inicio"]
    selected = 0
    
    if 'current_song' not in settings:
        settings['current_song'] = current_song
    
    # Clase dummy para fallback (se usa si audio_manager falla)
    class DummySound:
        def __init__(self, sound_name=None):
            self.sound_name = sound_name
        def play(self): 
            if hasattr(self, 'sound_name') and self.sound_name and audio_manager.audio_available:
                audio_manager.play_sound(self.sound_name)
        def set_volume(self, vol): pass
    
    # Usamos el audio_manager para los efectos de sonido
    sfx_cursor = DummySound("cursor")
    sfx_enter = DummySound("enter")
        
    # Configuramos los efectos a través de una función wrapper para usar audio_manager
    def play_cursor():
        audio_manager.play_sound("cursor")
        
    def play_enter():
        audio_manager.play_sound("enter")
        
    # Conectar las funciones dummy a los métodos del audio_manager
    sfx_cursor.play = play_cursor
    sfx_enter.play = play_enter

    from .controls import handle_pause_menu_controls

    while True:
        draw_pause_menu(screen, settings, selected, options)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            new_selected, action = handle_pause_menu_controls(event, selected, options, sfx_cursor, sfx_enter)
            selected = new_selected
            
            if action:
                return action

        clock.tick(60)


def start_game(screen, settings, game_mode='classic'):
    from .audio_manager import audio_manager
    from .debug_utils import debugger
    from .game_modes import create_game_mode
    
    clock = pygame.time.Clock()
    
    # Clase para crear objetos de sonido dummy como fallback
    class DummySound:
        def __init__(self, sound_name=None):
            self.sound_name = sound_name
        
        def play(self): 
            if self.sound_name and audio_manager.audio_available:
                audio_manager.play_sound(self.sound_name)
        
        def set_volume(self, vol): 
            pass
    
    # Asegurar que el audio esté precargado
    if not audio_manager.audio_available:
        debugger.warning("Audio no disponible, usando sonidos dummy")
        settings['mute'] = True
    
    # Inicializar la música
    current_song = settings.get('current_song', 'tetris.mp3')
    audio_manager.play_music(os.path.splitext(current_song)[0], -1)  # Quitar extensión
    
    # Configurar volumen según ajustes
    audio_manager.set_master_volume(settings['volume_general'])
    audio_manager.set_music_volume(settings['volume_bgm'])
    audio_manager.set_sfx_volume(settings['volume_sfx'])
    audio_manager.set_mute(settings['mute'])
    
    # Crear objetos de sonido que usarán el audio_manager
    sfx_pause = DummySound("pause")
    sfx_move = DummySound("move")
    sfx_rotate = DummySound("rotate")
    sfx_hard_drop = DummySound("harddrop")
    sfx_soft_drop = DummySound("softdrop")
    sfx_landing = DummySound("landing")
    sfx_single = DummySound("single")
    sfx_double = DummySound("double")
    sfx_triple = DummySound("triple")
    sfx_tetris = DummySound("tetris")
    sfx_tspin = DummySound("tspin")
    sfx_hold = DummySound("hold")
    sfx_drop = DummySound("landing")  # Compatibilidad con sfx_landing
    
    # Initialize game with selected mode
    debugger.debug(f"Iniciando juego en modo: {game_mode}")
    game = create_game_mode(game_mode)
    
    # Iniciar temporizador en modos de tiempo
    if game_mode in ['time_attack', 'ultra'] and hasattr(game, 'start'):
        game.start()
        
    renderer = TetrisRenderer(screen)
    
    # Visual effects
    particle_system = ParticleSystem()
    screen_shake = ScreenShake()
    combo_animator = ComboAnimator()
    combo_animator.sfx_vol = sfx_vol if 'sfx_vol' in locals() else 0
    dynamic_background = DynamicBackground(screen.get_width(), screen.get_height())
    
    # Game state
    last_move_down_time = time.time()
    running = True
    paused = False

    # DAS/ARR control variables
    das_left_pressed = das_right_pressed = das_down_pressed = False
    das_left_start = das_right_start = das_down_start = 0
    DAS_DELAY = 170
    ARR_INTERVAL = 40
    
    while running:
        current_time = time.time()
        screen.fill((0, 0, 0))  # Limpiar pantalla
        
        # Importar el módulo de controles unificado
        from .controls import handle_game_controls

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
                    
                    # Pausar temporizador en modos de tiempo
                    if hasattr(game, 'pause'):
                        game.pause()
                        
                    choice = pause_menu(screen, settings, settings.get('current_song', 'tetris.mp3'))
                    paused = False
                    
                    # Reanudar temporizador al salir de la pausa
                    if hasattr(game, 'unpause'):
                        game.unpause()
                    
                    # Procesar la elección del menú de pausa
                    if choice == "reanudar_juego":
                        pass
                    elif choice == "reintentar":
                        # Restart game with the same game mode
                        game_mode = None
                        if hasattr(game, 'mode_name'):
                            mode_name = game.mode_name.lower()
                            if mode_name == "clásico":
                                game_mode = "classic"
                            elif mode_name == "contrarreloj":
                                game_mode = "time_attack"
                            elif mode_name == "maratón":
                                game_mode = "marathon"
                            elif mode_name == "ultra":
                                game_mode = "ultra"
                        start_game(screen, settings, game_mode=game_mode)
                        return
                    elif choice == "cambiar_música":
                        # Cambiar entre las músicas usando audio_manager
                        from .audio_manager import audio_manager
                        
                        # Detener la música actual
                        audio_manager.stop_music()
                        
                        # Rotar entre las pistas disponibles
                        if settings.get('current_song') == 'tetris.mp3':
                            settings['current_song'] = 'tetrisB.mp3'
                        elif settings.get('current_song') == 'tetrisB.mp3':
                            settings['current_song'] = 'song3.mp3'
                        else:
                            settings['current_song'] = 'tetris.mp3'
                        
                        # Extraer el nombre sin extensión para el audio_manager
                        track_name = os.path.splitext(settings['current_song'])[0]
                        
                        # Reproducir la nueva pista
                        audio_manager.play_music(track_name, -1)
                    elif choice == "opciones":
                        from .audio_manager import audio_manager
                        
                        options_menu(screen, settings)
                        screen = pygame.display.set_mode(settings['resolution'])
                        
                        # Actualizar volumen a través del audio_manager
                        audio_manager.set_master_volume(settings['volume_general'])
                        audio_manager.set_music_volume(settings['volume_bgm'])
                        audio_manager.set_sfx_volume(settings['volume_sfx'])
                        audio_manager.set_mute(settings['mute'])
                    elif choice == "volver_a_inicio":
                        from .audio_manager import audio_manager
                        
                        # Detener la música actual y reproducir la del menú
                        audio_manager.stop_music()
                        audio_manager.play_music("menu", -1)
                        return
                    elif choice == "quit":
                        running = False
                
                # Handle key controls
                from .controls import check_gamepad_action, is_key_action, load_keybindings
                keybindings = load_keybindings()
                
                # Check for counter-clockwise rotation
                if ((event.type == pygame.KEYDOWN and is_key_action(event, "rotate_inv", keybindings)) or 
                    check_gamepad_action("rotate_inv")) and not paused and not game.game_over:
                    if game.rotate_inv():
                        sfx_rotate.play()
                
                # Handle hard drop (keyboard or gamepad)
                hard_drop_key = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
                hard_drop_gamepad = check_gamepad_action("hard_drop")
                
                if (hard_drop_key or hard_drop_gamepad) and not paused and not game.game_over:
                    # Log which input triggered the hard drop
                    if hard_drop_key:
                        debugger.debug("Hard drop activado por teclado (SPACE)")
                    else:
                        debugger.debug("Hard drop activado por gamepad (botón/D-pad arriba)")
                    
                    # Ejecutar el hard drop
                    game.drop()
                    sfx_hard_drop.play()
                    
                    # Activar vibración en todos los controladores conectados si fue por gamepad
                    if hard_drop_gamepad and pygame.joystick.get_init() and pygame.joystick.get_count() > 0:
                        try:
                            for i in range(pygame.joystick.get_count()):
                                joy = pygame.joystick.Joystick(i)
                                if joy.get_init():
                                    try:
                                        # Intentar vibrar (solo en controladores que lo soporten)
                                        joy.rumble(0.7, 0.7, 150)
                                    except:
                                        pass  # Ignorar si no tiene soporte de vibración
                        except Exception as e:
                            debugger.error(f"Error al intentar vibración: {str(e)}")
                    
                    # Fix piece and check for line clears
                    line_clear_result = game.fix_piece()
                    
                    if line_clear_result:
                        # Handle T-spin special effects
                        is_tspin = line_clear_result.get("is_tspin", False)
                        if is_tspin:
                            sfx_tspin.play()
                            shake_intensity = 8 if game.level_up_event else 6
                            shake_duration = 30 if game.level_up_event else 25
                            screen_shake.start_shake(shake_intensity, shake_duration)
                            # Add T-spin text animation with proper type
                            # Verificar si es T-spin mini o normal
                            mini_suffix = ""
                            if "tspin_type" in line_clear_result and line_clear_result["tspin_type"] == "T-spin mini":
                                mini_suffix = " Mini"
                                
                            tspin_type = "Single"
                            if line_clear_result['count'] == 2:
                                tspin_type = "Double"
                            elif line_clear_result['count'] == 3:
                                tspin_type = "Triple"
                            combo_animator.add_tspin_animation(f"{tspin_type}{mini_suffix}")
                        
                        # Check for perfect clear (all blocks removed from the field)
                        is_perfect = line_clear_result.get("is_perfect", False)
                        if is_perfect:
                            # Play perfect sound
                            audio_manager.play_sound("perfect")
                            # Add perfect animation
                            combo_animator.add_perfect_animation()
                            # Add screen shake
                            screen_shake.start_shake(10, 35)
                        
                        # Play appropriate sound effect for line clears
                        if line_clear_result["is_tetris"]:
                            sfx_tetris.play()
                            # Add Tetris text animation
                            combo_animator.add_tetris_animation()
                            # More intense shake for Tetris if not already shaking for T-spin or Perfect
                            if not is_tspin and not is_perfect:  # Avoid double shake
                                screen_shake.start_shake(7, 25)
                        elif line_clear_result["count"] == 3:
                            sfx_triple.play()
                        elif line_clear_result["count"] == 2:
                            sfx_double.play()
                        elif line_clear_result["count"] == 1:
                            sfx_single.play()
                            
                    # Reset move down timer after hard drop
                    last_move_down_time = current_time
        
        if not paused and not game.game_over:
            # Auto-drop based on game speed
            move_delay = game.game_speed
            if current_time - last_move_down_time > move_delay / 1000.0:
                if not game.move_down(is_soft_drop=False) and game.should_lock():
                    # Play landing sounds
                    sfx_soft_drop.play()
                    sfx_landing.play()
                    
                    # Fix piece and handle line clears
                    line_clear_result = game.fix_piece()
                    
                    if line_clear_result:
                        # Handle special spin effects (T-spin, J-spin, L-spin, etc.)
                        is_tspin = line_clear_result.get("is_tspin", False)
                        special_spin = line_clear_result.get("special_spin", False)
                        
                        if is_tspin or special_spin:
                            # Special spin effects
                            sfx_tspin.play()
                            shake_intensity = 8 if game.level_up_event else 6
                            shake_duration = 30 if game.level_up_event else 25
                            screen_shake.start_shake(shake_intensity, shake_duration)
                            
                            # Get the spin type and check for mini
                            tspin_type = line_clear_result.get("tspin_type", "T-spin")
                            
                            # Add spin text animation with proper type
                            spin_level = "Single"
                            if line_clear_result['count'] == 2:
                                spin_level = "Double"
                            elif line_clear_result['count'] == 3:
                                spin_level = "Triple"
                                
                            # Use existing T-spin animation for all spins
                            if "mini" in tspin_type.lower():
                                combo_animator.add_tspin_animation(f"{spin_level} Mini")
                            else:
                                combo_animator.add_tspin_animation(f"{spin_level}")
                        
                        # Check for perfect clear (all blocks removed from the field)
                        is_perfect = line_clear_result.get("is_perfect", False)
                        if is_perfect:
                            # Play perfect sound
                            audio_manager.play_sound("perfect")
                            # Add perfect animation
                            combo_animator.add_perfect_animation()
                            # Add screen shake
                            screen_shake.start_shake(10, 35)
                        
                        # Play appropriate sound for line clears
                        if line_clear_result["is_tetris"]:
                            sfx_tetris.play()
                            # Add Tetris text animation
                            combo_animator.add_tetris_animation()
                            # More intense shake for Tetris if not already shaking for T-spin or Perfect
                            if not is_tspin and not is_perfect:  # Avoid double shake
                                screen_shake.start_shake(7, 25)
                        elif line_clear_result["count"] == 3:
                            sfx_triple.play()
                        elif line_clear_result["count"] == 2:
                            sfx_double.play()
                        elif line_clear_result["count"] == 1:
                            sfx_single.play()

                # Reset drop timer
                last_move_down_time = current_time

        now = pygame.time.get_ticks()
        # Line clearing animation
        if game.animating_clear:
            # Optimized animation duration calculation
            base_duration = 250
            min_duration = 100 if game.level >= 10 else 150
            anim_duration = max(min_duration, base_duration - (game.level * 15))
            
            # Track elapsed time with safety check
            current_time = now
            elapsed = current_time - game.clear_animation_time
            
            # Fix invalid animation time
            if elapsed < 0 or elapsed > 2000:
                game.clear_animation_time = current_time - anim_duration
                elapsed = anim_duration

            # Draw game elements during animation
            dynamic_background.draw(screen)
            renderer.draw_field(game, highlight_lines=game.lines_to_clear)
            renderer.draw_current_piece(game)
            
            # Keep info panels visible during animation
            next_piece_x = renderer.offset_x + renderer.block_size * 12
            next_piece_y = renderer.offset_y + renderer.block_size * 2
            renderer.draw_game_info(game, next_piece_x, next_piece_y)
            
            # Create particles for cleared lines (optimized for level speed)
            particle_time = min(80, 40 + (game.level * 2))
            if elapsed < particle_time:
                block_size = renderer.block_size
                for line in game.lines_to_clear:
                    for x in range(game.width):
                        block_type = game.field[line][x]
                        if block_type != 0:
                            color = COLORS[block_type]
                            particle_count = min(5, max(3, 6 - game.level//3))
                            particle_system.add_particles_for_line_clear(
                                x * block_size, 
                                line * block_size, 
                                block_size,
                                color,
                                count=particle_count
                            )
            
            # Update and draw particles
            particle_system.update()
            particle_system.draw(screen, renderer.offset_x, renderer.offset_y)
            
            # Complete animation after duration
            if elapsed >= anim_duration:
                # Add tetris screen shake effect
                if len(game.lines_to_clear) == 4:
                    shake_intensity = min(5, 3 + game.level//3)
                    screen_shake.start_shake(shake_intensity, 20)
                    
                # Update combo animator
                combo_animator.add_combo(len(game.lines_to_clear))
                
                try:
                    game.finish_clear_animation()
                    game.new_piece()
                except Exception:
                    # Reset animation state on error
                    game.lines_to_clear = []
                    game.animating_clear = False
                    game.new_piece()

            pygame.display.flip()
            
            # Safety timeout to prevent game freeze
            if elapsed > 1000:
                try:
                    game.finish_clear_animation()
                    game.new_piece()
                except Exception:
                    game.lines_to_clear = []
                    game.animating_clear = False
                    game.new_piece()
            
            clock.tick(60)
            continue

        # DAS/ARR movement handling (simplified and optimized)
        for direction, pressed, start_time, move_func, sound in [
            ('left', das_left_pressed, das_left_start, game.move_left, sfx_move),
            ('right', das_right_pressed, das_right_start, game.move_right, sfx_move),
            ('down', das_down_pressed, das_down_start, 
             lambda: game.move_down(is_soft_drop=True), sfx_soft_drop)
        ]:
            if pressed:
                elapsed = now - start_time
                
                # First delay (DAS - Delayed Auto Shift)
                if elapsed >= DAS_DELAY:
                    # Calculate auto-repeat (ARR - Auto-Repeat Rate)
                    # Only move if enough time has passed since the last ARR step
                    if (elapsed - DAS_DELAY) % ARR_INTERVAL < clock.get_time():
                        if move_func():
                            sound.play()

        # Actualizar el fondo dinámico según el nivel
        dynamic_background.update(game.level)
        
        # Check if there was a level up and clear particles if needed
        if hasattr(game, 'level_up_event') and game.level_up_event:
            debugger.debug(f"Level up detected! Clearing particles...")
            particle_system.particles = []  # Clear all particles on level up
            
            # Reproducir sonido de nivel completado mediante audio_manager
            from .audio_manager import audio_manager
            audio_manager.play_sound("lvup")
            
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
        


        # Game Over handling
        if game.game_over:
            # Play Game Over sound once using audio_manager
            from .audio_manager import audio_manager
            
            if not hasattr(game, "gameover_sound_played"):
                # Check if it's a marathon completion (victory) to play clear.wav instead of gameover.wav
                if hasattr(game, 'game_won') and game.game_won:
                    audio_manager.play_sound("clear")
                else:
                    audio_manager.play_sound("gameover")
                game.gameover_sound_played = True
                
                # Handle high score
                from .highscore import is_high_score, add_high_score, get_player_name, show_high_scores
                
                # Get game mode for high scores
                game_mode = None
                if hasattr(game, 'mode_name'):
                    game_mode = game.mode_name.lower()
                    if game_mode == "clásico":
                        game_mode = "classic"
                    elif game_mode == "contrarreloj":
                        game_mode = "time_attack"
                    elif game_mode == "maratón":
                        game_mode = "marathon"
                    elif game_mode == "ultra":
                        game_mode = "ultra"
                
                if is_high_score(game.score, game_mode):
                    player_name = get_player_name(screen, game.score)
                    if player_name:
                        add_high_score(player_name, game.score, game.level, game.lines_cleared, game_mode)
                        show_high_scores(screen, settings, game.score, game.mode_name)
            
            # Draw Game Over screen
            renderer.draw_game_over(screen, game, settings)
            
            # Handle Game Over controls
            from .controls import handle_game_over_controls
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                    
                action = handle_game_over_controls(event)
                
                if action == "volver_a_inicio":
                    # Return to main menu with menu music using audio_manager
                    from .audio_manager import audio_manager
                    
                    audio_manager.stop_music()
                    audio_manager.play_music("menu", -1)
                    return
                    
                elif action == "reiniciar":
                    # Restart game with the same game mode
                    game_mode = None
                    if hasattr(game, 'mode_name'):
                        mode_name = game.mode_name.lower()
                        if mode_name == "clásico":
                            game_mode = "classic"
                        elif mode_name == "contrarreloj":
                            game_mode = "time_attack"
                        elif mode_name == "maratón":
                            game_mode = "marathon"
                        elif mode_name == "ultra":
                            game_mode = "ultra"
                    start_game(screen, settings, game_mode=game_mode)
                    return
                    
                elif action == "mostrar_puntuaciones":
                    # Show high scores and redraw game over screen
                    from .highscore import show_high_scores
                    
                    # Get game mode
                    game_mode = None
                    if hasattr(game, 'mode_name'):
                        game_mode = game.mode_name
                        
                    show_high_scores(screen, settings, None, game_mode)
                    renderer.draw_game_over(screen, game, settings)
        


        pygame.display.flip()
        clock.tick(60)

    # Detener la música al salir
    from .audio_manager import audio_manager
    audio_manager.stop_music()