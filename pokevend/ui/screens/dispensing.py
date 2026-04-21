from __future__ import annotations
import math
import threading
import time

import pygame

from pokevend.ui import theme
from pokevend.inventory import Pack


class DispensingScreen:
    _BALL_R = 60

    def __init__(self, app, lane_id: int):
        self._app = app
        self._lane_id = lane_id
        self._font_title = pygame.font.SysFont("sans-serif", theme.FONT_TITLE, bold=True)
        self._font_medium = pygame.font.SysFont("sans-serif", theme.FONT_MEDIUM)
        self._font_small = pygame.font.SysFont("sans-serif", theme.FONT_SMALL)

        # Vend inventory and log before servo fires
        self._pack: Pack = app.inventory.vend_lane(lane_id)
        app.stats_logger.record_vend(lane_id, self._pack)

        self._servo_thread = threading.Thread(
            target=app.servo_controller.vend,
            args=(lane_id,),
            daemon=True,
        )
        self._servo_thread.start()

        self._start = time.monotonic()
        self._spin_angle = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        pass  # no interaction during dispensing

    def update(self) -> None:
        self._spin_angle = (self._spin_angle + 4.0) % 360.0
        elapsed_ms = (time.monotonic() - self._start) * 1000
        if (elapsed_ms >= self._app.cfg.ui.dispensing_display_ms
                and not self._servo_thread.is_alive()):
            self._app.transition("home")

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(theme.DARK_BG)

        cx = theme.WIDTH // 2
        cy = theme.HEIGHT // 2 - 80

        self._draw_pokeball(surface, cx, cy)

        msg = self._font_title.render("Vending…", True, theme.POKEMON_YELLOW)
        surface.blit(msg, msg.get_rect(centerx=cx, top=cy + self._BALL_R + 28))

        if self._pack:
            name = self._font_medium.render(self._pack.name, True, theme.TEXT_PRIMARY)
            surface.blit(name, name.get_rect(centerx=cx, top=cy + self._BALL_R + 74))
            series = self._font_small.render(self._pack.series, True, theme.TEXT_SECONDARY)
            surface.blit(series, series.get_rect(centerx=cx, top=cy + self._BALL_R + 104))

    def _draw_pokeball(self, surface: pygame.Surface, cx: int, cy: int) -> None:
        r = self._BALL_R
        angle_rad = math.radians(self._spin_angle)

        # Top half red — use clip to paint only above center line
        pygame.draw.circle(surface, theme.DANGER_RED, (cx, cy), r)
        saved_clip = surface.get_clip()
        surface.set_clip(pygame.Rect(cx - r, cy, r * 2, r))
        pygame.draw.circle(surface, theme.WHITE, (cx, cy), r)
        surface.set_clip(saved_clip)

        # Center dividing line
        pygame.draw.line(surface, theme.BLACK, (cx - r, cy), (cx + r, cy), 4)

        # Center button
        pygame.draw.circle(surface, theme.DARK_BG, (cx, cy), 14)
        pygame.draw.circle(surface, theme.CARD_BORDER, (cx, cy), 14, 2)
        pygame.draw.circle(surface, theme.WHITE, (cx, cy), 8)

        # Rotating ticks around the ball to indicate spinning
        for i in range(12):
            tick_a = angle_rad + i * (math.pi * 2 / 12)
            brightness = int(255 * (1.0 - (i % 6) / 5))
            color = (brightness, brightness, brightness)
            sx = cx + int(math.cos(tick_a) * (r + 9))
            sy = cy + int(math.sin(tick_a) * (r + 9))
            ex = cx + int(math.cos(tick_a) * (r + 20))
            ey = cy + int(math.sin(tick_a) * (r + 20))
            pygame.draw.line(surface, color, (sx, sy), (ex, ey), 3)
