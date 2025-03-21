import pygame
import subprocess
import sys
import os
import random
import time
import json

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
PASTEL_BLUE = (173, 216, 230)  # Fallback background color
PASTEL_PINK = (255, 182, 193)  # Hover color
SHADOW_COLOR = (80, 80, 80)  # Lighter shadow for better contrast
BUTTON_COLOR = (255, 165, 0)  # Orange color for buttons
OVERLAY_COLOR = (50, 50, 50, 200)  # Semi-transparent overlay

# Load fonts
try:
    font = pygame.font.Font("LauncherAssets/PressStart2P-Regular.ttf", 24)  # For title
    button_font = pygame.font.Font("LauncherAssets/PressStart2P-Regular.ttf", 18)  # For buttons
    small_font = pygame.font.Font("LauncherAssets/PressStart2P-Regular.ttf", 16)  # For attribution and slider
    print("Custom font loaded: PressStart2P-Regular.ttf")
except FileNotFoundError:
    font = pygame.font.SysFont("monospace", 21, bold=True)
    button_font = pygame.font.SysFont("monospace", 18, bold=True)
    small_font = pygame.font.SysFont("monospace", 16, bold=True)
    print("Font not found, using default font")

# Load textures
try:
    background_image = pygame.image.load("LauncherAssets/background.png").convert()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    print("Background image loaded: background.png")
except FileNotFoundError:
    background_image = None
    print("Background image not found, using default color")

button_normal = None
button_hover = None

# Load game preview images
try:
    car_game_preview = pygame.image.load("LauncherAssets/car_game_preview.png").convert_alpha()
    car_game_preview = pygame.transform.scale(car_game_preview, (200, 150))
    snake_game_preview = pygame.image.load("LauncherAssets/snake_game_preview.png").convert_alpha()
    snake_game_preview = pygame.transform.scale(snake_game_preview, (200, 150))
    flappy_bird_preview = pygame.image.load("LauncherAssets/flappy_bird_preview.png").convert_alpha()
    flappy_bird_preview = pygame.transform.scale(flappy_bird_preview, (200, 150))
    print("Game preview images loaded")
except FileNotFoundError:
    car_game_preview = None
    snake_game_preview = None
    flappy_bird_preview = None
    print("Game preview images not found, previews will not be displayed")

# Load particle texture (optional)
try:
    particle_image = pygame.image.load("LauncherAssets/particle.png").convert_alpha()
    particle_image = pygame.transform.scale(particle_image, (5, 5))
    print("Particle image loaded: particle.png")
except FileNotFoundError:
    particle_image = None
    print("Particle image not found, using default circle")

# Load background music
music_playing = True
music_volume = 0.5
try:
    pygame.mixer.music.load("LauncherAssets/pixel_peeker_polka_faster.wav")
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1)  # Loop indefinitely
    print("Background music loaded: pixel_peeker_polka_faster.wav")
except pygame.error as e:
    print(f"Failed to load background music: {e}")
    music_playing = False

# Load sound effects
try:
    click_sound = pygame.mixer.Sound("LauncherAssets/click.wav")
    click_sound.set_volume(0.5)
    print("Click sound loaded: click.wav")
except FileNotFoundError:
    click_sound = None
    print("Click sound not found")

# Particle class for background effects
class Particle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed_x = random.uniform(-1, 1)
        self.speed_y = random.uniform(-1, 1)
        self.lifetime = random.randint(60, 120)  # Frames

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
        if self.x < 0:
            self.x = WIDTH
        elif self.x > WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = HEIGHT
        elif self.y > HEIGHT:
            self.y = 0

    def draw(self, surface):
        if particle_image:
            surface.blit(particle_image, (int(self.x), int(self.y)))
        else:
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 2)

