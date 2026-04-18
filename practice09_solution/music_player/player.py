from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pygame


@dataclass
class Track:
    title: str
    filename: str
    duration: float


class MusicPlayer:
    def __init__(self, music_dir: str | Path) -> None:
        self.music_dir = Path(music_dir)
        self.tracks = self._load_tracks()
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.track_start_ticks = 0
        self.pause_started = 0
        self.paused_total = 0
        self.end_event = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.end_event)

    def _load_tracks(self) -> list[Track]:
        tracks: list[Track] = []
        for path in sorted(self.music_dir.glob("*.wav")):
            sound = pygame.mixer.Sound(str(path))
            tracks.append(Track(title=path.stem.replace("_", " ").title(), filename=path.name, duration=sound.get_length()))
        return tracks

    def current_track(self) -> Track:
        return self.tracks[self.current_index]

    def load_current(self) -> None:
        pygame.mixer.music.load(str(self.music_dir / self.current_track().filename))

    def play(self) -> None:
        if not self.tracks:
            return
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.paused_total += pygame.time.get_ticks() - self.pause_started
            self.is_paused = False
            self.is_playing = True
            return
        self.load_current()
        pygame.mixer.music.play()
        self.track_start_ticks = pygame.time.get_ticks()
        self.paused_total = 0
        self.is_playing = True
        self.is_paused = False

    def stop(self) -> None:
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.track_start_ticks = 0
        self.paused_total = 0

    def pause(self) -> None:
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.pause_started = pygame.time.get_ticks()

    def next_track(self) -> None:
        if not self.tracks:
            return
        self.current_index = (self.current_index + 1) % len(self.tracks)
        self.play()

    def previous_track(self) -> None:
        if not self.tracks:
            return
        self.current_index = (self.current_index - 1) % len(self.tracks)
        self.play()

    def elapsed_time(self) -> float:
        if not self.is_playing:
            return 0.0
        now = self.pause_started if self.is_paused else pygame.time.get_ticks()
        return max(0.0, (now - self.track_start_ticks - self.paused_total) / 1000)

    def progress_ratio(self) -> float:
        track = self.current_track()
        if track.duration <= 0:
            return 0.0
        return min(1.0, self.elapsed_time() / track.duration)
