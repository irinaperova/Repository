from __future__ import annotations

import random
from dataclasses import dataclass
import pygame

WIDTH, HEIGHT = 480, 700
FPS = 60
ROAD_X = 80
ROAD_WIDTH = WIDTH - ROAD_X * 2
ROAD_LINE_WIDTH = 10

BG_COLOR = (40, 150, 40)
ROAD_COLOR = (60, 60, 60)
ROAD_EDGE = (220, 220, 220)
LANE_LINE = (245, 245, 180)
PLAYER_COLOR = (70, 140, 255)
ENEMY_COLOR = (220, 70, 70)
COIN_COLOR = (240, 210, 30)
TEXT_COLOR = (255, 255, 255)
OVERLAY = (0, 0, 0, 160)


@dataclass
class Car:
    x: int
    y: int
    width: int = 50
    height: int = 90

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface: pygame.Surface, color: tuple[int, int, int]) -> None:
        body = self.rect()
        pygame.draw.rect(surface, color, body, border_radius=10)
        pygame.draw.rect(surface, (30, 30, 30), body.inflate(-10, -18), border_radius=8)
        pygame.draw.rect(surface, (180, 220, 255), (self.x + 10, self.y + 12, self.width - 20, 18), border_radius=5)
        pygame.draw.rect(surface, (180, 220, 255), (self.x + 12, self.y + self.height - 32, self.width - 24, 12), border_radius=4)
        pygame.draw.rect(surface, (20, 20, 20), (self.x - 4, self.y + 12, 8, 20), border_radius=3)
        pygame.draw.rect(surface, (20, 20, 20), (self.x - 4, self.y + self.height - 32, 8, 20), border_radius=3)
        pygame.draw.rect(surface, (20, 20, 20), (self.x + self.width - 4, self.y + 12, 8, 20), border_radius=3)
        pygame.draw.rect(surface, (20, 20, 20), (self.x + self.width - 4, self.y + self.height - 32, 8, 20), border_radius=3)


@dataclass
class Coin:
    x: int
    y: int
    radius: int = 12
    value: int = 1

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, COIN_COLOR, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, (250, 240, 150), (self.x, self.y), self.radius - 4)
        pygame.draw.circle(surface, (180, 130, 20), (self.x, self.y), self.radius, 2)


def random_lane_x(car_width: int) -> int:
    min_x = ROAD_X + 20
    max_x = ROAD_X + ROAD_WIDTH - car_width - 20
    return random.randint(min_x, max_x)


