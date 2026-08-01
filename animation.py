"""
animation.py
============
Particle system, screen-shake, and sprite-sheet animation utilities.
All classes are game-agnostic and used across every mini-game.
"""

from __future__ import annotations

import math
import random
from typing import List, Optional, Tuple

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT


# ─────────────────────────────────────────────────────────────────────────────
#  Particle
# ─────────────────────────────────────────────────────────────────────────────

class Particle:
    """
    Single particle with position, velocity, colour, size and lifetime.

    Supports:
    - Linear colour fade  (start_colour → end_colour)
    - Size shrink over lifetime
    - Optional gravity pull
    - Optional glow (slightly larger, semi-transparent circle behind main)
    """

    __slots__ = (
        "x", "y", "vx", "vy",
        "colour", "end_colour",
        "size", "start_size",
        "lifetime", "max_lifetime",
        "gravity", "glow", "alive",
    )

    def __init__(
        self,
        x: float, y: float,
        vx: float, vy: float,
        colour: Tuple[int,int,int],
        size: float = 4.0,
        lifetime: float = 0.8,
        end_colour: Optional[Tuple[int,int,int]] = None,
        gravity: float = 0.0,
        glow: bool = False,
    ) -> None:
        self.x, self.y       = x, y
        self.vx, self.vy     = vx, vy
        self.colour          = colour
        self.end_colour      = end_colour if end_colour else (0, 0, 0)
        self.size            = size
        self.start_size      = size
        self.lifetime        = lifetime
        self.max_lifetime    = lifetime
        self.gravity         = gravity
        self.glow            = glow
        self.alive           = True

    def update(self, dt: float) -> None:
        """Advance physics and age the particle."""
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        ratio = self.lifetime / self.max_lifetime          # 1→0
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self.vy += self.gravity * dt
        self.size = max(0.0, self.start_size * ratio)

        # interpolate colour
        t = 1.0 - ratio
        sc, ec = self.colour, self.end_colour
        self.colour = (
            int(sc[0] + (ec[0] - sc[0]) * t),
            int(sc[1] + (ec[1] - sc[1]) * t),
            int(sc[2] + (ec[2] - sc[2]) * t),
        )

    def draw(self, surface: pygame.Surface, offset: Tuple[int,int] = (0, 0)) -> None:
        """Render the particle to *surface* with optional camera offset."""
        if not self.alive or self.size < 0.5:
            return
        px = int(self.x - offset[0])
        py = int(self.y - offset[1])
        r  = int(self.size)

        if self.glow:
            glow_surf = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.colour, 60), (r*2, r*2), r*2)
            surface.blit(glow_surf, (px - r*2, py - r*2), special_flags=pygame.BLEND_RGBA_ADD)

        pygame.draw.circle(surface, self.colour, (px, py), max(1, r))


# ─────────────────────────────────────────────────────────────────────────────
#  ParticleSystem
# ─────────────────────────────────────────────────────────────────────────────

