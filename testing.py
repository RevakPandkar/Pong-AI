import pygame
import random
import neat
import pickle

pygame.init()
WIDTH = 800
HEIGHT = 500
PADDLE_OFFSET = 25
window = pygame.display.set_mode((WIDTH, HEIGHT))
score_font = pygame.font.SysFont('timesnewroman', 50)
clock = pygame.time.Clock()
pygame.display.set_caption('Pong')


class Paddle:
    def __init__(self, x, y):
        self.length = 100
        self.width = 20
        self.original_x = x
        self.original_y = y
        self.rect = pygame.Rect(x - self.width // 2, y - self.length // 2, self.width, self.length)
        self.vel = 7
        self.hits = 0
        self.score = 0

    def draw(self, win):
        pygame.draw.rect(win, (255, 255, 255), self.rect)

    def move(self, direction):
        if direction == 'up':
            self.rect.y -= self.vel

        elif direction == 'down':
            self.rect.y += self.vel

    def reset(self):
        self.rect.centerx = self.original_x
        self.rect.centery = self.original_y


class Ball:
    def __init__(self, x, y):
        self.radius = 15
        self.max_vel = 7
        self.x_vel = self.max_vel
        self.y_vel = self.initialize_y_vel()
        self.rect = pygame.Rect(x - self.radius // 2, y - self.radius // 2, self.radius, self.radius)

    def initialize_y_vel(self):
        y_vel = random.randint(-3, 3)
        while y_vel == 0:
            y_vel = random.randint(-3, 3)

        return y_vel

    def draw(self, win):
        pygame.draw.ellipse(win, (255, 255, 255), self.rect)

    def move(self):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel

    def reset(self):
        self.rect.centerx = WIDTH // 2
        self.rect.centery = HEIGHT // 2
        self.y_vel = self.initialize_y_vel()


def draw_window(win, paddle1, paddle2, ball):
    win.fill('black')
    pygame.draw.line(win, (255, 255, 255), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 3)

    score1_text = score_font.render(f'{paddle1.score}', True, (255, 255, 255))
    score2_text = score_font.render(f'{paddle2.score}', True, (255, 255, 255))
    win.blit(score1_text, (WIDTH // 2 - score1_text.get_width() - 20, 10))
    win.blit(score2_text, (WIDTH // 2 + 20, 10))
    paddle1.draw(win)
    paddle2.draw(win)
    ball.draw(win)

    pygame.display.update()


def handle_collisions(ball, paddle1, paddle2):
    # Check for collisions with wall
    if ball.rect.top <= 0 or ball.rect.bottom >= HEIGHT:
        ball.y_vel = -ball.y_vel

    # Check for collisions on left and right sides
    if ball.rect.right <= 0:
        paddle2.score += 1
        ball.reset()
        ball.x_vel = ball.max_vel

    elif ball.rect.left >= WIDTH:
        paddle1.score += 1
        ball.reset()
        ball.x_vel = -ball.max_vel

    if ball.x_vel < 0:
        if paddle1.rect.y <= ball.rect.centery <= paddle1.rect.y + paddle1.length:
            if paddle1.rect.x + paddle1.width >= ball.rect.x:
                ball.x_vel = -ball.x_vel

                y_difference = paddle1.rect.centery - ball.rect.centery
                y_vel = (y_difference / (paddle1.length / 2)) * ball.max_vel
                ball.y_vel = -y_vel
                paddle1.hits += 1
    else:
        if paddle2.rect.y <= ball.rect.centery <= paddle2.rect.y + paddle2.length:
            if paddle2.rect.x <= ball.rect.x + ball.radius:
                ball.x_vel = -ball.x_vel

                y_difference = paddle2.rect.centery - ball.rect.centery
                y_vel = (y_difference / (paddle1.length / 2)) * ball.max_vel
                ball.y_vel = -y_vel
                paddle2.hits += 1


def player_paddle_movement(paddle):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and paddle.rect.top > 0:
        paddle.move('up')
    if keys[pygame.K_s] and paddle.rect.bottom < HEIGHT:
        paddle.move('down')


def move_ai_paddle(paddle, decision):
    # Move up
    if decision == 0 and paddle.rect.top > 0:
        paddle.move('up')
    # Move down
    elif decision == 1 and paddle.rect.bottom < HEIGHT:
        paddle.move('down')
    # Do nothing
    else:
        pass


def test_ai(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    paddle1 = Paddle(PADDLE_OFFSET, HEIGHT // 2)
    paddle2 = Paddle(WIDTH - PADDLE_OFFSET, HEIGHT // 2)
    ball = Ball(WIDTH // 2, HEIGHT // 2)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        player_paddle_movement(paddle1)

        output = net.activate((paddle2.rect.y, ball.rect.centery, abs(paddle2.rect.x - ball.rect.centerx)))
        decision = output.index(max(output))
        move_ai_paddle(paddle2, decision)

        ball.move()
        handle_collisions(ball, paddle1, paddle2)

        draw_window(window, paddle1, paddle2, ball)


if __name__ == '__main__':
    config_file = 'config.txt'
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Test the AI
    with open('winner.p', 'rb') as f:
        winner = pickle.load(f)

    test_ai(winner, config)
