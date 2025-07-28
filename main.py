import pygame
import sys
from gamescript.menu import main_menu
from gamescript.settings import init_settings
from gamescript.controls import initialize_controls


def main():
    pygame.init()
    
    # Initialize audio with fallback
    try:
        pygame.mixer.init()
        audio_available = True
    except pygame.error:
        print("Warning: Audio initialization failed. Game will run without sound.")
        audio_available = False

    # Initialize settings and controls
    settings = init_settings()
    if not audio_available:
        settings['mute'] = True
        
    initialize_controls()

    # Set up the game window
    screen = pygame.display.set_mode(settings['resolution'])
    pygame.display.set_caption("PyTris")

    # Launch main menu
    main_menu(screen, settings)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
