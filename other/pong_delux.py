import pygame
import sys
import random
from collections import deque

# Init
pygame.init()
WIDTH, HEIGHT = 1000, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Pong Power-Up Edition")
pygame.font.init()

# Load music
pygame.mixer.music.load('other/bg_music.mp3')
pygame.mixer.music.play(-1)

# Colors
BLACK = (10, 10, 10)
NEON = (0, 255, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Fonts
FONT = pygame.font.SysFont("Consolas", 40)
BIG_FONT = pygame.font.SysFont("Consolas", 60)

# Game settings
PADDLE_W, PADDLE_H = 15, 100
BALL_SIZE = 20
SCORE_LIMIT = 5
TRAIL_LENGTH = 12
POWERUP_SIZE = 25
POWERUP_INTERVAL = 8000  # milliseconds

# Rects
left_paddle = pygame.Rect(40, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
right_paddle = pygame.Rect(WIDTH - 55, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_SIZE, BALL_SIZE)
ball_vel = [random.choice([-6, 6]), random.choice([-4, 4])]
ball_trail = deque(maxlen=TRAIL_LENGTH)

# Game state
left_score = 0
right_score = 0
game_over = False
powerups = []
active_powerups = []
last_powerup_time = pygame.time.get_ticks()

# Timers
powerup_timers = {
    'grow': 0,
    'shrink': 0,
    'slow': 0,
    'boost': 0
}

clock = pygame.time.Clock()

# Power-Up Types
POWERUP_TYPES = ['grow', 'shrink', 'slow', 'boost']


def draw_trail():
    for i, pos in enumerate(ball_trail):
        alpha = int(255 * (i + 1) / len(ball_trail))
        trail_surface = pygame.Surface((BALL_SIZE, BALL_SIZE), pygame.SRCALPHA)
        trail_surface.fill((*NEON, alpha))
        WIN.blit(trail_surface, pos)


def draw_powerups():
    for pu in powerups:
        pygame.draw.circle(WIN, RED, pu['rect'].center, POWERUP_SIZE // 2)


def draw_game():
    WIN.fill(BLACK)
    draw_trail()
    draw_powerups()
    pygame.draw.rect(WIN, NEON, left_paddle, border_radius=10)
    pygame.draw.rect(WIN, NEON, right_paddle, border_radius=10)
    pygame.draw.ellipse(WIN, WHITE, ball)

    score_text = FONT.render(f"{left_score} : {right_score}", True, WHITE)
    WIN.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

    for ptype, end_time in powerup_timers.items():
        if pygame.time.get_ticks() < end_time:
            label = FONT.render(ptype.upper(), True, RED)
            WIN.blit(label, (20, 60 + 30 * list(powerup_timers.keys()).index(ptype)))

    pygame.display.update()


def draw_game_over():
    WIN.fill(BLACK)
    msg = "You Win!" if left_score > right_score else "AI Wins!"
    text = BIG_FONT.render(msg, True, NEON)
    sub = FONT.render("Press R to Restart", True, WHITE)
    WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
    WIN.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 10))
    pygame.display.update()


def move_ai():
    predict_y = ball.centery + ball_vel[1] * ((right_paddle.left - ball.right) // abs(ball_vel[0]) if ball_vel[0] > 0 else 0)
    center_diff = predict_y - right_paddle.centery
    speed = 5
    if pygame.time.get_ticks() < powerup_timers['shrink']:
        speed = 3
    if abs(center_diff) > 10:
        if center_diff > 0 and right_paddle.bottom < HEIGHT:
            right_paddle.y += speed
        elif center_diff < 0 and right_paddle.top > 0:
            right_paddle.y -= speed


def reset_ball():
    ball.center = (WIDTH // 2, HEIGHT // 2)
    ball_vel[0] *= random.choice([-1, 1])
    ball_vel[1] = random.choice([-5, 5])
    ball_trail.clear()


def handle_movement(keys):
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.y -= 7
    if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
        left_paddle.y += 7


def update_ball():
    global left_score, right_score, game_over
    speed_factor = 2 if pygame.time.get_ticks() < powerup_timers['boost'] else 1
    slow_factor = 0.5 if pygame.time.get_ticks() < powerup_timers['slow'] else 1
    
    ball.x += int(ball_vel[0] * speed_factor * slow_factor)
    ball.y += int(ball_vel[1] * speed_factor * slow_factor)
    ball_trail.append(ball.topleft)

    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_vel[1] *= -1

    if ball.colliderect(left_paddle) and ball_vel[0] < 0:
        ball_vel[0] *= -1
    if ball.colliderect(right_paddle) and ball_vel[0] > 0:
        ball_vel[0] *= -1

    if ball.left <= 0:
        right_score += 1
        reset_ball()
    elif ball.right >= WIDTH:
        left_score += 1
        reset_ball()

    if left_score >= SCORE_LIMIT or right_score >= SCORE_LIMIT:
        game_over = True

    check_powerup_collision()


def spawn_powerup():
    ptype = random.choice(POWERUP_TYPES)
    rect = pygame.Rect(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100), POWERUP_SIZE, POWERUP_SIZE)
    powerups.append({'type': ptype, 'rect': rect})


def check_powerup_collision():
    global powerup_timers
    for pu in powerups[:]:
        if ball.colliderect(pu['rect']):
            ptype = pu['type']
            powerup_timers[ptype] = pygame.time.get_ticks() + 5000
            powerups.remove(pu)
            if ptype == 'grow':
                left_paddle.height = 160
            elif ptype == 'shrink':
                right_paddle.height = 60
            elif ptype == 'slow':
                pass
            elif ptype == 'boost':
                pass


def check_powerup_expiry():
    if pygame.time.get_ticks() > powerup_timers['grow']:
        left_paddle.height = 100
    if pygame.time.get_ticks() > powerup_timers['shrink']:
        right_paddle.height = 100


def main():
    global left_score, right_score, game_over, last_powerup_time
    run = True
    while run:
        clock.tick(60)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                run = False
            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                left_score = 0
                right_score = 0
                game_over = False
                reset_ball()
                powerup_timers.update({k: 0 for k in powerup_timers})

        if not game_over:
            handle_movement(keys)
            move_ai()
            update_ball()
            if pygame.time.get_ticks() - last_powerup_time > POWERUP_INTERVAL:
                spawn_powerup()
                last_powerup_time = pygame.time.get_ticks()
            check_powerup_expiry()
            draw_game()
        else:
            draw_game_over()

    pygame.quit()
    sys.exit()


main()
