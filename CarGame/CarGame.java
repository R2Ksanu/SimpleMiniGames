public class CarGame {
    private int score;

    public CarGame() {
        this.score = 0;
    }

    public void increaseScore() {
        score += 1;
        System.out.println("Current Score: " + score);
    }

    public int getScore() {
        return score;
    }

    public static void main(String[] args) {
        CarGame game = new CarGame();
        // Simulate scoring
        for (int i = 0; i < 5; i++) {
            game.increaseScore();
        }
    }
}