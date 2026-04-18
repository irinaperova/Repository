from __future__ import annotations

from datetime import datetime
from pathlib import Path
import pygame

from clock import MickeyClock


pygame.init()

BASE_DIR = Path(__file__).resolve().parent

screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Practice 09 - Mickey's Clock")

clock_app = MickeyClock(BASE_DIR / "images")
run_clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            running = False

    now = datetime.now()
    clock_app.draw(screen, now)
    pygame.display.flip()
    run_clock.tick(clock_app.config.fps)

pygame.quit()