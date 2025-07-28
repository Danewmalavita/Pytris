# game.py
import pygame
import time
import random
from .options import options_menu
from .tetris_logic import TetrisGame, SHAPES, COLORS
from .visual_effects import ParticleSystem, ScreenShake, ComboAnimator, DynamicBackground
from .graphics import TetrisRenderer, draw_text, draw_pause_menu, BLACK, WHITE, GRAY
from .debug_utils import debugger

def pause_menu(screen, settings, current_song="tetris.mp3"):
    clock = pygame.time.Clock()
    options = ["Reanudar Juego", "Reintentar", "Cambiar Música", "Opciones", "Volver a inicio"]
    selected = 0
    
    if 'current_song' not in settings:
        settings['current_song'] = current_song
    
    # Setup audio
    audio_available = pygame.mixer.get_init() is not None
    
    if audio_available:
        try:
            sfx_cursor = pygame.mixer.Sound("assets/sounds/sfx/cursor.wav")
            sfx_enter = pygame.mixer.Sound("assets/sounds/sfx/enter.wav")
            sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
            sfx_cursor.set_volume(sfx_vol)
            sfx_enter.set_volume(sfx_vol)
        except (pygame.error, FileNotFoundError):
            audio_available = False
    
    # Create dummy sounds if audio unavailable
    if not audio_available:
        class DummySound:
            def play(self): pass
            def set_volume(self, vol): pass
        sfx_cursor = DummySound()
        sfx_enter = DummySound()

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


