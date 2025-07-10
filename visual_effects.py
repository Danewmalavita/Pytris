# visual_effects.py
# Módulo para efectos visuales en el juego Tetris

import pygame
import random
import math

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
        
    def add_particles_for_line_clear(self, x, y, width, color, count=20):
        """Añade partículas para el efecto de eliminación de línea"""
        for _ in range(count):
            particle_x = random.randint(x, x + width)
            self.particles.append(Particle(
                particle_x, y, 
                color,
                velocity_x=random.uniform(-2, 2),
                velocity_y=random.uniform(-3, -1)
            ))
    
    def update(self):
        """Actualiza todas las partículas y elimina las que han expirado"""
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()
    
    def draw(self, screen, offset_x=0, offset_y=0):
        """Dibuja todas las partículas en pantalla"""
        for particle in self.particles:
            particle.draw(screen, offset_x, offset_y)


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
        
    def add_combo(self, lines_cleared):
        """Registra un nuevo combo"""
        self.combo_count += 1
        self.combo_timer = self.combo_timeout
        self.text_scale = 1.5  # Empieza grande y se reduce
        self.display_time = 60  # Mostrar durante 1 segundo
        
    def update(self):
        """Actualiza el estado de la animación de combo"""
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer == 0:
                self.combo_count = 0
                
        if self.display_time > 0:
            self.display_time -= 1
            # Reducir la escala gradualmente
            if self.text_scale > 1.0:
                self.text_scale -= 0.025
        
    def draw(self, screen, center_x, center_y):
        """Dibuja la animación de combo en pantalla"""
        if self.combo_count > 1 and self.display_time > 0:
            font_size = int(32 * self.text_scale)
            font = pygame.font.SysFont("Arial", font_size, bold=True)
            
            # Color basado en el tamaño del combo
            if self.combo_count < 3:
                color = (255, 255, 100)
            elif self.combo_count < 5:
                color = (255, 150, 50)
            else:
                color = (255, 50, 50)
                
            text = font.render(f"COMBO x{self.combo_count}!", True, color)
            text_rect = text.get_rect(center=(center_x, center_y))
            
            # Añadir un poco de oscilación vertical
            bounce = math.sin(pygame.time.get_ticks() * 0.01) * 5
            text_rect.centery += bounce
            
            # Dibujar sombra para mejor visibilidad
            shadow = font.render(f"COMBO x{self.combo_count}!", True, (0, 0, 0))
            shadow_rect = shadow.get_rect(center=(center_x + 2, center_y + 2))
            screen.blit(shadow, shadow_rect)
            
            screen.blit(text, text_rect)


class DynamicBackground:
    """Fondo dinámico que cambia según el nivel"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_level = 0
        self.background = None
        self.pattern_offset = 0
        self.line_colors = []
        self.generate_background(1)
        
    def generate_background(self, level):
        """Genera un nuevo fondo basado en el nivel"""
        self.current_level = level
        self.background = pygame.Surface((self.screen_width, self.screen_height))
        
        # Color base según nivel
        base_hue = (level * 30) % 360
        saturation = 50 + (level % 5) * 10
        value = 20 + (level % 3) * 5
        
        # Convertir HSV a RGB
        c = saturation * value / 10000
        x = c * (1 - abs((base_hue / 60) % 2 - 1))
        m = value / 100 - c
        
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
                
        # Dibujar algunas formas basadas en el nivel
        for i in range(level % 10 + 5):
            size = random.randint(20, 80)
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            color_idx = random.randint(0, len(self.line_colors) - 1)
            alpha = random.randint(20, 80)
            
            shape_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            if i % 3 == 0:  # círculos
                pygame.draw.circle(shape_surface, (*self.line_colors[color_idx], alpha), 
                                  (size//2, size//2), size//2)
            elif i % 3 == 1:  # cuadrados
                pygame.draw.rect(shape_surface, (*self.line_colors[color_idx], alpha), 
                                (0, 0, size, size))
            else:  # triángulos
                points = [(size//2, 0), (0, size), (size, size)]
                pygame.draw.polygon(shape_surface, (*self.line_colors[color_idx], alpha), 
                                   points)
                
            self.background.blit(shape_surface, (x, y))
    
    def update(self, level):
        """Actualiza el fondo si el nivel ha cambiado"""
        if level != self.current_level:
            self.generate_background(level)
            
        # Actualizar desplazamiento para animación
        self.pattern_offset = (self.pattern_offset + 0.2) % 40
    
    def draw(self, screen):
        """Dibuja el fondo en pantalla"""
        # Primero dibuja el fondo base
        screen.blit(self.background, (0, 0))
        
        # Luego dibuja líneas móviles para animación
        offset = int(self.pattern_offset)
        for i in range(-offset, self.screen_width, 40):
            pygame.draw.line(screen, self.line_colors[2], 
                           (i + offset, 0), (i + offset + self.screen_height, self.screen_height),
                           1)