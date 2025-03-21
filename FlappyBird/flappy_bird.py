import pygame
import random
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Window settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SMG Flappy Bird")
clock = pygame.time.Clock()

# Colors
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
DARK_GRAY = (50, 50, 50, 200)
GLOW_COLOR = (255, 255, 255, 100)
DARK_RED = (139, 0, 0)
DARK_BLUE = (0, 0, 139)

# Stop any existing music (e.g., from the launcher)
pygame.mixer.music.stop()

# Load background music
music_loaded = False
try:
    pygame.mixer.music.load("FlappyBird/background_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    music_loaded = True
    print("Background music loaded: background_music.mp3")
except pygame.error as e:
    print(f"Failed to load background_music.mp3: {e}")
    try:
        pygame.mixer.music.load("FlappyBird/background_music.wav")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        music_loaded = True
        print("Background music loaded: background_music.wav")
    except pygame.error as e:
        print(f"Failed to load background_music.wav: {e}")
        print("Continuing without background music.")

# Load textures
try:
    background_image = pygame.image.load("FlappyBird/background.png").convert()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    print("Background image loaded")
except FileNotFoundError:
    background_image = pygame.Surface((WIDTH, HEIGHT))
    background_image.fill(GREEN)
    print("Background image not found, using default surface")

try:
    bird_image = pygame.image.load("FlappyBird/bird.png").convert_alpha()
    bird_image = pygame.transform.scale(bird_image, (40, 40))
    print("Bird image loaded")
except FileNotFoundError:
    bird_image = pygame.Surface((40, 40))
    bird_image.fill(WHITE)
    print("Bird image not found, using default surface")

try:
    pipe_image = pygame.image.load("FlappyBird/pipe.png").convert_alpha()
    print("Pipe image loaded")
except FileNotFoundError:
    pipe_image = None
    print("Pipe image not found, using default rectangles")

try:
    coin_image = pygame.image.load("FlappyBird/coin.png").convert_alpha()
    coin_image = pygame.transform.scale(coin_image, (20, 20))
    print("Coin image loaded")
except FileNotFoundError:
    coin_image = None
    print("Coin image not found, using default yellow circle")

# Load fonts
try:
    game_font = pygame.font.Font("FlappyBird/PressStart2P-Regular.ttf", 24)
    print("Custom font loaded: PressStart2P-Regular.ttf")
except FileNotFoundError:
    game_font = pygame.font.SysFont("Arial", 24, bold=True)
    print("Custom font not found, using Arial")

menu_font = pygame.font.SysFont("Comic Sans MS", 30, bold=True)
small_menu_font = pygame.font.SysFont("Comic Sans MS", 20)

# Initialize sound variables
flap_sound = None
score_sound = None
crash_sound = None
coin_sound = None

# Load sound effects
try:
    flap_sound = pygame.mixer.Sound("FlappyBird/flap.wav")
    print("Flap sound loaded")
except FileNotFoundError:
    flap_sound = None
    print("Flap sound not found")

try:
    score_sound = pygame.mixer.Sound("FlappyBird/score.wav")
    print("Score sound loaded")
except FileNotFoundError:
    score_sound = None
    print("Score sound not found")

try:
    crash_sound = pygame.mixer.Sound("FlappyBird/crash.wav")
    print("Crash sound loaded")
except FileNotFoundError:
    crash_sound = None
    print("Crash sound not found")

try:
    coin_sound = pygame.mixer.Sound("FlappyBird/coin.wav")
    print("Coin sound loaded")
except FileNotFoundError:
    coin_sound = None
    print("Coin sound not found")

# Load high score
high_score_file = "FlappyBird/high_score.txt"
high_score = 0
if os.path.exists(high_score_file):
    try:
        with open(high_score_file, "r") as f:
            high_score = int(f.read().strip())
        print(f"Loaded high score: {high_score}")
    except (ValueError, IOError) as e:
        print(f"Error loading high score: {e}")
        high_score = 0
else:
    print("High score file not found, starting with 0")

# Particle class for effects
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.radius = random.randint(3, 6)
        self.color = color
        self.velocity_x = random.uniform(-2, 2)
        self.velocity_y = random.uniform(-2, 2)
        self.lifetime = 30

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.lifetime -= 1
        alpha = max(0, int(255 * (self.lifetime / 30)))
        self.color = (self.color[0], self.color[1], self.color[2], alpha)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# Function to create a gradient surface
def create_gradient_surface(width, height, color1, color2, alpha=200):
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        ratio = y / height
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        pygame.draw.line(surface, (r, g, b, alpha), (0, y), (width, y))
    return surface

# Reset game state function
def reset_game():
    global bird, velocity, pipes, coins, score, game_over, particles, background_x
    difficulty = DIFFICULTY_LEVELS[selected_difficulty]
    multipliers = difficulty_multipliers[difficulty]

    bird = pygame.Rect(200, 300, 40, 40)
    velocity = 0
    pipes = [pygame.Rect(WIDTH, random.randint(100, 400), 60, HEIGHT)]
    coins = []
    score = 0
    game_over = False
    particles = []
    background_x = 0
    global gravity, pipe_speed, pipe_gap
    gravity = 0.5 * multipliers["gravity"]
    pipe_speed = 3 * multipliers["speed"]
    pipe_gap = int(150 * multipliers["gap"])
    print(f"Game state reset with difficulty: {difficulty}")

# Game objects
bird = pygame.Rect(200, 300, 40, 40)
velocity = 0
gravity = 0.5
pipe_speed = 3
pipe_gap = 150
pipes = [pygame.Rect(WIDTH, random.randint(100, 400), 60, HEIGHT)]
coins = []
score = 0
game_over = False
paused = False
return_to_launcher = False
particles = []
background_x = 0  # Position for scrolling background

# Animation variables
border_animation = 0

# Main menu variables
in_main_menu = True
main_menu_options = ["Play", "How to Play", "Difficulty", "Exit"]
main_menu_selected = 0
showing_instructions = False

# Difficulty settings
DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]
selected_difficulty = 1  # Default to Medium (index 1)
difficulty_multipliers = {
    "Easy": {"gravity": 0.8, "speed": 0.7, "gap": 1.2},  # Lower gravity, slower pipes, larger gap
    "Medium": {"gravity": 1.0, "speed": 1.0, "gap": 1.0},  # Default settings
    "Hard": {"gravity": 1.2, "speed": 1.3, "gap": 0.8}  # Higher gravity, faster pipes, smaller gap
}

