# visual_effects.py
# Módulo para efectos visuales en el juego Tetris

import pygame
import random
import math
import time
import traceback
from .debug_utils import debugger
from .tetris_logic import SHAPES, COLORS

class Particle:
    """Clase para representar partículas que se muestran cuando se eliminan líneas"""
    def __init__(self, x, y, color, velocity_x=None, velocity_y=None, size=None, life=None):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x if velocity_x is not None else random.uniform(-2, 2)
        self.velocity_y = velocity_y if velocity_y is not None else random.uniform(-4, -1)
        self.size = size if size is not None else random.randint(2, 6)
        self.life = life if life is not None else random.randint(30, 60)
        self.original_life = self.life
        self.gravity = 0.1
    
    def update(self):
        """Actualiza la posición y propiedades de la partícula"""
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += self.gravity
        self.life -= 1
        # Reducir tamaño gradualmente
        if self.life < self.original_life * 0.5:
            self.size = max(1, self.size * 0.99)
    
    def draw(self, screen, offset_x=0, offset_y=0):
        """Dibuja la partícula en pantalla"""
        # Calcular opacidad basada en vida restante
        opacity = int(255 * (self.life / self.original_life))
        particle_color = (*self.color[:3], opacity)
        
        pygame.draw.rect(
            screen, 
            particle_color,
            (int(self.x + offset_x), int(self.y + offset_y), int(self.size), int(self.size))
        )


