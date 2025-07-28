import pygame
import sys
import time
import math

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
WIDTH = 1000
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PYTRIS - Logo Tetris Mejorado")

# Colores de los tetrominós clásicos más vibrantes
COLORS = {
    'I': (0, 255, 255),    # Cian
    'O': (255, 255, 0),    # Amarillo
    'T': (160, 32, 240),   # Púrpura
    'S': (0, 255, 0),      # Verde
    'Z': (255, 0, 0),      # Rojo
    'J': (0, 100, 255),    # Azul
    'L': (255, 165, 0),    # Naranja
    'bg': (15, 15, 35),    # Fondo más oscuro
    'border': (100, 100, 100)
}

# Tamaño del bloque más grande
BLOCK_SIZE = 20

def draw_block(surface, x, y, color):
    """Dibujar un bloque individual con efecto 3D mejorado"""
    rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
    
    # Bloque principal
    pygame.draw.rect(surface, color, rect)
    
    # Borde superior e izquierdo (más claro)
    light_color = tuple(min(255, c + 60) for c in color)
    pygame.draw.line(surface, light_color, rect.topleft, rect.topright, 2)
    pygame.draw.line(surface, light_color, rect.topleft, rect.bottomleft, 2)
    
    # Borde inferior y derecho (más oscuro)
    dark_color = tuple(max(0, c - 60) for c in color)
    pygame.draw.line(surface, dark_color, rect.bottomleft, rect.bottomright, 2)
    pygame.draw.line(surface, dark_color, rect.topright, rect.bottomright, 2)
    
    # Borde negro fino
    pygame.draw.rect(surface, (0, 0, 0), rect, 1)

def draw_letter_blocks(surface, blocks, color, offset_x, offset_y):
    """Dibujar una letra usando una matriz de bloques"""
    for row_idx, row in enumerate(blocks):
        for col_idx, cell in enumerate(row):
            if cell == 1:
                draw_block(surface, offset_x + col_idx, offset_y + row_idx, color)

