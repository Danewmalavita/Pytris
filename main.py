import pygame
import sys
from menu import main_menu
from settings import init_settings

def main():
    pygame.init()
    pygame.mixer.init()

    # Inicializar configuraciones
    settings = init_settings()

    # Configurar la ventana con la resolución seleccionada
    screen = pygame.display.set_mode(settings['resolution'])
    pygame.display.set_caption("PyTris")

    # Lanzar el menú principal
    main_menu(screen, settings)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
