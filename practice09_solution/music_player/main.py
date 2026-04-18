from __future__ import annotations

from pathlib import Path
import pygame

from player import MusicPlayer


pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 900, 420
BG = (24, 24, 32)
PANEL = (38, 38, 50)
TEXT = (245, 245, 245)
ACCENT = (80, 170, 255)
MUTED = (150, 150, 170)

BASE_DIR = Path(__file__).resolve().parent
player = MusicPlayer(BASE_DIR / "music")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 09 - Music Player")
clock = pygame.time.Clock()
font_big = pygame.font.SysFont("arial", 30, bold=True)
font = pygame.font.SysFont("arial", 24)
font_small = pygame.font.SysFont("consolas", 20)


def format_seconds(seconds: float) -> str:
    total = max(0, int(seconds))
    return f"{total // 60:02d}:{total % 60:02d}"


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == player.end_event:
            player.next_track()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_p:
                player.play()
            elif event.key == pygame.K_s:
                player.stop()
            elif event.key == pygame.K_SPACE:
                player.pause()
            elif event.key == pygame.K_n:
                player.next_track()
            elif event.key == pygame.K_b:
                player.previous_track()

    screen.fill(BG)
    pygame.draw.rect(screen, PANEL, (40, 40, 820, 340), border_radius=20)

    title = font_big.render("Keyboard Music Player", True, TEXT)
    help_line = font.render("P - Play | SPACE - Pause | S - Stop | N - Next | B - Previous | Q - Quit", True, MUTED)
    screen.blit(title, (70, 70))
    screen.blit(help_line, (70, 110))

    if player.tracks:
        track = player.current_track()
        name = font_big.render(track.title, True, TEXT)
        status_value = "Playing" if player.is_playing and not player.is_paused else "Paused" if player.is_paused else "Stopped"
        status = font.render(f"Status: {status_value}", True, TEXT)
        playlist = font.render(f"Track {player.current_index + 1}/{len(player.tracks)}", True, TEXT)
        elapsed = player.elapsed_time()
        elapsed_text = font_small.render(f"{format_seconds(elapsed)} / {format_seconds(track.duration)}", True, TEXT)

        screen.blit(name, (70, 170))
        screen.blit(status, (70, 215))
        screen.blit(playlist, (70, 250))

        bar_x, bar_y, bar_w, bar_h = 70, 305, 760, 26
        pygame.draw.rect(screen, (70, 70, 90), (bar_x, bar_y, bar_w, bar_h), border_radius=13)
        pygame.draw.rect(screen, ACCENT, (bar_x, bar_y, int(bar_w * player.progress_ratio()), bar_h), border_radius=13)
        screen.blit(elapsed_text, (70, 345))
    else:
        no_music = font_big.render("No WAV files found in music folder", True, TEXT)
        screen.blit(no_music, (70, 190))

    pygame.display.flip()
    clock.tick(30)

player.stop()
pygame.mixer.quit()
pygame.quit()
