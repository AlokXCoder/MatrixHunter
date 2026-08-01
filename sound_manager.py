"""
sound_manager.py
================
Procedural sound generation (no external audio files required).
Uses numpy to synthesise waveforms and exposes them as pygame.mixer.Sound.
Falls back to silent stubs when numpy is unavailable or mixer init fails.
"""

from __future__ import annotations

import math
import random
from typing import Dict, Optional

import pygame

try:
    import numpy as np
    _NUMPY = True
except ImportError:
    _NUMPY = False


# ── waveform helpers ──────────────────────────────────────────────────────────

def _make_sound(
    frequency: float,
    duration:  float,
    volume:    float = 0.5,
    wave:      str   = "sine",
    decay:     bool  = True,
    sample_rate: int = 44100,
) -> Optional[pygame.mixer.Sound]:
    """
    Build a pygame Sound from a synthesised waveform.

    Parameters
    ----------
    frequency   : fundamental frequency in Hz
    duration    : length in seconds
    volume      : peak amplitude [0..1]
    wave        : 'sine' | 'square' | 'sawtooth' | 'noise'
    decay       : apply exponential decay envelope
    sample_rate : audio sample rate (must match mixer init)
    """
    if not _NUMPY:
        return None
    if not pygame.mixer.get_init():
        return None

    frames = int(duration * sample_rate)
    t = np.linspace(0, duration, frames, dtype=np.float32)

    if wave == "sine":
        data = np.sin(2 * np.pi * frequency * t)
    elif wave == "square":
        data = np.sign(np.sin(2 * np.pi * frequency * t)).astype(np.float32)
    elif wave == "sawtooth":
        data = (2 * (t * frequency - np.floor(t * frequency + 0.5))).astype(np.float32)
    elif wave == "noise":
        data = np.random.uniform(-1, 1, frames).astype(np.float32)
    else:
        data = np.sin(2 * np.pi * frequency * t)

    if decay:
        envelope = np.exp(-4.0 * t / duration).astype(np.float32)
        data = data * envelope

    data = (data * volume * 32767).astype(np.int16)
    stereo = np.column_stack([data, data])

    try:
        sound = pygame.sndarray.make_sound(stereo)
        return sound
    except Exception:
        return None


def _make_sweep(
    f_start: float,
    f_end:   float,
    duration: float,
    volume:  float = 0.5,
    sample_rate: int = 44100,
) -> Optional[pygame.mixer.Sound]:
    """Frequency-swept sine (chirp) for power-up / win effects."""
    if not _NUMPY or not pygame.mixer.get_init():
        return None
    frames = int(duration * sample_rate)
    t  = np.linspace(0, duration, frames, dtype=np.float32)
    f  = np.linspace(f_start, f_end, frames, dtype=np.float32)
    data = np.sin(2 * np.pi * np.cumsum(f) / sample_rate).astype(np.float32)
    envelope = np.exp(-2.0 * t / duration).astype(np.float32)
    data = (data * envelope * volume * 32767).astype(np.int16)
    stereo = np.column_stack([data, data])
    try:
        return pygame.sndarray.make_sound(stereo)
    except Exception:
        return None


class _SilentSound:
    """Stub used when sound generation is unavailable."""
    def play(self, loops: int = 0) -> None:  pass
    def stop(self) -> None:                  pass
    def set_volume(self, v: float) -> None:  pass


# ── SoundManager ─────────────────────────────────────────────────────────────

