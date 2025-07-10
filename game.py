# game.py
import pygame
import time
import random
from options import options_menu
from tetris_logic import TetrisGame, SHAPES, COLORS
from visual_effects import ParticleSystem, ScreenShake, ComboAnimator, DynamicBackground

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

def draw_text(surface, text, size, color, x, y):
    font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def pause_menu(screen, settings):
    clock = pygame.time.Clock()
    options = ["Reintentar", "Opciones", "Volver a inicio"]
    selected = 0

    # Cargar efectos de sonido
    sfx_cursor = pygame.mixer.Sound("assets/bgm/sfx/cursor.wav")
    sfx_enter = pygame.mixer.Sound("assets/bgm/sfx/enter.wav")
    
    # Ajustar volumen de efectos de sonido según la configuración
    sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
    sfx_cursor.set_volume(sfx_vol)
    sfx_enter.set_volume(sfx_vol)

    while True:
        screen.fill((50, 20, 20))

        draw_text(screen, "Pausa", 64, (255, 255, 255), screen.get_width() // 2, 80)

        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected else (180, 180, 180)
            label = option
            
            if option == "Volumen General":
                label += f": {int(settings['volume_general'] * 100)}%"
            elif option == "Volumen BGM":
                label += f": {int(settings['volume_bgm'] * 100)}%"
            elif option == "Volumen SFX":
                label += f": {int(settings['volume_sfx'] * 100)}%"
                
            draw_text(screen, label, 40, color, screen.get_width() // 2, 150 + i * 60)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                    sfx_cursor.play()

                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                    sfx_cursor.play()
                elif event.key == pygame.K_LEFT:
                    if options[selected] == "Volumen General":
                        settings['volume_general'] = max(0.0, settings['volume_general'] - 0.05)
                        # Actualizar volumen de música y SFX
                        actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
                        pygame.mixer.music.set_volume(actual_music_vol)
                        # Actualizar volumen de los SFX
                        sfx_cursor.set_volume(settings['volume_general'] * settings['volume_sfx'])
                        sfx_enter.set_volume(settings['volume_general'] * settings['volume_sfx'])
                        sfx_cursor.play()
                    elif options[selected] == "Volumen BGM":
                        settings['volume_bgm'] = max(0.0, settings['volume_bgm'] - 0.05)
                        # Actualizar volumen de música
                        actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
                        pygame.mixer.music.set_volume(actual_music_vol)
                        sfx_cursor.play()
                    elif options[selected] == "Volumen SFX":
                        settings['volume_sfx'] = max(0.0, settings['volume_sfx'] - 0.05)
                        # Actualizar volumen de los SFX
                        sfx_cursor.set_volume(settings['volume_general'] * settings['volume_sfx'])
                        sfx_enter.set_volume(settings['volume_general'] * settings['volume_sfx'])
                        sfx_cursor.play()
                elif event.key == pygame.K_RIGHT:
                    if options[selected] == "Volumen General":
                        settings['volume_general'] = min(1.0, settings['volume_general'] + 0.05)
                        # Actualizar volumen de música y SFX
                        actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
                        pygame.mixer.music.set_volume(actual_music_vol)
                        # Actualizar volumen de los SFX
                        sfx_cursor.set_volume(settings['volume_general'] * settings['volume_sfx'])
                        sfx_enter.set_volume(settings['volume_general'] * settings['volume_sfx'])
                        sfx_cursor.play()
                    elif options[selected] == "Volumen BGM":
                        settings['volume_bgm'] = min(1.0, settings['volume_bgm'] + 0.05)
                        # Actualizar volumen de música
                        actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
                        pygame.mixer.music.set_volume(actual_music_vol)
                        sfx_cursor.play()
                    elif options[selected] == "Volumen SFX":
                        settings['volume_sfx'] = min(1.0, settings['volume_sfx'] + 0.05)
                        # Actualizar volumen de los SFX
                        sfx_cursor.set_volume(settings['volume_general'] * settings['volume_sfx'])
                        sfx_enter.set_volume(settings['volume_general'] * settings['volume_sfx'])
                        sfx_cursor.play()
                elif event.key == pygame.K_RETURN:
                    sfx_enter.play()
                    if options[selected] not in ["Volumen General", "Volumen BGM", "Volumen SFX"]:
                        return options[selected].lower().replace(" ", "_")

        clock.tick(60)

class TetrisRenderer:
    def __init__(self, screen, block_size=30):
        self.screen = screen
        self.block_size = block_size
        
        # Cargar sprites
        self.sprite_sheet = pygame.image.load("assets/img/sprites.png")
        
        # Tamaño de cada sprite en la hoja de sprites
        self.sprite_size = 30  # Tamaño estándar de los sprites
        
        # Crear diccionario de sprites de bloques
        self.block_sprites = {}
        self.background = None
        self.extract_sprites()
        
        # Calcular offset para centrar el campo de juego
        screen_width, screen_height = screen.get_size()
        game_width = 10 * block_size  # 10 columnas del campo de juego
        game_height = 20 * block_size  # 20 filas del campo de juego
        self.offset_x = (screen_width - game_width) // 2
        self.offset_y = (screen_height - game_height) // 2
    
    def extract_sprites(self):
        """Extrae los sprites individuales de la hoja de sprites"""
        # Extraer los sprites de bloques (suponiendo que están en la primera fila)
        for i in range(8):  # 0 (vacío) + 7 colores de tetraminos
            # Obtener el rectángulo del sprite en la hoja
            sprite_rect = pygame.Rect(i * self.sprite_size, 0, self.sprite_size, self.sprite_size)
            
            # Crear una nueva superficie para el sprite
            block_sprite = pygame.Surface((self.sprite_size, self.sprite_size), pygame.SRCALPHA)
            
            # Copiar el sprite de la hoja a la nueva superficie
            block_sprite.blit(self.sprite_sheet, (0, 0), sprite_rect)
            
            # Guardar el sprite en el diccionario
            self.block_sprites[i] = block_sprite
        
        # También extraer el fondo del nivel (suponiendo que está en otra parte del sprite sheet)
        # Por ahora, simplemente crear un fondo negro
        self.background = pygame.Surface((10 * self.block_size, 20 * self.block_size))
        self.background.fill((20, 20, 40))  # Color de fondo oscuro para el campo de juego
    
    def draw_block(self, x, y, block_type, alpha=255, offset_x=0, offset_y=0):
        """Dibuja un bloque del tipo especificado en la posición (x,y) del campo"""
        if block_type >= 0 and block_type < len(self.block_sprites):
            # Obtener el sprite del bloque
            sprite = self.block_sprites[block_type]
            
            # Si se requiere transparencia
            if alpha < 255:
                sprite_copy = sprite.copy()
                sprite_copy.set_alpha(alpha)
                sprite = sprite_copy
            
            # Calcular la posición real en pantalla (incluyendo offset de efectos visuales)
            screen_x = self.offset_x + x * self.block_size + offset_x
            screen_y = self.offset_y + y * self.block_size + offset_y
            
            # Dibujar el sprite
            self.screen.blit(sprite, (screen_x, screen_y))
    
    def draw_field(self, game, highlight_lines=None, offset_x=0, offset_y=0):
        """Dibuja el campo de juego completo, resaltando líneas si se anima"""
        self.screen.blit(self.background, (self.offset_x + offset_x, self.offset_y + offset_y))
        
        for y in range(game.height):
            for x in range(game.width):
                block = game.field[y][x]
                if block != 0:
                    if highlight_lines and y in highlight_lines:
                        self.draw_block(x, y, block, alpha=120, offset_x=offset_x, offset_y=offset_y)  # Efecto visual tenue
                    else:
                        self.draw_block(x, y, block, offset_x=offset_x, offset_y=offset_y)
    
    def draw_current_piece(self, game, offset_x=0, offset_y=0):
        """Dibuja la pieza activa"""
        if game.game_over:
            return
            
        # Obtener la forma de la pieza activa
        shape = game.get_piece_shape()
        piece_type = game.get_piece_type()
        
        # Dibujar la posición fantasma (donde caería la pieza)
        ghost_y = game.get_ghost_position()
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col] != 0:
                    self.draw_block(game.piece_x + col, ghost_y + row, piece_type, alpha=80, offset_x=offset_x, offset_y=offset_y)  # Semi-transparente
        
        # Dibujar la pieza activa
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col] != 0:
                    self.draw_block(game.piece_x + col, game.piece_y + row, piece_type, offset_x=offset_x, offset_y=offset_y)
    
    def draw_next_piece(self, game, x, y):
        """Dibuja la próxima pieza centrada en una posición específica (4x4)"""
        if game.next_piece_type is None:
            return

        shape = game.next_piece_shape
        piece_type = game.next_piece_type + 1

        # Calcular dimensiones reales de la pieza
        rows = len(shape)
        cols = len(shape[0])
        min_x, min_y = 4, 4
        max_x, max_y = 0, 0

        for row in range(rows):
            for col in range(cols):
                if shape[row][col] != 0:
                    min_x = min(min_x, col)
                    max_x = max(max_x, col)
                    min_y = min(min_y, row)
                    max_y = max(max_y, row)

        width = max_x - min_x + 1
        height = max_y - min_y + 1

        # Centrar la pieza dentro del recuadro de 4x4
        offset_x = (4 - width) // 2
        offset_y = (4 - height) // 2

        for row in range(rows):
            for col in range(cols):
                if shape[row][col] != 0:
                    screen_x = x + (col - min_x + offset_x) * self.block_size
                    screen_y = y + (row - min_y + offset_y) * self.block_size
                    self.screen.blit(self.block_sprites[piece_type], (screen_x, screen_y))


