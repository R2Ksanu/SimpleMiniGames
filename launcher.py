import pygame
import subprocess
import sys
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Window settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SimpleMiniGames Launcher")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
PASTEL_BLUE = (173, 216, 230)  # Background color
PASTEL_PINK = (255, 182, 193)  # Hover color

# Load font
try:
    font = pygame.font.Font("LauncherAssets/PressStart2P-Regular.ttf", 24)
    small_font = pygame.font.Font("LauncherAssets/PressStart2P-Regular.ttf", 16)
except FileNotFoundError:
    font = pygame.font.SysFont("monospace", 24)
    small_font = pygame.font.SysFont("monospace", 16)
    print("Font not found, using default font")

# Load background music
music_playing = True
try:
    pygame.mixer.music.load("LauncherAssets/pixel_peeker_polka_faster.wav")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # Loop indefinitely
    print("Background music loaded: pixel_peeker_polka_faster.wav")
except pygame.error as e:
    print(f"Failed to load background music: {e}")
    music_playing = False

# Button class for interactive buttons
class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.action = action
        self.text_surface = font.render(text, True, BLACK)

    def draw(self, surface):
        # Check if mouse is hovering over the button
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, self.hover_color, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
        # Center the text on the button
        text_rect = self.text_surface.get_rect(center=self.rect.center)
        surface.blit(self.text_surface, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.rect.collidepoint(event.pos):
                self.action()

# Actions for each button
def launch_car_game():
    global music_playing
    # Stop the launcher music before starting the game
    if music_playing:
        pygame.mixer.music.pause()
        music_playing = False
    # Launch the game
    subprocess.run([sys.executable, "CarGame/car_game.py"])
    # Resume the launcher music after the game exits
    pygame.mixer.music.unpause()
    music_playing = True

def launch_snake_game():
    global music_playing
    # Stop the launcher music before starting the game
    if music_playing:
        pygame.mixer.music.pause()
        music_playing = False
    # Launch the game
    subprocess.run([sys.executable, "SnakeGame/snake_game.py"])
    # Resume the launcher music after the game exits
    pygame.mixer.music.unpause()
    music_playing = True

def launch_flappy_bird():
    global music_playing
    # Stop the launcher music before starting the game
    if music_playing:
        pygame.mixer.music.pause()
        music_playing = False
    # Launch the game
    subprocess.run([sys.executable, "FlappyBird/flappy_bird.py"])
    # Resume the launcher music after the game exits
    pygame.mixer.music.unpause()
    music_playing = True

def toggle_music():
    global music_playing
    if music_playing:
        pygame.mixer.music.pause()
        music_playing = False
    else:
        pygame.mixer.music.unpause()
        music_playing = True

# Create buttons
button_width, button_height = 300, 50
button_spacing = 20
start_y = HEIGHT // 2 - 100

car_game_button = Button("Car Game", WIDTH // 2 - button_width // 2, start_y, button_width, button_height, WHITE, PASTEL_PINK, launch_car_game)
snake_game_button = Button("Snake Game", WIDTH // 2 - button_width // 2, start_y + button_height + button_spacing, button_width, button_height, WHITE, PASTEL_PINK, launch_snake_game)
flappy_bird_button = Button("Flappy Bird", WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height, WHITE, PASTEL_PINK, launch_flappy_bird)
music_button = Button("Music: ON", WIDTH // 2.5 - 31, HEIGHT - 80, 220, 38, WHITE, PASTEL_PINK, toggle_music)

# Title text
title_text = font.render("SimpleMiniGames", True, WHITE)
title_rect = title_text.get_rect(center=(WIDTH // 2, 100))

# Attribution text
attribution_text = small_font.render('Music: "Pixel Peeker Polka-faster"by Kevin MacLeod', True, WHITE)
attribution_rect = attribution_text.get_rect(center=(WIDTH // 2, HEIGHT - 11))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Check for button clicks
        car_game_button.check_click(event)
        snake_game_button.check_click(event)
        flappy_bird_button.check_click(event)
        music_button.check_click(event)

    # Update music button text
    music_button.text = "Music: " + ("ON" if music_playing else "OFF")
    music_button.text_surface = small_font.render(music_button.text, True, BLACK)

    # Draw the screen
    screen.fill(PASTEL_BLUE)  # Background color
    screen.blit(title_text, title_rect)
    car_game_button.draw(screen)
    snake_game_button.draw(screen)
    flappy_bird_button.draw(screen)
    music_button.draw(screen)
    screen.blit(attribution_text, attribution_rect)

    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()