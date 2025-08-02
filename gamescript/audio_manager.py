# audio_manager.py
# Módulo para gestionar y precargar recursos de audio del juego Tetris

import pygame
import os
from .debug_utils import debugger

class AudioManager:
    """
    Gestor central de audio para cargar y reproducir todos los sonidos del juego.
    Precarga todos los archivos de audio durante la inicialización para mejorar el rendimiento.
    """
    def __init__(self):
        self.music_tracks = {}  # Diccionario para almacenar las rutas de las pistas de música
        self.sound_effects = {}  # Diccionario para almacenar los efectos de sonido cargados
        self.current_track = None  # Pista de música actual
        self.sfx_volume = 1.0  # Volumen de efectos de sonido (0.0 a 1.0)
        self.music_volume = 1.0  # Volumen de música (0.0 a 1.0)
        self.master_volume = 1.0  # Volumen maestro (0.0 a 1.0)
        self.muted = False  # Estado de silencio
        
        # Verificar disponibilidad de audio de manera más robusta
        try:
            self.audio_available = pygame.mixer.get_init() is not None
            if not self.audio_available:
                debugger.warning("Audio no inicializado correctamente en AudioManager")
        except Exception as e:
            debugger.error(f"Error al verificar estado de audio: {str(e)}")
            self.audio_available = False

    def preload_resources(self):
        """
        Precarga todos los recursos de audio (música y efectos de sonido)
        para evitar retrasos durante el juego.
        """
        debugger.debug("Iniciando precarga de recursos de audio...")
        start_time = pygame.time.get_ticks()
        
        # Verificar el estado del audio
        self.audio_available = pygame.mixer.get_init() is not None
            
        if not self.audio_available:
            debugger.warning("Audio no disponible. No se cargarán recursos de audio.")
            return False
            
        try:
            # Verificar directorios de audio
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            bgm_dir = os.path.join(base_dir, "assets/sounds/bgm")
            sfx_dir = os.path.join(base_dir, "assets/sounds/sfx")
            
            if not os.path.exists(bgm_dir) or not os.path.exists(sfx_dir):
                debugger.error(f"Directorios de audio faltantes: BGM: {os.path.exists(bgm_dir)}, SFX: {os.path.exists(sfx_dir)}")
                return False
                
            # Precargar música de fondo
            self._preload_music()
            
            # Precargar efectos de sonido
            self._preload_sfx()
            
            end_time = pygame.time.get_ticks()
            duration = (end_time - start_time) / 1000.0  # Convertir a segundos
            debugger.debug(f"Precarga de audio completada en {duration:.2f} segundos.")
            return True
            
        except Exception as e:
            debugger.error(f"Error durante la precarga de audio: {str(e)}")
            self.audio_available = False
            return False
    
    def _get_assets_dir(self, type_dir):
        """
        Obtiene la ruta del directorio de recursos de audio.
        
        Args:
            type_dir (str): Tipo de directorio ('bgm' o 'sfx')
            
        Returns:
            str: Ruta absoluta al directorio de recursos
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, f"assets/sounds/{type_dir}")
    
    def _preload_music(self):
        """Precarga todas las pistas de música de fondo."""
        music_dir = self._get_assets_dir('bgm')
        if not os.path.exists(music_dir):
            debugger.error(f"Directorio de música no encontrado: {music_dir}")
            return
            
        try:
            # Escanear el directorio de música
            music_files = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.ogg', '.wav'))]
            debugger.debug(f"Encontrados {len(music_files)} archivos de música.")
            
            # Almacenar las rutas de los archivos (no cargamos los MP3 en memoria)
            for filename in music_files:
                track_name = os.path.splitext(filename)[0]  # Nombre sin extensión
                self.music_tracks[track_name] = os.path.join(music_dir, filename)
                debugger.debug(f"Música indexada: {track_name}")
                
        except Exception as e:
            debugger.error(f"Error al precargar música: {str(e)}")
    
    def _preload_sfx(self):
        """Precarga todos los efectos de sonido."""
        sfx_dir = self._get_assets_dir('sfx')
        if not os.path.exists(sfx_dir):
            debugger.error(f"Directorio de efectos de sonido no encontrado: {sfx_dir}")
            return
            
        try:
            # Escanear el directorio de efectos de sonido
            sfx_files = [f for f in os.listdir(sfx_dir) if f.endswith(('.wav', '.ogg'))]
            debugger.debug(f"Encontrados {len(sfx_files)} archivos de efectos de sonido.")
            
            # Cargar los efectos de sonido en memoria
            for filename in sfx_files:
                sfx_name = os.path.splitext(filename)[0]  # Nombre sin extensión
                try:
                    sound = pygame.mixer.Sound(os.path.join(sfx_dir, filename))
                    self.sound_effects[sfx_name] = sound
                    debugger.debug(f"Efecto de sonido cargado: {sfx_name}")
                except Exception as e:
                    debugger.error(f"Error al cargar el efecto {sfx_name}: {str(e)}")
        
        except Exception as e:
            debugger.error(f"Error al precargar efectos de sonido: {str(e)}")
    
    def play_music(self, track_name, loop=-1):
        """
        Reproduce una pista de música.
        
        Args:
            track_name (str): Nombre de la pista a reproducir (sin extensión)
            loop (int): Número de repeticiones (-1 para infinito)
        """
        if not self.audio_available or self.muted:
            return False
            
        try:
            if track_name in self.music_tracks:
                # Solo cargar y reproducir si es diferente a la pista actual
                if self.current_track != track_name:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(self.music_tracks[track_name])
                    actual_volume = self.master_volume * self.music_volume
                    pygame.mixer.music.set_volume(actual_volume)
                    pygame.mixer.music.play(loop)
                    self.current_track = track_name
                    return True
            else:
                debugger.warning(f"Pista de música no encontrada: {track_name}")
                return False
        except Exception as e:
            debugger.error(f"Error al reproducir música: {str(e)}")
            return False
    
    def stop_music(self):
        """Detiene la reproducción de música actual."""
        if not self.audio_available:
            return
            
        try:
            pygame.mixer.music.stop()
            self.current_track = None
        except Exception as e:
            debugger.error(f"Error al detener música: {str(e)}")
    
    def play_sound(self, sound_name):
        """
        Reproduce un efecto de sonido.
        
        Args:
            sound_name (str): Nombre del efecto de sonido a reproducir
            
        Returns:
            bool: True si el sonido se reprodujo correctamente, False en caso contrario
        """
        if not self.audio_available or self.muted:
            return False
            
        try:
            # Obtener o cargar el sonido
            sound = self._get_sound(sound_name)
            if sound:
                actual_volume = self.master_volume * self.sfx_volume
                sound.set_volume(actual_volume)
                sound.play()
                return True
            return False
        except Exception as e:
            debugger.error(f"Error al reproducir efecto de sonido: {str(e)}")
            return False
            
    def _get_sound(self, sound_name):
        """
        Obtiene un objeto de sonido, cargándolo bajo demanda si no está ya en memoria.
        
        Args:
            sound_name (str): Nombre del efecto de sonido
            
        Returns:
            pygame.mixer.Sound o None: Objeto de sonido o None si no se pudo cargar
        """
        # Si ya tenemos el sonido en memoria, lo devolvemos directamente
        if sound_name in self.sound_effects:
            return self.sound_effects[sound_name]
            
        # Intentar cargar el sonido bajo demanda
        try:
            sfx_dir = self._get_assets_dir('sfx')
            sound_path = os.path.join(sfx_dir, f"{sound_name}.wav")
            
            if os.path.exists(sound_path):
                sound = pygame.mixer.Sound(sound_path)
                # Guardar para uso futuro
                self.sound_effects[sound_name] = sound
                return sound
            else:
                debugger.warning(f"Archivo de sonido no encontrado: {sound_path}")
                return None
        except Exception as e:
            debugger.error(f"Error al cargar sonido '{sound_name}': {str(e)}")
            return None
    
    def set_music_volume(self, volume):
        """
        Establece el volumen de la música.
        
        Args:
            volume (float): Nivel de volumen entre 0.0 y 1.0
        """
        self.music_volume = max(0.0, min(1.0, volume))
        if self.audio_available and not self.muted:
            actual_volume = self.master_volume * self.music_volume
            pygame.mixer.music.set_volume(actual_volume)
    
    def set_sfx_volume(self, volume):
        """
        Establece el volumen de los efectos de sonido.
        
        Args:
            volume (float): Nivel de volumen entre 0.0 y 1.0
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        # No es necesario actualizar cada sonido aquí, se hará cuando se reproduzcan
    
    def set_master_volume(self, volume):
        """
        Establece el volumen maestro que afecta tanto a música como efectos.
        
        Args:
            volume (float): Nivel de volumen entre 0.0 y 1.0
        """
        self.master_volume = max(0.0, min(1.0, volume))
        if self.audio_available and not self.muted:
            # Actualizar volumen de música
            actual_music_vol = self.master_volume * self.music_volume
            pygame.mixer.music.set_volume(actual_music_vol)
            # El volumen de efectos se actualizará cuando se reproduzcan
    
    def toggle_mute(self):
        """Alterna el estado de silencio."""
        self.muted = not self.muted
        if self.audio_available:
            if self.muted:
                pygame.mixer.music.set_volume(0)
            else:
                actual_volume = self.master_volume * self.music_volume
                pygame.mixer.music.set_volume(actual_volume)
        return self.muted
    
    def set_mute(self, muted):
        """
        Establece el estado de silencio.
        
        Args:
            muted (bool): True para silenciar, False para activar sonido
        """
        if self.muted != muted:
            self.muted = muted
            if self.audio_available:
                if self.muted:
                    pygame.mixer.music.set_volume(0)
                else:
                    actual_volume = self.master_volume * self.music_volume
                    pygame.mixer.music.set_volume(actual_volume)
        return self.muted
    
    def get_dummy_sound(self):
        """
        Devuelve un objeto de sonido ficticio para usar cuando el audio no está disponible.
        """
        class DummySound:
            def play(self): pass
            def stop(self): pass
            def set_volume(self, vol): pass
        return DummySound()

# Crear una instancia global del gestor de audio
audio_manager = AudioManager()