def start_game(screen, settings):
    clock = pygame.time.Clock()
    pygame.mixer.music.load("assets/bgm/tetris.mp3")
    
    # Aplicar los ajustes de volumen
    actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
    pygame.mixer.music.set_volume(actual_music_vol)
    
    if not settings['mute']:
        pygame.mixer.music.play(-1)

    # Cargar efecto de pausa y otros efectos de sonido
    sfx_pause = pygame.mixer.Sound("assets/bgm/sfx/pause.wav")
    sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
    sfx_pause.set_volume(sfx_vol)
    
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
    
    # Cargar efectos de sonido del juego
    sfx_move = pygame.mixer.Sound("assets/bgm/sfx/move.wav")  # Movimiento de pieza
    sfx_rotate = pygame.mixer.Sound("assets/bgm/sfx/rotate.wav")  # Rotación de pieza
    sfx_hard_drop = pygame.mixer.Sound("assets/bgm/sfx/landing.wav")   # Aterrizaje con espacio (hard drop)
    sfx_soft_drop = pygame.mixer.Sound("assets/bgm/sfx/softdrop.wav")   # Aterrizaje sin espacio (soft drop)
    sfx_single = pygame.mixer.Sound("assets/bgm/sfx/single.wav")   # Sonido al hacer una línea
    sfx_tetris = pygame.mixer.Sound("assets/bgm/sfx/tetris.wav")   # Sonido al hacer una linea de 4 (tetris)
    sfx_drop = sfx_hard_drop  # Mantener compatibilidad con código existente
    
    # Ajustar volumen de todos los efectos
    sfx_move.set_volume(sfx_vol)
    sfx_rotate.set_volume(sfx_vol)
    sfx_hard_drop.set_volume(sfx_vol)
    sfx_soft_drop.set_volume(sfx_vol)
    sfx_single.set_volume(sfx_vol)
    sfx_tetris.set_volume(sfx_vol)
    sfx_drop.set_volume(sfx_vol)
    
    # Cargar efectos de sonido del juego
    sfx_move = pygame.mixer.Sound("assets/bgm/sfx/move.wav")  
    
    # Movimiento de pieza
    sfx_rotate = pygame.mixer.Sound("assets/bgm/sfx/rotate.wav")  # Rotación de pieza
    sfx_hard_drop = pygame.mixer.Sound("assets/bgm/sfx/landing.wav")   # Aterrizaje con espacio (hard drop)
    sfx_soft_drop = pygame.mixer.Sound("assets/bgm/sfx/softdrop.wav")   # Aterrizaje sin espacio (soft drop)
    sfx_single = pygame.mixer.Sound("assets/bgm/sfx/single.wav")   # Sonido al hacer una línea
    sfx_tetris = pygame.mixer.Sound("assets/bgm/sfx/tetris.wav")   # Sonido al hacer una linea de 4 (tetris)
    sfx_drop = sfx_hard_drop  # Mantener compatibilidad con código existente
    
    # Ajustar volumen de todos los efectos
    sfx_move.set_volume(sfx_vol)
    sfx_rotate.set_volume(sfx_vol)
    sfx_hard_drop.set_volume(sfx_vol)
    sfx_soft_drop.set_volume(sfx_vol)
    sfx_single.set_volume(sfx_vol)
    sfx_tetris.set_volume(sfx_vol)
    sfx_drop.set_volume(sfx_vol)  # Para compatibilidad con código existente
    
    while running:
        current_time = time.time()
        screen.fill((0, 0, 0))  # Limpiar pantalla
        
        # Manejar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sfx_pause.play()
                    paused = True
                    choice = pause_menu(screen, settings)
                    paused = False
                    if choice == "reintentar":
                        # Reiniciar juego
                        game = TetrisGame()
                        start_game(screen, settings)
                        return
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
                
                # Controles del juego
                if not paused and not game.game_over:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        if game.move_left():
                            sfx_move.play()
                        das_left_pressed = True
                        das_left_start = pygame.time.get_ticks()

                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        if game.move_right():
                            sfx_move.play()
                        das_right_pressed = True
                        das_right_start = pygame.time.get_ticks()
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        if game.rotate():
                            sfx_rotate.play()
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if game.move_down():
                            # Usar explícitamente softdrop.wav para soft drop
                            sfx_soft_drop = pygame.mixer.Sound("assets/bgm/sfx/softdrop.wav")
                            sfx_soft_drop.set_volume(sfx_vol)
                            sfx_soft_drop.play()
                        das_down_pressed = True
                        das_down_start = pygame.time.get_ticks()
                    elif event.key == pygame.K_c:
                        if not paused and not game.game_over:
                            game.hold_piece()
                    elif event.key == pygame.K_SPACE:
                        # Primero verificar si el juego ya terminó
                        if not game.game_over:
                            game.drop()
                            # Usar explícitamente harddrop.wav para hard drop
                            sfx_hard_drop = pygame.mixer.Sound("assets/bgm/sfx/harddrop.wav")
                            sfx_hard_drop.set_volume(sfx_vol)
                            sfx_hard_drop.play()
                            
                            # Fijar pieza y comprobar líneas
                            line_clear_result = game.fix_piece()
                            
                            # Reproducir sonido de eliminación de líneas si corresponde
                            if line_clear_result:
                                if line_clear_result["is_tetris"]:
                                    sfx_tetris.play()
                                elif line_clear_result["count"] > 0:
                                    sfx_single.play()
                                    
                            last_move_down_time = current_time  # Resetear tiempo tras hard drop
            
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    das_down_pressed = False    
                if event.key in [pygame.K_LEFT, pygame.K_a]:
                    das_left_pressed = False
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    das_right_pressed = False
        
        if not paused and not game.game_over:
            # Movimiento automático hacia abajo
            move_delay = game.game_speed
            if current_time - last_move_down_time > move_delay / 1000.0:  # Convertir a segundos
                if not game.move_down():
                    if game.should_lock():
                        sfx_soft_drop.play()
                        
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
            anim_duration = 200  # ms
            elapsed = now - game.clear_animation_time

            # Dibujar el fondo dinámico
            dynamic_background.draw(screen)
            
            # Dibujar el campo con líneas atenuadas
            renderer.draw_field(game, highlight_lines=game.lines_to_clear)
            renderer.draw_current_piece(game)  # para que no desaparezca
            
            # Crear partículas para las líneas que se eliminarán
            if elapsed < 50:  # Solo añadir partículas en la primera parte de la animación
                block_size = renderer.block_size
                for line in game.lines_to_clear:
                    for x in range(game.width):
                        block_type = game.field[line][x]
                        if block_type != 0:
                            # Obtener color del bloque
                            color = COLORS[block_type]
                            # Añadir partículas en la posición del bloque
                            particle_system.add_particles_for_line_clear(
                                x * block_size, 
                                line * block_size, 
                                block_size,
                                color,
                                count=5  # 5 partículas por bloque
                            )
            
            # Actualizar y dibujar partículas
            particle_system.update()
            particle_system.draw(screen, renderer.offset_x, renderer.offset_y)
            
            if elapsed >= anim_duration:
                # Si se hizo un tetris, aplicar efecto de temblor de pantalla
                if len(game.lines_to_clear) == 4:
                    screen_shake.start_shake(5, 20)  # Intensidad 5, duración 20 frames
                    
                # Actualizar animador de combo si hubo líneas eliminadas
                combo_animator.add_combo(len(game.lines_to_clear))
                
                game.finish_clear_animation()
                game.new_piece()

            # Mostrar frame y detener avance hasta terminar animación
            pygame.display.flip()
            clock.tick(60)
            continue

        # DAS movimiento continuo
        if das_left_pressed:
            elapsed = now - das_left_start
            if elapsed >= DAS_DELAY and (elapsed - DAS_DELAY) % ARR_INTERVAL < clock.get_time():
                if game.move_left():
                    sfx_move.play()

        if das_right_pressed:
            elapsed = now - das_right_start
            if elapsed >= DAS_DELAY and (elapsed - DAS_DELAY) % ARR_INTERVAL < clock.get_time():
                if game.move_right():
                    sfx_move.play()

        if das_down_pressed:
            elapsed = now - das_down_start
            if elapsed >= DAS_DELAY and (elapsed - DAS_DELAY) % ARR_INTERVAL < clock.get_time():
                if game.move_down():
                    # Usar explícitamente softdrop.wav para soft drop
                    sfx_soft_drop = pygame.mixer.Sound("assets/bgm/sfx/softdrop.wav")
                    sfx_soft_drop.set_volume(sfx_vol)
                    sfx_soft_drop.play()

        # Actualizar el fondo dinámico según el nivel
        dynamic_background.update(game.level)
        
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
        
        # Recuadro de próxima pieza (4x4)
        next_piece_x = renderer.offset_x + renderer.block_size * 12
        next_piece_y = renderer.offset_y + renderer.block_size * 2

        pygame.draw.rect(screen, (80, 80, 80),
            (next_piece_x - 5, next_piece_y - 5, renderer.block_size * 4 + 10, renderer.block_size * 4 + 10),
            2)
        draw_text(screen, "Next", 20, WHITE, next_piece_x + renderer.block_size * 2, next_piece_y - 20)

        # Dibujar próxima pieza
        renderer.draw_next_piece(game, next_piece_x, next_piece_y)

        # Recuadro de Hold (máximo 4x4)
        hold_x = renderer.offset_x - renderer.block_size * 5  # Ajustar para que no toque el área de juego
        hold_y = renderer.offset_y + renderer.block_size * 2

        pygame.draw.rect(screen, (80, 80, 80),
            (hold_x - 5, hold_y - 5, renderer.block_size * 4 + 10, renderer.block_size * 4 + 10),
            2)
        draw_text(screen, "Hold", 20, WHITE, hold_x + renderer.block_size * 2, hold_y - 20)

        # Dibujar pieza Hold si existe
        if game.hold_piece_type is not None:
            shape = SHAPES[game.hold_piece_type][0]
            piece_type = game.hold_piece_type + 1

            rows = len(shape)
            cols = len(shape[0])
            min_x, min_y = 4, 4
            max_x, max_y = 0, 0

            for row in range(rows):
                for col in range(cols):
                    if shape[row][col] != 0:
                        min_x = min(min_x, col)
                        max_x = max(max_x, col)
                        min_y = min(min_y, row)
                        max_y = max(max_y, row)

            width = max_x - min_x + 1
            height = max_y - min_y + 1

            offset_x = (4 - width) // 2
            offset_y = (4 - height) // 2

            for row in range(rows):
                for col in range(cols):
                    if shape[row][col] != 0:
                        screen.blit(renderer.block_sprites[piece_type],
                                    (hold_x + (col - min_x + offset_x) * renderer.block_size,
                                    hold_y + (row - min_y + offset_y) * renderer.block_size))

        
        # Dibujar puntuación, nivel y líneas
        score_y = next_piece_y + renderer.block_size * 6
        draw_text(screen, f"Puntuación: {game.score}", 24, WHITE, next_piece_x + renderer.block_size * 3, score_y)
        draw_text(screen, f"Nivel: {game.level}", 24, WHITE, next_piece_x + renderer.block_size * 3, score_y + 30)
        draw_text(screen, f"Líneas: {game.lines_cleared}", 24, WHITE, next_piece_x + renderer.block_size * 3, score_y + 60)
        
        # Dibujar controles
        controls_y = score_y + 120
        draw_text(screen, "Controles:", 20, WHITE, next_piece_x + renderer.block_size * 3, controls_y)
        draw_text(screen, "←/→: Mover", 18, GRAY, next_piece_x + renderer.block_size * 3, controls_y + 25)
        draw_text(screen, "↑: Rotar", 18, GRAY, next_piece_x + renderer.block_size * 3, controls_y + 45)
        draw_text(screen, "↓: Caída rápida", 18, GRAY, next_piece_x + renderer.block_size * 3, controls_y + 65)
        draw_text(screen, "Espacio: Soltar", 18, GRAY, next_piece_x + renderer.block_size * 3, controls_y + 85)
        draw_text(screen, "ESC: Pausar", 18, GRAY, next_piece_x + renderer.block_size * 3, controls_y + 105)
        


        # Si el juego ha terminado, mostrar pantalla de Game Over
        if game.game_over:
            # Reproducir sonido de Game Over si no se ha reproducido ya
            if not hasattr(game, "gameover_sound_played"):
                sfx_gameover = pygame.mixer.Sound("assets/bgm/sfx/gameover.wav")
                sfx_gameover.set_volume(sfx_vol)
                sfx_gameover.play()
                game.gameover_sound_played = True
            
            # Dibujar un panel semi-transparente
            overlay = pygame.Surface((screen.get_width(), screen.get_height()))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            center_x = screen.get_width() // 2
            center_y = screen.get_height() // 2
            
            draw_text(screen, "¡GAME OVER!", 48, WHITE, center_x, center_y - 50)
            draw_text(screen, f"Puntuación final: {game.score}", 30, WHITE, center_x, center_y)
            draw_text(screen, "ESC para volver al menú", 24, WHITE, center_x, center_y + 50)
            draw_text(screen, "ENTER para reintentar", 24, WHITE, center_x, center_y + 80)
            
            # Esperar a que el jugador decida qué hacer
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("assets/bgm/menu.mp3")
                        actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
                        pygame.mixer.music.set_volume(actual_music_vol)
                        if not settings['mute']:
                            pygame.mixer.music.play(-1)
                        return
                    elif event.key == pygame.K_RETURN:
                        start_game(screen, settings)
                        return
        


        pygame.display.flip()
        clock.tick(60)

    pygame.mixer.music.stop()