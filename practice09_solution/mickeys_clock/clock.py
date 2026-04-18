from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import math
import pygame


@dataclass
class ClockConfig:
    width: int = 800
    height: int = 800
    fps: int = 30
    bg_color: tuple[int, int, int] = (240, 240, 240)


class MickeyClock:
    def __init__(self, asset_dir: str | Path) -> None:
        self.config = ClockConfig()
        self.asset_dir = Path(asset_dir)
        self.center = (self.config.width // 2, self.config.height // 2)
        self.radius = 290
        self.background = self._load_background()
        self.font = pygame.font.SysFont("arial", 34, bold=True)
        self.small_font = pygame.font.SysFont("arial", 22)

    def _load_background(self) -> pygame.Surface:
        image_path = self.asset_dir / "mickeyclock.jpeg"
        if image_path.exists():
            image = pygame.image.load(str(image_path)).convert()
            return pygame.transform.smoothscale(image, (self.config.width, self.config.height))

        surface = pygame.Surface((self.config.width, self.config.height))
        surface.fill((250, 244, 224))
        pygame.draw.circle(surface, (210, 210, 210), self.center, 320)
        pygame.draw.circle(surface, (255, 248, 231), self.center, 300)
        return surface

    @staticmethod
    def _angle_for_minute(minute: int, second: int) -> float:
        return (minute + second / 60) * 6

    @staticmethod
    def _angle_for_second(second: int) -> float:
        return second * 6

    @staticmethod
    def _polar_to_cartesian(center: tuple[int, int], length: float, angle_deg: float) -> tuple[int, int]:
        angle_rad = math.radians(angle_deg - 90)
        x = center[0] + length * math.cos(angle_rad)
        y = center[1] + length * math.sin(angle_rad)
        return int(x), int(y)

    def _draw_hand(
        self,
        screen: pygame.Surface,
        angle_deg: float,
        length: int,
        side: str,
        arm_color: tuple[int, int, int] = (35, 35, 35),
    ) -> None:
        shoulder_offset = 22 if side == "right" else -22
        shoulder = (self.center[0] + shoulder_offset, self.center[1] - 18)
        elbow = self._polar_to_cartesian(shoulder, length * 0.45, angle_deg)
        wrist = self._polar_to_cartesian(shoulder, length, angle_deg)

        pygame.draw.line(screen, arm_color, shoulder, elbow, 18)
        pygame.draw.line(screen, arm_color, elbow, wrist, 14)

        glove_radius = 24
        pygame.draw.circle(screen, (255, 255, 255), wrist, glove_radius)
        pygame.draw.circle(screen, (20, 20, 20), wrist, glove_radius, 2)

        finger_base = self._polar_to_cartesian(wrist, 12, angle_deg)
        spread = -18 if side == "right" else 18
        finger1 = self._polar_to_cartesian(finger_base, 28, angle_deg + spread)
        finger2 = self._polar_to_cartesian(finger_base, 34, angle_deg)
        finger3 = self._polar_to_cartesian(finger_base, 28, angle_deg - spread)
        thumb = self._polar_to_cartesian(wrist, 20, angle_deg + (55 if side == "right" else -55))

        for start, end, width in (
            (wrist, finger1, 7),
            (wrist, finger2, 8),
            (wrist, finger3, 7),
            (wrist, thumb, 8),
        ):
            pygame.draw.line(screen, (255, 255, 255), start, end, width)
            pygame.draw.circle(screen, (255, 255, 255), end, 5)
            pygame.draw.line(screen, (20, 20, 20), start, end, 1)

    def draw(self, screen: pygame.Surface, current_time: datetime) -> None:
        screen.blit(self.background, (0, 0))

        minute_angle = self._angle_for_minute(current_time.minute, current_time.second)
        second_angle = self._angle_for_second(current_time.second)

        self._draw_hand(screen, minute_angle, 210, side="right")
        self._draw_hand(screen, second_angle, 165, side="left")

        pygame.draw.circle(screen, (40, 40, 40), self.center, 10)
        pygame.draw.circle(screen, (230, 0, 0), self.center, 4)

        time_text = self.font.render(current_time.strftime("%M:%S"), True, (25, 25, 25))
        subtitle = self.small_font.render(
            "Right hand = minutes, left hand = seconds", True, (30, 30, 30)
        )
        screen.blit(time_text, time_text.get_rect(center=(self.center[0], 730)))
        screen.blit(subtitle, subtitle.get_rect(center=(self.center[0], 770)))