class ParticleSystem:
    """
    Manages a pool of Particle objects.
    Call emit_*() to spawn bursts; update()/draw() each frame.
    """

    def __init__(self, max_particles: int = 500) -> None:
        self._pool: List[Particle] = []
        self._max  = max_particles

    # ── emitters ──────────────────────────────────────────────────

    def emit_burst(
        self,
        x: float, y: float,
        count: int,
        colour: Tuple[int,int,int],
        speed:  float = 120.0,
        size:   float = 5.0,
        lifetime: float = 0.7,
        gravity: float = 200.0,
        spread: float = math.pi * 2,
        end_colour: Optional[Tuple[int,int,int]] = None,
        glow: bool = False,
    ) -> None:
        """Isotropic burst of particles (e.g. explosion)."""
        if end_colour is None:
            end_colour = (0, 0, 0)
        for _ in range(count):
            angle = random.uniform(0, spread)
            spd   = random.uniform(speed * 0.4, speed * 1.2)
            vx    = math.cos(angle) * spd
            vy    = math.sin(angle) * spd
            lt    = random.uniform(lifetime * 0.6, lifetime * 1.4)
            sz    = random.uniform(size * 0.5, size * 1.5)
            self._add(Particle(x, y, vx, vy, colour, sz, lt, end_colour, gravity, glow))

    def emit_trail(
        self,
        x: float, y: float,
        colour: Tuple[int,int,int],
        angle:  float = 0.0,
        speed:  float = 30.0,
        size:   float = 3.0,
        lifetime: float = 0.3,
    ) -> None:
        """Single particle trailing behind a moving object."""
        spread = random.uniform(-0.4, 0.4)
        vx = math.cos(angle + spread) * speed
        vy = math.sin(angle + spread) * speed
        self._add(Particle(x, y, vx, vy, colour, size, lifetime))

    def emit_sparks(
        self,
        x: float, y: float,
        count: int,
        colour: Tuple[int,int,int],
        direction: float = 0.0,
        spread: float = math.pi / 4,
        speed: float = 200.0,
        lifetime: float = 0.4,
    ) -> None:
        """Directional spark shower (e.g. bullet impact)."""
        for _ in range(count):
            angle = direction + random.uniform(-spread, spread)
            spd   = random.uniform(speed * 0.5, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            sz = random.uniform(1.5, 3.5)
            lt = random.uniform(lifetime * 0.5, lifetime)
            self._add(Particle(x, y, vx, vy, colour, sz, lt, (0,0,0), 300.0))

    def emit_ring(
        self,
        x: float, y: float,
        count: int,
        colour: Tuple[int,int,int],
        radius: float = 20.0,
        speed:  float = 60.0,
        lifetime: float = 0.5,
    ) -> None:
        """Evenly spaced ring of particles (power-up collect)."""
        for i in range(count):
            angle = (2 * math.pi / count) * i
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self._add(Particle(px, py, vx, vy, colour, 4.0, lifetime, (0,0,0), 0.0, True))

    # ── internals ─────────────────────────────────────────────────

    def _add(self, p: Particle) -> None:
        if len(self._pool) < self._max:
            self._pool.append(p)

    def update(self, dt: float) -> None:
        for p in self._pool:
            p.update(dt)
        self._pool = [p for p in self._pool if p.alive]

    def draw(self, surface: pygame.Surface, offset: Tuple[int,int] = (0, 0)) -> None:
        for p in self._pool:
            p.draw(surface, offset)

    def clear(self) -> None:
        self._pool.clear()

    @property
    def count(self) -> int:
        return len(self._pool)


# ─────────────────────────────────────────────────────────────────────────────
#  ScreenShake
# ─────────────────────────────────────────────────────────────────────────────

class ScreenShake:
    """
    Adds a randomised pixel-level camera offset for impact feedback.
    Call shake() to trigger; query offset each frame before drawing.
    """

    def __init__(self) -> None:
        self._duration  : float = 0.0
        self._intensity : float = 0.0
        self._enabled   : bool  = True

    def shake(self, intensity: float = 8.0, duration: float = 0.25) -> None:
        """Trigger a screen shake (larger values = stronger shake)."""
        if not self._enabled:
            return
        # Allow accumulation up to a cap
        self._intensity = min(self._intensity + intensity, 30.0)
        self._duration  = max(self._duration,  duration)

    def update(self, dt: float) -> None:
        if self._duration > 0:
            self._duration -= dt
            self._intensity *= 0.85   # dampen each frame

    @property
    def offset(self) -> Tuple[int, int]:
        """Current pixel offset to apply to the render target."""
        if self._duration <= 0 or self._intensity < 0.5:
            return (0, 0)
        ox = int(random.uniform(-self._intensity, self._intensity))
        oy = int(random.uniform(-self._intensity, self._intensity))
        return (ox, oy)

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        if not enabled:
            self._duration = 0.0


# ─────────────────────────────────────────────────────────────────────────────
#  AnimatedSprite
# ─────────────────────────────────────────────────────────────────────────────

class AnimatedSprite:
    """
    Frame-based animation built from a list of pygame.Surface frames.
    Supports looping, one-shot, and ping-pong playback modes.
    """

    def __init__(
        self,
        frames: List[pygame.Surface],
        fps: float = 12.0,
        loop: bool = True,
        pingpong: bool = False,
    ) -> None:
        if not frames:
            raise ValueError("AnimatedSprite requires at least one frame.")
        self._frames    = frames
        self._fps       = fps
        self._loop      = loop
        self._pingpong  = pingpong
        self._timer     = 0.0
        self._idx       = 0
        self._direction = 1      # +1 or -1 for ping-pong
        self.finished   = False  # True after one-shot completes

    def update(self, dt: float) -> None:
        if self.finished and not self._loop:
            return
        self._timer += dt
        advance = int(self._timer * self._fps)
        if advance >= 1:
            self._timer -= advance / self._fps
            self._idx   += advance * self._direction
            n = len(self._frames)

            if self._pingpong:
                if self._idx >= n - 1:
                    self._idx     = n - 1
                    self._direction = -1
                elif self._idx <= 0:
                    self._idx     = 0
                    self._direction = 1
            elif self._loop:
                self._idx = self._idx % n
            else:
                if self._idx >= n:
                    self._idx   = n - 1
                    self.finished = True

    @property
    def current(self) -> pygame.Surface:
        return self._frames[self._idx]

    def reset(self) -> None:
        self._timer     = 0.0
        self._idx       = 0
        self._direction = 1
        self.finished   = False


# ─────────────────────────────────────────────────────────────────────────────
#  MatrixRain  (decorative background effect for menus)
# ─────────────────────────────────────────────────────────────────────────────

class MatrixRain:
    """
    Classic Matrix-style falling green character columns.
    Drawn on a cached surface for performance.
    """

    _CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()[]{}|<>~`"

    def __init__(
        self,
        width: int  = SCREEN_WIDTH,
        height: int = SCREEN_HEIGHT,
        font_size: int = 16,
        speed: float = 80.0,
    ) -> None:
        self._w        = width
        self._h        = height
        self._fsize    = font_size
        self._speed    = speed
        self._cols     = width // font_size
        self._font     = pygame.font.SysFont("Courier", font_size, bold=True)

        # Each column: (y-position, brightness 0-1)
        self._drops: List[List[float]] = [
            [random.uniform(-height, 0), random.random()]
            for _ in range(self._cols)
        ]
        self._surface  = pygame.Surface((width, height), pygame.SRCALPHA)
        self._bg_surf  = pygame.Surface((width, height))
        self._bg_surf.fill((0, 0, 0))

    def update(self, dt: float) -> None:
        for col in self._drops:
            col[0] += self._speed * dt
            if col[0] > self._h + self._fsize:
                col[0] = random.uniform(-self._h * 0.5, 0)
                col[1] = random.random()

    def draw(self, surface: pygame.Surface) -> None:
        # Fade the background with a semi-transparent black overlay
        fade = pygame.Surface((self._w, self._h))
        fade.set_alpha(30)
        fade.fill((0, 0, 0))
        surface.blit(fade, (0, 0))

        for i, (col) in enumerate(self._drops):
            y, bright = col
            x = i * self._fsize
            char = random.choice(self._CHARS)

            # Head (bright white-green)
            head_col = (180, 255, 180)
            txt = self._font.render(char, True, head_col)
            surface.blit(txt, (x, int(y)))

            # Trail (dimmer green)
            for trail in range(1, 6):
                ty = int(y) - trail * self._fsize
                if 0 <= ty < self._h:
                    alpha = max(0, int(bright * 200 - trail * 35))
                    tc = self._font.render(
                        random.choice(self._CHARS), True,
                        (0, int(80 + bright * 120), 30)
                    )
                    tc.set_alpha(alpha)
                    surface.blit(tc, (x, ty))


# ─────────────────────────────────────────────────────────────────────────────
#  Starfield  (background for Space Battle)
# ─────────────────────────────────────────────────────────────────────────────

class Starfield:
    """Parallax three-layer starfield for the space shooter."""

    def __init__(self, width: int, height: int, star_count: int = 200) -> None:
        self._w = width
        self._h = height
        # Each star: [x, y, layer (0=far,1=mid,2=near), brightness]
        self._stars = [
            [random.uniform(0, width), random.uniform(0, height),
             random.randint(0, 2),     random.uniform(0.3, 1.0)]
            for _ in range(star_count)
        ]
        self._speeds = [20.0, 45.0, 80.0]  # px/s per layer

    def update(self, dt: float, scroll_x: float = 0.0, scroll_y: float = 1.0) -> None:
        for star in self._stars:
            spd = self._speeds[int(star[2])]
            star[1] += spd * scroll_y * dt
            star[0] -= spd * scroll_x * dt * 0.1
            if star[1] > self._h:
                star[1] = 0.0
                star[0] = random.uniform(0, self._w)
            if star[0] < 0:
                star[0] = self._w
            elif star[0] > self._w:
                star[0] = 0

    def draw(self, surface: pygame.Surface) -> None:
        sizes  = [1, 2, 3]
        shades = [100, 170, 220]
        for star in self._stars:
            layer = int(star[2])
            b     = int(shades[layer] * star[3])
            colour = (b, b, b)
            pygame.draw.circle(surface, colour, (int(star[0]), int(star[1])), sizes[layer])
