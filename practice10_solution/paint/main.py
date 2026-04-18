from __future__ import annotations

import math
from dataclasses import dataclass
import pygame

WIDTH, HEIGHT = 1000, 700
TOOLBAR_HEIGHT = 90
CANVAS_RECT = pygame.Rect(0, TOOLBAR_HEIGHT, WIDTH, HEIGHT - TOOLBAR_HEIGHT)

BG = (230, 232, 236)
TOOLBAR_BG = (40, 44, 55)
TEXT = (245, 245, 245)
WHITE = (255, 255, 255)

COLORS = [
    (0, 0, 0),
    (220, 20, 60),
    (50, 120, 255),
    (20, 170, 95),
    (240, 190, 30),
    (160, 70, 220),
    (255, 255, 255),
]


@dataclass
class ToolState:
    tool: str = "pencil"
    color: tuple[int, int, int] = (0, 0, 0)
    size: int = 6
    drawing: bool = False
    start_pos: tuple[int, int] | None = None
    prev_pos: tuple[int, int] | None = None


def draw_text(surface: pygame.Surface, font: pygame.font.Font, text: str, pos: tuple[int, int]) -> None:
    surface.blit(font.render(text, True, TEXT), pos)


def draw_toolbar(surface: pygame.Surface, font: pygame.font.Font, state: ToolState):
    pygame.draw.rect(surface, TOOLBAR_BG, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    draw_text(surface, font, "Tools: P-pencil  R-rectangle  C-circle  E-eraser", (16, 10))
    draw_text(surface, font, "Colors: 1..7 | Brush: [ ] | SPACE: clear | Q: quit", (16, 38))
    draw_text(surface, font, f"Current: {state.tool} | Size: {state.size}", (16, 64))

    swatches = []
    x = WIDTH - 320
    for i, color in enumerate(COLORS, start=1):
        rect = pygame.Rect(x, 18, 34, 34)
        pygame.draw.rect(surface, color, rect, border_radius=6)
        pygame.draw.rect(surface, (255, 255, 255) if color == state.color else (25, 25, 25), rect, 3 if color == state.color else 2, border_radius=6)
        number = font.render(str(i), True, (255, 255, 255) if sum(color) < 450 else (0, 0, 0))
        surface.blit(number, number.get_rect(center=rect.center))
        swatches.append((rect, color))
        x += 42
    return swatches


def draw_line_brush(surface: pygame.Surface, color: tuple[int, int, int], start: tuple[int, int], end: tuple[int, int], size: int) -> None:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = max(1, int(math.hypot(dx, dy)))
    for step in range(distance + 1):
        x = int(start[0] + dx * step / distance)
        y = int(start[1] + dy * step / distance)
        pygame.draw.circle(surface, color, (x, y), size)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Practice 10 - Paint")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 22)

    canvas = pygame.Surface(CANVAS_RECT.size)
    canvas.fill(WHITE)
    state = ToolState()
    swatches = []

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_p:
                    state.tool = "pencil"
                elif event.key == pygame.K_r:
                    state.tool = "rectangle"
                elif event.key == pygame.K_c:
                    state.tool = "circle"
                elif event.key == pygame.K_e:
                    state.tool = "eraser"
                elif event.key == pygame.K_SPACE:
                    canvas.fill(WHITE)
                elif event.key == pygame.K_LEFTBRACKET:
                    state.size = max(1, state.size - 1)
                elif event.key == pygame.K_RIGHTBRACKET:
                    state.size = min(40, state.size + 1)
                elif pygame.K_1 <= event.key <= pygame.K_7:
                    index = event.key - pygame.K_1
                    if 0 <= index < len(COLORS):
                        state.color = COLORS[index]
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if CANVAS_RECT.collidepoint(event.pos):
                    canvas_pos = (event.pos[0] - CANVAS_RECT.x, event.pos[1] - CANVAS_RECT.y)
                    state.drawing = True
                    state.start_pos = canvas_pos
                    state.prev_pos = canvas_pos
                    if state.tool == "pencil":
                        pygame.draw.circle(canvas, state.color, canvas_pos, state.size)
                    elif state.tool == "eraser":
                        pygame.draw.circle(canvas, WHITE, canvas_pos, state.size * 2)
                else:
                    for rect, color in swatches:
                        if rect.collidepoint(event.pos):
                            state.color = color
            elif event.type == pygame.MOUSEMOTION and state.drawing and CANVAS_RECT.collidepoint(event.pos):
                canvas_pos = (event.pos[0] - CANVAS_RECT.x, event.pos[1] - CANVAS_RECT.y)
                if state.tool == "pencil" and state.prev_pos is not None:
                    draw_line_brush(canvas, state.color, state.prev_pos, canvas_pos, state.size)
                elif state.tool == "eraser" and state.prev_pos is not None:
                    draw_line_brush(canvas, WHITE, state.prev_pos, canvas_pos, state.size * 2)
                state.prev_pos = canvas_pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and state.drawing:
                end_pos = (event.pos[0] - CANVAS_RECT.x, event.pos[1] - CANVAS_RECT.y) if CANVAS_RECT.collidepoint(event.pos) else state.prev_pos
                if state.start_pos is not None and end_pos is not None:
                    x1, y1 = state.start_pos
                    x2, y2 = end_pos
                    rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
                    if state.tool == "rectangle":
                        pygame.draw.rect(canvas, state.color, rect, max(1, state.size))
                    elif state.tool == "circle":
                        radius = int(math.hypot(x2 - x1, y2 - y1))
                        pygame.draw.circle(canvas, state.color, state.start_pos, radius, max(1, state.size))
                state.drawing = False
                state.start_pos = None
                state.prev_pos = None

        screen.fill(BG)
        swatches = draw_toolbar(screen, font, state)
        screen.blit(canvas, CANVAS_RECT.topleft)
        pygame.draw.rect(screen, (40, 40, 40), CANVAS_RECT, 2)

        if state.drawing and state.start_pos is not None and state.tool in {"rectangle", "circle"}:
            preview = canvas.copy()
            mouse = pygame.mouse.get_pos()
            if CANVAS_RECT.collidepoint(mouse):
                end_pos = (mouse[0] - CANVAS_RECT.x, mouse[1] - CANVAS_RECT.y)
                x1, y1 = state.start_pos
                x2, y2 = end_pos
                if state.tool == "rectangle":
                    rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
                    pygame.draw.rect(preview, state.color, rect, max(1, state.size))
                else:
                    radius = int(math.hypot(x2 - x1, y2 - y1))
                    pygame.draw.circle(preview, state.color, state.start_pos, radius, max(1, state.size))
                screen.blit(preview, CANVAS_RECT.topleft)
                pygame.draw.rect(screen, (40, 40, 40), CANVAS_RECT, 2)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
