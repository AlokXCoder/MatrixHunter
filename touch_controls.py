"""
touch_controls.py
=================
Virtual on-screen controls for mobile / touchscreen play.
Automatically rendered when a FINGERDOWN event is detected.

Provides:
  • TouchJoystick  — left-side analog stick (movement)
  • TouchButton    — right-side circular buttons (action)
  • TouchOverlay   — manager that wires everything to a fake "keys" dict

Usage in game update loop:
    from touch_controls import TouchOverlay
    overlay = TouchOverlay()
    # In event loop:
    overlay.handle_event(event)
    # Then get a key-state dict compatible with pygame.key.get_pressed():
    keys = overlay.get_keys()
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, MATRIX_GREEN, NEON_CYAN, NEON_RED, NEON_ORANGE, WHITE, DARK_GRAY


# ─────────────────────────────────────────────────────────────────────────────
#  TouchJoystick
# ─────────────────────────────────────────────────────────────────────────────

class TouchJoystick:
    """
    Circular virtual joystick displayed in the bottom-left corner.
    Finger movement relative to the initial touch becomes direction + magnitude.
    """

    RADIUS      = 70    # outer ring radius
    NUB_RADIUS  = 28    # moveable nub radius
    DEAD_ZONE   = 0.15  # ignore tiny movements

    def __init__(self, cx: int, cy: int) -> None:
        self._base   = (cx, cy)
        self._nub    = (cx, cy)
        self._finger: Optional[int] = None    # tracking finger id
        self._dx     = 0.0
        self._dy     = 0.0
        self._active = False

    @property
    def dx(self) -> float:
        return self._dx if abs(self._dx) > self.DEAD_ZONE else 0.0

    @property
    def dy(self) -> float:
        return self._dy if abs(self._dy) > self.DEAD_ZONE else 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.FINGERDOWN:
            fx = int(event.x * SCREEN_WIDTH)
            fy = int(event.y * SCREEN_HEIGHT)
            if self._finger is None and fx < SCREEN_WIDTH // 2:
                self._base = (fx, fy)
                self._nub = (fx, fy)
                self._finger = event.finger_id
                self._active = True

        elif event.type == pygame.FINGERMOTION:
            if event.finger_id == self._finger:
                fx = int(event.x * SCREEN_WIDTH)
                fy = int(event.y * SCREEN_HEIGHT)
                bx, by    = self._base
                dx, dy    = fx - bx, fy - by
                dist      = math.hypot(dx, dy)
                if dist > 0:
                    ndx, ndy = dx / dist, dy / dist
                    clamped  = min(dist, self.RADIUS)
                    self._nub = (int(bx + ndx * clamped), int(by + ndy * clamped))
                    self._dx  = ndx * (clamped / self.RADIUS)
                    self._dy  = ndy * (clamped / self.RADIUS)

        elif event.type == pygame.FINGERUP:
            if event.finger_id == self._finger:
                self._finger = None
                self._nub    = self._base
                self._dx     = 0.0
                self._dy     = 0.0
                self._active = False

    def draw(self, surface: pygame.Surface) -> None:
        bx, by  = self._base
        nx, ny  = self._nub
        alpha   = 160 if self._active else 80

        # Outer ring
        ring = pygame.Surface((self.RADIUS*2+4, self.RADIUS*2+4), pygame.SRCALPHA)
        pygame.draw.circle(ring, (255,255,255, alpha//2),
                           (self.RADIUS+2, self.RADIUS+2), self.RADIUS, 2)
        surface.blit(ring, (bx - self.RADIUS - 2, by - self.RADIUS - 2))

        # Nub
        nub = pygame.Surface((self.NUB_RADIUS*2, self.NUB_RADIUS*2), pygame.SRCALPHA)
        col = MATRIX_GREEN if self._active else DARK_GRAY
        pygame.draw.circle(nub, (*col, alpha+60),
                           (self.NUB_RADIUS, self.NUB_RADIUS), self.NUB_RADIUS)
        pygame.draw.circle(nub, (255,255,255, alpha),
                           (self.NUB_RADIUS, self.NUB_RADIUS), self.NUB_RADIUS, 2)
        surface.blit(nub, (nx - self.NUB_RADIUS, ny - self.NUB_RADIUS))


# ─────────────────────────────────────────────────────────────────────────────
#  TouchButton
# ─────────────────────────────────────────────────────────────────────────────

class TouchButton:
    """Single circular touch button mapped to a pygame key constant."""

    RADIUS = 36

    def __init__(
        self,
        cx: int, cy: int,
        label: str,
        key: int,
        colour: Tuple[int,int,int] = NEON_CYAN,
    ) -> None:
        self._cx      = cx
        self._cy      = cy
        self._label   = label
        self.key      = key
        self._colour  = colour
        self._pressed = False
        self._fingers: List[int] = []
        self._font    = None

    def _in_range(self, x: int, y: int) -> bool:
        return math.hypot(x - self._cx, y - self._cy) < self.RADIUS * 1.3

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.FINGERDOWN:
            fx = int(event.x * SCREEN_WIDTH)
            fy = int(event.y * SCREEN_HEIGHT)
            if self._in_range(fx, fy):
                self._fingers.append(event.finger_id)
                self._pressed = True
        elif event.type == pygame.FINGERUP:
            if event.finger_id in self._fingers:
                self._fingers.remove(event.finger_id)
            self._pressed = len(self._fingers) > 0

    @property
    def is_pressed(self) -> bool:
        return self._pressed

    def draw(self, surface: pygame.Surface) -> None:
        alpha = 200 if self._pressed else 100
        col   = self._colour if self._pressed else DARK_GRAY

        btn = pygame.Surface((self.RADIUS*2, self.RADIUS*2), pygame.SRCALPHA)
        pygame.draw.circle(btn, (*col, alpha),
                           (self.RADIUS, self.RADIUS), self.RADIUS)
        pygame.draw.circle(btn, (255,255,255, alpha),
                           (self.RADIUS, self.RADIUS), self.RADIUS, 2)
        surface.blit(btn, (self._cx - self.RADIUS, self._cy - self.RADIUS))

        # Label
        if self._font is None:
            self._font = pygame.font.SysFont("Consolas", 16, bold=True)
        lbl = self._font.render(self._label, True, WHITE)
        lbl.set_alpha(alpha)
        r = lbl.get_rect(center=(self._cx, self._cy))
        surface.blit(lbl, r)


# ─────────────────────────────────────────────────────────────────────────────
#  TouchOverlay
# ─────────────────────────────────────────────────────────────────────────────

class TouchOverlay:
    """
    Manages all touch controls and translates them into a key-state
    dictionary compatible with pygame.key.get_pressed().

    Layout:
        Left side  : joystick  (movement — WASD keys)
        Right side : buttons   (SPACE = jump/fire, LCTRL = slide/crouch,
                                Z = scope/bomb, X = bomb-drop, E = interact)
    """

    def __init__(self) -> None:
        jx = 110
        jy = SCREEN_HEIGHT - 120
        self._joystick = TouchJoystick(jx, jy)

        rx = SCREEN_WIDTH - 80
        ry = SCREEN_HEIGHT - 220

        self._buttons: List[TouchButton] = [
            TouchButton(rx,        ry,        "FIRE\n[Z]",  pygame.K_z,      NEON_CYAN),
            TouchButton(rx + 85,   ry + 60,   "ACT\n[E]",  pygame.K_e,      NEON_ORANGE),
            TouchButton(rx,        ry + 120,  "JUMP\n[SPC]",pygame.K_SPACE,  MATRIX_GREEN),
            TouchButton(rx - 85,   ry + 60,   "SLIDE\n[C]", pygame.K_c,      NEON_RED),
        ]

        self._visible = False   # only shown after first touch

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            self._visible = True
        self._joystick.handle_event(event)
        for btn in self._buttons:
            btn.handle_event(event)

    def get_keys(self) -> Dict[int, bool]:
        """
        Return a dict mapping pygame key constants → bool.
        Merge with actual keyboard state in the game loop.
        """
        dx, dy = self._joystick.dx, self._joystick.dy
        result: Dict[int, bool] = {
            pygame.K_w:    dy < -0.1,
            pygame.K_s:    dy >  0.1,
            pygame.K_a:    dx < -0.1,
            pygame.K_d:    dx >  0.1,
            pygame.K_UP:   dy < -0.1,
            pygame.K_DOWN: dy >  0.1,
            pygame.K_LEFT: dx < -0.1,
            pygame.K_RIGHT:dx >  0.1,
        }
        for btn in self._buttons:
            result[btn.key] = btn.is_pressed
        return result

    def draw(self, surface: pygame.Surface) -> None:
        if not self._visible:
            return
        self._joystick.draw(surface)
        for btn in self._buttons:
            btn.draw(surface)
