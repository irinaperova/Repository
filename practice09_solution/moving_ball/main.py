from __future__ import annotations

import pygame

from ball import Ball


pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 09 - Moving Ball")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)
ball = Ball(x=WIDTH // 2, y=HEIGHT // 2)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_LEFT:
                ball.move(-1, 0, WIDTH, HEIGHT)
            elif event.key == pygame.K_RIGHT:
                ball.move(1, 0, WIDTH, HEIGHT)
            elif event.key == pygame.K_UP:
                ball.move(0, -1, WIDTH, HEIGHT)
            elif event.key == pygame.K_DOWN:
                ball.move(0, 1, WIDTH, HEIGHT)

    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, ball.color, (ball.x, ball.y), ball.radius)
    info = font.render("Use arrow keys to move the ball. Q to quit.", True, (40, 40, 40))
    screen.blit(info, (20, 20))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
