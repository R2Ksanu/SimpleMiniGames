# SimpleMiniGames

A collection of mini-games built with Python and Pygame, including Car Game, Snake Game, and Flappy Bird Game. Use the launcher to select and play a game.

## Games Included
- **Car Game**: Navigate a car to collect coins, avoid obstacles, and use power-ups.
- **Snake Game**: Control a snake to eat food and grow while avoiding collisions.
- **Flappy Bird Game**: Guide a bird through a series of pipes by flapping its wings.

## Prerequisites
- Python 3.6 or higher
- Pygame library (`pip install pygame`)

## How to Run
1. Clone this repository to your local machine:

      - git clone https://github.com/your-username/SimpleMiniGames.git

cd SimpleMiniGames

3. Install the required dependencies:
            -   pip install pygame

4. Run the launcher:
      -python launcher.py


5. In the launcher, enter a number to select a game:
- `1` for Car Game
- `2` for Snake Game
- `3` for Flappy Bird Game
Then click "Play" or press Enter.

## Controls
### Car Game
- **Left Arrow**: Move car left
- **Right Arrow**: Move car right
- **ESC**: Open the escape menu
- In the escape menu, use **Up/Down Arrows** to navigate and **Enter** to select an option.

### Snake Game
- **Arrow Keys**: Move the snake (up, down, left, right)
- **ESC**: Open the escape menu (if implemented)

### Flappy Bird Game
- **Spacebar**: Flap the bird’s wings to fly
- **ESC**: Open the escape menu (if implemented)

## Troubleshooting
- If a game fails to load assets (e.g., images or sounds), ensure all files are in the respective game folder (`CarGame`, `SnakeGame`, `FlappyBird`).
- If you encounter a `pygame.error`, ensure Pygame is installed correctly.
- If the launcher fails to start a game, verify that the game files (`car_game.py`, `snake_game.py`, `flappy_bird.py`) are in their respective folders.

## Issues
If you encounter any problems while running the games, please create an issue on this repository: [New Issue](https://github.com/R2Ksanu/SimpleMiniGames/issues/new)