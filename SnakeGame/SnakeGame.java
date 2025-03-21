public class SnakeGame {
    private int highScore;

    public SnakeGame() {
        this.highScore = 0;
    }

    public void updateHighScore(int currentScore) {
        if (currentScore > highScore) {
            highScore = currentScore;
            System.out.println("New High Score: " + highScore);
        }
    }

    public int getHighScore() {
        return highScore;
    }

    public static void main(String[] args) {
        SnakeGame game = new SnakeGame();
        game.updateHighScore(5);
        game.updateHighScore(10);
    }
}