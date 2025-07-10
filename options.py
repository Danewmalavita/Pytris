# options.py
import pygame
from settings import resol

def draw_text(surface, text, size, color, x, y):
    font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def options_menu(screen, settings):
    clock = pygame.time.Clock()
    
    # Cargar efectos de sonido
    sfx_cursor = pygame.mixer.Sound("assets/bgm/sfx/cursor.wav")
    sfx_enter = pygame.mixer.Sound("assets/bgm/sfx/enter.wav")
    
    # Ajustar volumen de efectos de sonido según la configuración
    sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
    sfx_cursor.set_volume(sfx_vol)
    sfx_enter.set_volume(sfx_vol)

    options = ["Volumen General", "Volumen BGM", "Volumen SFX", "Mute", "Resolución", "Volver"]
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
                        # Actualizar volumen de los SFX
                        sfx_cursor.set_volume(settings['volume_general'] * settings['volume_sfx'])
                        sfx_enter.set_volume(settings['volume_general'] * settings['volume_sfx'])
                        sfx_cursor.play()
                    elif options[selected] == "Volumen BGM":
                        settings['volume_bgm'] = max(0.0, settings['volume_bgm'] - 0.05)
                        sfx_cursor.play()
                    elif options[selected] == "Volumen SFX":
                        settings['volume_sfx'] = max(0.0, settings['volume_sfx'] - 0.05)
                        # Actualizar volumen de los SFX
                        sfx_cursor.set_volume(settings['volume_general'] * settings['volume_sfx'])
                        sfx_enter.set_volume(settings['volume_general'] * settings['volume_sfx'])
                        sfx_cursor.play()
                    elif options[selected] == "Resolución":
                        current_res_index = (current_res_index - 1) % len(resolution_keys)
                        sfx_cursor.play()
                elif event.key == pygame.K_RIGHT:
                    if options[selected] == "Volumen General":
                        settings['volume_general'] = min(1.0, settings['volume_general'] + 0.05)
                        # Actualizar volumen de los SFX
                        sfx_cursor.set_volume(settings['volume_general'] * settings['volume_sfx'])
                        sfx_enter.set_volume(settings['volume_general'] * settings['volume_sfx'])
                        sfx_cursor.play()
                    elif options[selected] == "Volumen BGM":
                        settings['volume_bgm'] = min(1.0, settings['volume_bgm'] + 0.05)
                        sfx_cursor.play()
                    elif options[selected] == "Volumen SFX":
                        settings['volume_sfx'] = min(1.0, settings['volume_sfx'] + 0.05)
                        # Actualizar volumen de los SFX
                        sfx_cursor.set_volume(settings['volume_general'] * settings['volume_sfx'])
                        sfx_enter.set_volume(settings['volume_general'] * settings['volume_sfx'])
                        sfx_cursor.play()
                    elif options[selected] == "Resolución":
                        current_res_index = (current_res_index + 1) % len(resolution_keys)
                        sfx_cursor.play()
                elif event.key == pygame.K_RETURN:
                    sfx_enter.play()
                    if options[selected] == "Mute":
                        settings['mute'] = not settings['mute']
                        # Actualizar inmediatamente el volumen de los SFX
                        sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
                        sfx_cursor.set_volume(sfx_vol)
                        sfx_enter.set_volume(sfx_vol)
                    elif options[selected] == "Volver":
                        # Aplicar cambios
                        settings['resolution_label'] = resolution_keys[current_res_index]
                        settings['resolution'] = resol[settings['resolution_label']]
                        screen = pygame.display.set_mode(settings['resolution'])
                        return

        # Aplicar los ajustes de volumen a la música
        actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
        pygame.mixer.music.set_volume(actual_music_vol)
        clock.tick(60)