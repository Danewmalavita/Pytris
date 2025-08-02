import pygame
import sys
import time
from gamescript.menu import main_menu
from gamescript.settings import init_settings
from gamescript.controls import initialize_controls
from gamescript.audio_manager import audio_manager
from gamescript.sprite_manager import sprite_manager
from gamescript.debug_utils import debugger


def load_splash_screen(screen):
    """Muestra una pantalla de carga mientras se precargan los recursos."""
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont("Arial", 32)
    text = font.render("Cargando recursos...", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()


def preload_resources(screen):
    """Precarga todos los recursos del juego."""
    load_splash_screen(screen)
    
    start_time = time.time()
    debugger.debug("Iniciando precarga de recursos...")
    
    # Precargar sprites
    sprite_manager.preload_resources()
    
    # Precargar audio
    audio_manager.preload_resources()
    
    elapsed = time.time() - start_time
    debugger.debug(f"Precarga de recursos completada en {elapsed:.2f} segundos")


def main():
    pygame.init()
    
    # Configurar el debugger para mostrar solo errores y advertencias
    debugger.production_mode()
    
    # Inicializar sistema de audio con múltiples intentos de configuración
    audio_available = False
    
    # Intentar diferentes configuraciones de audio en caso de fallo
    audio_configs = [
        {'frequency': 44100, 'size': -16, 'channels': 2, 'buffer': 512},  # Configuración original
        {'frequency': 44100, 'size': -16, 'channels': 1, 'buffer': 1024}, # Mono con buffer mayor
        {'frequency': 22050, 'size': -16, 'channels': 2, 'buffer': 1024}, # Frecuencia menor
        {'frequency': 22050, 'size': -16, 'channels': 1, 'buffer': 2048}, # Configuración mínima
        {}  # Dejar que pygame use valores predeterminados
    ]
    
    for config in audio_configs:
        try:
            debugger.debug(f"Intentando inicializar audio con configuración: {config}")
            pygame.mixer.quit()  # Asegurar que no haya inicialización previa
            pygame.mixer.init(**config)
            
            # Verificar que el mixer realmente esté inicializado
            if pygame.mixer.get_init() is not None:
                debugger.info(f"Audio inicializado correctamente con: {config}")
                audio_available = True
                break
        except Exception as e:
            debugger.warning(f"Falló inicialización de audio con {config}: {str(e)}")
    
    if not audio_available:
        debugger.warning("No se pudo inicializar el audio. El juego se ejecutará sin sonido.")

    # Inicializar configuración y controles
    settings = init_settings()
    if not audio_available:
        settings['mute'] = True
        
    initialize_controls()

    # Configurar ventana del juego
    screen = pygame.display.set_mode(settings['resolution'])
    pygame.display.set_caption("PyTris 2.0")
    
    # Precargar recursos (sprites, audio, etc.)
    preload_resources(screen)
    
    # Configurar el gestor de audio según las configuraciones
    audio_manager.set_master_volume(settings['volume_general'])
    audio_manager.set_music_volume(settings['volume_bgm'])
    audio_manager.set_sfx_volume(settings['volume_sfx'])
    audio_manager.set_mute(settings['mute'])
    
    # Iniciar el juego con el menú principal
    main_menu(screen, settings)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
