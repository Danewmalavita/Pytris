# debug_utils.py
# Utilidades para debug y registro de eventos en el juego

import datetime
import os

class Debugger:
    """
    Clase para gestionar el registro (logging) y depuración en el juego
    """
    def __init__(self, enabled=True, log_to_file=True, log_file="pytris_debug.log", show_debug=False):
        self.enabled = enabled
        self.log_to_file = log_to_file
        self.log_file = log_file
        
        # Configuración de visualización de mensajes
        self.show_debug = True    # Deshabilitar mensajes de debug por defecto
        self.show_info = True     # Deshabilitar mensajes info por defecto
        self.show_warning = True   # Habilitar mensajes warning por defecto
        self.show_error = True     # Habilitar mensajes error por defecto
        
        # Crear directorio de logs si no existe
        if self.log_to_file:
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                try:
                    os.makedirs(log_dir)
                except:
                    self.log_to_file = False
            
            # Iniciar archivo de logs
            if self.log_to_file:
                with open(self.log_file, 'w') as f:
                    f.write(f"=== PyTris Debug Log - {datetime.datetime.now()} ===\n")
    
    def _log(self, level, message):
        """
        Registra un mensaje con el nivel especificado
        """
        if not self.enabled:
            return
            
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        formatted_msg = f"[{timestamp}] [{level}] {message}"
        
        # Mostrar en consola según la configuración
        show_message = False
        if level == "DEBUG" and self.show_debug:
            show_message = True
        elif level == "INFO" and self.show_info:
            show_message = True
        elif level == "WARNING" and self.show_warning:
            show_message = True
        elif level == "ERROR" and self.show_error:
            show_message = True
        elif level == "CRITICAL":  # Los críticos siempre se muestran
            show_message = True
            
        if show_message:
            print(formatted_msg)
        
        # Guardar en archivo si está activado
        if self.log_to_file:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(formatted_msg + "\n")
            except:
                pass
    
    def debug(self, message):
        """
        Registra un mensaje de depuración
        """
        self._log("DEBUG", message)
    
    def info(self, message):
        """
        Registra un mensaje informativo
        """
        self._log("INFO", message)
    
    def warning(self, message):
        """
        Registra una advertencia
        """
        self._log("WARNING", message)
    
    def error(self, message):
        """
        Registra un mensaje de error
        """
        self._log("ERROR", message)
    
    def critical(self, message):
        """
        Registra un error crítico
        """
        self._log("CRITICAL", message)

    def set_display_options(self, debug=None, info=None, warning=None, error=None):
        """
        Configura qué tipos de mensajes se muestran en consola
        
        Args:
            debug (bool, optional): Mostrar mensajes de depuración
            info (bool, optional): Mostrar mensajes informativos
            warning (bool, optional): Mostrar advertencias
            error (bool, optional): Mostrar errores
        """
        if debug is not None:
            self.show_debug = debug
        if info is not None:
            self.show_info = info
        if warning is not None:
            self.show_warning = warning
        if error is not None:
            self.show_error = error
            
    def enable_all_messages(self):
        """Activa todos los tipos de mensajes"""
        self.set_display_options(debug=True, info=True, warning=True, error=True)
        
    def disable_all_messages(self):
        """Desactiva todos los mensajes (excepto críticos)"""
        self.set_display_options(debug=False, info=False, warning=False, error=False)
        
    def production_mode(self):
        """Configura para modo producción (solo errores y advertencias)"""
        self.set_display_options(debug=False, info=False, warning=True, error=True)
        
    def development_mode(self):
        """Configura para modo desarrollo (todos los mensajes)"""
        self.enable_all_messages()

# Crear una instancia global del debugger
debugger = Debugger(enabled=True, log_to_file=False)