import pygame
import random
import math
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Window settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SMG Car Game")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
LIGHT_GREEN = (100, 255, 100)
DARK_GREEN = (0, 200, 0)
TRANSPARENT_PURPLE = (128, 0, 128, 150)
CYAN = (0, 255, 255)
DARK_GRAY = (50, 50, 50, 200)
GLOW_COLOR = (255, 255, 255, 100)
DARK_RED = (139, 0, 0)
DARK_BLUE = (0, 0, 139)
PASTEL_PINK = (255, 182, 193)
PASTEL_BLUE = (173, 216, 230)

# Stop any existing music (e.g., from the launcher)
pygame.mixer.music.stop()

# Load background music
music_loaded = False
try:
    pygame.mixer.music.load("CarGame/background_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    music_loaded = True
    print("Background music loaded: background_music.mp3")
except pygame.error as e:
    print(f"Failed to load background_music.mp3: {e}")
    try:
        pygame.mixer.music.load("CarGame/background_music.wav")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        music_loaded = True
        print("Background music loaded: background_music.wav")
    except pygame.error as e:
        print(f"Failed to load background_music.wav: {e}")
        print("Continuing without background music.")

# Load textures
try:
    car_image = pygame.image.load("CarGame/car.png").convert_alpha()
    car_image = pygame.transform.scale(car_image, (40, 70))
    print("Car image loaded")
except FileNotFoundError:
    car_image = pygame.Surface((50, 80))
    car_image.fill(WHITE)
    print("Car image not found, using default surface")

try:
    enemy_car_image = pygame.image.load("CarGame/enemy_car.png").convert_alpha()
    enemy_car_image = pygame.transform.scale(enemy_car_image, (50, 80))
    print("Enemy car image loaded")
except FileNotFoundError:
    enemy_car_image = pygame.Surface((50, 80))
    enemy_car_image.fill(RED)
    print("Enemy car image not found, using default surface")

try:
    background_image = pygame.image.load("CarGame/background.png").convert()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    print("Background image loaded")
except FileNotFoundError:
    background_image = pygame.Surface((WIDTH, HEIGHT))
    background_image.fill(GREEN)
    print("Background image not found, using default surface")

# Load custom font
try:
    dashboard_font = pygame.font.Font("CarGame/PressStart2P-Regular.ttf", 14)
    print("Custom font loaded: PressStart2P-Regular.ttf")
except FileNotFoundError:
    dashboard_font = pygame.font.SysFont("Arial", 18, bold=True)
    print("Custom font not found, using Arial")

# Load menu font
menu_font = pygame.font.SysFont("Comic Sans MS", 30, bold=True)
small_menu_font = pygame.font.SysFont("Comic Sans MS", 20)

# Initialize sound variables
coin_sound = None
powerup_sound = None
crash_sound = None
engine_sound = None
enemy_spawn_sound = None
game_over_sound = None

# Load sound effects
try:
    coin_sound = pygame.mixer.Sound("CarGame/coin.wav")
    print("Coin sound loaded")
except FileNotFoundError:
    coin_sound = None
    print("Coin sound not found")

try:
    powerup_sound = pygame.mixer.Sound("CarGame/powerup.wav")
    print("Powerup sound loaded")
except FileNotFoundError:
    powerup_sound = None
    print("Powerup sound not found")

try:
    crash_sound = pygame.mixer.Sound("CarGame/crash.wav")
    print("Crash sound loaded")
except FileNotFoundError:
    crash_sound = None
    print("Crash sound not found")

try:
    engine_sound = pygame.mixer.Sound("CarGame/engine.wav")
    engine_sound.set_volume(0.3)
    engine_sound.play(-1)
    print("Engine sound loaded and playing")
except FileNotFoundError:
    engine_sound = None
    print("Engine sound not found")

try:
    enemy_spawn_sound = pygame.mixer.Sound("CarGame/enemy_spawn.wav")
    print("Enemy spawn sound loaded")
except FileNotFoundError:
    enemy_spawn_sound = None
    print("Enemy spawn sound not found")

try:
    game_over_sound = pygame.mixer.Sound("CarGame/game_over.wav")
    print("Game over sound loaded")
except FileNotFoundError:
    game_over_sound = None
    print("Game over sound not found")

# Load high score
high_score_file = "CarGame/high_score.txt"
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
    global car, car_speed, obstacles, coins, powerups, enemy_cars, particles, score, distance_traveled
    global background_y, game_over, shield_active, speed_boost_active, shield_timer, speed_boost_timer
    global obstacle_spawn_timer, coin_spawn_timer, powerup_spawn_timer, enemy_spawn_timer
    global base_car_speed, background_speed, powerup_duration

    difficulty = DIFFICULTY_LEVELS[selected_difficulty]
    multipliers = difficulty_multipliers[difficulty]

    car = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 150, 50, 80)
    base_car_speed = 5 * multipliers["speed"]
    car_speed = base_car_speed
    obstacles = []
    coins = []
    powerups = []
    enemy_cars = []
    particles = []
    score = 0
    distance_traveled = 0
    background_y = 0
    background_speed = 2 * multipliers["speed"]
    game_over = False
    shield_active = False
    speed_boost_active = False
    shield_timer = 0
    speed_boost_timer = 0
    obstacle_spawn_timer = 0
    coin_spawn_timer = 0
    powerup_spawn_timer = 0
    enemy_spawn_timer = 0
    powerup_duration = int(600 * multipliers["powerup_duration"])
    print(f"Game state reset with difficulty: {difficulty}")

