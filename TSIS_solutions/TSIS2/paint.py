import datetime as dt
import pygame
from tools import COLORS, TOOLS, WHITE, BLACK, draw_shape, flood_fill

pygame.init()
WIDTH, HEIGHT = 1100, 720
TOOLBAR_H = 92
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS2 Extended Paint")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 18)
big = pygame.font.SysFont("arial", 24)

canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_H))
canvas.fill(WHITE)
current_tool = "pencil"
current_color = BLACK
brush_size = 5
drawing = False
start_pos = None
last_pos = None
text_mode = False
text_pos = None
text_buffer = ""


def canvas_pos(pos):
    return pos[0], pos[1] - TOOLBAR_H


def in_canvas(pos):
    return pos[1] >= TOOLBAR_H


def draw_toolbar():
    screen.fill((230, 230, 230), (0, 0, WIDTH, TOOLBAR_H))
    x = 10
    for tool in TOOLS:
        rect = pygame.Rect(x, 10, 82, 30)
        pygame.draw.rect(screen, (180, 210, 255) if current_tool == tool else (245, 245, 245), rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, rect, 1, border_radius=5)
        screen.blit(font.render(tool, True, BLACK), (x + 5, 16))
        x += 88
    x = 10
    for color in COLORS:
        rect = pygame.Rect(x, 52, 34, 28)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 3 if color == current_color else 1)
        x += 42
    screen.blit(big.render(f"Brush: {brush_size}px  | keys 1/2/3 sizes | Ctrl+S save", True, BLACK), (380, 53))


def handle_toolbar_click(pos):
    global current_tool, current_color
    x = 10
    for tool in TOOLS:
        if pygame.Rect(x, 10, 82, 30).collidepoint(pos):
            current_tool = tool
            return True
        x += 88
    x = 10
    for color in COLORS:
        if pygame.Rect(x, 52, 34, 28).collidepoint(pos):
            current_color = color
            return True
        x += 42
    return False


def save_canvas():
    filename = f"paint_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    pygame.image.save(canvas, filename)
    print("Saved", filename)

running = True
while running:
    preview = canvas.copy()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                save_canvas()
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                brush_size = {pygame.K_1: 2, pygame.K_2: 5, pygame.K_3: 10}[event.key]
            elif text_mode:
                if event.key == pygame.K_RETURN:
                    canvas.blit(big.render(text_buffer, True, current_color), text_pos)
                    text_mode, text_buffer = False, ""
                elif event.key == pygame.K_ESCAPE:
                    text_mode, text_buffer = False, ""
                elif event.key == pygame.K_BACKSPACE:
                    text_buffer = text_buffer[:-1]
                else:
                    text_buffer += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not in_canvas(event.pos):
                handle_toolbar_click(event.pos)
            else:
                pos = canvas_pos(event.pos)
                if current_tool == "fill":
                    flood_fill(canvas, pos, current_color)
                elif current_tool == "text":
                    text_mode, text_pos, text_buffer = True, pos, ""
                else:
                    drawing = True
                    start_pos = last_pos = pos
        elif event.type == pygame.MOUSEMOTION and drawing:
            pos = canvas_pos(event.pos)
            if current_tool in ("pencil", "eraser"):
                color = WHITE if current_tool == "eraser" else current_color
                pygame.draw.line(canvas, color, last_pos, pos, brush_size)
                last_pos = pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drawing:
            end_pos = canvas_pos(event.pos)
            if current_tool not in ("pencil", "eraser"):
                draw_shape(canvas, current_tool, current_color, start_pos, end_pos, brush_size)
            drawing = False

    if drawing and current_tool not in ("pencil", "eraser"):
        draw_shape(preview, current_tool, current_color, start_pos, canvas_pos(pygame.mouse.get_pos()), brush_size)
    if text_mode and text_pos:
        preview.blit(big.render(text_buffer + "|", True, current_color), text_pos)

    screen.blit(preview, (0, TOOLBAR_H))
    draw_toolbar()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
