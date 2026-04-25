import random
import pygame

# Initialize pygame
pygame.init()

# Grid settings
CELL = 20
COLS = 30
ROWS = 20
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 11 - Snake")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 42)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 140, 0)
RED = (220, 50, 50)
ORANGE = (255, 165, 0)
YELLOW = (255, 215, 0)
GRAY = (40, 40, 40)

# Snake state
snake = [(5, 5), (4, 5), (3, 5)]
direction = (1, 0)
next_direction = direction

# Speed / score
score = 0
fps = 8
game_over = False

# Food settings
FOOD_LIFETIME_MS = 5000  # food disappears after 5 seconds


def spawn_food():
    """Create food in a free cell with a random weight."""
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in snake:
            weight = random.choice([1, 2, 3])
            born_time = pygame.time.get_ticks()
            return {
                "pos": pos,
                "weight": weight,
                "born_time": born_time,
            }


food = spawn_food()

running = True
while running:
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Change direction with arrow keys
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != (0, 1):
                next_direction = (0, -1)
            elif event.key == pygame.K_DOWN and direction != (0, -1):
                next_direction = (0, 1)
            elif event.key == pygame.K_LEFT and direction != (1, 0):
                next_direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                next_direction = (1, 0)
            elif event.key == pygame.K_r and game_over:
                # Restart game
                snake = [(5, 5), (4, 5), (3, 5)]
                direction = (1, 0)
                next_direction = direction
                score = 0
                fps = 8
                game_over = False
                food = spawn_food()

    if not game_over:
        # Replace expired food
        current_time = pygame.time.get_ticks()
        if current_time - food["born_time"] > FOOD_LIFETIME_MS:
            food = spawn_food()

        # Apply next direction
        direction = next_direction

        # Move snake
        head_x, head_y = snake[0]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)

        # Check wall collision
        if (
            new_head[0] < 0 or new_head[0] >= COLS or
            new_head[1] < 0 or new_head[1] >= ROWS or
            new_head in snake
        ):
            game_over = True
        else:
            snake.insert(0, new_head)

            # Check if food is eaten
            if new_head == food["pos"]:
                score += food["weight"]

                # Increase speed a little after eating
                fps = min(20, fps + food["weight"])
                food = spawn_food()
            else:
                snake.pop()

    # Draw background
    screen.fill(BLACK)

    # Draw grid
    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

    # Draw snake
    for i, segment in enumerate(snake):
        rect = pygame.Rect(segment[0] * CELL, segment[1] * CELL, CELL, CELL)
        pygame.draw.rect(screen, GREEN if i == 0 else DARK_GREEN, rect)

    # Draw food
    fx, fy = food["pos"]
    food_rect = pygame.Rect(fx * CELL, fy * CELL, CELL, CELL)

    if food["weight"] == 1:
        color = RED
    elif food["weight"] == 2:
        color = ORANGE
    else:
        color = YELLOW

    pygame.draw.rect(screen, color, food_rect)

    # Draw food weight
    weight_text = font.render(str(food["weight"]), True, BLACK)
    screen.blit(weight_text, (fx * CELL + 4, fy * CELL - 2))

    # Remaining time for food
    time_left = max(0, (FOOD_LIFETIME_MS - (pygame.time.get_ticks() - food["born_time"])) // 1000)

    # UI
    score_text = font.render(f"Score: {score}", True, WHITE)
    speed_text = font.render(f"Speed: {fps}", True, WHITE)
    timer_text = font.render(f"Food timer: {time_left}", True, WHITE)

    screen.blit(score_text, (10, 10))
    screen.blit(speed_text, (10, 35))
    screen.blit(timer_text, (10, 60))

    if game_over:
        over_text = big_font.render("GAME OVER", True, WHITE)
        restart_text = font.render("Press R to restart", True, WHITE)
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))

    pygame.display.flip()

pygame.quit()