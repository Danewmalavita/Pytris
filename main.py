import pygame
import sys
from menu import main_menu
from settings import init_settings
from controls import initialize_controls

def main():
    pygame.init()
    
    # Try to initialize mixer, but continue even if it fails
    try:
        pygame.mixer.init()
        audio_available = True
    except pygame.error:
        print("Warning: Audio initialization failed. Game will run without sound.")
        audio_available = False

    # Inicializar configuraciones
    settings = init_settings()
    
    # If audio isn't available, ensure mute setting is on
    if not audio_available:
        settings['mute'] = True
        
    # Inicializar los controles (gamepads y joysticks)
    initialize_controls()

    # Configurar la ventana con la resolución seleccionada
    screen = pygame.display.set_mode(settings['resolution'])
    pygame.display.set_caption("PyTris")

    # Lanzar el menú principal
    main_menu(screen, settings)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
