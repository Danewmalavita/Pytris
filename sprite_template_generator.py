import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Create a new image with transparency
sprite_size = 30
num_sprites = 8
width = sprite_size * num_sprites
height = sprite_size

# Create a transparent image
template = Image.new('RGBA', (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(template)

# Define colors for each tetramino
colors = [
    (0, 0, 0, 0),      # Transparent (empty)
    (255, 0, 0, 255),  # Red - Z piece
    (0, 255, 0, 255),  # Green - S piece
    (0, 0, 255, 255),  # Blue - J piece
    (255, 255, 0, 255), # Yellow - O piece
    (0, 255, 255, 255), # Cyan - I piece
    (255, 0, 255, 255), # Magenta - T piece
    (255, 128, 0, 255), # Orange - L piece
]

# Draw each sprite block with a 3D effect
for i, color in enumerate(colors):
    x = i * sprite_size
    y = 0
    
    # If it's not the empty block
    if i > 0:
        # Main block color
        draw.rectangle([(x+2, y+2), (x+sprite_size-3, y+sprite_size-3)], 
                       fill=color)
        
        # Dark edges (bottom, right)
        dark_color = tuple(max(0, c - 80) for c in color[:3]) + (255,)
        draw.rectangle([(x+sprite_size-4, y+2), (x+sprite_size-2, y+sprite_size-3)], 
                      fill=dark_color)  # Right edge
        draw.rectangle([(x+2, y+sprite_size-4), (x+sprite_size-3, y+sprite_size-2)], 
                      fill=dark_color)  # Bottom edge
        
        # Highlight edges (top, left)
        light_color = tuple(min(255, c + 80) for c in color[:3]) + (255,)
        draw.rectangle([(x+1, y+2), (x+3, y+sprite_size-3)], 
                      fill=light_color)  # Left edge
        draw.rectangle([(x+2, y+1), (x+sprite_size-3, y+3)], 
                      fill=light_color)  # Top edge
        
        # Draw a thin border
        border_color = tuple(max(0, c - 50) for c in color[:3]) + (255,)
        draw.rectangle([(x+1, y+1), (x+sprite_size-2, y+sprite_size-2)], 
                      outline=border_color, width=1)
        
        # Add the sprite number as text
        try:
            font = ImageFont.truetype("Arial.ttf", 12)
        except IOError:
            font = ImageFont.load_default()
            
        draw.text((x + sprite_size//2, y + sprite_size//2), str(i), 
                 fill=(255, 255, 255, 200), font=font, anchor="mm")

# Save the template
template.save('templates/sprite_template.png')
template.save('templates/sprite_template_large.png', scale=3)  # Save a larger version for easier editing

# Save a version with grid lines to make editing easier
grid_template = template.copy()
draw = ImageDraw.Draw(grid_template)
for i in range(num_sprites+1):
    draw.line([(i * sprite_size, 0), (i * sprite_size, height)], fill=(128, 128, 128, 128))
draw.line([(0, 0), (width, 0)], fill=(128, 128, 128, 128))
draw.line([(0, height-1), (width, height-1)], fill=(128, 128, 128, 128))
grid_template.save('templates/sprite_template_grid.png')

print("Sprite templates generated in 'templates' folder.")