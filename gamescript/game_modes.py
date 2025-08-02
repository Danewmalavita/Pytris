# game_modes.py
import time
import pygame
from .tetris_logic import TetrisGame
from .debug_utils import debugger

class ClassicMode(TetrisGame):
    """Modo clásico de Tetris: el juego continúa hasta que se pierde."""
    
    def __init__(self):
        super().__init__()
        self.mode_name = "Clásico"
        self.mode_description = "¡Aguanta lo máximo posible!"
        debugger.debug("Modo clásico iniciado")

class TimeAttackMode(TetrisGame):
    """Modo contrarreloj: 3 minutos para conseguir la mayor puntuación."""
    
    def __init__(self):
        super().__init__()
        self.mode_name = "Contrarreloj"
        self.mode_description = "¡3 minutos para la máxima puntuación!"
        self.time_limit = 180  # 3 minutos en segundos
        self.start_time = None
        self.remaining_time = self.time_limit
        self.is_paused = False
        self.paused_at = 0
        self.pause_total = 0
        self.game_over_reason = "¡TIEMPO AGOTADO!"
        debugger.debug("Modo contrarreloj iniciado")
    
    def start(self):
        """Inicia el temporizador del modo."""
        self.start_time = time.time()
    
    def pause(self):
        """Pausa el temporizador."""
        if not self.is_paused and self.start_time is not None:
            self.paused_at = time.time()
            self.is_paused = True
            debugger.debug("Modo contrarreloj pausado")
    
    def unpause(self):
        """Reanuda el temporizador."""
        if self.is_paused and self.start_time is not None:
            # Añadir el tiempo pausado al total de pausa
            pause_duration = time.time() - self.paused_at
            self.pause_total += pause_duration
            self.is_paused = False
            debugger.debug(f"Modo contrarreloj reanudado, tiempo pausado: {pause_duration:.2f}s")
    
    def update(self):
        """Actualiza el temporizador y comprueba si se ha acabado el tiempo."""
        if self.start_time is None or self.is_paused:
            return
            
        # Calcular tiempo transcurrido considerando pausas
        elapsed = time.time() - self.start_time - self.pause_total
        previous_time = self.remaining_time
        self.remaining_time = max(0, self.time_limit - elapsed)
        
        # Comprobar hitos de tiempo para advertencias
        if not hasattr(self, "time_warnings_played"):
            self.time_warnings_played = set()
            
        # Almacenar referencia al combo_animator para mostrar advertencias
        if not hasattr(self, "combo_animator"):
            from .visual_effects import ComboAnimator
            self.combo_animator = ComboAnimator()
        
        for time_threshold in [30, 10, 5]:
            # Comprobar si acabamos de pasar el umbral de tiempo (antes era > threshold, ahora es <= threshold)
            if previous_time > time_threshold and self.remaining_time <= time_threshold and time_threshold not in self.time_warnings_played:
                # Reproducir sonido de advertencia
                from .audio_manager import audio_manager
                audio_manager.play_sound("time")
                
                # Añadir animación de tiempo
                if hasattr(self, "combo_animator"):
                    self.combo_animator.add_time_warning(time_threshold)
                
                # Registrar que hemos reproducido esta advertencia
                self.time_warnings_played.add(time_threshold)
                debugger.debug(f"Advertencia de tiempo: {time_threshold}s restantes")
        
        # Game over cuando se acaba el tiempo
        if self.remaining_time <= 0 and not self.game_over:
            self.game_over = True
            debugger.debug("Tiempo agotado en modo contrarreloj")
    
    def get_time_str(self):
        """Devuelve el tiempo restante en formato MM:SS."""
        minutes = int(self.remaining_time) // 60
        seconds = int(self.remaining_time) % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def move_down(self, is_soft_drop=False):
        """Sobrescribe el método move_down para actualizar el tiempo."""
        self.update()
        return super().move_down(is_soft_drop)

class MarathonMode(TetrisGame):
    """Modo maratón: completa 150 líneas para ganar."""
    
    def __init__(self):
        super().__init__()
        self.mode_name = "Maratón"
        self.mode_description = "¡Completa 150 líneas!"
        self.target_lines = 150
        self.game_won = False
        self.game_over_reason = "¡COMPLETADO!"
        debugger.debug("Modo maratón iniciado")
    
    def fix_piece(self):
        """Sobrescribe fix_piece para comprobar si se han completado las líneas objetivo."""
        result = super().fix_piece()
        
        if self.lines_cleared >= self.target_lines and not self.game_won:
            self.game_won = True
            self.game_over = True
            debugger.debug(f"Maratón completada: {self.lines_cleared}/{self.target_lines} líneas")
        
        return result
    
    def get_progress_str(self):
        """Devuelve el progreso actual de la maratón."""
        return f"Líneas: {self.lines_cleared}/{self.target_lines}"

