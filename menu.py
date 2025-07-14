# menu.py
import pygame
from options import options_menu
from settings import resol
# Import start_game conditionally to avoid circular import
# game will be imported when needed

def draw_text(surface, text, size, color, x, y):
    font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def main_menu(screen, settings):
    clock = pygame.time.Clock()
    
    # Importar el módulo de controles
    from controls import handle_main_menu_controls
    
    # Comprobar si el audio está disponible
    audio_available = pygame.mixer.get_init() is not None
    
    # Configuración de audio solo si está disponible
    if audio_available:
        try:
            pygame.mixer.music.load("assets/bgm/menu.mp3")
            
            # Aplicar los ajustes de volumen
            actual_music_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_bgm'])
            pygame.mixer.music.set_volume(actual_music_vol)
            
            if not settings['mute']:
                pygame.mixer.music.play(-1)
                
            # Cargar efectos de sonido
            sfx_cursor = pygame.mixer.Sound("assets/bgm/sfx/cursor.wav")
            sfx_enter = pygame.mixer.Sound("assets/bgm/sfx/enter.wav")
            sfx_back = pygame.mixer.Sound("assets/bgm/sfx/back.wav")
            
            # Ajustar volumen de efectos de sonido según la configuración
            sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
            sfx_cursor.set_volume(sfx_vol)
            sfx_enter.set_volume(sfx_vol)
            sfx_back.set_volume(sfx_vol)
        except (pygame.error, FileNotFoundError):
            audio_available = False
            settings['mute'] = True
    else:
        settings['mute'] = True
        
    # Crear objetos nulos para los efectos si no hay audio
    if not audio_available:
        class DummySound:
            def play(self): pass
            def set_volume(self, vol): pass
            
        sfx_cursor = DummySound()
        sfx_enter = DummySound()
        sfx_back = DummySound()

    menu_items = ["Modo Arcade", "Puntuaciones", "Opciones", "Salir"]
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
            
            # Usar el módulo de controles unificado
            selected, action, exit_flag = handle_main_menu_controls(
                event, selected, menu_items, sfx_cursor, sfx_enter, sfx_back
            )
            
            if exit_flag:
                if pygame.mixer.get_init() is not None:
                    pygame.time.wait(100)  # Pequeña pausa para permitir que suene el efecto
                running = False
                
            if action:
                if pygame.mixer.get_init() is not None:
                    pygame.time.wait(100)  # Pequeña pausa para permitir que suene el efecto
                
                if action == "modo_arcade":
                    if pygame.mixer.get_init() is not None:
                        pygame.mixer.music.stop()
                    from game import start_game
                    start_game(screen, settings)
                elif action == "puntuaciones":
                    # Import here to avoid circular import
                    from highscore import show_high_scores
                    show_high_scores(screen, settings)
                elif action == "opciones":
                    options_menu(screen, settings)

        clock.tick(60)

    # Stop music only if mixer is available
    if pygame.mixer.get_init() is not None:
        pygame.mixer.music.stop()
