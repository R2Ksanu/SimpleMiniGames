import pygame
import random
import os
import math

# Initialize Pygame
pygame.init()

# Window settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SMG Snake Game")
clock = pygame.time.Clock()

# Colors
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PURPLE = (128, 0, 128)
DARK_GREEN = (0, 200, 0)
LIGHT_GREEN = (100, 255, 100)
TRANSPARENT_PURPLE = (128, 0, 128, 150)

# Load textures (place these files in the SnakeGame/ folder)
try:
    snake_head_image = pygame.image.load("SnakeGame/snake_head.png").convert_alpha()
    snake_head_image = pygame.transform.scale(snake_head_image, (30, 30))
except FileNotFoundError:
    snake_head_image = pygame.Surface((20, 20))
    snake_head_image.fill(WHITE)

try:
    snake_body_image = pygame.image.load("SnakeGame/snake_body.png").convert_alpha()
    snake_body_image = pygame.transform.scale(snake_body_image, (22, 22))
except FileNotFoundError:
    snake_body_image = snake_head_image

try:
    food_image = pygame.image.load("SnakeGame/food.png").convert_alpha()
    food_base_size = (25, 25)
    food_image = pygame.transform.scale(food_image, food_base_size)
except FileNotFoundError:
    food_image = pygame.Surface((26, 26))
    food_image.fill(RED)

try:
    background_image = pygame.image.load("SnakeGame/background.png").convert()
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
except FileNotFoundError:
    background_image = pygame.Surface((WIDTH, HEIGHT))
    background_image.fill(GREEN)

# Particle class for death animation
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(5, 10)
        self.color = (GREEN[0], GREEN[1], GREEN[2], 255)
        self.velocity_x = random.uniform(-3, 3)
        self.velocity_y = random.uniform(-3, 3)
        self.lifetime = 60

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.lifetime -= 1
        alpha = max(0, int(255 * (self.lifetime / 60)))
        self.color = (GREEN[0], GREEN[1], GREEN[2], alpha)

    def draw(self, surface):
        pygame.draw.circle(surface, (self.color[0], self.color[1], self.color[2], self.color[3]), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, PURPLE, (int(self.x), int(self.y)), self.radius, 1)

# Score pop-up class for animation
class ScorePopup:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.lifetime = 60
        self.alpha = 255

    def update(self):
        self.y -= 1
        self.lifetime -= 1
        self.alpha = max(0, int(255 * (self.lifetime / 60)))

    def draw(self, surface):
        font = pygame.font.SysFont("Arial", 16, bold=True)  # Reduced from 20 to 16
        text = font.render(f"+{self.value}", True, RED)
        text.set_alpha(self.alpha)
        text_rect = text.get_rect(center=(self.x, self.y))
        surface.blit(text, text_rect)

# Snake and food
GRID_SIZE = 30
snake = [(400, 300)]
direction = (GRID_SIZE, 0)
food = pygame.Rect(
    random.randint(0, WIDTH - GRID_SIZE) // GRID_SIZE * GRID_SIZE,
    random.randint(0, HEIGHT - GRID_SIZE) // GRID_SIZE * GRID_SIZE,
    GRID_SIZE, GRID_SIZE
)
score = 0
score_animation_scale = 1.0
score_popups = []

# Animation variables
animation_time = 0
background_y = 0
background_speed = 1
glow_animation = 0

# Death animation variables
particles = []
death_animation_duration = 120
death_animation_timer = 0
game_over = False