# Game objects
car = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 150, 50, 80)
car_speed = 5
base_car_speed = 5
obstacles = []
coins = []
powerups = []
enemy_cars = []
particles = []
score = 0
distance_traveled = 0
background_y = 0
background_speed = 2
game_over = False
paused = False
return_to_launcher = False

# Power-up states
shield_active = False
speed_boost_active = False
powerup_duration = 600
shield_timer = 0
speed_boost_timer = 0

# Animation variables
glow_animation = 0
border_animation = 0

# Spawn timers
obstacle_spawn_timer = 0
coin_spawn_timer = 0
powerup_spawn_timer = 0
enemy_spawn_timer = 0

# Difficulty progression
difficulty_multiplier = 1.0  # Increases over time
base_obstacle_spawn_rate = 60
base_enemy_spawn_rate = 120

# Escape menu variables
menu_options = ["Back to the game", "Reload", "Launcher menu", "Exit"]
selected_option = 0
key_cooldown = 0

# Main menu variables
in_main_menu = True
main_menu_options = ["Play", "How to Play", "Difficulty", "Exit"]
main_menu_selected = 0

# Difficulty settings
DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]
selected_difficulty = 1  # Default to Medium (index 1)
difficulty_multipliers = {
    "Easy": {"spawn_rate": 1.5, "speed": 0.8, "powerup_duration": 1.5},  # Slower, less frequent spawns, longer power-ups
    "Medium": {"spawn_rate": 1.0, "speed": 1.0, "powerup_duration": 1.0},  # Default settings
    "Hard": {"spawn_rate": 0.7, "speed": 1.2, "powerup_duration": 0.8}  # Faster, more frequent spawns, shorter power-ups
}

