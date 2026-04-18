from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Ball:
    x: int
    y: int
    radius: int = 25
    step: int = 20
    color: tuple[int, int, int] = (255, 0, 0)

    def move(self, dx: int, dy: int, width: int, height: int) -> None:
        new_x = self.x + dx * self.step
        new_y = self.y + dy * self.step

        if self.radius <= new_x <= width - self.radius:
            self.x = new_x
        if self.radius <= new_y <= height - self.radius:
            self.y = new_y
