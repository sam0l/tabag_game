import pygame
import sys
import random

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong Game")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

paddle1_img = pygame.image.load("tabag.png").convert_alpha()
paddle2_img = pygame.image.load("tabag.png").convert_alpha()
ball_img = pygame.image.load("eviltabag.png").convert_alpha()
speed_img = pygame.image.load("tabagbike.jpg").convert_alpha()
size_img = pygame.image.load("tabagcart.jpg").convert_alpha()
multi_img = pygame.image.load("tabagpower.jpg").convert_alpha()

paddle1_img = pygame.transform.scale(paddle1_img, (30, 120))
paddle2_img = pygame.transform.scale(paddle2_img, (30, 120))
ball_img = pygame.transform.scale(ball_img, (30, 30))
speed_img = pygame.transform.scale(speed_img, (50, 50))
size_img = pygame.transform.scale(size_img, (50, 50))
multi_img = pygame.transform.scale(multi_img, (50, 50))

player1 = paddle1_img.get_rect(x=50, centery=HEIGHT//2)
player2 = paddle2_img.get_rect(x=WIDTH-80, centery=HEIGHT//2)
balls = [ball_img.get_rect(center=(WIDTH//2, HEIGHT//2))]
ball_speeds = [(7, 7)]
DEFAULT_PADDLE_SIZE = (30, 120)
POWERUP_SIZE = (30, HEIGHT//2)

powerups = []
consecutive_scores = 0
speed_timer = 0
size1_timer = 0
size2_timer = 0
last_hit = None  # Track last player to hit the ball

score1 = 0
score2 = 0
WIN_SCORE = 10

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 74)
winner = None
replay_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)

def reset_game():
    global score1, score2, winner, balls, ball_speeds, consecutive_scores, powerups, last_hit
    score1 = 0
    score2 = 0
    winner = None
    balls = [ball_img.get_rect(center=(WIDTH//2, HEIGHT//2))]
    ball_speeds = [(7, 7)]
    consecutive_scores = 0
    powerups = []
    last_hit = None
    player1.size = DEFAULT_PADDLE_SIZE
    player2.size = DEFAULT_PADDLE_SIZE
    paddle1_img_scaled = pygame.transform.scale(paddle1_img, DEFAULT_PADDLE_SIZE)
    paddle2_img_scaled = pygame.transform.scale(paddle2_img, DEFAULT_PADDLE_SIZE)
    player1.centery = HEIGHT//2
    player2.centery = HEIGHT//2
    return paddle1_img_scaled, paddle2_img_scaled

def spawn_powerup():
    powerup_types = ["speed", "size", "multi"]
    type = random.choice(powerup_types)
    x = random.randint(200, WIDTH-200)
    y = random.randint(100, HEIGHT-100)
    if type == "speed":
        powerup = speed_img.get_rect(center=(x, y))
    elif type == "size":
        powerup = size_img.get_rect(center=(x, y))
    else:
        powerup = multi_img.get_rect(center=(x, y))
    powerups.append((type, powerup))

paddle1_img_scaled, paddle2_img_scaled = reset_game()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and winner:
            if replay_button.collidepoint(event.pos):
                paddle1_img_scaled, paddle2_img_scaled = reset_game()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and player1.top > 0:
        player1.y -= 5
    if keys[pygame.K_s] and player1.bottom < HEIGHT:
        player1.y += 5
    if keys[pygame.K_UP] and player2.top > 0:
        player2.y -= 5
    if keys[pygame.K_DOWN] and player2.bottom < HEIGHT:
        player2.y += 5

    if speed_timer > 0:
        speed_timer -= clock.get_time()
    if size1_timer > 0:
        size1_timer -= clock.get_time()
        if size1_timer <= 0:
            player1.size = DEFAULT_PADDLE_SIZE
            paddle1_img_scaled = pygame.transform.scale(paddle1_img, DEFAULT_PADDLE_SIZE)
    if size2_timer > 0:
        size2_timer -= clock.get_time()
        if size2_timer <= 0:
            player2.size = DEFAULT_PADDLE_SIZE
            paddle2_img_scaled = pygame.transform.scale(paddle2_img, DEFAULT_PADDLE_SIZE)

    if not winner:
        for i in range(len(balls) - 1, -1, -1):
            ball = balls[i]
            ball.x += ball_speeds[i][0]
            ball.y += ball_speeds[i][1]

            if ball.top <= 0 or ball.bottom >= HEIGHT:
                ball_speeds[i] = (ball_speeds[i][0], -ball_speeds[i][1])

            if speed_timer > 0:
                continue
            if ball.colliderect(player1):
                ball_speeds[i] = (-ball_speeds[i][0], ball_speeds[i][1])
                last_hit = "P1"  # Track Player 1 hit
            elif ball.colliderect(player2):
                ball_speeds[i] = (-ball_speeds[i][0], ball_speeds[i][1])
                last_hit = "P2"  # Track Player 2 hit

            if ball.left <= 0:
                score2 += 1
                consecutive_scores += 1
                del balls[i]
                del ball_speeds[i]
            elif ball.right >= WIDTH:
                score1 += 1
                consecutive_scores += 1
                del balls[i]
                del ball_speeds[i]

        if not balls:
            balls.append(ball_img.get_rect(center=(WIDTH//2, HEIGHT//2)))
            ball_speeds.append((7, 7))

        if consecutive_scores >= 2:
            spawn_powerup()
            consecutive_scores = 0

        for powerup in powerups[:]:
            type, rect = powerup
            for ball in balls:
                if ball.colliderect(rect):
                    powerups.remove(powerup)
                    if type == "speed":
                        speed_timer = 2000
                    elif type == "size" and last_hit:
                        if last_hit == "P1":
                            player1.size = POWERUP_SIZE
                            paddle1_img_scaled = pygame.transform.scale(paddle1_img, POWERUP_SIZE)
                            size1_timer = 5000
                        elif last_hit == "P2":
                            player2.size = POWERUP_SIZE
                            paddle2_img_scaled = pygame.transform.scale(paddle2_img, POWERUP_SIZE)
                            size2_timer = 5000
                    elif type == "multi":
                        new_balls = random.randint(1, 4)
                        for _ in range(new_balls):
                            new_ball = ball_img.get_rect(center=balls[0].center)
                            balls.append(new_ball)
                            angle = random.uniform(-1, 1)
                            ball_speeds.append((7 if ball_speeds[0][0] > 0 else -7, 7 * angle))
                    break

        if score1 >= WIN_SCORE:
            winner = "P 1"
        elif score2 >= WIN_SCORE:
            winner = "P 2"

    screen.fill(BLACK)
    screen.blit(paddle1_img_scaled, player1)
    screen.blit(paddle2_img_scaled, player2)
    for ball in balls:
        screen.blit(ball_img, ball)
    for type, rect in powerups:
        if type == "speed":
            screen.blit(speed_img, rect)
        elif type == "size":
            screen.blit(size_img, rect)
        else:
            screen.blit(multi_img, rect)
    
    pygame.draw.aaline(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))
    p1_text = font.render("P 1", True, WHITE)
    p2_text = font.render("P 2", True, WHITE)
    score_text = font.render(f"{score1} - {score2}", True, WHITE)
    screen.blit(p1_text, (WIDTH//4, 20))
    screen.blit(p2_text, (3*WIDTH//4, 20))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))

    if winner:
        win_text = big_font.render(f"{winner} you are the best engineer!", True, WHITE)
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 50))
        pygame.draw.rect(screen, WHITE, replay_button)
        replay_text = font.render("Replay", True, BLACK)
        screen.blit(replay_text, (replay_button.x + 60, replay_button.y + 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()