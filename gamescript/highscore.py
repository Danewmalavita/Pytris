# highscore.py
import os
import json
import pygame
from .menu import draw_text

# Constants
MAX_HIGH_SCORES = 10  # Maximum number of high scores to store
HIGHSCORE_FILE = "highscores.json"  # File to store high scores

def load_high_scores():
    """Load high scores from file"""
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            # If file is corrupted or can't be read, return empty list
            return []
    return []

def save_high_scores(high_scores):
    """Save high scores to file with proper error handling"""
    try:
        with open(HIGHSCORE_FILE, 'w') as file:
            json.dump(high_scores, file)
        return True
    except (IOError, OSError, PermissionError) as e:
        print(f"Error saving high scores: {e}")
        # Could display an error message to the user here
        return False

def is_high_score(score):
    """Check if a score qualifies as a high score"""
    high_scores = load_high_scores()
    
    # If we have fewer than MAX_HIGH_SCORES, any score qualifies
    if len(high_scores) < MAX_HIGH_SCORES:
        return True
    
    # Otherwise check if the score is higher than the lowest score in the list
    return score > min(high_scores, key=lambda x: x["score"])["score"] if high_scores else 0

def add_high_score(name, score, level, lines):
    """Add a new high score to the list with error handling"""
    high_scores = load_high_scores()
    
    # Add the new score
    new_entry = {
        "name": name,
        "score": score,
        "level": level,
        "lines": lines
    }
    high_scores.append(new_entry)
    
    # Sort by score (highest first)
    high_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # Keep only the top MAX_HIGH_SCORES
    high_scores = high_scores[:MAX_HIGH_SCORES]
    
    # Save back to file and check if it was successful
    save_success = save_high_scores(high_scores)
    
    if not save_success:
        # If saving failed, we can still return the position
        # but the score might not be persisted
        print("Warning: High score may not have been saved permanently.")
        # Could show a message to the player here
    
    # Return position in high score list (0-based)
    return high_scores.index(new_entry)

def get_player_name(screen, score):
    """Show screen for player to enter their name"""
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 32)
    name = ""
    
    # Importar el módulo de controles unificado
    from .controls import handle_highscore_input_controls
    
    # Load keyboard sound effects
    sfx_key = pygame.mixer.Sound("assets/sounds/sfx/cursor.wav")
    sfx_enter = pygame.mixer.Sound("assets/sounds/sfx/enter.wav")
    sfx_key.set_volume(0.5)
    sfx_enter.set_volume(0.5)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return ""
            
            # Usar el módulo de controles unificado para la entrada de nombre
            name, confirm, cancel = handle_highscore_input_controls(event, name, sfx_key, sfx_enter)
            
            if confirm:
                pygame.time.wait(100)  # Small delay to let the sound effect play
                return name
            elif cancel:
                # If ESC is pressed, use a default name
                sfx_enter.play()
                pygame.time.wait(100)
                return "Player"
        
        # Draw screen
        screen.fill((10, 10, 50))  # Same background color as menu
        
        draw_text(screen, "¡Nueva Puntuación Alta!", 48, (255, 255, 255), screen.get_width() // 2, 100)
        draw_text(screen, f"Tu Puntuación: {score}", 36, (255, 255, 255), screen.get_width() // 2, 170)
        draw_text(screen, "Introduce tu nombre:", 32, (255, 255, 255), screen.get_width() // 2, 240)
        
        # Draw text input box
        input_rect = pygame.Rect(screen.get_width() // 2 - 150, 300, 300, 50)
        pygame.draw.rect(screen, (200, 200, 200), input_rect, 2)
        
        # Draw entered name
        name_surface = font.render(name + "▌", True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=input_rect.center)
        screen.blit(name_surface, name_rect)
        
        draw_text(screen, "Presiona ENTER para continuar", 24, (180, 180, 180), screen.get_width() // 2, 380)
        
        pygame.display.flip()
        clock.tick(60)

def show_high_scores(screen, settings, current_score=None):
    """Display the high scores screen"""
    clock = pygame.time.Clock()
    high_scores = load_high_scores()
    
    # Importar el módulo de controles unificado
    from .controls import handle_highscore_view_controls
    
    # Load sound effects
    sfx_cursor = pygame.mixer.Sound("assets/sounds/sfx/cursor.wav")
    sfx_back = pygame.mixer.Sound("assets/sounds/sfx/back.wav")
    
    # Adjust volume based on settings
    sfx_vol = 0 if settings['mute'] else (settings['volume_general'] * settings['volume_sfx'])
    sfx_cursor.set_volume(sfx_vol)
    sfx_back.set_volume(sfx_vol)
    
    # Determine if the current score made it to the high scores list
    highlight_position = None
    if current_score is not None:
        for i, score in enumerate(high_scores):
            if score["score"] == current_score:
                highlight_position = i
                break
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Signal to quit the game
            
            # Usar el módulo de controles unificado para ver puntuaciones
            exit_view = handle_highscore_view_controls(event, sfx_back)
            if exit_view:
                running = False
        
        # Draw screen
        screen.fill((10, 10, 50))  # Same background color as menu
        
        draw_text(screen, "PUNTUACIONES ALTAS", 48, (255, 255, 255), screen.get_width() // 2, 80)
        
        if not high_scores:
            draw_text(screen, "No hay puntuaciones guardadas", 32, (180, 180, 180), screen.get_width() // 2, 250)
        else:
            # Draw table headers
            draw_text(screen, "POSICIÓN", 28, (200, 200, 200), screen.get_width() // 2 - 180, 150)
            draw_text(screen, "NOMBRE", 28, (200, 200, 200), screen.get_width() // 2, 150)
            draw_text(screen, "PUNTUACIÓN", 28, (200, 200, 200), screen.get_width() // 2 + 180, 150)
            
            # Draw horizontal separator line
            pygame.draw.line(screen, (100, 100, 100), 
                            (screen.get_width() // 2 - 300, 170), 
                            (screen.get_width() // 2 + 300, 170), 2)
            
            # Draw high scores
            for i, score in enumerate(high_scores):
                y_pos = 200 + i * 35
                
                # Highlight the player's score if it matches
                color = (255, 255, 0) if i == highlight_position else (255, 255, 255)
                
                # Position column
                draw_text(screen, f"{i + 1}.", 24, color, screen.get_width() // 2 - 180, y_pos)
                
                # Name column
                draw_text(screen, score["name"], 24, color, screen.get_width() // 2, y_pos)
                
                # Score column
                draw_text(screen, f"{score['score']}", 24, color, screen.get_width() // 2 + 180, y_pos)
        
        draw_text(screen, "Presiona ESCAPE o ENTER para volver", 24, (180, 180, 180), screen.get_width() // 2, screen.get_height() - 80)
        
        pygame.display.flip()
        clock.tick(60)
    
    return True  # Continue the game