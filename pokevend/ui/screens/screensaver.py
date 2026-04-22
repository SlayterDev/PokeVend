from __future__ import annotations
import math
import random
import time

import pygame

from pokevend.ui import theme


_ART_SIZE = (110, 201)
_NUM_SPRITES = 6
_SPEED_MIN = 0.6
_SPEED_MAX = 1.6


class _Sprite:
    def __init__(self, surf: pygame.Surface, x: float, y: float, vx: float, vy: float):
        self.surf = surf
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        w, h = self.surf.get_size()
        if self.x < 0:
            self.x = 0
            self.vx = abs(self.vx)
        elif self.x + w > theme.WIDTH:
            self.x = theme.WIDTH - w
            self.vx = -abs(self.vx)
        if self.y < 0:
            self.y = 0
            self.vy = abs(self.vy)
        elif self.y + h > theme.HEIGHT:
            self.y = theme.HEIGHT - h
            self.vy = -abs(self.vy)

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surf, (int(self.x), int(self.y)))


class ScreensaverScreen:
    def __init__(self, app):
        self._app = app
        self._font_title = pygame.font.SysFont("sans-serif", 52, bold=True)
        self._font_prompt = pygame.font.SysFont("sans-serif", theme.FONT_MEDIUM)
        self._overlay = self._make_overlay()
        self._sprites = self._make_sprites()

    def _make_overlay(self) -> pygame.Surface:
        surf = pygame.Surface((theme.WIDTH, theme.HEIGHT), pygame.SRCALPHA)
        surf.fill((theme.DARK_BG[0], theme.DARK_BG[1], theme.DARK_BG[2], 140))
        return surf

    def _make_sprites(self) -> list[_Sprite]:
        # Collect one surface per non-empty lane; fall back to placeholder
        surfs: list[pygame.Surface] = []
        for lane in self._app.inventory.lanes:
            if not lane.is_empty and lane.front:
                surfs.append(self._app.image_loader.load(lane.front.image, _ART_SIZE))
        if not surfs:
            surfs = [self._app.image_loader.load("", _ART_SIZE)]

        sprites: list[_Sprite] = []
        for i in range(_NUM_SPRITES):
            surf = surfs[i % len(surfs)]
            w, h = surf.get_size()
            x = random.uniform(0, max(0, theme.WIDTH - w))
            y = random.uniform(0, max(0, theme.HEIGHT - h))
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(_SPEED_MIN, _SPEED_MAX)
            # Ensure at least some horizontal and vertical movement
            if abs(math.cos(angle)) < 0.2:
                angle += 0.3
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            sprites.append(_Sprite(surf=surf, x=x, y=y, vx=vx, vy=vy))

        return sprites

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN, pygame.KEYDOWN):
            self._app.transition("home")

    def update(self) -> None:
        for sprite in self._sprites:
            sprite.update()

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(theme.DARK_BG)

        for sprite in self._sprites:
            sprite.draw(surface)

        # Dim overlay so text is legible over the pack art
        surface.blit(self._overlay, (0, 0))

        cx = theme.WIDTH // 2
        cy = theme.HEIGHT // 2

        title = self._font_title.render("POKÉVEND", True, theme.POKEMON_YELLOW)
        surface.blit(title, title.get_rect(centerx=cx, centery=cy - 24))

        # Pulsing "touch to start" text
        brightness = int(170 + 85 * math.sin(time.monotonic() * 1.8))
        prompt = self._font_prompt.render("Touch screen to start", True,
                                          (brightness, brightness, brightness))
        surface.blit(prompt, prompt.get_rect(centerx=cx, centery=cy + 34))