class UltraMode(TetrisGame):
    """Modo Ultra: consigue la mayor puntuación en 2 minutos."""
    
    def __init__(self):
        super().__init__()
        self.mode_name = "Ultra"
        self.mode_description = "¡2 minutos para puntuación máxima!"
        self.time_limit = 120  # 2 minutos en segundos
        self.start_time = None
        self.remaining_time = self.time_limit
        self.is_paused = False
        self.paused_at = 0
        self.pause_total = 0
        self.game_over_reason = "¡TIEMPO AGOTADO!"
        # Aumentar la velocidad base para hacer el modo más desafiante
        self.base_speed = 800  # Más rápido que el modo clásico
        debugger.debug("Modo Ultra iniciado")
    
    def start(self):
        """Inicia el temporizador del modo."""
        self.start_time = time.time()
    
    def pause(self):
        """Pausa el temporizador."""
        if not self.is_paused and self.start_time is not None:
            self.paused_at = time.time()
            self.is_paused = True
            debugger.debug("Modo Ultra pausado")
    
    def unpause(self):
        """Reanuda el temporizador."""
        if self.is_paused and self.start_time is not None:
            # Añadir el tiempo pausado al total de pausa
            pause_duration = time.time() - self.paused_at
            self.pause_total += pause_duration
            self.is_paused = False
            debugger.debug(f"Modo Ultra reanudado, tiempo pausado: {pause_duration:.2f}s")
    
    def update(self):
        """Actualiza el temporizador y comprueba si se ha acabado el tiempo."""
        if self.start_time is None or self.is_paused:
            return
            
        # Calcular tiempo transcurrido considerando pausas
        elapsed = time.time() - self.start_time - self.pause_total
        previous_time = self.remaining_time
        self.remaining_time = max(0, self.time_limit - elapsed)
        
        # Comprobar hitos de tiempo para advertencias
        if not hasattr(self, "time_warnings_played"):
            self.time_warnings_played = set()
            
        # Almacenar referencia al combo_animator para mostrar advertencias
        if not hasattr(self, "combo_animator"):
            from .visual_effects import ComboAnimator
            self.combo_animator = ComboAnimator()
        
        for time_threshold in [30, 10, 5]:
            # Comprobar si acabamos de pasar el umbral de tiempo (antes era > threshold, ahora es <= threshold)
            if previous_time > time_threshold and self.remaining_time <= time_threshold and time_threshold not in self.time_warnings_played:
                # Reproducir sonido de advertencia
                from .audio_manager import audio_manager
                audio_manager.play_sound("time")
                
                # Añadir animación de tiempo
                if hasattr(self, "combo_animator"):
                    self.combo_animator.add_time_warning(time_threshold)
                
                # Registrar que hemos reproducido esta advertencia
                self.time_warnings_played.add(time_threshold)
                debugger.debug(f"Advertencia de tiempo: {time_threshold}s restantes")
        
        # Game over cuando se acaba el tiempo
        if self.remaining_time <= 0 and not self.game_over:
            self.game_over = True
            debugger.debug("Tiempo agotado en modo Ultra")
    
    def get_time_str(self):
        """Devuelve el tiempo restante en formato MM:SS."""
        minutes = int(self.remaining_time) // 60
        seconds = int(self.remaining_time) % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def move_down(self, is_soft_drop=False):
        """Sobrescribe el método move_down para actualizar el tiempo."""
        self.update()
        return super().move_down(is_soft_drop)

def create_game_mode(mode_name):
    """
    Crea una instancia del modo de juego especificado.
    
    Args:
        mode_name (str): Nombre del modo ('classic', 'time_attack', 'marathon', 'ultra')
        
    Returns:
        TetrisGame: Instancia del modo de juego correspondiente
    """
    mode_map = {
        'classic': ClassicMode,
        'time_attack': TimeAttackMode,
        'marathon': MarathonMode,
        'ultra': UltraMode
    }
    
    if mode_name in mode_map:
        return mode_map[mode_name]()
    else:
        debugger.warning(f"Modo de juego desconocido: {mode_name}. Usando modo clásico.")
        return ClassicMode()