from collections import deque
import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (40, 180, 90)
BLUE = (40, 110, 220)
YELLOW = (240, 210, 60)
PURPLE = (160, 90, 210)
ORANGE = (230, 140, 40)

COLORS = [BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE, WHITE]
TOOLS = ["pencil", "line", "rect", "circle", "square", "right_tri", "eq_tri", "rhombus", "eraser", "fill", "text"]


def draw_shape(surface, tool, color, start, end, width):
    x1, y1 = start
    x2, y2 = end
    rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
    if tool == "line":
        pygame.draw.line(surface, color, start, end, width)
    elif tool == "rect":
        pygame.draw.rect(surface, color, rect, width)
    elif tool == "circle":
        radius = max(rect.width, rect.height) // 2
        pygame.draw.circle(surface, color, start, radius, width)
    elif tool == "square":
        side = max(abs(x2 - x1), abs(y2 - y1))
        square = pygame.Rect(x1, y1, side if x2 >= x1 else -side, side if y2 >= y1 else -side)
        square.normalize()
        pygame.draw.rect(surface, color, square, width)
    elif tool == "right_tri":
        points = [(x1, y1), (x1, y2), (x2, y2)]
        pygame.draw.polygon(surface, color, points, width)
    elif tool == "eq_tri":
        side = x2 - x1
        h = int(abs(side) * 0.866)
        points = [(x1, y2), (x2, y2), ((x1 + x2) // 2, y2 - h if y2 > y1 else y2 + h)]
        pygame.draw.polygon(surface, color, points, width)
    elif tool == "rhombus":
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        points = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
        pygame.draw.polygon(surface, color, points, width)


def flood_fill(surface, pos, new_color):
    w, h = surface.get_size()
    x, y = pos
    if not (0 <= x < w and 0 <= y < h):
        return
    target = surface.get_at((x, y))
    replacement = pygame.Color(*new_color)
    if target == replacement:
        return
    q = deque([(x, y)])
    while q:
        px, py = q.popleft()
        if not (0 <= px < w and 0 <= py < h):
            continue
        if surface.get_at((px, py)) != target:
            continue
        surface.set_at((px, py), replacement)
        q.extend([(px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1)])