def create_pytris_logo():
    """Crear el logo PYTRIS mejorado"""
    clock = pygame.time.Clock()
    
    # Definir cada letra como una matriz de bloques (más parecido a la imagen)
    letters = {
        'P': {
            'blocks': [
                [1, 1, 1, 1],
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [1, 1, 1, 1],
                [1, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 0, 0, 0]
            ],
            'color': COLORS['T']
        },
        'Y': {
            'blocks': [
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0]
            ],
            'color': COLORS['O']
        },
        'T': {
            'blocks': [
                [1, 1, 1, 1, 1],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0]
            ],
            'color': COLORS['I']
        },
        'R': {
            'blocks': [
                [1, 1, 1, 1],
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [1, 1, 1, 1],
                [1, 1, 0, 0],
                [1, 0, 1, 0],
                [1, 0, 0, 1],
                [1, 0, 0, 1]
            ],
            'color': COLORS['S']
        },
        'I': {
            'blocks': [
                [1, 1, 1],
                [0, 1, 0],
                [0, 1, 0],
                [0, 1, 0],
                [0, 1, 0],
                [0, 1, 0],
                [0, 1, 0],
                [1, 1, 1]
            ],
            'color': COLORS['Z']
        },
        'S': {
            'blocks': [
                [1, 1, 1, 1],
                [1, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 1, 1, 0],
                [0, 0, 0, 1],
                [0, 0, 0, 1],
                [0, 0, 0, 1],
                [1, 1, 1, 1]
            ],
            'color': COLORS['L']
        }
    }
    
    # Posiciones de las letras (más espaciadas)
    letter_positions = [
        ('P', 50, 150),
        ('Y', 140, 150),
        ('T', 230, 150),
        ('R', 330, 150),
        ('I', 430, 150),
        ('S', 500, 150)
    ]
    
    # Variables de animación
    current_letter = 0
    animation_timer = 0
    animation_speed = 400  # millisegundos entre letras
    bg_animation = 0
    show_glow = False
    glow_timer = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Reiniciar animación
                    current_letter = 0
                    animation_timer = 0
                    show_glow = False
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        # Actualizar animación
        current_time = pygame.time.get_ticks()
        if current_time - animation_timer > animation_speed and current_letter < len(letter_positions):
            current_letter += 1
            animation_timer = current_time
        
        # Fondo animado
        bg_animation += 1
        bg_color = (
            15 + int(8 * abs(math.sin(bg_animation * 0.008))),
            15 + int(8 * abs(math.sin(bg_animation * 0.010))),
            35 + int(15 * abs(math.sin(bg_animation * 0.012)))
        )
        screen.fill(bg_color)
        
        
        # Dibujar letras que ya han aparecido
        for i in range(min(current_letter, len(letter_positions))):
            letter_name, x, y = letter_positions[i]
            letter_data = letters[letter_name]
            
            # Efecto de aparición con escala
            if i == current_letter - 1 and current_time - animation_timer < 200:
                # Letra recién aparecida con efecto de escala
                scale_factor = 1.2 - 0.2 * ((current_time - animation_timer) / 200)
                scaled_blocks = letter_data['blocks']
                scaled_x = x - int((len(scaled_blocks[0]) * BLOCK_SIZE * (scale_factor - 1)) / 2)
                scaled_y = y - int((len(scaled_blocks) * BLOCK_SIZE * (scale_factor - 1)) / 2)
                
                # Dibujar con color más brillante
                bright_color = tuple(min(255, c + 50) for c in letter_data['color'])
                draw_letter_blocks(screen, scaled_blocks, bright_color, scaled_x // BLOCK_SIZE, scaled_y // BLOCK_SIZE)
            else:
                draw_letter_blocks(screen, letter_data['blocks'], letter_data['color'], x // BLOCK_SIZE, y // BLOCK_SIZE)
        

        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

def generate_static_logo():
    """Generar una imagen estática del logo mejorado"""
    logo_surface = pygame.Surface((600, 200))
    logo_surface.fill(COLORS['bg'])
    
    # Definir letras para logo estático
    letters = {
        'P': {
            'blocks': [
                [1, 1, 1, 1, 0],
                [1, 0, 0, 1, 0],
                [1, 0, 0, 1, 0],
                [1, 1, 1, 1, 0],
                [1, 0, 0, 0, 0],
                [1, 0, 0, 0, 0]
            ],
            'color': COLORS['T']
        },
        'Y': {
            'blocks': [
                [1, 0, 0, 1, 0],
                [1, 0, 0, 1, 0],
                [0, 1, 1, 0, 0],
                [0, 1, 1, 0, 0],
                [0, 1, 1, 0, 0],
                [0, 1, 1, 0, 0]
            ],
            'color': COLORS['O']
        },
        'T': {
            'blocks': [
                [0, 1, 1, 1, 1, 1, 0],
                [0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0]
            ],
            'color': COLORS['I']
        },
        'R': {
            'blocks': [
                [1, 1, 1, 1, 0],
                [1, 0, 0, 1, 0],
                [1, 1, 1, 1, 0],
                [1, 1, 0, 0, 0],
                [1, 0, 1, 0, 0],
                [1, 0, 0, 1, 0]
            ],
            'color': COLORS['S']
        },
        'I': {
            'blocks': [
                [1, 1, 1, 0],
                [0, 1, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 0, 0],
                [1, 1, 1, 0]
            ],
            'color': COLORS['Z']
        },
        'S': {
            'blocks': [
                [1, 1, 1, 1],
                [1, 0, 0, 0],
                [1, 1, 1, 0],
                [0, 0, 0, 1],
                [0, 0, 0, 1],
                [1, 1, 1, 1]
            ],
            'color': COLORS['L']
        }
    }
    
    # Posiciones para logo estático
    letter_positions = [
        ('P', 10, 50),
        ('Y', 90, 50),
        ('T', 170, 50),
        ('R', 270, 50),
        ('I', 370, 50),
        ('S', 430, 50)
    ]
    
    # Dibujar todas las letras
    for letter_name, x, y in letter_positions:
        letter_data = letters[letter_name]
        draw_letter_blocks(logo_surface, letter_data['blocks'], letter_data['color'], x // BLOCK_SIZE, y // BLOCK_SIZE)
    
    return logo_surface

if __name__ == "__main__":

    create_pytris_logo()