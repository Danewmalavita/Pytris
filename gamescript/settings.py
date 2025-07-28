# settings.py

# Resoluciones disponibles
resol = {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080)
}

def init_settings():
    # Configuración por defecto
    return {
        'resolution': resol["720p"],      # Por defecto 720p
        'resolution_label': "720p",
        'volume_general': 1.0,           # Volumen general por defecto 100%
        'volume_bgm': 0.75,              # Volumen música por defecto 75%
        'volume_sfx': 0.85,              # Volumen efectos por defecto 85%
        'mute': False                    # Silenciar todo
    }
