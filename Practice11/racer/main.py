
import random
import pygame

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 11 - Racer")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 40)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (60, 60, 60)
GREEN = (0, 200, 0)
RED = (220, 50, 50)
YELLOW = (255, 215, 0)
BLUE = (50, 100, 255)

# Road settings
ROAD_LEFT = 50
ROAD_RIGHT = WIDTH - 50

# Player settings
player_w, player_h = 40, 70
player_x = WIDTH // 2 - player_w // 2
player_y = HEIGHT - player_h - 20
player_speed = 6

# Enemy settings
enemy_w, enemy_h = 40, 70
enemy_x = random.randint(ROAD_LEFT, ROAD_RIGHT - enemy_w)
enemy_y = -enemy_h
enemy_speed = 5

# Coin settings
coin_size = 24
coin_x = random.randint(ROAD_LEFT, ROAD_RIGHT - coin_size)
coin_y = -coin_size
coin_speed = 5

# Coin weight can be 1, 2, or 3 points
coin_weight = random.choice([1, 2, 3])

# Score and progression
coins_collected = 0
N_COINS_TO_SPEED_UP = 5
enemy_speed_increase = 1

running = True
game_over = False

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Player movement
    if keys[pygame.K_LEFT] and player_x > ROAD_LEFT:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < ROAD_RIGHT - player_w:
        player_x += player_speed

    if not game_over:
        # Move enemy
        enemy_y += enemy_speed
        if enemy_y > HEIGHT:
            enemy_y = -enemy_h
            enemy_x = random.randint(ROAD_LEFT, ROAD_RIGHT - enemy_w)

        # Move coin
        coin_y += coin_speed
        if coin_y > HEIGHT:
            coin_y = -coin_size
            coin_x = random.randint(ROAD_LEFT, ROAD_RIGHT - coin_size)
            coin_weight = random.choice([1, 2, 3])

        # Rectangles for collision detection
        player_rect = pygame.Rect(player_x, player_y, player_w, player_h)
        enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_w, enemy_h)
        coin_rect = pygame.Rect(coin_x, coin_y, coin_size, coin_size)

        # Check collision with coin
        if player_rect.colliderect(coin_rect):
            coins_collected += coin_weight
            coin_y = -coin_size
            coin_x = random.randint(ROAD_LEFT, ROAD_RIGHT - coin_size)
            coin_weight = random.choice([1, 2, 3])

            # Increase enemy speed after every N coins
            if coins_collected % N_COINS_TO_SPEED_UP == 0:
                enemy_speed += enemy_speed_increase

        # Check collision with enemy
        if player_rect.colliderect(enemy_rect):
            game_over = True

    # Drawing background
    screen.fill(GREEN)
    pygame.draw.rect(screen, GRAY, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))
    pygame.draw.line(screen, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 4)
    pygame.draw.line(screen, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)

    # Dashed center line
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, WHITE, (WIDTH // 2, y), (WIDTH // 2, y + 20), 3)

    # Draw player car
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_w, player_h), border_radius=8)
    pygame.draw.rect(screen, BLACK, (player_x + 5, player_y + 10, 30, 20), border_radius=4)

    # Draw enemy car
    pygame.draw.rect(screen, RED, (enemy_x, enemy_y, enemy_w, enemy_h), border_radius=8)
    pygame.draw.rect(screen, BLACK, (enemy_x + 5, enemy_y + 10, 30, 20), border_radius=4)

    # Draw coin
    coin_color = YELLOW if coin_weight == 1 else (255, 165, 0) if coin_weight == 2 else (255, 100, 0)
    pygame.draw.circle(screen, coin_color, (coin_x + coin_size // 2, coin_y + coin_size // 2), coin_size // 2)
    weight_text = font.render(str(coin_weight), True, BLACK)
    screen.blit(weight_text, (coin_x + 6, coin_y + 2))

    # UI text
    coins_text = font.render(f"Coins: {coins_collected}", True, BLACK)
    speed_text = font.render(f"Enemy speed: {enemy_speed}", True, BLACK)
    screen.blit(coins_text, (10, 10))
    screen.blit(speed_text, (10, 40))

    if game_over:
        over_text = big_font.render("GAME OVER", True, BLACK)
        hint_text = font.render("Close the window", True, BLACK)
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 + 20))

    pygame.display.flip()

pygame.quit()