# Button class with sound effects
class Button:
    def __init__(self, text, x, y, width, height, action, preview_image=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.preview_image = preview_image
        self.text_surface = button_font.render(text, True, WHITE)
        self.text_shadow = button_font.render(text, True, SHADOW_COLOR)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if button_hover:
                surface.blit(button_hover, self.rect.topleft)
            else:
                pygame.draw.rect(surface, PASTEL_PINK, self.rect, border_radius=10)
        else:
            if button_normal:
                surface.blit(button_normal, self.rect.topleft)
            else:
                pygame.draw.rect(surface, BUTTON_COLOR, self.rect, border_radius=10)
        text_rect = self.text_surface.get_rect(center=self.rect.center)
        shadow_rect = self.text_shadow.get_rect(center=(text_rect.centerx + 3, text_rect.centery + 3))
        surface.blit(self.text_shadow, shadow_rect)
        surface.blit(self.text_surface, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if click_sound:
                    click_sound.play()
                self.action()
                return True
        return False

# Slider class for volume control
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.handle_rect = pygame.Rect(x + (initial_val / max_val) * width - 5, y - 5, 10, height + 10)
        self.dragging = False
        self.label = small_font.render("Volume", True, WHITE)
        self.label_shadow = small_font.render("Volume", True, SHADOW_COLOR)

    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect)
        pygame.draw.rect(surface, WHITE, self.handle_rect)
        label_rect = self.label.get_rect(midright=(self.rect.left - 10, self.rect.centery))
        shadow_rect = self.label_shadow.get_rect(midright=(label_rect.left + 3, label_rect.centery + 3))
        surface.blit(self.label_shadow, shadow_rect)
        surface.blit(self.label, label_rect)

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_x = event.pos[0]
            self.handle_rect.x = max(self.rect.left, min(mouse_x - self.handle_rect.width // 2, self.rect.right - self.handle_rect.width))
            self.value = self.min_val + (self.handle_rect.x - self.rect.x) / self.rect.width * (self.max_val - self.min_val)
            pygame.mixer.music.set_volume(self.value)

# Loading screen function
def show_loading_screen(game_name):
    # Create semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(OVERLAY_COLOR)
    screen.blit(overlay, (0, 0))

    # Animate loading text with dots
    for i in range(3):  # Show for 3 frames (0.5 seconds total at 60 FPS)
        screen.blit(overlay, (0, 0))
        loading_text = small_font.render(f"Loading {game_name}" + "." * (i + 1), True, WHITE)
        loading_shadow = small_font.render(f"Loading {game_name}" + "." * (i + 1), True, SHADOW_COLOR)
        loading_rect = loading_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        shadow_rect = loading_shadow.get_rect(center=(loading_rect.centerx + 3, loading_rect.centery + 3))
        screen.blit(loading_shadow, shadow_rect)
        screen.blit(loading_text, loading_rect)
        pygame.display.flip()
        pygame.time.delay(200)  # Delay for 200ms per frame

# Actions for each button
def launch_car_game():
    global music_playing
    show_loading_screen("Car Game")
    if music_playing:
        pygame.mixer.music.pause()
        music_playing = False
    subprocess.run([sys.executable, "CarGame/car_game.py"])
    pygame.mixer.music.unpause()
    music_playing = True

def launch_snake_game():
    global music_playing
    show_loading_screen("Snake Game")
    if music_playing:
        pygame.mixer.music.pause()
        music_playing = False
    subprocess.run([sys.executable, "SnakeGame/snake_game.py"])
    pygame.mixer.music.unpause()
    music_playing = True

def launch_flappy_bird():
    global music_playing
    show_loading_screen("Flappy Bird")
    if music_playing:
        pygame.mixer.music.pause()
        music_playing = False
    subprocess.run([sys.executable, "FlappyBird/flappy_bird.py"])
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

def show_settings():
    global current_menu
    current_menu = "settings"

def back_to_main():
    global current_menu
    current_menu = "main"

def show_quit_dialog():
    global current_menu
    current_menu = "quit_dialog"

def confirm_quit():
    pygame.quit()
    sys.exit()

# Create buttons
button_width, button_height = 200, 40
button_spacing = 15
start_y = HEIGHT // 2 - 80

# Main menu buttons
car_game_button = Button("Car Game", WIDTH // 2 - button_width // 2, start_y, button_width, button_height, launch_car_game, car_game_preview)
snake_game_button = Button("Snake Game", WIDTH // 2 - button_width // 2, start_y + button_height + button_spacing, button_width, button_height, launch_snake_game, snake_game_preview)
flappy_bird_button = Button("Flappy Bird", WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height, launch_flappy_bird, flappy_bird_preview)
settings_button = Button("Settings", WIDTH // 2 - button_width // 2, start_y + 3 * (button_height + button_spacing), button_width, button_height, show_settings)
quit_button = Button("Quit", WIDTH // 2 - button_width // 2, start_y + 4 * (button_height + button_spacing), button_width, button_height, show_quit_dialog)

# Settings menu buttons
music_toggle_button = Button("Music: ON", WIDTH // 2 - button_width // 2, HEIGHT // 2 - 50, button_width, button_height, toggle_music)
volume_slider = Slider(WIDTH // 2 - 100, HEIGHT // 2, 200, 10, 0.0, 1.0, music_volume)
back_button = Button("Back", WIDTH // 2 - button_width // 2, HEIGHT // 2 + 50, button_width, button_height, back_to_main)

# Quit dialog buttons
quit_yes_button = Button("Yes", WIDTH // 2 - button_width - 20, HEIGHT // 2 + 20, button_width, button_height, confirm_quit)
quit_no_button = Button("No", WIDTH // 2 + 20, HEIGHT // 2 + 20, button_width, button_height, back_to_main)

# Title with animation
title_text = font.render("SimpleMiniGames", True, WHITE)
title_shadow = font.render("SimpleMiniGames", True, SHADOW_COLOR)
title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
title_alpha = 255
title_fade_direction = -1

# Settings title
settings_title = font.render("Settings", True, WHITE)
settings_title_shadow = font.render("Settings", True, SHADOW_COLOR)
settings_title_rect = settings_title.get_rect(center=(WIDTH // 2, 150))

# Quit dialog title
quit_dialog_title = font.render("Are you sure you want to quit?", True, WHITE)
quit_dialog_title_shadow = font.render("Are you sure you want to quit?", True, SHADOW_COLOR)
quit_dialog_title_rect = quit_dialog_title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))

# Attribution text
attribution_text = small_font.render('Music: "Pixel Peeker Polka-faster" by Kevin MacLeod', True, WHITE)
attribution_shadow = small_font.render('Music: "Pixel Peeker Polka-faster" by Kevin MacLeod', True, SHADOW_COLOR)
attribution_rect = attribution_text.get_rect(center=(WIDTH // 2, HEIGHT - 20))

# Game preview display
selected_game_preview = None

# Particle effects
particles = [Particle() for _ in range(20)]

# Menu state
current_menu = "main"

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Handle button clicks based on current menu
        if current_menu == "main":
            if car_game_button.check_click(event):
                selected_game_preview = car_game_preview
            if snake_game_button.check_click(event):
                selected_game_preview = snake_game_preview
            if flappy_bird_button.check_click(event):
                selected_game_preview = flappy_bird_preview
            settings_button.check_click(event)
            quit_button.check_click(event)
        elif current_menu == "settings":
            music_toggle_button.check_click(event)
            volume_slider.update(event)
            back_button.check_click(event)
        elif current_menu == "quit_dialog":
            quit_yes_button.check_click(event)
            quit_no_button.check_click(event)

    # Update particles
    for particle in particles:
        particle.update()
        if particle.lifetime <= 0:
            particles.remove(particle)
            particles.append(Particle())

    # Animate title
    title_alpha += title_fade_direction * 2
    if title_alpha <= 150:
        title_fade_direction = 1
    elif title_alpha >= 255:
        title_fade_direction = -1
    title_text.set_alpha(title_alpha)
    title_shadow.set_alpha(title_alpha)
    settings_title.set_alpha(title_alpha)
    settings_title_shadow.set_alpha(title_alpha)
    quit_dialog_title.set_alpha(title_alpha)
    quit_dialog_title_shadow.set_alpha(title_alpha)

    # Draw the screen
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill(PASTEL_BLUE)

    # Draw particles
    for particle in particles:
        particle.draw(screen)

    # Draw title with shadow
    shadow_rect = title_shadow.get_rect(center=(title_rect.centerx + 3, title_rect.centery + 3))
    screen.blit(title_shadow, shadow_rect)
    screen.blit(title_text, title_rect)

    # Draw menu based on current state
    if current_menu == "main":
        car_game_button.draw(screen)
        snake_game_button.draw(screen)
        flappy_bird_button.draw(screen)
        settings_button.draw(screen)
        quit_button.draw(screen)

        mouse_pos = pygame.mouse.get_pos()
        if car_game_button.rect.collidepoint(mouse_pos):
            selected_game_preview = car_game_preview
        elif snake_game_button.rect.collidepoint(mouse_pos):
            selected_game_preview = snake_game_preview
        elif flappy_bird_button.rect.collidepoint(mouse_pos):
            selected_game_preview = flappy_bird_preview
        else:
            selected_game_preview = None

        if selected_game_preview:
            preview_rect = selected_game_preview.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 180))
            screen.blit(selected_game_preview, preview_rect)
    elif current_menu == "settings":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        shadow_rect = settings_title_shadow.get_rect(center=(settings_title_rect.centerx + 3, settings_title_rect.centery + 3))
        screen.blit(settings_title_shadow, shadow_rect)
        screen.blit(settings_title, settings_title_rect)

        music_toggle_button.text = "Music: " + ("ON" if music_playing else "OFF")
        music_toggle_button.text_surface = button_font.render(music_toggle_button.text, True, WHITE)
        music_toggle_button.text_shadow = button_font.render(music_toggle_button.text, True, SHADOW_COLOR)
        music_toggle_button.draw(screen)
        volume_slider.draw(screen)
        back_button.draw(screen)
    elif current_menu == "quit_dialog":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        shadow_rect = quit_dialog_title_shadow.get_rect(center=(quit_dialog_title_rect.centerx + 3, quit_dialog_title_rect.centery + 3))
        screen.blit(quit_dialog_title_shadow, shadow_rect)
        screen.blit(quit_dialog_title, quit_dialog_title_rect)

        quit_yes_button.draw(screen)
        quit_no_button.draw(screen)

    # Draw attribution with shadow
    shadow_rect = attribution_shadow.get_rect(center=(attribution_rect.centerx + 3, attribution_rect.centery + 3))
    screen.blit(attribution_shadow, shadow_rect)
    screen.blit(attribution_text, attribution_rect)

    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()