class SoundManager:
    """
    Generates and caches all game sound effects and music tracks.
    All sounds are synthesised at init time — no external files required.
    """

    # Channel allocation
    _CH_SFX   = 0
    _CH_MUSIC = 7   # channel used for looped music simulation

    def __init__(self) -> None:
        self._sounds:      Dict[str, pygame.mixer.Sound | _SilentSound] = {}
        self._music_sound: Optional[pygame.mixer.Sound] = None
        self._music_ch:    Optional[pygame.mixer.Channel] = None
        self._sfx_vol:     float = 0.8
        self._music_vol:   float = 0.5
        self._muted:       bool  = False

        if not pygame.mixer.get_init():
            return

        pygame.mixer.set_num_channels(16)
        self._build_all()

    # ── build library ──────────────────────────────────────────────

    def _store(self, name: str, sound: Optional[pygame.mixer.Sound]) -> None:
        self._sounds[name] = sound if sound is not None else _SilentSound()

    def _build_all(self) -> None:
        """Synthesise every SFX and music cue."""
        # ── UI ──────────────────────────────────────────────────────
        self._store("menu_click", _make_sound(880,  0.08, 0.4, "sine",    decay=True))
        self._store("menu_hover", _make_sound(440,  0.04, 0.2, "sine",    decay=True))
        self._store("menu_back",  _make_sound(220,  0.12, 0.3, "sine",    decay=True))

        # ── Sniper ──────────────────────────────────────────────────
        self._store("pistol",    _make_sound(300,  0.10, 0.7, "square",  decay=True))
        self._store("rifle",     _make_sound(180,  0.15, 0.8, "square",  decay=True))
        self._store("shotgun",   _make_sound(120,  0.18, 0.9, "noise",   decay=True))
        self._store("sniper_shot",_make_sound(600, 0.12, 0.7, "sine",    decay=True))
        self._store("reload",    _make_sweep(400,  150,  0.25, 0.4))
        self._store("empty_gun", _make_sound(1200, 0.07, 0.3, "square",  decay=True))

        # ── Assassin ────────────────────────────────────────────────
        self._store("footstep",  _make_sound(80,   0.06, 0.2, "noise",   decay=True))
        self._store("key_pickup",_make_sweep(500,  1500, 0.2, 0.5))
        self._store("door_open", _make_sound(200,  0.3,  0.5, "sawtooth",decay=True))
        self._store("alarm",     _make_sound(880,  0.5,  0.6, "square",  decay=False))
        self._store("alarm_off", _make_sound(440,  0.3,  0.4, "square",  decay=True))
        self._store("stealth",   _make_sound(660,  0.1,  0.3, "sine",    decay=True))
        self._store("spotted",   _make_sweep(300,  900,  0.3, 0.7))

        # ── Space Battle ────────────────────────────────────────────
        self._store("laser",     _make_sweep(800,  200,  0.15, 0.6))
        self._store("laser2",    _make_sweep(1200, 300,  0.12, 0.5))
        self._store("explosion", _make_sound(80,   0.35, 0.9, "noise",   decay=True))
        self._store("big_explosion",_make_sound(50,0.55, 1.0, "noise",   decay=True))
        self._store("powerup",   _make_sweep(440,  1760, 0.3, 0.6))
        self._store("shield_hit",_make_sound(600,  0.15, 0.5, "square",  decay=True))
        self._store("warp",      _make_sweep(200,  2000, 0.4, 0.5))

        # ── Runner ──────────────────────────────────────────────────
        self._store("jump",      _make_sweep(200,  600,  0.2, 0.5))
        self._store("land",      _make_sound(100,  0.08, 0.4, "noise",   decay=True))
        self._store("slide",     _make_sound(200,  0.15, 0.3, "sawtooth",decay=True))
        self._store("coin",      _make_sweep(660,  1320, 0.1, 0.5))
        self._store("crash",     _make_sound(100,  0.4,  0.8, "noise",   decay=True))
        self._store("speed_up",  _make_sweep(300,  900,  0.25, 0.5))

        # ── Shared ──────────────────────────────────────────────────
        self._store("hit",       _make_sound(150,  0.15, 0.6, "noise",   decay=True))
        self._store("player_hit",_make_sound(200,  0.2,  0.7, "noise",   decay=True))
        self._store("death",     _make_sweep(400,  50,   0.5, 0.8))
        self._store("boss_roar", _make_sound(60,   0.6,  0.9, "sawtooth",decay=True))
        self._store("level_up",  _make_sweep(440,  880,  0.5, 0.6))
        self._store("game_over", _make_sweep(600,  100,  0.8, 0.7))
        self._store("victory",   _make_sweep(440,  1760, 0.6, 0.7))

        # ── Background music (looping tone) ─────────────────────────
        self._store("music_menu",  self._build_music_loop(80, 1.0))
        self._store("music_sniper",self._build_music_loop(120, 1.0))
        self._store("music_assassin",self._build_music_loop(60, 1.0))
        self._store("music_space", self._build_music_loop(100, 1.0))
        self._store("music_runner",self._build_music_loop(140, 1.0))

    def _build_music_loop(self, bpm: int, duration_bars: float) -> Optional[pygame.mixer.Sound]:
        """Create a simple pulsing bass-drum loop for background ambience."""
        if not _NUMPY or not pygame.mixer.get_init():
            return None
        sr      = 44100
        beat_s  = 60.0 / bpm
        frames  = int(beat_s * 4 * duration_bars * sr)   # 4 beats per bar
        data    = np.zeros(frames, dtype=np.float32)

        # place a kick every beat
        kick_len = int(0.18 * sr)
        t_kick   = np.linspace(0, 0.18, kick_len, dtype=np.float32)
        kick     = np.sin(2*np.pi*55*t_kick) * np.exp(-14*t_kick)

        beat_frames = int(beat_s * sr)
        for b in range(4):
            start = b * beat_frames
            end   = start + kick_len
            if end <= frames:
                data[start:end] += kick * 0.5

        # soft hi-hat every half-beat
        hat_len = int(0.04 * sr)
        t_hat   = np.linspace(0, 0.04, hat_len, dtype=np.float32)
        hat     = np.random.uniform(-1,1,hat_len).astype(np.float32) * np.exp(-40*t_hat)
        for b in range(8):
            start = int(b * beat_frames / 2)
            end   = start + hat_len
            if end <= frames:
                data[start:end] += hat * 0.15

        data = np.clip(data, -1, 1)
        data = (data * 0.4 * 32767).astype(np.int16)
        stereo = np.column_stack([data, data])
        try:
            return pygame.sndarray.make_sound(stereo)
        except Exception:
            return None

    # ── playback API ──────────────────────────────────────────────

    def play(self, name: str, loops: int = 0) -> None:
        """Play a named sound effect once (or looped)."""
        if self._muted:
            return
        snd = self._sounds.get(name)
        if snd is None:
            return
        if isinstance(snd, _SilentSound):
            return
        snd.set_volume(self._sfx_vol)
        ch = pygame.mixer.find_channel(True)
        if ch:
            ch.play(snd, loops=loops)

    def play_music(self, name: str) -> None:
        """Start looping background music track (replaces current)."""
        self.stop_music()
        snd = self._sounds.get(name)
        if snd is None or isinstance(snd, _SilentSound) or self._muted:
            return
        ch = pygame.mixer.Channel(self._CH_MUSIC)
        snd.set_volume(self._music_vol)
        ch.play(snd, loops=-1)
        self._music_ch = ch

    def stop_music(self) -> None:
        if self._music_ch:
            self._music_ch.stop()
            self._music_ch = None

    def set_sfx_volume(self, v: float) -> None:
        self._sfx_vol = max(0.0, min(1.0, v))

    def set_music_volume(self, v: float) -> None:
        self._music_vol = max(0.0, min(1.0, v))
        if self._music_ch and self._music_ch.get_busy():
            snd = self._music_ch.get_sound()
            if snd:
                snd.set_volume(self._music_vol)

    def set_muted(self, muted: bool) -> None:
        self._muted = muted
        if muted:
            self.stop_music()
