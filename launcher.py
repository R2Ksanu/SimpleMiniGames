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
PASTEL_BLUE = (173, 216, 230)  # Fallback background color
PASTEL_PINK = (255, 182, 193)  # Hover color
SHADOW_COLOR = (80, 80, 80)  # Lighter shadow for better contrast
BUTTON_COLOR = (255, 165, 0)  # Orange color for buttons (matching screenshot)

# Load fonts
try:
    font = pygame.font.Font("LauncherAssets/PressStart2P-Regular.ttf", 24)  # For title
    button_font = pygame.font.Font("LauncherAssets/PressStart2P-Regular.ttf", 18)  # Slightly larger for buttons
    small_font = pygame.font.Font("LauncherAssets/PressStart2P-Regular.ttf", 16)  # For attribution and slider
    print("Custom font loaded: PressStart2P-Regular.ttf")
except FileNotFoundError:
    font = pygame.font.SysFont("monospace", 24, bold=True)
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

# Commenting out button textures since the screenshot shows solid colors
# try:
#     button_normal = pygame.image.load("LauncherAssets/button_normal.png").convert_alpha()
#     button_normal = pygame.transform.scale(button_normal, (200, 40))
#     button_hover = pygame.image.load("LauncherAssets/button_hover.png").convert_alpha()
#     button_hover = pygame.transform.scale(button_hover, (200, 40))
#     print("Button textures loaded")
# except FileNotFoundError:
#     button_normal = None
#     button_hover = None
#     print("Button textures not found, using default rectangles")
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

# Button class with improved text rendering
class Button:
    def __init__(self, text, x, y, width, height, action, preview_image=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.preview_image = preview_image
        self.text_surface = button_font.render(text, True, WHITE)  # Changed to white for better contrast
        self.text_shadow = button_font.render(text, True, SHADOW_COLOR)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        # Draw button with solid color (orange) or texture
        if self.rect.collidepoint(mouse_pos):
            if button_hover:
                surface.blit(button_hover, self.rect.topleft)
            else:
                pygame.draw.rect(surface, PASTEL_PINK, self.rect, border_radius=10)  # Rounded corners
        else:
            if button_normal:
                surface.blit(button_normal, self.rect.topleft)
            else:
                pygame.draw.rect(surface, BUTTON_COLOR, self.rect, border_radius=10)  # Orange buttons
        # Draw text with shadow (increased offset for clarity)
        text_rect = self.text_surface.get_rect(center=self.rect.center)
        shadow_rect = self.text_shadow.get_rect(center=(text_rect.centerx + 3, text_rect.centery + 3))  # Increased offset
        surface.blit(self.text_shadow, shadow_rect)
        surface.blit(self.text_surface, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if self.rect.collidepoint(event.pos):
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
        # Draw slider track
        pygame.draw.rect(surface, GRAY, self.rect)
        # Draw handle
        pygame.draw.rect(surface, WHITE, self.handle_rect)
        # Draw label with shadow
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

# Actions for each button
def launch_car_game():
    global music_playing
    if music_playing:
        pygame.mixer.music.pause()
        music_playing = False
    subprocess.run([sys.executable, "CarGame/car_game.py"])
    pygame.mixer.music.unpause()
    music_playing = True

def launch_snake_game():
    global music_playing
    if music_playing:
        pygame.mixer.music.pause()
        music_playing = False
    subprocess.run([sys.executable, "SnakeGame/snake_game.py"])
    pygame.mixer.music.unpause()
    music_playing = True

def launch_flappy_bird():
    global music_playing
    if music_playing:
        pygame.mixer.music.pause()
        music_playing = False
    subprocess.run([sys.executable, "FlappyBird/flappy_bird.py"])
    pygame.mixer.music.unpause()
    music_playing = True

def quit_launcher():
    pygame.quit()
    sys.exit()

# Create buttons and slider
button_width, button_height = 200, 40
button_spacing = 15
start_y = HEIGHT // 2 - 80

car_game_button = Button("Car Game", WIDTH // 2 - button_width // 2, start_y, button_width, button_height, launch_car_game, car_game_preview)
snake_game_button = Button("Snake Game", WIDTH // 2 - button_width // 2, start_y + button_height + button_spacing, button_width, button_height, launch_snake_game, snake_game_preview)
flappy_bird_button = Button("Flappy Bird", WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height, launch_flappy_bird, flappy_bird_preview)
quit_button = Button("Quit", WIDTH // 2 - button_width // 2, start_y + 3 * (button_height + button_spacing), button_width, button_height, quit_launcher)

volume_slider = Slider(WIDTH // 2 - 100, HEIGHT - 50, 200, 10, 0.0, 1.0, music_volume)

# Title with animation
title_text = font.render("SimpleMiniGames", True, WHITE)
title_shadow = font.render("SimpleMiniGames", True, SHADOW_COLOR)
title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
title_alpha = 255
title_fade_direction = -1

# Attribution text
attribution_text = small_font.render('Music: "Pixel Peeker Polka-faster" by Kevin MacLeod', True, WHITE)
attribution_shadow = small_font.render('Music: "Pixel Peeker Polka-faster" by Kevin MacLeod', True, SHADOW_COLOR)
attribution_rect = attribution_text.get_rect(center=(WIDTH // 2, HEIGHT - 20))

# Game preview display
selected_game_preview = None

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Check for button clicks
        if car_game_button.check_click(event):
            selected_game_preview = car_game_preview
        if snake_game_button.check_click(event):
            selected_game_preview = snake_game_preview
        if flappy_bird_button.check_click(event):
            selected_game_preview = flappy_bird_preview
        quit_button.check_click(event)
        # Update volume slider
        volume_slider.update(event)

    # Animate title (fade effect)
    title_alpha += title_fade_direction * 2
    if title_alpha <= 150:
        title_fade_direction = 1
    elif title_alpha >= 255:
        title_fade_direction = -1
    title_text.set_alpha(title_alpha)
    title_shadow.set_alpha(title_alpha)

    # Draw the screen
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill(PASTEL_BLUE)

    # Draw title with shadow
    shadow_rect = title_shadow.get_rect(center=(title_rect.centerx + 3, title_rect.centery + 3))
    screen.blit(title_shadow, shadow_rect)
    screen.blit(title_text, title_rect)

    # Draw buttons
    car_game_button.draw(screen)
    snake_game_button.draw(screen)
    flappy_bird_button.draw(screen)
    quit_button.draw(screen)

    # Draw volume slider
    volume_slider.draw(screen)

    # Draw game preview if a button is hovered
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

    # Draw attribution with shadow
    shadow_rect = attribution_shadow.get_rect(center=(attribution_rect.centerx + 3, attribution_rect.centery + 3))
    screen.blit(attribution_shadow, shadow_rect)
    screen.blit(attribution_text, attribution_rect)

    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()