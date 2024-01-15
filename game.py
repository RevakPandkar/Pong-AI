import pygame
import random


class Paddle:
    def __init__(self, x, y):
        self.length = 100
        self.width = 20
        self.original_x = x
        self.original_y = y
        self.rect = pygame.Rect(x - self.width // 2, y - self.length // 2, self.width, self.length)
        self.vel = 7

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
        self.x_vel = -self.max_vel
        self.y_vel = 0
        self.rect = pygame.Rect(x - self.radius // 2, y - self.radius // 2, self.radius, self.radius)

    def draw(self, win):
        pygame.draw.ellipse(win, (255, 255, 255), self.rect)

    def move(self):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel

    def reset(self):
        self.rect.centerx = 800 // 2
        self.rect.centery = 500 // 2
        self.y_vel = random.randint(-3, 3)


class Pong:
    pygame.init()
    WIDTH = 800
    HEIGHT = 500
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption('Pong')
    player1_score = 0
    player2_score = 0
    winning_score = 10
    winner = 0
    score_font = pygame.font.SysFont('timesnewroman', 50)
    win_msg_font = pygame.font.SysFont('timesnewroman', 60)
    title_font = pygame.font.SysFont('timesnewroman', 80)
    button_font = pygame.font.SysFont('timesnewroman', 45)
    bg_music = pygame.mixer.Sound('SFX/music.wav')
    bg_music.set_volume(0.4)
    bg_music.play(loops=-1)
    score_sfx = pygame.mixer.Sound('SFX/ding.wav')
    wall_sfx = pygame.mixer.Sound('SFX/pong.wav')
    paddle_sfx = pygame.mixer.Sound('SFX/ping.wav')
    game_active = False
    game_over = False
    pvp = False
    PADDLE_OFFSET = 25
    paddle1 = Paddle(PADDLE_OFFSET, HEIGHT // 2)
    paddle2 = Paddle(WIDTH - PADDLE_OFFSET, HEIGHT // 2)
    ball = Ball(WIDTH // 2, HEIGHT // 2)

    last_hit_time = 0
    AI_LEVEL = 7
    AI_MOVE_DELAY = 500

    def draw_window(self, win, paddle1, paddle2, ball, player1_score, player2_score,draw_trajectory=False):
        win.fill('black')
        pygame.draw.line(win, (255, 255, 255), (self.WIDTH // 2, 0), (self.WIDTH // 2, self.HEIGHT), 3)

        score1_text = self.score_font.render(f'{player1_score}', True, (255, 255, 255))
        score2_text = self.score_font.render(f'{player2_score}', True, (255, 255, 255))
        win.blit(score1_text, (self.WIDTH // 2 - score1_text.get_width() - 20, 10))
        win.blit(score2_text, (self.WIDTH // 2 + 20, 10))
        paddle1.draw(win)
        paddle2.draw(win)
        if draw_trajectory:
            self.calculate_trajectory(ball, True)
        ball.draw(win)

        pygame.display.update()

    def paddle_movement(self, paddle1, paddle2):
        keys = pygame.key.get_pressed()
        self.player1_paddle_movement(paddle1)

        if keys[pygame.K_UP] and paddle2.rect.top > 0:
            paddle2.move('up')
        if keys[pygame.K_DOWN] and paddle2.rect.bottom < self.HEIGHT:
            paddle2.move('down')

    def player1_paddle_movement(self, paddle1):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and paddle1.rect.top > 0:
            paddle1.move('up')
        if keys[pygame.K_s] and paddle1.rect.bottom < self.HEIGHT:
            paddle1.move('down')

    def calculate_new_coordinates(self, ball_x, ball_y, x_vel, y_vel):
        # x_length and y_length are basically the no of steps the ball has to take
        # Dividing by x_vel and y_vel we get the no of steps (negative in some cases because no of steps must be +ve)
        if x_vel > 0:
            x_length = (self.WIDTH - self.PADDLE_OFFSET - ball_x) / x_vel
        else:
            x_length = (ball_x - self.PADDLE_OFFSET) / -x_vel

        if y_vel > 0:
            y_length = (self.HEIGHT - ball_y) / y_vel
        elif y_vel < 0:
            y_length = ball_y / -y_vel
        else:
            # We handle y_vel = 0 separately to avoid Zero Division Error
            # In cases when y_vel = 0 the ball will definitely collide with paddles and not the wall, so we can set
            # the no of steps in the y direction to be the same as the no of steps in the x direction
            # We cannot set y_length = 0 because min is calculated later on which will mess up new_x and new_y
            y_length = x_length

        # The new x and y that the ball will end up at will be its vel times the number of steps
        # Min is taken because we want to take the shorter distance so whether the ball collides with the wall or
        # the paddle first will be determined
        new_x = ball_x + x_vel * min(x_length, y_length)
        new_y = ball_y + y_vel * min(x_length, y_length)

        # if x_length is greater than y_length we will hit the top or bottom, so we have to draw another line
        return new_x, new_y, x_length > y_length

    def calculate_trajectory(self, ball, draw=False):
        new_x, new_y, hit_top_or_bottom = self.calculate_new_coordinates(ball.rect.centerx, ball.rect.centery,
                                                                         ball.x_vel, ball.y_vel)
        # Draw the first line
        if draw:
            pygame.draw.line(self.window, (255, 0, 0), (ball.rect.centerx, ball.rect.centery), (new_x, new_y), 3)

        # If ball hits the top or bottom we draw another line and pass the new_x and new_y as starting coordinates
        # The y_vel is negated because the ball changes direction if hit top or bottom
        if hit_top_or_bottom:
            new_x2, new_y2, _ = self.calculate_new_coordinates(new_x, new_y, ball.x_vel, -ball.y_vel)
            if draw:
                pygame.draw.line(self.window, (255, 0, 0), (new_x, new_y), (new_x2, new_y2), 3)
            return new_y2

        return new_y

    def comp_paddle_movement(self, paddle2, ball):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit_time >= self.AI_MOVE_DELAY:
            ball_trajectory_y = self.calculate_trajectory(ball)
            if ball_trajectory_y < paddle2.rect.centery - 5 and paddle2.rect.top > 0:
                paddle2.move('up')
            elif ball_trajectory_y > paddle2.rect.centery + 5 and paddle2.rect.bottom < self.HEIGHT:
                paddle2.move('down')

    def handle_collisions(self, ball, paddle1, paddle2):
        # Check for collisions with wall
        if ball.rect.top <= 0 or ball.rect.bottom + ball.y_vel >= self.HEIGHT:
            ball.y_vel = -ball.y_vel
            self.wall_sfx.play()

        # Check for collisions on left and right sides
        if ball.rect.right <= 0:
            self.player2_score += 1
            ball.reset()
            ball.x_vel = ball.max_vel
            self.score_sfx.play()

        elif ball.rect.left >= self.WIDTH:
            self.player1_score += 1
            ball.reset()
            ball.x_vel = -ball.max_vel
            self.score_sfx.play()

        if ball.x_vel < 0:
            if paddle1.rect.y <= ball.rect.centery <= paddle1.rect.bottom + 5:
                if paddle1.rect.x + paddle1.width >= ball.rect.x:
                    ball.x_vel = -ball.x_vel

                    y_difference = paddle1.rect.centery - ball.rect.centery
                    y_vel = (y_difference / (paddle1.length / 2)) * ball.max_vel
                    ball.y_vel = -y_vel
                    self.last_hit_time = pygame.time.get_ticks()
                    self.paddle_sfx.play()
        else:
            if paddle2.rect.y <= ball.rect.centery <= paddle2.rect.bottom + 5:
                if paddle2.rect.x <= ball.rect.centerx + ball.radius:
                    ball.x_vel = -ball.x_vel

                    y_difference = paddle2.rect.centery - ball.rect.centery
                    y_vel = (y_difference / (paddle1.length / 2)) * ball.max_vel
                    ball.y_vel = -y_vel
                    self.last_hit_time = pygame.time.get_ticks()
                    self.paddle_sfx.play()

    def draw_start_screen(self, win):
        win.fill('black')
        game_name = self.title_font.render('Pong', True, (255, 255, 255))
        game_name_rect = game_name.get_rect(center=(self.WIDTH // 2, 100))
        win.blit(game_name, game_name_rect)

        pvp_button = pygame.Surface((225, 60))
        pvp_button.fill('White')
        pvp_button_rect = pvp_button.get_rect(center=(self.WIDTH // 2, 275))
        win.blit(pvp_button, pvp_button_rect)

        pvp_text = self.button_font.render('Vs. Player', True, (0, 0, 0))
        pvp_text_rect = pvp_text.get_rect(center=(self.WIDTH // 2, 275))
        win.blit(pvp_text, pvp_text_rect)

        pvc_button = pygame.Surface((215, 60))
        pvc_button.fill('White')
        pvc_button_rect = pvc_button.get_rect(center=(self.WIDTH // 2, 375))
        win.blit(pvc_button, pvc_button_rect)

        pvc_text = self.button_font.render('Vs. Comp', True, (0, 0, 0))
        pvc_text_rect = pvc_text.get_rect(center=(self.WIDTH // 2, 375))
        win.blit(pvc_text, pvc_text_rect)

        game_active = False
        pvp = None

        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            if pvp_button_rect.collidepoint(mouse_pos):
                game_active = True
                pvp = True
            if pvc_button_rect.collidepoint(mouse_pos):
                game_active = True
                pvp = False

        pygame.display.update()
        return game_active, pvp

    def draw_win_message(self, win, winner):
        if winner == 1:
            msg_pos_x = self.WIDTH // 2 - 200
            button_pos_x = self.WIDTH // 2 - 200
        else:
            msg_pos_x = self.WIDTH // 2 + 200
            button_pos_x = self.WIDTH // 2 + 200

        win_msg = self.win_msg_font.render('Win!', True, (255, 255, 255))
        win_msg_rect = win_msg.get_rect(center=(msg_pos_x, 150))

        win.blit(win_msg, win_msg_rect)

        restart_button = pygame.Surface((175, 50))
        restart_button.fill('White')
        restart_button_rect = restart_button.get_rect(center=(button_pos_x, 300))
        win.blit(restart_button, restart_button_rect)

        restart_text = self.button_font.render('Restart', True, (0, 0, 0))
        restart_text_rect = restart_text.get_rect(center=(button_pos_x, 300))
        win.blit(restart_text, restart_text_rect)

        main_menu_button = pygame.Surface((250, 50))
        main_menu_button.fill('White')
        main_menu_button_rect = main_menu_button.get_rect(center=(button_pos_x, 375))
        win.blit(main_menu_button, main_menu_button_rect)

        main_menu_text = self.button_font.render('Main Menu', True, (0, 0, 0))
        main_menu_text_rect = main_menu_text.get_rect(center=(button_pos_x, 375))
        win.blit(main_menu_text, main_menu_text_rect)

        restart = False
        main_menu = False

        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            if restart_button_rect.collidepoint(mouse_pos):
                restart = True
            if main_menu_button_rect.collidepoint(mouse_pos):
                main_menu = True

        pygame.display.update()
        return restart, main_menu

    def reset(self):
        self.game_over = False
        self.player1_score = 0
        self.player2_score = 0
        self.paddle1.reset()
        self.paddle2.reset()

    def run(self):
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            if self.game_active:
                if not self.game_over:
                    if self.pvp:
                        # Moving the paddles
                        self.paddle_movement(self.paddle1, self.paddle2)

                        # Move the ball
                        self.ball.move()

                        # Handling collisions
                        self.handle_collisions(self.ball, self.paddle1, self.paddle2)

                    else:
                        self.player1_paddle_movement(self.paddle1)
                        self.comp_paddle_movement(self.paddle2, self.ball)
                        self.ball.move()
                        self.handle_collisions(self.ball, self.paddle1, self.paddle2)

                    self.draw_window(self.window, self.paddle1, self.paddle2, self.ball, self.player1_score,
                                     self.player2_score,draw_trajectory=False)

                    if self.player1_score == self.winning_score:
                        self.game_over = True
                        self.winner = 1

                    elif self.player2_score == self.winning_score:
                        self.game_over = True
                        self.winner = 2

                else:
                    restart, main_menu = self.draw_win_message(self.window, self.winner)
                    if restart:
                        self.reset()

                    elif main_menu:
                        self.game_active = False
                        self.reset()

            else:
                self.game_active, self.pvp = self.draw_start_screen(self.window)
                if not self.pvp and self.pvp is not None:
                    self.paddle2.vel = self.AI_LEVEL


if __name__ == '__main__':
    game = Pong()
    game.run()
