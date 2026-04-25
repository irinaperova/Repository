import math
import pygame

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 11 - Paint")

font = pygame.font.SysFont("Arial", 22)
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (40, 180, 60)
BLUE = (50, 100, 255)
YELLOW = (255, 215, 0)
PURPLE = (170, 70, 200)
GRAY = (220, 220, 220)

# Drawing area background
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)

# Current settings
current_color = BLACK
tool = "square"
start_pos = None
drawing = False

TOOLS = ["square", "right_triangle", "equilateral_triangle", "rhombus"]

COLOR_BUTTONS = [
    (BLACK, pygame.Rect(20, 20, 30, 30)),
    (RED, pygame.Rect(60, 20, 30, 30)),
    (GREEN, pygame.Rect(100, 20, 30, 30)),
    (BLUE, pygame.Rect(140, 20, 30, 30)),
    (YELLOW, pygame.Rect(180, 20, 30, 30)),
    (PURPLE, pygame.Rect(220, 20, 30, 30)),
]

TOOL_BUTTONS = {
    "square": pygame.Rect(280, 15, 140, 40),
    "right_triangle": pygame.Rect(430, 15, 170, 40),
    "equilateral_triangle": pygame.Rect(610, 15, 210, 40),
    "rhombus": pygame.Rect(830, 15, 140, 40),
}


def draw_square(surface, color, start, end):
    """Draw a square using the dragged mouse area."""
    x1, y1 = start
    x2, y2 = end
    side = min(abs(x2 - x1), abs(y2 - y1))

    left = x1 if x2 >= x1 else x1 - side
    top = y1 if y2 >= y1 else y1 - side

    rect = pygame.Rect(left, top, side, side)
    pygame.draw.rect(surface, color, rect, 3)


def draw_right_triangle(surface, color, start, end):
    """Draw a right triangle inside the dragged area."""
    x1, y1 = start
    x2, y2 = end
    points = [(x1, y2), (x1, y1), (x2, y2)]
    pygame.draw.polygon(surface, color, points, 3)


def draw_equilateral_triangle(surface, color, start, end):
    """Draw an equilateral triangle based on dragged width."""
    x1, y1 = start
    x2, y2 = end

    side = abs(x2 - x1)
    if side < 2:
        return

    # Use mathematical height for equilateral triangle
    height = int((math.sqrt(3) / 2) * side)

    left_x = min(x1, x2)
    top_y = min(y1, y2)

    p1 = (left_x + side // 2, top_y)
    p2 = (left_x, top_y + height)
    p3 = (left_x + side, top_y + height)

    pygame.draw.polygon(surface, color, [p1, p2, p3], 3)


def draw_rhombus(surface, color, start, end):
    """Draw a rhombus inside the dragged rectangle."""
    x1, y1 = start
    x2, y2 = end

    left = min(x1, x2)
    right = max(x1, x2)
    top = min(y1, y2)
    bottom = max(y1, y2)

    cx = (left + right) // 2
    cy = (top + bottom) // 2

    points = [
        (cx, top),
        (right, cy),
        (cx, bottom),
        (left, cy),
    ]
    pygame.draw.polygon(surface, color, points, 3)


def draw_preview(surface, color, tool_name, start, end):
    """Draw a temporary preview shape."""
    if tool_name == "square":
        draw_square(surface, color, start, end)
    elif tool_name == "right_triangle":
        draw_right_triangle(surface, color, start, end)
    elif tool_name == "equilateral_triangle":
        draw_equilateral_triangle(surface, color, start, end)
    elif tool_name == "rhombus":
        draw_rhombus(surface, color, start, end)


running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # Check color buttons
            clicked_ui = False
            for color, rect in COLOR_BUTTONS:
                if rect.collidepoint(mx, my):
                    current_color = color
                    clicked_ui = True
                    break

            # Check tool buttons
            if not clicked_ui:
                for tool_name, rect in TOOL_BUTTONS.items():
                    if rect.collidepoint(mx, my):
                        tool = tool_name
                        clicked_ui = True
                        break

            # Start drawing if user clicked on canvas
            if not clicked_ui and my > 70:
                start_pos = event.pos
                drawing = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if drawing and start_pos:
                end_pos = event.pos

                if tool == "square":
                    draw_square(canvas, current_color, start_pos, end_pos)
                elif tool == "right_triangle":
                    draw_right_triangle(canvas, current_color, start_pos, end_pos)
                elif tool == "equilateral_triangle":
                    draw_equilateral_triangle(canvas, current_color, start_pos, end_pos)
                elif tool == "rhombus":
                    draw_rhombus(canvas, current_color, start_pos, end_pos)

            drawing = False
            start_pos = None

    # Draw saved canvas
    screen.blit(canvas, (0, 0))

    # Draw toolbar background
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, 70))

    # Draw color buttons
    for color, rect in COLOR_BUTTONS:
        pygame.draw.rect(screen, color, rect)
        if color == current_color:
            pygame.draw.rect(screen, BLACK, rect, 3)
        else:
            pygame.draw.rect(screen, BLACK, rect, 1)

    # Draw tool buttons
    for tool_name, rect in TOOL_BUTTONS.items():
        pygame.draw.rect(screen, WHITE, rect)
        pygame.draw.rect(screen, BLACK, rect, 3 if tool == tool_name else 1)

        label = tool_name.replace("_", " ")
        text = font.render(label, True, BLACK)
        screen.blit(
            text,
            (rect.x + rect.width // 2 - text.get_width() // 2,
             rect.y + rect.height // 2 - text.get_height() // 2)
        )

    # Draw preview while dragging
    if drawing and start_pos:
        preview_surface = screen.copy()
        current_pos = pygame.mouse.get_pos()
        draw_preview(preview_surface, current_color, tool, start_pos, current_pos)
        screen.blit(preview_surface, (0, 0))

        # Redraw UI on top
        pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, 70))
        for color, rect in COLOR_BUTTONS:
            pygame.draw.rect(screen, color, rect)
            if color == current_color:
                pygame.draw.rect(screen, BLACK, rect, 3)
            else:
                pygame.draw.rect(screen, BLACK, rect, 1)

        for tool_name, rect in TOOL_BUTTONS.items():
            pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, BLACK, rect, 3 if tool == tool_name else 1)
            label = tool_name.replace("_", " ")
            text = font.render(label, True, BLACK)
            screen.blit(
                text,
                (rect.x + rect.width // 2 - text.get_width() // 2,
                 rect.y + rect.height // 2 - text.get_height() // 2)
            )

    pygame.display.flip()

pygame.quit()