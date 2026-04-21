from __future__ import annotations
import pygame
from pokevend.ui import theme
from pokevend.ui.components.button import Button


class ConfirmScreen:
    def __init__(self, app, lane_id: int):
        self._app = app
        self._lane_id = lane_id
        self._lane = app.inventory.get_lane(lane_id)
        self._pack = self._lane.front
        self._font_header = pygame.font.SysFont("sans-serif", theme.FONT_MEDIUM)
        self._font_large = pygame.font.SysFont("sans-serif", theme.FONT_LARGE, bold=True)
        self._font_medium = pygame.font.SysFont("sans-serif", theme.FONT_MEDIUM, bold=True)
        self._font_small = pygame.font.SysFont("sans-serif", theme.FONT_SMALL)

        img_ref = self._pack.image if self._pack else ""
        self._art = app.image_loader.load(img_ref, theme.CONFIRM_ART_SIZE)

        btn_y = theme.HEIGHT - theme.BUTTON_H - 24
        self._cancel_btn = Button(
            pygame.Rect(16, btn_y, 140, theme.BUTTON_H),
            "CANCEL", theme.CARD_BG, theme.TEXT_SECONDARY, self._font_header,
        )
        self._vend_btn = Button(
            pygame.Rect(168, btn_y, theme.WIDTH - 168 - 16, theme.BUTTON_H),
            "VEND IT!", theme.POKEMON_YELLOW, theme.BLACK, self._font_medium,
        )

    def _touch_pos(self, event: pygame.event.Event) -> tuple[int, int]:
        if event.type == pygame.FINGERDOWN:
            return (int(event.x * theme.WIDTH), int(event.y * theme.HEIGHT))
        return event.pos

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            pos = self._touch_pos(event)
            if self._cancel_btn.is_hit(pos):
                self._app.transition("home")
            elif self._vend_btn.is_hit(pos):
                self._app.transition("dispensing", lane_id=self._lane_id)

    def update(self) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(theme.DARK_BG)

        # Header
        hdr = self._font_header.render("Confirm Vend", True, theme.TEXT_SECONDARY)
        surface.blit(hdr, hdr.get_rect(centerx=theme.WIDTH // 2, centery=35))
        pygame.draw.line(surface, theme.CARD_BORDER, (0, 70), (theme.WIDTH, 70))

        # Pack art
        art_rect = self._art.get_rect(centerx=theme.WIDTH // 2, top=82)
        surface.blit(self._art, art_rect)

        if self._pack:
            y = art_rect.bottom + 14

            name = self._font_large.render(self._pack.name, True, theme.TEXT_PRIMARY)
            surface.blit(name, name.get_rect(centerx=theme.WIDTH // 2, top=y))
            y += name.get_height() + 4

            series = self._font_small.render(self._pack.series, True, theme.TEXT_SECONDARY)
            surface.blit(series, series.get_rect(centerx=theme.WIDTH // 2, top=y))
            y += series.get_height() + 4

            qty = self._font_small.render(f"{self._lane.quantity} remaining in lane", True, theme.TEXT_SECONDARY)
            surface.blit(qty, qty.get_rect(centerx=theme.WIDTH // 2, top=y))

        self._cancel_btn.draw(surface)
        self._vend_btn.draw(surface)