# Pause menu variables
menu_options = ["Resume", "Restart", "Launcher menu", "Exit"]
selected_option = 0
key_cooldown = 0

# Game loop
running = True
print("Starting game loop")
try:
    while running:
        if in_main_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return_to_launcher = False
                    print("Quit event received")

            if key_cooldown > 0:
                key_cooldown -= 1

            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN] and key_cooldown == 0:
                main_menu_selected = (main_menu_selected + 1) % len(main_menu_options)
                key_cooldown = 10
                print(f"Main menu selected option: {main_menu_options[main_menu_selected]}")
            if keys[pygame.K_UP] and key_cooldown == 0:
                main_menu_selected = (main_menu_selected - 1) % len(main_menu_options)
                key_cooldown = 10
                print(f"Main menu selected option: {main_menu_options[main_menu_selected]}")
            if keys[pygame.K_LEFT] and main_menu_options[main_menu_selected] == "Difficulty" and key_cooldown == 0:
                selected_difficulty = (selected_difficulty - 1) % len(DIFFICULTY_LEVELS)
                key_cooldown = 10
                print(f"Difficulty set to: {DIFFICULTY_LEVELS[selected_difficulty]}")
            if keys[pygame.K_RIGHT] and main_menu_options[main_menu_selected] == "Difficulty" and key_cooldown == 0:
                selected_difficulty = (selected_difficulty + 1) % len(DIFFICULTY_LEVELS)
                key_cooldown = 10
                print(f"Difficulty set to: {DIFFICULTY_LEVELS[selected_difficulty]}")

            if keys[pygame.K_RETURN] and key_cooldown == 0:
                key_cooldown = 10
                if main_menu_options[main_menu_selected] == "Play":
                    in_main_menu = False
                    showing_instructions = False
                    reset_game()
                    print("Starting game")
                elif main_menu_options[main_menu_selected] == "How to Play":
                    showing_instructions = True
                    print("Showing instructions")
                elif main_menu_options[main_menu_selected] == "Difficulty":
                    # Already handled by Left/Right keys
                    pass
                elif main_menu_options[main_menu_selected] == "Exit":
                    running = False
                    return_to_launcher = False
                    print("Exiting game from main menu")

            # Draw the main menu (static background in main menu)
            screen.blit(background_image, (0, 0))
            if showing_instructions:
                title_text = menu_font.render("How to Play", True, WHITE)
                title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
                title_shadow = menu_font.render("How to Play", True, DARK_GRAY)
                title_shadow_rect = title_rect.move(2, 2)
                screen.blit(title_shadow, title_shadow_rect)
                screen.blit(title_text, title_rect)

                instruction_text = small_menu_font.render("Press SPACE to flap and avoid pipes", True, WHITE)
                instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                instruction_shadow = small_menu_font.render("Press SPACE to flap and avoid pipes", True, DARK_GRAY)
                instruction_shadow_rect = instruction_rect.move(2, 2)
                screen.blit(instruction_shadow, instruction_shadow_rect)
                screen.blit(instruction_text, instruction_rect)

                back_text = small_menu_font.render("Press ENTER to go back", True, WHITE)
                back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
                back_shadow = small_menu_font.render("Press ENTER to go back", True, DARK_GRAY)
                back_shadow_rect = back_rect.move(2, 2)
                screen.blit(back_shadow, back_shadow_rect)
                screen.blit(back_text, back_rect)
            else:
                title_text = menu_font.render("SMG Flappy Bird", True, WHITE)
                title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
                title_shadow = menu_font.render("SMG Flappy Bird", True, DARK_GRAY)
                title_shadow_rect = title_rect.move(2, 2)
                screen.blit(title_shadow, title_shadow_rect)
                screen.blit(title_text, title_rect)

                credits_text = small_menu_font.render("By R2K", True, WHITE)
                credits_rect = credits_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
                credits_shadow = small_menu_font.render("By R2K", True, DARK_GRAY)
                credits_shadow_rect = credits_rect.move(2, 2)
                screen.blit(credits_shadow, credits_shadow_rect)
                screen.blit(credits_text, credits_rect)

                for i, option in enumerate(main_menu_options):
                    if option == "Difficulty":
                        text = f"Difficulty: {DIFFICULTY_LEVELS[selected_difficulty]}"
                    else:
                        text = option
                    color = YELLOW if i == main_menu_selected else WHITE
                    option_text = menu_font.render(text, True, color)
                    option_rect = option_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 40))
                    option_shadow = menu_font.render(text, True, DARK_GRAY)
                    option_shadow_rect = option_rect.move(2, 2)
                    screen.blit(option_shadow, option_shadow_rect)
                    screen.blit(option_text, option_rect)

        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return_to_launcher = False
                    print("Quit event received")
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not game_over:
                        velocity = -10
                        if flap_sound:
                            flap_sound.play()
                    if event.key == pygame.K_ESCAPE and key_cooldown == 0:
                        paused = not paused
                        key_cooldown = 10
                        print(f"Paused: {paused}")

            if key_cooldown > 0:
                key_cooldown -= 1

            keys = pygame.key.get_pressed()
            if not game_over and not paused:
                # Update background position
                background_x -= pipe_speed * 0.5  # Background moves slower than pipes for parallax effect
                if background_x <= -WIDTH:
                    background_x = 0

                # Bird physics
                velocity += gravity
                bird.y += velocity

                # Move pipes and spawn coins
                for pipe in pipes[:]:
                    pipe.x -= pipe_speed
                    if pipe.x < -pipe.width:
                        pipes.remove(pipe)
                        new_pipe = pygame.Rect(WIDTH, random.randint(100, 400), 60, HEIGHT)
                        pipes.append(new_pipe)
                        # Spawn a coin in the gap between the pipes
                        coin_y = new_pipe.y + pipe_gap // 2
                        coins.append(pygame.Rect(WIDTH + 30, coin_y - 10, 20, 20))
                        score += 1
                        if score_sound:
                            score_sound.play()
                        print(f"Score: {score}")

                # Move coins
                for coin in coins[:]:
                    coin.x -= pipe_speed
                    if coin.x < -coin.width:
                        coins.remove(coin)

                # Check for coin collection
                for coin in coins[:]:
                    if bird.colliderect(coin):
                        coins.remove(coin)
                        score += 5  # +5 points for each coin
                        if coin_sound:
                            coin_sound.play()
                        for _ in range(5):
                            particle = Particle(coin.centerx, coin.centery, YELLOW)
                            particles.append(particle)
                        print(f"Coin collected! Score: {score}")

                # Collision with pipes
                if (bird.y < 0 or bird.y > HEIGHT or
                    any(bird.colliderect(pygame.Rect(pipe.x, 0, pipe.width, pipe.y)) or
                        bird.colliderect(pygame.Rect(pipe.x, pipe.y + pipe_gap, pipe.width, HEIGHT))
                        for pipe in pipes)):
                    game_over = True
                    if crash_sound:
                        crash_sound.play()
                    for _ in range(10):
                        particle = Particle(bird.centerx, bird.centery, WHITE)
                        particles.append(particle)
                    print("Game over: Collided with pipe or out of bounds")

                # Update particles
                for particle in particles[:]:
                    particle.update()
                    if particle.lifetime <= 0:
                        particles.remove(particle)

            # Draw scrolling background
            screen.blit(background_image, (background_x, 0))
            screen.blit(background_image, (background_x + WIDTH, 0))

            for pipe in pipes:
                if pipe_image:
                    # Top pipe: Scale to fit from top to pipe.y
                    top_pipe_height = pipe.y
                    if top_pipe_height > 0:
                        top_pipe = pygame.transform.scale(pipe_image, (60, top_pipe_height))
                        top_pipe = pygame.transform.flip(top_pipe, False, True)  # Flip for top pipe
                        screen.blit(top_pipe, (pipe.x, 0))
                    # Bottom pipe: Scale to fit from pipe.y + pipe_gap to bottom
                    bottom_pipe_height = HEIGHT - (pipe.y + pipe_gap)
                    if bottom_pipe_height > 0:
                        bottom_pipe = pygame.transform.scale(pipe_image, (60, bottom_pipe_height))
                        screen.blit(bottom_pipe, (pipe.x, pipe.y + pipe_gap))
                else:
                    pygame.draw.rect(screen, RED, (pipe.x, 0, pipe.width, pipe.y))
                    pygame.draw.rect(screen, RED, (pipe.x, pipe.y + pipe_gap, pipe.width, HEIGHT))

            # Draw coins
            for coin in coins:
                if coin_image:
                    screen.blit(coin_image, coin)
                else:
                    pygame.draw.circle(screen, YELLOW, coin.center, 10)

            screen.blit(bird_image, bird)

            for particle in particles:
                particle.draw(screen)

            score_text = game_font.render(f"Score: {score}", True, WHITE)
            score_rect = score_text.get_rect(topleft=(10, 10))
            score_shadow = game_font.render(f"Score: {score}", True, DARK_GRAY)
            score_shadow_rect = score_rect.move(2, 2)
            screen.blit(score_shadow, score_shadow_rect)
            screen.blit(score_text, score_rect)

            if game_over:
                if score > high_score:
                    high_score = score
                    try:
                        with open(high_score_file, "w") as f:
                            f.write(str(high_score))
                        print(f"New high score: {high_score}")
                    except IOError as e:
                        print(f"Error saving high score: {e}")

                game_over_text = menu_font.render("Game Over!", True, RED)
                game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
                screen.blit(game_over_text, game_over_rect)

                final_score_text = game_font.render(f"Score: {score}", True, WHITE)
                final_score_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(final_score_text, final_score_rect)

                high_score_text = game_font.render(f"High Score: {high_score}", True, YELLOW)
                high_score_rect = high_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
                screen.blit(high_score_text, high_score_rect)

                restart_text = small_menu_font.render("Press R to Restart", True, WHITE)
                restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
                screen.blit(restart_text, restart_rect)

                if keys[pygame.K_r] and key_cooldown == 0:
                    reset_game()
                    key_cooldown = 10
                    print("Game restarted")

            if paused:
                # Draw gradient background for the menu
                menu_width, menu_height = 400, 300
                menu_surface = create_gradient_surface(menu_width, menu_height, DARK_RED, DARK_BLUE, alpha=200)
                menu_rect = menu_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(menu_surface, menu_rect)

                # Animate the border
                border_animation += 0.05
                border_colors = [DARK_RED, DARK_BLUE]
                border_color = border_colors[int(border_animation % len(border_colors))]
                pygame.draw.rect(screen, border_color, menu_rect, 3, border_radius=10)

                # Draw title
                title_text = menu_font.render("Paused", True, WHITE)
                title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
                title_shadow = menu_font.render("Paused", True, DARK_GRAY)
                title_shadow_rect = title_rect.move(2, 2)
                screen.blit(title_shadow, title_shadow_rect)
                screen.blit(title_text, title_rect)

                # Handle menu navigation
                if keys[pygame.K_DOWN] and key_cooldown == 0:
                    selected_option = (selected_option + 1) % len(menu_options)
                    key_cooldown = 10
                    print(f"Selected option: {menu_options[selected_option]}")
                if keys[pygame.K_UP] and key_cooldown == 0:
                    selected_option = (selected_option - 1) % len(menu_options)
                    key_cooldown = 10
                    print(f"Selected option: {menu_options[selected_option]}")

                if keys[pygame.K_RETURN] and key_cooldown == 0:
                    key_cooldown = 10
                    if menu_options[selected_option] == "Resume":
                        paused = False
                        print("Resuming game")
                    elif menu_options[selected_option] == "Restart":
                        reset_game()
                        paused = False
                        print("Game restarted")
                    elif menu_options[selected_option] == "Launcher menu":
                        running = False
                        return_to_launcher = True
                        print("Returning to launcher menu")
                    elif menu_options[selected_option] == "Exit":
                        running = False
                        return_to_launcher = False
                        print("Exiting game")

                # Draw menu options
                for i, option in enumerate(menu_options):
                    color = YELLOW if i == selected_option else WHITE
                    option_text = menu_font.render(f"[ {option} ]", True, color)
                    x_offset = 0
                    if option == "Resume":
                        x_offset = 0
                    elif option == "Restart":
                        x_offset = 0
                    elif option == "Launcher menu":
                        x_offset = -15
                    else:  # Exit
                        x_offset = 15
                    option_rect = option_text.get_rect(center=(WIDTH // 2 + x_offset, HEIGHT // 2 + i * 40))
                    option_shadow = menu_font.render(f"[ {option} ]", True, DARK_GRAY)
                    option_shadow_rect = option_rect.move(2, 2)
                    screen.blit(option_shadow, option_shadow_rect)
                    screen.blit(option_text, option_rect)

        pygame.display.flip()
        clock.tick(60)

except Exception as e:
    print(f"Unexpected error in game loop: {e}")
    running = False
    return_to_launcher = False

# Cleanup
pygame.mixer.music.stop()
pygame.quit()

if return_to_launcher:
    print("Exiting with return code 0 (return to launcher)")
    exit(0)
else:
    print("Exiting with return code 1 (full exit)")
    exit(1)