class ParticleSystem:
    """Sistema para gestionar partículas de efectos visuales"""
    def __init__(self):
        self.particles = []
        self.max_particles = 450  # Reduced from 500 to 450 to prevent warnings
        self.disabled = False
        self.last_cleanup_time = time.time()
        self.cleanup_interval = 5.0  # Seconds between periodic cleanups
        
    def add_particles_for_line_clear(self, x, y, width, color, count=20):
        """Añade partículas para el efecto de eliminación de línea"""
        try:
            # Calculate available space for new particles - keep 20% below max to avoid constant warnings
            available_space = max(0, int(self.max_particles * 0.8) - len(self.particles))
            
            # If we have no space, remove oldest particles to make room
            if available_space <= 0:
                if len(self.particles) >= self.max_particles:
                    # Remove 20% of particles to create space
                    particles_to_remove = int(len(self.particles) * 0.2)
                    self.particles = self.particles[particles_to_remove:]
                    available_space = int(self.max_particles * 0.2)
                    debugger.debug(f"Cleared {particles_to_remove} old particles to make room for new ones")
            
            # Check if particle system is disabled
            if self.disabled:
                return
                
            # Safety check for inputs
            if not (isinstance(x, (int, float)) and isinstance(y, (int, float)) and isinstance(width, (int, float))):
                debugger.error(f"Invalid particle parameters: x={x}, y={y}, width={width}")
                return
                
            # Validate color
            if not (isinstance(color, tuple) and len(color) >= 3):
                debugger.error(f"Invalid particle color: {color}")
                color = (255, 255, 255)  # Default to white
                
            # Limit particles per call - use available space or requested count, whichever is smaller
            actual_count = min(count, 5, available_space)  # Reduced from 10 to 5 for performance
            
            start_time = time.time()
            
            for _ in range(actual_count):
                try:
                    particle_x = random.randint(int(x), int(x + width))
                    self.particles.append(Particle(
                        particle_x, y, 
                        color,
                        velocity_x=random.uniform(-2, 2),
                        velocity_y=random.uniform(-3, -1)
                    ))
                except (ValueError, TypeError) as e:
                    debugger.error(f"Error creating particle: {str(e)}")
            
            # Log performance if slow
            elapsed = time.time() - start_time
            if elapsed > 0.01:
                debugger.warning(f"Slow particle creation: {elapsed:.4f}s for {actual_count} particles")
                
        except Exception as e:
            debugger.error(f"Error in add_particles_for_line_clear: {str(e)}")
            debugger.error(traceback.format_exc())
            self.disabled = True  # Disable on error
    
    def add_shape_particles(self, x, y, shape_type, block_size=30, count_per_block=5):
        """Añade partículas con forma de tetromino"""
        try:
            # Calculate available space for new particles
            available_space = max(0, int(self.max_particles * 0.7) - len(self.particles))
            
            # If we have little space, remove oldest particles to make room
            if available_space <= 20:  # Need space for at least a few particles
                if len(self.particles) >= self.max_particles * 0.7:
                    # Remove 30% of particles to create space
                    particles_to_remove = int(len(self.particles) * 0.3)
                    self.particles = self.particles[particles_to_remove:]
                    available_space = int(self.max_particles * 0.3)
                    debugger.debug(f"Cleared {particles_to_remove} old particles for shape particles")
                    
            # Check if we should skip this
            if self.disabled:
                return
                
            # Reduce count for performance and based on available space
            count_per_block = min(count_per_block, 2)  # Reduced from 3 to 2
                
            # Safety check for shape_type
            if not (0 <= shape_type < len(SHAPES)):
                debugger.error(f"Invalid shape type: {shape_type}")
                return
                
            shape = SHAPES[shape_type][0]  # Usa la primera rotación
            
            # Safety check for color index
            color_index = shape_type + 1
            if not (0 <= color_index < len(COLORS)):
                debugger.error(f"Invalid color index: {color_index}")
                color = (255, 255, 255)  # Default to white
            else:
                color = COLORS[color_index]  # Los colores comienzan en 1 (0 es vacío)
            
            # Count total blocks to estimate particle count
            total_blocks = sum(sum(1 for cell in row if cell != 0) for row in shape)
            total_particles = total_blocks * count_per_block
            
            # If we would exceed available space, reduce count_per_block
            if total_particles > available_space and total_blocks > 0:
                count_per_block = max(1, available_space // total_blocks)
            
            for row in range(len(shape)):
                for col in range(len(shape[row])):
                    if shape[row][col] != 0:
                        block_x = x + col * block_size
                        block_y = y + row * block_size
                        
                        for _ in range(count_per_block):
                            particle_x = block_x + random.randint(0, block_size)
                            particle_y = block_y + random.randint(0, block_size)
                            self.particles.append(Particle(
                                particle_x, particle_y,
                                color,
                                velocity_x=random.uniform(-3, 3),
                                velocity_y=random.uniform(-5, -2),
                                size=random.randint(3, 7),
                                life=random.randint(40, 60)  # Reduced life from 80 to 60
                            ))
                            
                            # Check if we're adding too many particles
                            if len(self.particles) >= self.max_particles * 0.9:
                                return
        except Exception as e:
            debugger.error(f"Error in add_shape_particles: {str(e)}")
            debugger.error(traceback.format_exc())
            self.disabled = True  # Disable on error
    
    def add_tetris_celebration_particles(self, screen_width, screen_height, count=100):
        """Añade partículas por toda la pantalla para celebrar un Tetris"""
        try:
            # Calculate available space for new particles
            available_space = max(0, int(self.max_particles * 0.6) - len(self.particles))
            
            # If we have little space, remove oldest particles to make room for celebration
            if available_space < 30:  # Need at least 30 particles for a good celebration effect
                # Remove 40% of particles to create space for celebration
                particles_to_remove = int(len(self.particles) * 0.4)
                self.particles = self.particles[particles_to_remove:]
                available_space = int(self.max_particles * 0.4)
                debugger.debug(f"Cleared {particles_to_remove} old particles for Tetris celebration!")
                    
            # Check if we should skip this
            if self.disabled:
                return
                
            # Reduce count for performance and available space
            count = min(count, 40, available_space)  # Reduced from 50 to 40 and limited by available space
                
            start_time = time.time()
            
            for _ in range(count):
                x = random.randint(0, screen_width)
                y = random.randint(0, screen_height)
                
                # Safety check for color index
                color_idx = random.randint(1, min(len(COLORS) - 1, 7))  # Ensure within bounds
                color = COLORS[color_idx]
                
                self.particles.append(Particle(
                    x, y,
                    color,
                    velocity_x=random.uniform(-3, 3),
                    velocity_y=random.uniform(-8, -3),
                    size=random.randint(4, 8),  # Reduced max size from 10 to 8
                    life=random.randint(50, 90)  # Reduced life from 60-120 to 50-90
                ))
                
                # Check if we're approaching the limit
                if len(self.particles) >= self.max_particles * 0.9:
                    break
            
            # Log performance if slow
            elapsed = time.time() - start_time
            if elapsed > 0.01:
                debugger.warning(f"Slow celebration particles: {elapsed:.4f}s for {count} particles")
                
        except Exception as e:
            debugger.error(f"Error in add_tetris_celebration_particles: {str(e)}")
            debugger.error(traceback.format_exc())
            self.disabled = True  # Disable on error
    
    def update(self):
        """Actualiza todas las partículas y elimina las que han expirado"""
        try:
            # Early return if disabled
            if self.disabled:
                return
                
            start_time = time.time()
            
            # More aggressive particle management to prevent warnings
            if len(self.particles) >= self.max_particles * 0.95:
                # If we're approaching the limit, remove 25% of the oldest particles
                particles_to_remove = int(len(self.particles) * 0.25)
                if particles_to_remove > 0:
                    self.particles = self.particles[particles_to_remove:]
                    debugger.debug(f"Proactively removed {particles_to_remove} particles to prevent overflow")
            
            # Use a more efficient approach for large numbers of particles
            if len(self.particles) > 100:
                # For larger sets, use a more efficient filtering approach
                alive_particles = []
                for p in self.particles:
                    p.life -= 1
                    if p.life > 0:
                        p.update()
                        alive_particles.append(p)
                self.particles = alive_particles
            else:
                # For smaller sets, use the original list comprehension
                self.particles = [p for p in self.particles if p.life > 0]
                for particle in self.particles:
                    particle.update()
            
            # Additional check - if still too many particles after update, trim again
            if len(self.particles) > self.max_particles:
                excess = len(self.particles) - self.max_particles
                self.particles = self.particles[excess:]
                
            # Log performance if this is taking too long
            elapsed = time.time() - start_time
            if elapsed > 0.01 and len(self.particles) > 50:
                debugger.warning(f"Slow particle update: {elapsed:.4f}s for {len(self.particles)} particles")
                
                # If updates are consistently slow, reduce the max_particles limit
                if elapsed > 0.03 and self.max_particles > 300:
                    self.max_particles = max(300, int(self.max_particles * 0.9))
                    debugger.warning(f"Reducing max particles to {self.max_particles} due to performance issues")
                
        except Exception as e:
            debugger.error(f"Error in particle update: {str(e)}")
            debugger.error(traceback.format_exc())
            self.disabled = True  # Disable on error
            self.particles = []  # Reset particles to recover
    
    def draw(self, screen, offset_x=0, offset_y=0):
        """Dibuja todas las partículas en pantalla"""
        try:
            # Skip if disabled
            if self.disabled:
                return
                
            start_time = time.time()
            
            # Don't try to draw too many particles
            particle_count = len(self.particles)
            
            # If we have a lot of particles, only draw a subset for performance
            if particle_count > 200:
                step = particle_count // 200
                particles_to_draw = self.particles[::step]
            else:
                particles_to_draw = self.particles
                
            for particle in particles_to_draw:
                try:
                    particle.draw(screen, offset_x, offset_y)
                except Exception as e:
                    debugger.error(f"Error drawing particle: {str(e)}")
            
            # Log performance if slow
            elapsed = time.time() - start_time
            if elapsed > 0.02:
                debugger.warning(f"Slow particle drawing: {elapsed:.4f}s for {len(particles_to_draw)} particles")
                if len(particles_to_draw) > 100:
                    debugger.warning("Reducing particles due to slow drawing")
                    self.particles = self.particles[:100]  # Aggressive reduction if drawing is slow
                    
        except Exception as e:
            debugger.error(f"Error in particle drawing: {str(e)}")
            debugger.error(traceback.format_exc())
            self.disabled = True
            self.particles = []


class ScreenShake:
    """Efecto de temblor de pantalla"""
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.offset_x = 0
        self.offset_y = 0
        
    def start_shake(self, intensity, duration):
        """Inicia un temblor de pantalla con intensidad y duración dadas"""
        self.intensity = intensity
        self.duration = duration
        
    def update(self):
        """Actualiza el estado del temblor de pantalla"""
        if self.duration > 0:
            self.offset_x = random.uniform(-self.intensity, self.intensity)
            self.offset_y = random.uniform(-self.intensity, self.intensity)
            self.duration -= 1
        else:
            self.offset_x = 0
            self.offset_y = 0
            
    def get_offset(self):
        """Devuelve el desplazamiento actual para aplicar al renderizado"""
        return (self.offset_x, self.offset_y)


class ComboAnimator:
    """Animador para efectos de combo al eliminar líneas consecutivamente"""
    def __init__(self):
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_timeout = 180  # Frames (3 segundos a 60 FPS)
        self.text_scale = 1.0
        self.display_time = 0
        self.rotation = 0
        self.pulse_factor = 1.0
        self.pulse_direction = 0.05
        # Para animaciones de texto personalizadas
        self.custom_text = ""
        self.custom_text_color = (255, 255, 255)
        self.custom_text_time = 0
        # Para reproducción de sonidos
        self.sfx_vol = 1.0
        
    def add_combo(self, lines_cleared):
        """Registra un nuevo combo"""
        self.combo_count += 1
        self.combo_timer = self.combo_timeout
        self.text_scale = 1.5  # Empieza grande y se reduce
        self.display_time = 90  # Mostrar durante 1.5 segundos
        self.rotation = random.uniform(-10, 10)  # Rotación aleatoria
        
        # Reproducir sonido de combo al mostrar la animación (si hay 2 o más combos)
        # El primer combo (combo_count == 1) no debe reproducir sonido aquí,
        # ya que es el sonido normal de la línea que se acaba de eliminar
        if self.combo_count >= 2:
            try:
                # Los archivos de sonido comienzan en combo2.wav para combo x2, combo3.wav para combo x3, etc.
                # Por lo tanto, el número de archivo coincide con el contador de combo
                combo_num = min(8, self.combo_count)  # Limitado a 8 máximo
                combo_sound = pygame.mixer.Sound(f"assets/sounds/sfx/combo{combo_num}.wav")
                
                # Usar el volumen de efectos configurado
                try:
                    if pygame.mixer.get_init() is not None:
                        combo_sound.set_volume(self.sfx_vol)
                        combo_sound.play()
                except Exception as e:
                    # Si hay un error al reproducir el sonido, simplemente lo ignoramos
                    pass
            except Exception:
                # Si hay un error al cargar el sonido, simplemente lo ignoramos
                pass
    
    def add_text_animation(self, text, color=(255, 255, 255)):
        """Añade una animación de texto personalizada (ej: T-Spin)"""
        self.custom_text = text
        self.custom_text_color = color
        self.custom_text_time = 120  # Mostrar durante 2 segundos
        self.text_scale = 1.5  # Empieza grande y se reduce
        self.rotation = random.uniform(-5, 5)  # Rotación aleatoria menos intensa que el combo
        
    def update(self):
        """Actualiza el estado de la animación de combo"""
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer == 0:
                # Cuando se acaba el tiempo del combo, reiniciamos el contador
                self.combo_count = 0
                # También reiniciamos la animación para evitar textos flotantes
                self.display_time = 0
                
        if self.display_time > 0:
            self.display_time -= 1
            # Reducir la escala gradualmente
            if self.text_scale > 1.0:
                self.text_scale -= 0.01
                
            # Efecto de pulso
            self.pulse_factor += self.pulse_direction
            if self.pulse_factor >= 1.2:
                self.pulse_direction = -0.03
            elif self.pulse_factor <= 0.9:
                self.pulse_direction = 0.03
                
            # Reducir rotación para estabilizarse
            self.rotation *= 0.95
        
    def draw(self, screen, center_x, center_y):
        """Dibuja la animación de combo en pantalla"""
        # Dibujar la animación de combo si está activa
        if self.combo_count > 1 and self.display_time > 0:
            font_size = int(32 * self.text_scale * self.pulse_factor)
            font = pygame.font.SysFont("Arial", font_size, bold=True)
            
            # Color basado en el tamaño del combo
            if self.combo_count < 3:
                color = (255, 255, 100)
            elif self.combo_count < 5:
                color = (255, 150, 50)
            else:
                color = (255, 50, 50)
            
            # Texto con efectos
            text = f"COMBO x{self.combo_count}!"
            if self.combo_count >= 5:
                text = f"¡SUPER COMBO x{self.combo_count}!"
                
            text_surface = font.render(text, True, color)
            
            # Rotar el texto para efecto dinámico
            text_surface = pygame.transform.rotate(text_surface, self.rotation)
            text_rect = text_surface.get_rect(center=(center_x, center_y))
            
            # Añadir un poco de oscilación vertical
            bounce = math.sin(pygame.time.get_ticks() * 0.01) * 5
            text_rect.centery += bounce
            
            # Dibujar sombra para mejor visibilidad
            shadow_surface = font.render(text, True, (0, 0, 0))
            shadow_surface = pygame.transform.rotate(shadow_surface, self.rotation)
            shadow_rect = shadow_surface.get_rect(center=(center_x + 2, center_y + 2))
            screen.blit(shadow_surface, shadow_rect)
            
            screen.blit(text_surface, text_rect)
            
        # Dibujar animación de texto personalizada si está activa
        if self.custom_text and self.custom_text_time > 0:
            # Ajustar tamaño según el tiempo restante
            scale_factor = min(1.0, self.custom_text_time / 60)
            font_size = int(36 * self.text_scale * scale_factor)
            font = pygame.font.SysFont("Arial", font_size, bold=True)
            
            # Reducir el tiempo de animación
            self.custom_text_time -= 1
            
            # Crear superficie de texto
            text_surface = font.render(self.custom_text, True, self.custom_text_color)
            
            # Rotar el texto para efecto dinámico
            text_surface = pygame.transform.rotate(text_surface, self.rotation)
            text_rect = text_surface.get_rect(center=(center_x, center_y - 50))  # Mostrar encima del combo
            
            # Dibujar sombra para mejor visibilidad
            shadow_surface = font.render(self.custom_text, True, (0, 0, 0))
            shadow_surface = pygame.transform.rotate(shadow_surface, self.rotation)
            shadow_rect = shadow_surface.get_rect(center=(center_x + 2, center_y - 50 + 2))
            screen.blit(shadow_surface, shadow_rect)
            
            screen.blit(text_surface, text_rect)
            
            # Limpiar el texto cuando termine la animación
            if self.custom_text_time <= 0:
                self.custom_text = ""


class TetrominoVisualizer:
    """Clase para visualizar y animar tetrominos"""
    def __init__(self, block_sprites=None):
        self.block_sprites = block_sprites
    
    def set_block_sprites(self, sprites):
        """Establece los sprites de bloques a utilizar"""
        self.block_sprites = sprites
    
    def draw_shape(self, screen, shape_type, rotation, x, y, block_size=30, alpha=255, ghost=False):
        """Dibuja un tetromino en la posición especificada"""
        if shape_type is None:
            return
            
        shape = SHAPES[shape_type][rotation]
        piece_type = shape_type + 1  # Los índices de color comienzan desde 1 (0 es vacío)
        
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col] != 0:
                    screen_x = x + col * block_size
                    screen_y = y + row * block_size
                    
                    if self.block_sprites:
                        # Usar sprites si están disponibles
                        sprite = self.block_sprites[piece_type]
                        
                        # Aplicar transparencia si es necesario
                        if ghost or alpha < 255:
                            sprite_copy = sprite.copy()
                            sprite_copy.set_alpha(80 if ghost else alpha)
                            screen.blit(sprite_copy, (screen_x, screen_y))
                        else:
                            screen.blit(sprite, (screen_x, screen_y))
                    else:
                        # Fallback a rectángulos coloreados si no hay sprites
                        color = COLORS[piece_type]
                        if ghost:
                            color = (*color[:3], 80)
                        elif alpha < 255:
                            color = (*color[:3], alpha)
                            
                        pygame.draw.rect(
                            screen, 
                            color,
                            (screen_x, screen_y, block_size, block_size)
                        )
                        
                        # Borde interno para dar profundidad
                        pygame.draw.rect(
                            screen,
                            (min(color[0] + 40, 255), min(color[1] + 40, 255), min(color[2] + 40, 255)),
                            (screen_x, screen_y, block_size, block_size),
                            1
                        )

    def draw_centered_shape(self, screen, shape_type, x, y, box_size=4, block_size=30):
        """Dibuja un tetromino centrado en una caja de tamaño específico (para Next y Hold)"""
        if shape_type is None:
            return
            
        shape = SHAPES[shape_type][0]  # Primera rotación
        
        # Calcular dimensiones reales de la pieza
        rows = len(shape)
        cols = len(shape[0])
        min_x, min_y = cols, rows
        max_x, max_y = 0, 0
        
        for row in range(rows):
            for col in range(cols):
                if shape[row][col] != 0:
                    min_x = min(min_x, col)
                    max_x = max(max_x, col)
                    min_y = min(min_y, row)
                    max_y = max(max_y, row)
        
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        
        # Centrar la pieza dentro del recuadro
        offset_x = (box_size - width) // 2
        offset_y = (box_size - height) // 2
        
        self.draw_shape(
            screen,
            shape_type,
            0,  # Primera rotación
            x - min_x * block_size + offset_x * block_size,
            y - min_y * block_size + offset_y * block_size,
            block_size
        )


