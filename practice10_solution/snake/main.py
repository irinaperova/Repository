import random
import pygame

pygame.init()

CELL = 20
COLS = 30
ROWS = 20
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL

WHITE = (255, 255, 255)
GREEN = (0, 180, 0)
DARK_GREEN = (0, 120, 0)
RED = (220, 50, 50)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 10 - Snake")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

snake = [(5, 5), (4, 5), (3, 5)]
direction = (1, 0)
next_direction = direction

food = (10, 10)
score = 0
level = 1
fps = 8


def spawn_food():
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in snake:
            return pos


food = spawn_food()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != (0, 1):
                next_direction = (0, -1)
            elif event.key == pygame.K_DOWN and direction != (0, -1):
                next_direction = (0, 1)
            elif event.key == pygame.K_LEFT and direction != (1, 0):
                next_direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                next_direction = (1, 0)

    direction = next_direction

    head_x, head_y = snake[0]
    dx, dy = direction
    new_head = (head_x + dx, head_y + dy)

    if (
        new_head[0] < 0 or new_head[0] >= COLS or
        new_head[1] < 0 or new_head[1] >= ROWS or
        new_head in snake
    ):
        running = False
        continue

    snake.insert(0, new_head)

    if new_head == food:
        score += 1
        if score % 4 == 0:
            level += 1
            fps += 2
        food = spawn_food()
    else:
        snake.pop()

    screen.fill(BLACK)

    for x in range(0, WIDTH, CELL):
        pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL):
        pygame.draw.line(screen, (40, 40, 40), (0, y), (WIDTH, y))

    for i, segment in enumerate(snake):
        rect = pygame.Rect(segment[0] * CELL, segment[1] * CELL, CELL, CELL)
        pygame.draw.rect(screen, GREEN if i == 0 else DARK_GREEN, rect)

    food_rect = pygame.Rect(food[0] * CELL, food[1] * CELL, CELL, CELL)
    pygame.draw.rect(screen, RED, food_rect)

    text = font.render(f"Score: {score}   Level: {level}", True, WHITE)
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()