# Debug timer
game_timer = 0

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
                    print("Starting game")
                elif main_menu_options[main_menu_selected] == "How to Play":
                    print("Showing instructions")
                    # We'll add instructions display later
                elif main_menu_options[main_menu_selected] == "Difficulty":
                    # Already handled by Left/Right keys
                    pass
                elif main_menu_options[main_menu_selected] == "Exit":
                    running = False
                    return_to_launcher = False
                    print("Exiting game from main menu")

            # Draw the main menu
            screen.blit(background_image, (0, 0))  # Static background for the menu
            title_text = menu_font.render("SMG Car Game", True, WHITE)
            title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
            title_shadow = menu_font.render("SMG Car Game", True, DARK_GRAY)
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
            game_timer += 1
            if game_timer % 60 == 0:
                print(f"Game running for {game_timer // 60} seconds")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return_to_launcher = False
                    print("Quit event received")

            if key_cooldown > 0:
                key_cooldown -= 1

            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE] and key_cooldown == 0:
                paused = not paused
                key_cooldown = 10
                print(f"Paused: {paused}")

            if not game_over and not paused:
                obstacle_spawn_timer += 1
                coin_spawn_timer += 1
                powerup_spawn_timer += 1
                enemy_spawn_timer += 1
                glow_animation += 0.05
                border_animation += 0.05

                # Increase difficulty based on distance traveled
                difficulty_multiplier = 1.0 + (distance_traveled / 1000)
                difficulty = DIFFICULTY_LEVELS[selected_difficulty]
                multipliers = difficulty_multipliers[difficulty]
                adjusted_background_speed = (2 + (distance_traveled / 500)) * multipliers["speed"]
                background_speed = min(5 * multipliers["speed"], adjusted_background_speed)

                adjusted_obstacle_spawn_rate = max(30, (base_obstacle_spawn_rate / difficulty_multiplier) * multipliers["spawn_rate"])
                adjusted_enemy_spawn_rate = max(60, (base_enemy_spawn_rate / difficulty_multiplier) * multipliers["spawn_rate"])
                adjusted_coin_spawn_rate = 90 * multipliers["spawn_rate"]
                adjusted_powerup_spawn_rate = 240 * multipliers["spawn_rate"]

                if shield_active:
                    shield_timer -= 1
                    if shield_timer <= 0:
                        shield_active = False
                        print("Shield deactivated")
                if speed_boost_active:
                    speed_boost_timer -= 1
                    if speed_boost_timer <= 0:
                        speed_boost_active = False
                        car_speed = base_car_speed
                        print(f"Speed boost ended. car_speed reset to {car_speed}")

                distance_traveled += background_speed

                if keys[pygame.K_LEFT] and car.left > 0:
                    car.x -= car_speed
                if keys[pygame.K_RIGHT] and car.right < WIDTH:
                    car.x += car_speed

                if obstacle_spawn_timer > adjusted_obstacle_spawn_rate:
                    obstacle = pygame.Rect(random.randint(0, WIDTH - 30), -50, 30, 30)
                    obstacles.append(obstacle)
                    obstacle_spawn_timer = 0

                if coin_spawn_timer > adjusted_coin_spawn_rate:
                    coin = pygame.Rect(random.randint(0, WIDTH - 20), -50, 20, 20)
                    coins.append(coin)
                    coin_spawn_timer = 0

                if powerup_spawn_timer > adjusted_powerup_spawn_rate:
                    powerup_type = random.choice(["speed", "shield"])
                    powerup = pygame.Rect(random.randint(0, WIDTH - 40), -50, 40, 40)
                    powerups.append((powerup, powerup_type))
                    powerup_spawn_timer = 0

                if enemy_spawn_timer > adjusted_enemy_spawn_rate:
                    enemy = pygame.Rect(random.randint(0, WIDTH - 50), -50, 50, 80)
                    enemy_cars.append(enemy)
                    if enemy_spawn_sound:
                        enemy_spawn_sound.play()
                    enemy_spawn_timer = 0

                for obstacle in obstacles[:]:
                    obstacle.y += 5
                    if obstacle.y > HEIGHT:
                        obstacles.remove(obstacle)

                for coin in coins[:]:
                    coin.y += 3
                    if coin.y > HEIGHT:
                        coins.remove(coin)

                for powerup, powerup_type in powerups[:]:
                    powerup.y += 3
                    if powerup.y > HEIGHT:
                        powerups.remove((powerup, powerup_type))

                for enemy in enemy_cars[:]:
                    enemy.y += 4
                    if enemy.x < car.x:
                        enemy.x += 1
                    elif enemy.x > car.x:
                        enemy.x -= 1
                    if enemy.y > HEIGHT:
                        enemy_cars.remove(enemy)

                for particle in particles[:]:
                    particle.update()
                    if particle.lifetime <= 0:
                        particles.remove(particle)

                for obstacle in obstacles[:]:
                    if car.colliderect(obstacle):
                        if shield_active:
                            obstacles.remove(obstacle)
                            shield_active = False
                            shield_timer = 0
                            print("Shield used to destroy obstacle")
                        else:
                            game_over = True
                            if crash_sound:
                                crash_sound.play()
                            if game_over_sound:
                                game_over_sound.play()
                            if engine_sound:
                                engine_sound.stop()
                            print("Game over: Collided with obstacle")

                for coin in coins[:]:
                    if car.colliderect(coin):
                        coins.remove(coin)
                        score += 1
                        if coin_sound:
                            coin_sound.play()
                        for _ in range(5):
                            particle = Particle(coin.centerx, coin.centery, GREEN)
                            particles.append(particle)
                        print(f"Coin collected. Score: {score}")

                for powerup, powerup_type in powerups[:]:
                    if car.colliderect(powerup):
                        powerups.remove((powerup, powerup_type))
                        if powerup_sound:
                            powerup_sound.play()
                        particle_color = RED if powerup_type == "speed" else PURPLE
                        for _ in range(5):
                            particle = Particle(powerup.centerx, powerup.centery, particle_color)
                            particles.append(particle)
                        if powerup_type == "speed":
                            speed_boost_active = True
                            speed_boost_timer = powerup_duration
                            car_speed = base_car_speed * 1.5
                            print(f"Speed boost collected! car_speed = {car_speed}, timer = {speed_boost_timer}")
                        elif powerup_type == "shield":
                            shield_active = True
                            shield_timer = powerup_duration
                            print(f"Shield collected! timer = {shield_timer}")

                for enemy in enemy_cars[:]:
                    if car.colliderect(enemy):
                        if shield_active:
                            enemy_cars.remove(enemy)
                            shield_active = False
                            shield_timer = 0
                            print("Shield used to destroy enemy car")
                        else:
                            game_over = True
                            if crash_sound:
                                crash_sound.play()
                            if game_over_sound:
                                game_over_sound.play()
                            if engine_sound:
                                engine_sound.stop()
                            print("Game over: Collided with enemy car")

            background_y += background_speed
            if background_y >= HEIGHT:
                background_y = 0

            screen.blit(background_image, (0, background_y - HEIGHT))
            screen.blit(background_image, (0, background_y))

            if not game_over:
                for obstacle in obstacles:
                    pygame.draw.rect(screen, RED, obstacle)

                for coin in coins:
                    pygame.draw.circle(screen, YELLOW, coin.center, 10)

                for powerup, powerup_type in powerups:
                    color = RED if powerup_type == "speed" else PURPLE
                    pygame.draw.rect(screen, color, powerup)

                for enemy in enemy_cars:
                    screen.blit(enemy_car_image, enemy)

                if shield_active or speed_boost_active:
                    glow_color = PURPLE if shield_active else RED
                    glow_scale = 1 + 0.1 * math.sin(glow_animation)
                    glow_surface = pygame.Surface((car.width + 20, car.height + 20), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surface, (*glow_color, 150), (10, 10, car.width, car.height), border_radius=5)
                    glow_surface = pygame.transform.scale(glow_surface, (int((car.width + 20) * glow_scale), int((car.height + 20) * glow_scale)))
                    screen.blit(glow_surface, (car.x - 10 * glow_scale, car.y - 10 * glow_scale))
                screen.blit(car_image, car)

                for particle in particles:
                    particle.draw(screen)

            shadow_offset = 1
            glow_scale = 1 + 0.03 * math.sin(glow_animation)

            coins_text = dashboard_font.render(f"Coins: {score}", True, YELLOW)
            coins_rect = coins_text.get_rect(topleft=(20, 15))
            coins_panel = pygame.Surface((coins_rect.width + 20, coins_rect.height + 6), pygame.SRCALPHA)
            for y in range(coins_panel.get_height()):
                alpha = int(200 * (1 - y / coins_panel.get_height()))
                pygame.draw.line(coins_panel, (DARK_GRAY[0], DARK_GRAY[1], DARK_GRAY[2], alpha), (0, y), (coins_panel.get_width(), y))
            pygame.draw.rect(coins_panel, WHITE, (0, 0, coins_panel.get_width(), coins_panel.get_height()), 1, border_radius=5)
            screen.blit(coins_panel, (10, 10))
            glow_rect = pygame.Rect(10 - 2 * glow_scale, 10 - 2 * glow_scale, coins_panel.get_width() + 4 * glow_scale, coins_panel.get_height() + 4 * glow_scale)
            pygame.draw.rect(screen, GLOW_COLOR, glow_rect, 2, border_radius=5)
            coins_shadow_text = dashboard_font.render(f"Coins: {score}", True, DARK_GRAY)
            coins_shadow_rect = coins_text.get_rect(topleft=(20 + shadow_offset, 15 + shadow_offset))
            screen.blit(coins_shadow_text, coins_shadow_rect)
            screen.blit(coins_text, coins_rect)

            distance_text = dashboard_font.render(f"M: {int(distance_traveled)}", True, CYAN)
            distance_rect = distance_text.get_rect(topleft=(20, 45))
            distance_panel = pygame.Surface((distance_rect.width + 20, distance_rect.height + 6), pygame.SRCALPHA)
            for y in range(distance_panel.get_height()):
                alpha = int(200 * (1 - y / distance_panel.get_height()))
                pygame.draw.line(distance_panel, (DARK_GRAY[0], DARK_GRAY[1], DARK_GRAY[2], alpha), (0, y), (distance_panel.get_width(), y))
            pygame.draw.rect(distance_panel, WHITE, (0, 0, distance_panel.get_width(), distance_panel.get_height()), 1, border_radius=5)
            screen.blit(distance_panel, (10, 40))
            glow_rect = pygame.Rect(10 - 2 * glow_scale, 40 - 2 * glow_scale, distance_panel.get_width() + 4 * glow_scale, distance_panel.get_height() + 4 * glow_scale)
            pygame.draw.rect(screen, GLOW_COLOR, glow_rect, 2, border_radius=5)
            distance_shadow_text = dashboard_font.render(f"M: {int(distance_traveled)}", True, DARK_GRAY)
            distance_shadow_rect = distance_text.get_rect(topleft=(20 + shadow_offset, 45 + shadow_offset))
            screen.blit(distance_shadow_text, distance_shadow_rect)
            screen.blit(distance_text, distance_rect)

            speed_text = dashboard_font.render(f"Speed: {int(car_speed)}", True, WHITE)
            speed_rect = speed_text.get_rect(topright=(WIDTH - 20, HEIGHT - 15))
            speed_panel = pygame.Surface((speed_rect.width + 20, speed_rect.height + 6), pygame.SRCALPHA)
            for y in range(speed_panel.get_height()):
                alpha = int(200 * (1 - y / speed_panel.get_height()))
                pygame.draw.line(speed_panel, (DARK_GRAY[0], DARK_GRAY[1], DARK_GRAY[2], alpha), (0, y), (speed_panel.get_width(), y))
            pygame.draw.rect(speed_panel, WHITE, (0, 0, speed_panel.get_width(), speed_panel.get_height()), 1, border_radius=5)
            screen.blit(speed_panel, (WIDTH - speed_rect.width - 30, HEIGHT - speed_rect.height - 20))
            glow_rect = pygame.Rect(WIDTH - speed_rect.width - 30 - 2 * glow_scale, HEIGHT - speed_rect.height - 20 - 2 * glow_scale, speed_panel.get_width() + 4 * glow_scale, speed_panel.get_height() + 4 * glow_scale)
            pygame.draw.rect(screen, GLOW_COLOR, glow_rect, 2, border_radius=5)
            speed_shadow_text = dashboard_font.render(f"Speed: {int(car_speed)}", True, DARK_GRAY)
            speed_shadow_rect = speed_text.get_rect(topright=(WIDTH - 20 + shadow_offset, HEIGHT - 15 + shadow_offset))
            screen.blit(speed_shadow_text, speed_shadow_rect)
            screen.blit(speed_text, speed_rect)

            if game_over:
                if score > high_score:
                    high_score = score
                    try:
                        with open("CarGame/high_score.txt", "w") as f:
                            f.write(str(high_score))
                        print(f"New high score: {high_score}")
                    except IOError as e:
                        print(f"Error saving high score: {e}")

                font = pygame.font.SysFont("Arial", 50)
                game_over_text = font.render("Game Over!", True, RED)
                game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
                screen.blit(game_over_text, game_over_rect)

                high_score_text = font.render(f"High Score: {high_score}", True, YELLOW)
                high_score_rect = high_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
                screen.blit(high_score_text, high_score_rect)

            if paused:
                # Draw gradient background for the menu (dark red to dark blue, semi-transparent)
                menu_width, menu_height = 400, 300
                menu_surface = create_gradient_surface(menu_width, menu_height, DARK_RED, DARK_BLUE, alpha=200)
                menu_rect = menu_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(menu_surface, menu_rect)

                # Animate the border (dark red to dark blue)
                border_colors = [DARK_RED, DARK_BLUE]
                border_color = border_colors[int(border_animation % len(border_colors))]
                pygame.draw.rect(screen, border_color, menu_rect, 3, border_radius=10)

                # Draw title and credits with shadow
                title_text = menu_font.render("SMG-Car", True, WHITE)
                title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
                title_shadow = menu_font.render("SMG-Car", True, DARK_GRAY)
                title_shadow_rect = title_rect.move(2, 2)
                screen.blit(title_shadow, title_shadow_rect)
                screen.blit(title_text, title_rect)

                credits_text = small_menu_font.render("By R2K", True, WHITE)
                credits_rect = credits_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
                credits_shadow = small_menu_font.render("By R2K", True, DARK_GRAY)
                credits_shadow_rect = credits_rect.move(2, 2)
                screen.blit(credits_shadow, credits_shadow_rect)
                screen.blit(credits_text, credits_rect)

                # Draw separator lines
                separator = "=" * 16
                separator_text = menu_font.render(separator, True, WHITE)
                separator_rect = separator_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
                separator_shadow = menu_font.render(separator, True, DARK_GRAY)
                separator_shadow_rect = separator_rect.move(2, 2)
                screen.blit(separator_shadow, separator_shadow_rect)
                screen.blit(separator_text, separator_rect)
                separator_rect = separator_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
                separator_shadow_rect = separator_rect.move(2, 2)
                screen.blit(separator_shadow, separator_shadow_rect)
                screen.blit(separator_text, separator_rect)

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
                    if menu_options[selected_option] == "Back to the game":
                        paused = False
                        print("Resuming game")
                    elif menu_options[selected_option] == "Reload":
                        reset_game()
                        paused = False
                        print("Game reloaded")
                    elif menu_options[selected_option] == "Launcher menu":
                        running = False
                        return_to_launcher = True
                        print("Returning to launcher menu")
                    elif menu_options[selected_option] == "Exit":
                        running = False
                        return_to_launcher = False
                        print("Exiting game")

                # Draw menu options with precise alignment
                for i, option in enumerate(menu_options):
                    color = YELLOW if i == selected_option else WHITE
                    option_text = menu_font.render(f"[ {option} ]", True, color)
                    # Adjust x-position for alignment
                    if option == "Back to the game":
                        x_offset = -30  # Adjusted for better alignment
                    elif option == "Reload":
                        x_offset = 0    # Centered
                    elif option == "Launcher menu":
                        x_offset = -15  # Adjusted for better alignment
                    else:  # Exit
                        x_offset = 15   # Adjusted for better alignment
                    option_rect = option_text.get_rect(center=(WIDTH // 2 + x_offset, HEIGHT // 2 + i * 40))
                    # Add shadow for 3D effect
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
if engine_sound is not None:
    engine_sound.stop()
pygame.mixer.music.stop()

pygame.quit()

if return_to_launcher:
    print("Exiting with return code 0 (return to launcher)")
    exit(0)
else:
    print("Exiting with return code 1 (full exit)")
    exit(1)