# menu.py
import pygame
from game import start_game
from options import options_menu
from settings import resol

def draw_text(surface, text, size, color, x, y):
    font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def main_menu(screen, settings):
    clock = pygame.time.Clock()
    pygame.mixer.music.load("assets/bgm/menu.mp3")
    
    # Aplicar los ajustes de volumen
    actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
    pygame.mixer.music.set_volume(actual_music_vol)
    
    if not settings['mute']:
        pygame.mixer.music.play(-1)
        
    # Cargar efectos de sonido
    sfx_cursor = pygame.mixer.Sound("assets/bgm/sfx/cursor.wav")
    sfx_enter = pygame.mixer.Sound("assets/bgm/sfx/enter.wav")
    
    # Ajustar volumen de efectos de sonido según la configuración
    sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
    sfx_cursor.set_volume(sfx_vol)
    sfx_enter.set_volume(sfx_vol)

    menu_items = ["Nuevo Juego", "Opciones", "Salir"]
    selected = 0

    running = True
    while running:
        screen.fill((10, 10, 50))

        for i, item in enumerate(menu_items):
            color = (255, 255, 255) if i == selected else (150, 150, 150)
            draw_text(screen, item, 48, color, screen.get_width() // 2, 200 + i * 80)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(menu_items)
                    sfx_cursor.play()
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(menu_items)
                    sfx_cursor.play()
                elif event.key == pygame.K_RETURN:
                    sfx_enter.play()
                    pygame.time.wait(100)  # Small delay to let the sound effect play before changing screens
                    if menu_items[selected] == "Nuevo Juego":
                        pygame.mixer.music.stop()
                        start_game(screen, settings)
                    elif menu_items[selected] == "Opciones":
                        options_menu(screen, settings)
                    elif menu_items[selected] == "Salir":
                        running = False

        clock.tick(60)

    pygame.mixer.music.stop()
