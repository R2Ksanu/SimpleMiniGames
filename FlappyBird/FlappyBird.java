public class FlappyBird {
    private boolean isGameOver;
    private int score;

    public FlappyBird() {
        this.isGameOver = false;
        this.score = 0;
    }

    public void flap() {
        System.out.println("Bird flaps!");
    }

    public void endGame() {
        isGameOver = true;
        System.out.println("Game Over! Score: " + score);
    }

    public void increaseScore() {
        score += 1;
    }

    public static void main(String[] args) {
        FlappyBird game = new FlappyBird();
        game.flap();
        game.increaseScore();
        game.endGame();
    }
}