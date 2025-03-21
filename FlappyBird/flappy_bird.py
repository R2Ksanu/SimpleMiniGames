import pygame
import random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SMG Flappy Bird")
clock = pygame.time.Clock()

# Colors
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Bird and pipes
bird = pygame.Rect(200, 300, 40, 40)
velocity = 0
gravity = 0.5
pipes = [pygame.Rect(WIDTH, random.randint(100, 400), 60, HEIGHT)]

# Game loop
running = True
score = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            velocity = -10

    # Bird physics
    velocity += gravity
    bird.y += velocity

    # Move pipes
    for pipe in pipes[:]:
        pipe.x -= 3
        if pipe.x < -pipe.width:
            pipes.remove(pipe)
            pipes.append(pygame.Rect(WIDTH, random.randint(100, 400), 60, HEIGHT))
            score += 1

    # Collision
    if bird.y < 0 or bird.y > HEIGHT or any(bird.colliderect(pygame.Rect(pipe.x, 0, pipe.width, pipe.y)) or bird.colliderect(pygame.Rect(pipe.x, pipe.y + 150, pipe.width, HEIGHT)) for pipe in pipes):
        running = False

    # Draw
    screen.fill(GREEN)
    pygame.draw.rect(screen, WHITE, bird)
    for pipe in pipes:
        pygame.draw.rect(screen, RED, (pipe.x, 0, pipe.width, pipe.y))
        pygame.draw.rect(screen, RED, (pipe.x, pipe.y + 150, pipe.width, HEIGHT))
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()