import pygame
import random
import neat
import time
import pickle

pygame.init()
WIDTH = 800
HEIGHT = 500
PADDLE_OFFSET = 25
window = pygame.display.set_mode((WIDTH, HEIGHT))
score_font = pygame.font.SysFont('timesnewroman', 40)
clock = pygame.time.Clock()
pygame.display.set_caption('Pong')
GEN = 0


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


def draw_window(win, paddle1, paddle2, ball, GEN):
    win.fill('black')
    pygame.draw.line(win, (255, 255, 255), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 3)

    gen_text = score_font.render(f'Gen: {GEN}', True, (255, 255, 255))
    win.blit(gen_text, (10, 10))
    hits_text = score_font.render(f'Hits :{paddle1.hits + paddle2.hits}', True, (255, 0, 0))
    win.blit(hits_text, (WIDTH // 4, 10))
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


def player1_paddle_movement(paddle1):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and paddle1.rect.top > 0:
        paddle1.move('up')
    if keys[pygame.K_s] and paddle1.rect.bottom < HEIGHT:
        paddle1.move('down')


def move_ai_paddle(paddle, decision, genome):
    # Move up
    if decision == 0:
        if paddle.rect.top > 0:
            paddle.move('up')
        # Reduce fitness if the AI tries to go up, but it can't go up
        else:
            genome.fitness -= 1

    # Move down
    elif decision == 1:
        if paddle.rect.bottom < HEIGHT:
            paddle.move('down')
        # Same for down
        else:
            genome.fitness -= 1

    # Do nothing
    else:
        # Reduce fitness if the AI stands still
        # Maybe not necessary
        genome.fitness -= 0.01


def calulate_fitness(paddle, duration):
    return paddle.hits + duration


def train_ai(genome1, genome2, config, GEN):
    start_time = time.time()
    max_hits = 50

    net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
    net2 = neat.nn.FeedForwardNetwork.create(genome2, config)

    paddle1 = Paddle(PADDLE_OFFSET, HEIGHT // 2)
    paddle2 = Paddle(WIDTH - PADDLE_OFFSET, HEIGHT // 2)
    ball = Ball(WIDTH // 2, HEIGHT // 2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        output1 = net1.activate((paddle1.rect.y, ball.rect.centery, abs(paddle1.rect.x - ball.rect.centerx)))
        output2 = net2.activate((paddle2.rect.y, ball.rect.centery, abs(paddle2.rect.x - ball.rect.centerx)))

        decision1 = output1.index(max(output1))
        decision2 = output2.index(max(output2))

        move_ai_paddle(paddle1, decision1, genome1)
        move_ai_paddle(paddle2, decision2, genome2)

        ball.move()
        handle_collisions(ball, paddle1, paddle2)

        # Amount of time they both played
        duration = time.time() - start_time

        if paddle1.score > 0 or paddle2.score > 0 or paddle1.hits >= max_hits:
            genome1.fitness += calulate_fitness(paddle1, duration)
            genome2.fitness += calulate_fitness(paddle2, duration)
            break

        draw_window(window, paddle1, paddle2, ball, GEN)


def eval_genomes(genomes, config):
    global GEN
    GEN += 1
    for i, (genome_id1, genome1) in enumerate(genomes):
        if i == len(genomes) - 1:
            break
        genome1.fitness = 0
        for genome_id2, genome2 in genomes[i + 1:]:
            genome2.fitness = 0 if genome2.fitness is None else genome2.fitness
            train_ai(genome1, genome2, config, GEN)


def run_neat(config):
    # p = neat.Checkpointer.restore_checkpoint('')
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())
    p.add_reporter(neat.Checkpointer(1))

    winner = p.run(eval_genomes, 50)

    with open('winner.p', 'wb') as f:
        pickle.dump(winner, f)


if __name__ == '__main__':
    config_file = 'config.txt'
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Train the AI
    run_neat(config)
