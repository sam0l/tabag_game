import pygame
import socket
import json
import threading
import sys

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Online Ping Pong")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Load images (replace with your PNGs)
paddle1_img = pygame.image.load("paddle1.png").convert_alpha()
paddle2_img = pygame.image.load("paddle2.png").convert_alpha()
ball_img = pygame.image.load("ball.png").convert_alpha()
paddle1_img = pygame.transform.scale(paddle1_img, (30, 120))
paddle2_img = pygame.transform.scale(paddle2_img, (30, 120))
ball_img = pygame.transform.scale(ball_img, (30, 30))

player1 = paddle1_img.get_rect(x=50, centery=HEIGHT//2)
player2 = paddle2_img.get_rect(x=WIDTH-80, centery=HEIGHT//2)
DEFAULT_PADDLE_SIZE = (30, 120)

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 74)
replay_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)

# Network setup
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 5555))  # Change to server IP for remote play

# Game state
game_state = None
player_idx = None
winner = None
text_input = ""
input_active = True

def receive_data():
    global game_state, player_idx, winner
    while True:
        try:
            data = client.recv(1024).decode()
            if not data:
                break
            msg = json.loads(data)
            if msg["type"] == "start":
                player_idx = msg["player"]
            elif msg["type"] == "update":
                game_state = msg["state"]
                if game_state["score1"] >= 3:
                    winner = "P 1" if player_idx == 0 else "P 2"
                elif game_state["score2"] >= 3:
                    winner = "P 2" if player_idx == 0 else "P 1"
            elif msg["type"] == "error":
                print(msg["msg"])
                pygame.quit()
                sys.exit()
        except:
            break

threading.Thread(target=receive_data, daemon=True).start()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if input_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and text_input:
                    client.send(text_input.encode())
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]
                else:
                    text_input += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN and winner:
            if replay_button.collidepoint(event.pos):
                client.close()
                pygame.quit()
                sys.exit()  # Restart logic could be added here
        elif event.type == pygame.KEYDOWN and not winner:
            keys = pygame.key.get_pressed()
            y = player1.centery if player_idx == 0 else player2.centery
            if (player_idx == 0 and keys[pygame.K_w]) or (player_idx == 1 and keys[pygame.K_UP]):
                y = max(0, y - 5)
            if (player_idx == 0 and keys[pygame.K_s]) or (player_idx == 1 and keys[pygame.K_DOWN]):
                y = min(HEIGHT - DEFAULT_PADDLE_SIZE[1], y + 5)
            client.send(json.dumps({"type": "move", "y": y}).encode())

    screen.fill(BLACK)

    if input_active:
        text = font.render("Enter Game Code: " + text_input, True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
    elif game_state:
        player1.centery = game_state["p1_y"]
        player2.centery = game_state["p2_y"]
        screen.blit(paddle1_img, player1)
        screen.blit(paddle2_img, player2)
        for ball in game_state["balls"]:
            ball_rect = ball_img.get_rect(center=(ball["x"], ball["y"]))
            screen.blit(ball_img, ball_rect)

        pygame.draw.aaline(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))
        p1_text = font.render("P 1", True, WHITE)
        p2_text = font.render("P 2", True, WHITE)
        score_text = font.render(f"{game_state['score1']} - {game_state['score2']}", True, WHITE)
        screen.blit(p1_text, (WIDTH//4, 20))
        screen.blit(p2_text, (3*WIDTH//4, 20))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))

        if winner:
            win_text = big_font.render(f"{winner} you are the best engineer!", True, WHITE)
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 50))
            pygame.draw.rect(screen, WHITE, replay_button)
            replay_text = font.render("Quit", True, BLACK)
            screen.blit(replay_text, (replay_button.x + 60, replay_button.y + 10))

    pygame.display.flip()
    clock.tick(60)

client.close()
pygame.quit()
sys.exit()