def start_game(screen, settings):
    clock = pygame.time.Clock()
    
    # Audio setup
    audio_available = pygame.mixer.get_init() is not None
    
    class DummySound:
        def play(self): pass
        def set_volume(self, vol): pass
    
    # Initialize sound effects
    if audio_available:
        try:
            # Load selected music
            current_song = settings.get('current_song', 'tetris.mp3')
            pygame.mixer.music.load(f"assets/sounds/bgm/{current_song}")
            
            actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
            pygame.mixer.music.set_volume(actual_music_vol)
            
            if not settings['mute']:
                pygame.mixer.music.play(-1)
    
            # Load all sound effects
            sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
            
            sfx_pause = pygame.mixer.Sound("assets/sounds/sfx/pause.wav")
            sfx_move = pygame.mixer.Sound("assets/sounds/sfx/move.wav")
            sfx_rotate = pygame.mixer.Sound("assets/sounds/sfx/rotate.wav")
            sfx_hard_drop = pygame.mixer.Sound("assets/sounds/sfx/harddrop.wav")
            sfx_soft_drop = pygame.mixer.Sound("assets/sounds/sfx/softdrop.wav")
            sfx_landing = pygame.mixer.Sound("assets/sounds/sfx/landing.wav")
            sfx_single = pygame.mixer.Sound("assets/sounds/sfx/single.wav")
            sfx_double = pygame.mixer.Sound("assets/sounds/sfx/double.wav")
            sfx_triple = pygame.mixer.Sound("assets/sounds/sfx/triple.wav")
            sfx_tetris = pygame.mixer.Sound("assets/sounds/sfx/tetris.wav")
            sfx_tspin = pygame.mixer.Sound("assets/sounds/sfx/tspin.wav")
            sfx_hold = pygame.mixer.Sound("assets/sounds/sfx/hold.wav")
            sfx_drop = sfx_landing  # For compatibility
            
            # Set volume for all effects
            for sfx in [sfx_pause, sfx_move, sfx_rotate, sfx_hard_drop, sfx_soft_drop, 
                        sfx_landing, sfx_single, sfx_double, sfx_triple, sfx_tetris, 
                        sfx_tspin, sfx_hold, sfx_drop]:
                sfx.set_volume(sfx_vol)
                
        except (pygame.error, FileNotFoundError):
            audio_available = False
            settings['mute'] = True
    
    # Use dummy sounds if audio not available
    if not audio_available:
        settings['mute'] = True
        sfx_pause = sfx_move = sfx_rotate = sfx_hard_drop = sfx_soft_drop = DummySound()
        sfx_landing = sfx_single = sfx_double = sfx_triple = sfx_tetris = DummySound()
        sfx_tspin = sfx_hold = sfx_drop = DummySound()
    
    # Initialize game components
    game = TetrisGame()
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
                                pygame.mixer.music.load(f"assets/sounds/bgm/{settings['current_song']}")
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
                        pygame.mixer.music.load("assets/sounds/bgm/menu.mp3")
                        actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
                        pygame.mixer.music.set_volume(actual_music_vol)
                        if not settings['mute']:
                            pygame.mixer.music.play(-1)
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
                    game.drop()
                    sfx_hard_drop.play()
                    
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
                        
                        # Play appropriate sound effect for line clears
                        if line_clear_result["is_tetris"]:
                            sfx_tetris.play()
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
                        # Handle T-spin special effects
                        is_tspin = line_clear_result.get("is_tspin", False)
                        
                        if is_tspin:
                            # T-spin effects
                            sfx_tspin.play()
                            shake_intensity = 8 if game.level_up_event else 6
                            shake_duration = 30 if game.level_up_event else 25
                            screen_shake.start_shake(shake_intensity, shake_duration)
                            
                            # Add T-spin text animation
                            tspin_text = "¡T-SPIN!"
                            combo_animator.add_text_animation(
                                f"{tspin_text} +{line_clear_result['count']} LÍNEAS", 
                                (255, 50, 255)
                            )
                        
                        # Play appropriate sound for line clears
                        if line_clear_result["is_tetris"]:
                            sfx_tetris.play()
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

        # DAS/ARR movement handling (optimized)
        for direction, pressed, start_time, move_func, sound in [
            ('left', das_left_pressed, das_left_start, game.move_left, sfx_move),
            ('right', das_right_pressed, das_right_start, game.move_right, sfx_move),
            ('down', das_down_pressed, das_down_start, 
             lambda: game.move_down(is_soft_drop=True), sfx_soft_drop)
        ]:
            if pressed and (elapsed := now - start_time) >= DAS_DELAY:
                arr_elapsed = elapsed - DAS_DELAY
                arr_steps = arr_elapsed // ARR_INTERVAL
                
                # Apply movement on ARR timing
                if arr_steps > 0 and arr_elapsed % ARR_INTERVAL < clock.get_time():
                    if move_func():
                        sound.play()

        # Actualizar el fondo dinámico según el nivel
        dynamic_background.update(game.level)
        
        # Check if there was a level up and clear particles if needed
        if hasattr(game, 'level_up_event') and game.level_up_event:
            debugger.debug(f"Level up detected! Clearing particles...")
            particle_system.particles = []  # Clear all particles on level up
            
            # Reproducir sonido de nivel completado
            sfx_lvup = pygame.mixer.Sound("assets/sounds/sfx/lvup.wav")
            sfx_lvup.set_volume(sfx_vol)
            sfx_lvup.play()
            
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
            # Play Game Over sound once
            if not hasattr(game, "gameover_sound_played"):
                sfx_gameover = pygame.mixer.Sound("assets/sounds/sfx/gameover.wav")
                sfx_gameover.set_volume(sfx_vol)
                sfx_gameover.play()
                game.gameover_sound_played = True
                
                # Handle high score
                from .highscore import is_high_score, add_high_score, get_player_name, show_high_scores
                
                if is_high_score(game.score):
                    player_name = get_player_name(screen, game.score)
                    if player_name:
                        add_high_score(player_name, game.score, game.level, game.lines_cleared)
                        show_high_scores(screen, settings, game.score)
            
            # Draw Game Over screen
            renderer.draw_game_over(screen, game, settings)
            
            # Handle Game Over controls
            from .controls import handle_game_over_controls
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                    
                action = handle_game_over_controls(event)
                
                if action == "volver_a_inicio":
                    # Return to main menu with menu music
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("assets/sounds/bgm/menu.mp3")
                    actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
                    pygame.mixer.music.set_volume(actual_music_vol)
                    if not settings['mute']:
                        pygame.mixer.music.play(-1)
                    return
                    
                elif action == "reiniciar":
                    # Restart game
                    start_game(screen, settings)
                    return
                    
                elif action == "mostrar_puntuaciones":
                    # Show high scores and redraw game over screen
                    from .highscore import show_high_scores
                    show_high_scores(screen, settings)
                    renderer.draw_game_over(screen, game, settings)
        


        pygame.display.flip()
        clock.tick(60)

    pygame.mixer.music.stop()