class DynamicBackground:
    """Fondo dinámico que cambia según el nivel"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_level = 0
        self.background = None
        self.pattern_offset = 0
        self.line_colors = []
        self.tetromino_shapes = []  # Almacenar formas de tetrominos para fondo
        self.tetromino_visualizer = TetrominoVisualizer()
        self.max_shapes = 30  # Limit number of background tetrominos to prevent performance issues
        self.error_count = 0  # Track errors to disable features if needed
        self.disabled_features = set()  # Track which features are disabled
        self.generate_background(1)
        
    def generate_background(self, level):
        """Genera un nuevo fondo basado en el nivel"""
        try:
            start_time = time.time()
            debugger.debug(f"Generating background for level {level}")
            
            self.current_level = level
            self.background = pygame.Surface((self.screen_width, self.screen_height))
            
            # Color base según nivel
            base_hue = (level * 30) % 360
            saturation = 50 + (level % 5) * 10
            value = 20 + (level % 3) * 5
            
            debugger.debug(f"Background base color: hue={base_hue}, sat={saturation}, val={value}")
            
            # Convertir HSV a RGB
            c = saturation * value / 10000
            x = c * (1 - abs((base_hue / 60) % 2 - 1))
            m = value / 100 - c
        except Exception as e:
            debugger.error(f"Error in background color calculation: {str(e)}")
            # Default to a dark blue color if there's an error
            base_hue, saturation, value = 240, 50, 20
            c, x, m = 0.1, 0, 0.1
        
        if base_hue < 60:
            r, g, b = c, x, 0
        elif base_hue < 120:
            r, g, b = x, c, 0
        elif base_hue < 180:
            r, g, b = 0, c, x
        elif base_hue < 240:
            r, g, b = 0, x, c
        elif base_hue < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        r, g, b = (r + m) * 255, (g + m) * 255, (b + m) * 255
        base_color = (int(r), int(g), int(b))
        
        # Llenar con color base
        self.background.fill(base_color)
        
        # Generar colores para líneas del patrón
        self.line_colors = []
        for i in range(3):  # 3 tipos de líneas
            bright = min(255, (base_hue + 120 * i) % 360)
            line_hue = bright
            line_sat = min(100, saturation + 20)
            line_val = min(100, value + 30 + i * 10)
            
            c = line_sat * line_val / 10000
            x = c * (1 - abs((line_hue / 60) % 2 - 1))
            m = line_val / 100 - c
            
            if line_hue < 60:
                r, g, b = c, x, 0
            elif line_hue < 120:
                r, g, b = x, c, 0
            elif line_hue < 180:
                r, g, b = 0, c, x
            elif line_hue < 240:
                r, g, b = 0, x, c
            elif line_hue < 300:
                r, g, b = x, 0, c
            else:
                r, g, b = c, 0, x
                
            r, g, b = (r + m) * 255, (g + m) * 255, (b + m) * 255
            self.line_colors.append((int(r), int(g), int(b)))
        
        # Añadir algunos elementos decorativos según el nivel
        if level % 5 == 0:  # Cada 5 niveles, un patrón especial
            for i in range(0, self.screen_height, 40):
                pygame.draw.rect(self.background, self.line_colors[0], 
                                (0, i, self.screen_width, 2))
                
        if level % 3 == 0:  # Cada 3 niveles, otro patrón
            for i in range(0, self.screen_width, 40):
                pygame.draw.rect(self.background, self.line_colors[1], 
                                (i, 0, 2, self.screen_height))
        
        # Generar tetrominos de fondo
        self.tetromino_shapes = []
        
        # Limit number of shapes based on level to prevent performance issues
        num_shapes = min(5 + level // 2, self.max_shapes)  # Cap at max_shapes
        debugger.debug(f"Adding {num_shapes} background tetrominos")
        
        try:
            for _ in range(num_shapes):
                shape_type = random.randint(0, 6)  # 7 tipos de tetrominos
                rotation = random.randint(0, 3)  # 4 rotaciones posibles
                x = random.randint(-50, self.screen_width)
                y = random.randint(-50, self.screen_height)
                scale = random.uniform(0.5, 2.0)
                alpha = random.randint(20, 60)
                
                # Safety check - don't make speed too high at high levels
                base_speed = random.uniform(0.1, 0.3)
                level_multiplier = min(1 + level * 0.05, 2.0)  # Cap speed increase
                speed = base_speed * level_multiplier
                
                self.tetromino_shapes.append({
                    'type': shape_type,
                    'rotation': rotation,
                    'x': x,
                    'y': y,
                    'scale': scale,
                    'alpha': alpha,
                    'speed': speed,
                    'direction': random.choice([-1, 1])
                })
            
            elapsed = time.time() - start_time
            if elapsed > 0.1:
                debugger.warning(f"Slow background generation: {elapsed:.4f}s")
                
        except Exception as e:
            debugger.error(f"Error generating background tetrominos: {str(e)}")
            debugger.error(traceback.format_exc())
    
    def update(self, level):
        """Actualiza el fondo si el nivel ha cambiado"""
        try:
            if level != self.current_level:
                debugger.debug(f"Background level changing from {self.current_level} to {level}")
                self.generate_background(level)
                
            # Actualizar desplazamiento para animación
            self.pattern_offset = (self.pattern_offset + 0.2) % 40
            
            # Skip tetromino animation if disabled
            if 'tetromino_animation' in self.disabled_features:
                return
                
            # Limit the number of tetrominos that can be updated per frame
            max_updates = min(len(self.tetromino_shapes), 30)
            
            # Actualizar animación de tetrominos
            for i in range(max_updates):
                shape = self.tetromino_shapes[i]
                shape['y'] += shape['speed'] * shape['direction']
                if shape['y'] < -100 or shape['y'] > self.screen_height + 100:
                    shape['direction'] *= -1  # Invertir dirección
                    
        except Exception as e:
            self.error_count += 1
            debugger.error(f"Error in background update: {str(e)}")
            
            # If we have multiple errors, start disabling features
            if self.error_count > 3:
                debugger.warning("Disabling background tetromino animation due to errors")
                self.disabled_features.add('tetromino_animation')
    
    def draw(self, screen):
        """Dibuja el fondo en pantalla"""
        try:
            start_time = time.time()
            
            # Primero dibuja el fondo base
            screen.blit(self.background, (0, 0))
            
            # Skip tetromino drawing if disabled
            if 'tetromino_drawing' not in self.disabled_features:
                # Limit the number of tetrominos that can be drawn per frame
                max_draws = min(len(self.tetromino_shapes), 20)
                
                # Dibujar tetrominos en el fondo
                for i in range(max_draws):
                    shape = self.tetromino_shapes[i]
                    try:
                        block_size = 15 * shape['scale']  # Tamaño más pequeño para el fondo
                        
                        # Skip if block_size is invalid
                        if not (1 <= block_size <= 50):
                            continue
                        
                        # Crear una superficie para el tetromino con transparencia
                        shape_surface = pygame.Surface((6 * block_size, 6 * block_size), pygame.SRCALPHA)
                        
                        # Dibujar tetromino en la superficie
                        self.tetromino_visualizer.draw_shape(
                            shape_surface,
                            shape['type'],
                            shape['rotation'],
                            block_size,
                            block_size,
                            block_size,
                            alpha=shape['alpha']
                        )
                        
                        # Dibujar la superficie en la pantalla
                        screen.blit(shape_surface, (shape['x'], shape['y']))
                    except Exception as e:
                        debugger.error(f"Error drawing background tetromino: {str(e)}")
            
            # Skip pattern lines if disabled
            if 'pattern_lines' not in self.disabled_features:
                # Luego dibuja líneas móviles para animación
                offset = int(self.pattern_offset)
                for i in range(-offset, self.screen_width, 40):
                    pygame.draw.line(screen, self.line_colors[2], 
                                (i + offset, 0), (i + offset + self.screen_height, self.screen_height),
                                1)
            
            # Track performance
            elapsed = time.time() - start_time
            if elapsed > 0.03:  # More than 30ms is too slow for background drawing
                debugger.warning(f"Slow background drawing: {elapsed:.4f}s")
                
                # Disable features if drawing is consistently slow
                if 'tetromino_drawing' not in self.disabled_features:
                    debugger.warning("Disabling background tetrominos due to performance")
                    self.disabled_features.add('tetromino_drawing')
                elif 'pattern_lines' not in self.disabled_features:
                    debugger.warning("Disabling pattern lines due to performance")
                    self.disabled_features.add('pattern_lines')
                    
        except Exception as e:
            debugger.error(f"Error in background drawing: {str(e)}")
            debugger.error(traceback.format_exc())
            # Disable all background features on error
            self.disabled_features.add('tetromino_drawing')
            self.disabled_features.add('pattern_lines')


class ShapeEffects:
    """Efectos visuales específicos para las piezas de Tetris"""
    def __init__(self):
        self.tetromino_visualizer = TetrominoVisualizer()
    
    def draw_tetromino_shadow(self, screen, shape_type, rotation, x, y, block_size=30, alpha=40):
        """Dibuja una sombra detrás del tetromino para dar efecto de profundidad"""
        offset = 3  # Píxeles de desplazamiento para la sombra
        
        # Primero dibujar la sombra
        self.tetromino_visualizer.draw_shape(
            screen,
            shape_type,
            rotation,
            x + offset,
            y + offset,
            block_size,
            alpha=alpha
        )
        
        # Luego dibujar el tetromino
        self.tetromino_visualizer.draw_shape(
            screen,
            shape_type,
            rotation,
            x,
            y,
            block_size
        )
    
    def draw_tetromino_trail(self, screen, shape_type, rotation, x, y, block_size=30, trail_length=5):
        """Dibuja un efecto de estela tras el tetromino"""
        for i in range(trail_length, 0, -1):
            offset_y = i * 3  # Espacio entre cada imagen de estela
            alpha = 200 - (i * 30)  # Disminuir opacidad para estelas más lejanas
            
            self.tetromino_visualizer.draw_shape(
                screen,
                shape_type,
                rotation,
                x,
                y - offset_y,
                block_size,
                alpha=alpha
            )
    
    def draw_landing_effect(self, screen, shape_type, rotation, x, y, block_size=30, frame=0):
        """Dibuja un efecto de aterrizaje cuando la pieza toca el suelo"""
        max_frames = 10
        if frame >= max_frames:
            return False  # Animación terminada
        
        # Calcular factor de escala basado en el frame actual
        scale_factor = 1.0 + (frame / max_frames) * 0.3
        
        # Calcular alfa basado en el frame actual
        alpha = 255 - int((frame / max_frames) * 200)
        
        # Calcular nuevo tamaño de bloque y desplazamiento para centrar
        new_block_size = block_size * scale_factor
        offset = (new_block_size - block_size) / 2
        
        # Dibujar forma escalada y con transparencia
        self.tetromino_visualizer.draw_shape(
            screen,
            shape_type,
            rotation,
            x - offset,
            y - offset,
            new_block_size,
            alpha=alpha
        )
        
        return True  # Animación en curso