def draw_road(surface: pygame.Surface, scroll: int) -> None:
    surface.fill(BG_COLOR)
    pygame.draw.rect(surface, ROAD_COLOR, (ROAD_X, 0, ROAD_WIDTH, HEIGHT))
    pygame.draw.line(surface, ROAD_EDGE, (ROAD_X, 0), (ROAD_X, HEIGHT), 4)
    pygame.draw.line(surface, ROAD_EDGE, (ROAD_X + ROAD_WIDTH, 0), (ROAD_X + ROAD_WIDTH, HEIGHT), 4)
    lane_count = 3
    lane_gap = ROAD_WIDTH // lane_count
    for i in range(1, lane_count):
        x = ROAD_X + i * lane_gap
        for y in range(-50 + scroll % 60, HEIGHT, 60):
            pygame.draw.rect(surface, LANE_LINE, (x - ROAD_LINE_WIDTH // 2, y, ROAD_LINE_WIDTH, 35), border_radius=3)


def draw_hud(surface: pygame.Surface, font: pygame.font.Font, score: int, coins: int, speed: int) -> None:
    surface.blit(font.render(f"Dodged: {score}", True, TEXT_COLOR), (14, 12))
    surface.blit(font.render(f"Speed: {speed}", True, TEXT_COLOR), (14, 42))
    coins_text = font.render(f"Coins: {coins}", True, TEXT_COLOR)
    surface.blit(coins_text, coins_text.get_rect(topright=(WIDTH - 14, 12)))


def draw_game_over(surface: pygame.Surface, title_font: pygame.font.Font, font: pygame.font.Font, score: int, coins: int) -> None:
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(OVERLAY)
    surface.blit(overlay, (0, 0))
    lines = [
        title_font.render("GAME OVER", True, (255, 240, 240)),
        font.render(f"Dodged cars: {score}", True, TEXT_COLOR),
        font.render(f"Coins collected: {coins}", True, TEXT_COLOR),
        font.render("Press R to restart or Q to quit", True, TEXT_COLOR),
    ]
    y = HEIGHT // 2 - 70
    for line in lines:
        surface.blit(line, line.get_rect(center=(WIDTH // 2, y)))
        y += 45


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Practice 10 - Racer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 26)
    title_font = pygame.font.SysFont("arial", 42, bold=True)

    def reset():
        player = Car(WIDTH // 2 - 25, HEIGHT - 120)
        enemies = [Car(random_lane_x(50), -120, 50, 90)]
        coins = []
        road_scroll = 0
        enemy_speed = 6
        dodged = 0
        collected_coins = 0
        game_over = False
        return player, enemies, coins, road_scroll, enemy_speed, dodged, collected_coins, game_over

    player, enemies, coins, road_scroll, enemy_speed, dodged, collected_coins, game_over = reset()
    running = True

    while running:
        clock.tick(FPS)
        road_scroll += enemy_speed

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif game_over and event.key == pygame.K_r:
                    player, enemies, coins, road_scroll, enemy_speed, dodged, collected_coins, game_over = reset()

        keys = pygame.key.get_pressed()
        if not game_over:
            if keys[pygame.K_LEFT]:
                player.x -= 6
            if keys[pygame.K_RIGHT]:
                player.x += 6
            if keys[pygame.K_UP]:
                enemy_speed = min(15, enemy_speed + 0.03)
            if keys[pygame.K_DOWN]:
                enemy_speed = max(4, enemy_speed - 0.03)

        player.x = max(ROAD_X + 8, min(player.x, ROAD_X + ROAD_WIDTH - player.width - 8))

        if not game_over:
            if len(enemies) < 3 and random.random() < 0.02:
                enemies.append(Car(random_lane_x(50), -130, 50, 90))
            if len(coins) < 3 and random.random() < 0.03:
                coin_x = random.randint(ROAD_X + 25, ROAD_X + ROAD_WIDTH - 25)
                coins.append(Coin(coin_x, -20, radius=random.choice([10, 12, 14]), value=random.choice([1, 1, 2])))

            for enemy in enemies:
                enemy.y += int(enemy_speed)
            for coin in coins:
                coin.y += int(enemy_speed)

            for enemy in enemies:
                if enemy.y > HEIGHT + 10:
                    enemy.y = random.randint(-220, -120)
                    enemy.x = random_lane_x(enemy.width)
                    dodged += 1
                    if dodged % 5 == 0:
                        enemy_speed = min(16, enemy_speed + 0.5)

            coins = [coin for coin in coins if coin.y < HEIGHT + 30]
            player_rect = player.rect()

            for enemy in enemies:
                if player_rect.colliderect(enemy.rect()):
                    game_over = True

            remaining_coins = []
            for coin in coins:
                if player_rect.colliderect(coin.rect()):
                    collected_coins += coin.value
                else:
                    remaining_coins.append(coin)
            coins = remaining_coins

        draw_road(screen, road_scroll)
        for coin in coins:
            coin.draw(screen)
        for enemy in enemies:
            enemy.draw(screen, ENEMY_COLOR)
        player.draw(screen, PLAYER_COLOR)
        draw_hud(screen, font, dodged, collected_coins, int(enemy_speed))
        if game_over:
            draw_game_over(screen, title_font, font, dodged, collected_coins)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
