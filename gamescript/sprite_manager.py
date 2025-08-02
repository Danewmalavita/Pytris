# sprite_manager.py
# Módulo para gestionar y precargar recursos gráficos del juego Tetris

import pygame
import os
from .debug_utils import debugger

class SpriteManager:
    """
    Gestor central de sprites para cargar y proporcionar todos los recursos gráficos del juego.
    Precarga todos los sprites durante la inicialización para mejorar el rendimiento.
    """
    def __init__(self):
        self.sprites = {}  # Diccionario para almacenar todos los sprites
        self.block_sprites = {}  # Sprites específicos de los bloques
        self.ui_elements = {}  # Elementos de interfaz como marcos, botones, etc.
        self.backgrounds = {}  # Fondos y texturas
        self.loaded = False  # Indicador de si los sprites ya están cargados
    
    def preload_resources(self):
        """
        Precarga todos los recursos gráficos para evitar retrasos durante el juego.
        """
        if self.loaded:
            debugger.debug("Los sprites ya están cargados.")
            return True
            
        debugger.debug("Iniciando precarga de recursos gráficos...")
        start_time = pygame.time.get_ticks()
        
        try:
            # Precargar sprites básicos de bloques
            self._preload_block_sprites()
            
            # Precargar elementos de UI
            self._preload_ui_elements()
            
            # Precargar fondos y texturas
            self._preload_backgrounds()
            
            self.loaded = True
            end_time = pygame.time.get_ticks()
            duration = (end_time - start_time) / 1000.0  # Convertir a segundos
            debugger.debug(f"Precarga de sprites completada en {duration:.2f} segundos.")
            return True
            
        except Exception as e:
            debugger.error(f"Error durante la precarga de sprites: {str(e)}")
            return False
    
    def _preload_block_sprites(self):
        """Precarga los sprites de bloques desde la hoja de sprites."""
        try:
            # Cargar la hoja de sprites principal
            sprite_sheet_path = "assets/img/sprites.png"
            if not os.path.exists(sprite_sheet_path):
                debugger.error(f"Hoja de sprites no encontrada: {sprite_sheet_path}")
                return False
                
            sprite_sheet = pygame.image.load(sprite_sheet_path)
            self.sprites["sprite_sheet"] = sprite_sheet
            
            # Tamaño de cada sprite en la hoja
            sprite_size = 30
            
            # Extraer los sprites de bloques individuales
            for i in range(8):  # 0 (vacío) + 7 colores de tetrominos
                sprite_rect = pygame.Rect(i * sprite_size, 0, sprite_size, sprite_size)
                block_sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
                block_sprite.blit(sprite_sheet, (0, 0), sprite_rect)
                self.block_sprites[i] = block_sprite
                
            debugger.debug(f"Cargados {len(self.block_sprites)} sprites de bloques.")
            return True
            
        except Exception as e:
            debugger.error(f"Error al precargar sprites de bloques: {str(e)}")
            return False
    
    def _preload_ui_elements(self):
        """Precarga elementos de interfaz de usuario como marcos, botones, etc."""
        ui_elements = {
            "board_frame": "assets/img/boardframe.png",
            "hold_frame": "assets/img/holdframe.png",
            "next_frame": "assets/img/nextframe.png",
            # Agregar más elementos UI aquí según sea necesario
        }
        
        for name, path in ui_elements.items():
            try:
                if os.path.exists(path):
                    self.ui_elements[name] = pygame.image.load(path)
                    debugger.debug(f"Cargado elemento UI: {name}")
                else:
                    debugger.warning(f"Elemento UI no encontrado: {path}")
            except Exception as e:
                debugger.error(f"Error al cargar elemento UI {name}: {str(e)}")
        
        debugger.debug(f"Cargados {len(self.ui_elements)} elementos de UI.")
    
    def _preload_backgrounds(self):
        """Precarga fondos y texturas."""
        backgrounds = {
            "main_bg": "assets/img/mainbg.jpg",
            "tile_bg": "assets/img/bgtile.png",
            # Agregar más fondos aquí según sea necesario
        }
        
        for name, path in backgrounds.items():
            try:
                if os.path.exists(path):
                    self.backgrounds[name] = pygame.image.load(path)
                    debugger.debug(f"Cargado fondo: {name}")
                else:
                    debugger.warning(f"Fondo no encontrado: {path}")
            except Exception as e:
                debugger.error(f"Error al cargar fondo {name}: {str(e)}")
        
        debugger.debug(f"Cargados {len(self.backgrounds)} fondos y texturas.")
    
    def get_block_sprite(self, block_type):
        """
        Obtiene el sprite de un bloque específico.
        
        Args:
            block_type (int): Tipo de bloque (0-7)
            
        Returns:
            pygame.Surface: Sprite del bloque
        """
        if block_type in self.block_sprites:
            return self.block_sprites[block_type]
        return None
    
    def get_ui_element(self, name):
        """
        Obtiene un elemento de UI por nombre.
        
        Args:
            name (str): Nombre del elemento
            
        Returns:
            pygame.Surface: Sprite del elemento UI
        """
        if name in self.ui_elements:
            return self.ui_elements[name]
        
        # Intenta cargar bajo demanda si no está precargado
        try:
            path = f"assets/img/{name}.png"
            if os.path.exists(path):
                element = pygame.image.load(path)
                self.ui_elements[name] = element
                return element
        except Exception as e:
            debugger.error(f"Error al cargar elemento UI bajo demanda '{name}': {str(e)}")
        
        return None
    
    def get_background(self, name):
        """
        Obtiene un fondo por nombre.
        
        Args:
            name (str): Nombre del fondo
            
        Returns:
            pygame.Surface: Imagen del fondo
        """
        if name in self.backgrounds:
            return self.backgrounds[name]
        
        # Intenta cargar bajo demanda si no está precargado
        extensions = ['.jpg', '.png']
        for ext in extensions:
            try:
                path = f"assets/img/{name}{ext}"
                if os.path.exists(path):
                    background = pygame.image.load(path)
                    self.backgrounds[name] = background
                    return background
            except Exception:
                pass
                
        debugger.warning(f"Fondo no encontrado: {name}")
        return None

# Crear una instancia global del gestor de sprites
sprite_manager = SpriteManager()