# Game loop
running = True
last_direction = direction
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        # Update animation time
        animation_time += 0.1
        glow_animation += 0.05

        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and direction != (0, GRID_SIZE):
            direction = (0, -GRID_SIZE)
        if keys[pygame.K_DOWN] and direction != (0, -GRID_SIZE):
            direction = (0, GRID_SIZE)
        if keys[pygame.K_LEFT] and direction != (GRID_SIZE, 0):
            direction = (-GRID_SIZE, 0)
        if keys[pygame.K_RIGHT] and direction != (-GRID_SIZE, 0):
            direction = (GRID_SIZE, 0)

        # Update snake
        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        snake.insert(0, new_head)
        if pygame.Rect(new_head[0], new_head[1], GRID_SIZE, GRID_SIZE).colliderect(food):
            food.topleft = (
                random.randint(0, WIDTH - GRID_SIZE) // GRID_SIZE * GRID_SIZE,
                random.randint(0, HEIGHT - GRID_SIZE) // GRID_SIZE * GRID_SIZE
            )
            score += 1
            score_animation_scale = 1.3
            score_popups.append(ScorePopup(new_head[0] + GRID_SIZE // 2, new_head[1], 1))
        else:
            snake.pop()

        # Collision
        if (new_head[0] < 0 or new_head[0] >= WIDTH or
            new_head[1] < 0 or new_head[1] >= HEIGHT or
            new_head in snake[1:]):
            game_over = True
            for segment in snake:
                for _ in range(5):
                    particle = Particle(segment[0] + GRID_SIZE // 2, segment[1] + GRID_SIZE // 2)
                    particles.append(particle)

    # Scroll the background
    background_y += background_speed
    if background_y >= HEIGHT:
        background_y = 0

    # Draw the scrolling background
    screen.blit(background_image, (0, background_y - HEIGHT))
    screen.blit(background_image, (0, background_y))

    if not game_over:
        # Draw snake with animation
        for i, segment in enumerate(snake):
            if i == 0:
                head_rotated = snake_head_image
                if direction == (GRID_SIZE, 0):
                    head_rotated = pygame.transform.rotate(snake_head_image, 0)
                elif direction == (-GRID_SIZE, 0):
                    head_rotated = pygame.transform.rotate(snake_head_image, 180)
                elif direction == (0, -GRID_SIZE):
                    head_rotated = pygame.transform.rotate(snake_head_image, 90)
                elif direction == (0, GRID_SIZE):
                    head_rotated = pygame.transform.rotate(snake_head_image, -90)
                screen.blit(head_rotated, (segment[0], segment[1]))
            else:
                scale = 1 + 0.1 * math.sin(animation_time + i * 0.5)
                body_scaled = pygame.transform.scale(
                    snake_body_image,
                    (int(30 * scale), int(30 * scale))
                )
                body_rect = body_scaled.get_rect(center=(segment[0] + 15, segment[1] + 15))
                screen.blit(body_scaled, body_rect)

        # Draw food with pulsing animation
        food_scale = 1 + 0.05 * math.sin(animation_time * 2)
        food_scaled = pygame.transform.scale(
            food_image,
            (int(food_base_size[0] * food_scale), int(food_base_size[1] * food_scale))
        )
        food_rect = food_scaled.get_rect(center=(food.x + GRID_SIZE // 2, food.y + GRID_SIZE // 2))
        screen.blit(food_scaled, food_rect)

    # Draw particles for death animation
    if game_over:
        death_animation_timer += 1
        for particle in particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.lifetime <= 0:
                particles.remove(particle)
        if death_animation_timer >= death_animation_duration:
            running = False

    # Update score animation
    score_animation_scale = max(1.0, score_animation_scale - 0.05)

    # Draw beautiful scoreboard on the right side (smaller)
    font = pygame.font.SysFont("Arial", 24, bold=True)  # Reduced from 30 to 24 (Line 1)
    score_text = font.render(f"Score: {score}", True, WHITE)
    score_text_scaled = pygame.transform.scale(
        score_text,
        (int(score_text.get_width() * score_animation_scale), int(score_text.get_height() * score_animation_scale))
    )
    score_rect = score_text_scaled.get_rect(topright=(WIDTH - 15, 15))  # Adjusted margin (Line 2)

    # Draw background box with gradient effect
    box_padding = 5  # Reduced from 10 to 5 (Line 3)
    box_rect = pygame.Rect(
        score_rect.x - box_padding,
        score_rect.y - box_padding,
        score_rect.width + 2 * box_padding,
        score_rect.height + 2 * box_padding
    )
    gradient_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
    for y in range(box_rect.height):
        alpha = int(200 * (1 - y / box_rect.height))
        pygame.draw.line(gradient_surface, (LIGHT_GREEN[0], LIGHT_GREEN[1], LIGHT_GREEN[2], alpha), (0, y), (box_rect.width, y))
    screen.blit(gradient_surface, (box_rect.x, box_rect.y))

    # Draw glowing border
    glow_scale = 1 + 0.03 * math.sin(glow_animation)  # Reduced glow size (Line 4)
    glow_rect = pygame.Rect(
        box_rect.x - 3 * glow_scale,  # Reduced from 5 to 3 (Line 5)
        box_rect.y - 3 * glow_scale,  # Reduced from 5 to 3 (Line 6)
        box_rect.width + 6 * glow_scale,  # Reduced from 10 to 6 (Line 7)
        box_rect.height + 6 * glow_scale  # Reduced from 10 to 6 (Line 8)
    )
    pygame.draw.rect(screen, TRANSPARENT_PURPLE, glow_rect, 2)  # Reduced thickness from 3 to 2 (Line 9)
    pygame.draw.rect(screen, PURPLE, box_rect, 1)  # Reduced thickness from 2 to 1 (Line 10)

    # Draw score text with shadow
    shadow_offset = 1  # Reduced from 2 to 1 (Line 11)
    shadow_text = font.render(f"Score: {score}", True, (50, 50, 50))
    shadow_rect = shadow_text.get_rect(topright=(WIDTH - 15 + shadow_offset, 15 + shadow_offset))
    screen.blit(shadow_text, shadow_rect)
    screen.blit(score_text_scaled, score_rect)

    # Draw score pop-ups
    for popup in score_popups[:]:
        popup.update()
        popup.draw(screen)
        if popup.lifetime <= 0:
            score_popups.remove(popup)

    pygame.display.flip()
    clock.tick(60 if game_over else 10)

pygame.quit()