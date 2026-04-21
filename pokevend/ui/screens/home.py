from __future__ import annotations
import pygame
from pokevend.ui import theme
from pokevend.ui.components.pack_card import PackCard


class HomeScreen:
    def __init__(self, app):
        self._app = app
        self._font_title = pygame.font.SysFont("sans-serif", theme.FONT_TITLE, bold=True)
        self._font_large = pygame.font.SysFont("sans-serif", theme.FONT_LARGE)
        self._font_small = pygame.font.SysFont("sans-serif", theme.FONT_SMALL)
        self._cards = self._build_cards()

    def _build_cards(self) -> list[PackCard]:
        pad = theme.CARD_PADDING
        card_w = (theme.WIDTH - pad * 3) // 2
        grid_h = theme.HEIGHT - theme.TITLE_BAR_H - theme.STATS_BAR_H - pad * 3
        card_h = grid_h // 2

        col_x = [pad, pad * 2 + card_w]
        row_y = [
            theme.TITLE_BAR_H + pad,
            theme.TITLE_BAR_H + pad * 2 + card_h,
        ]
        positions = [
            (col_x[0], row_y[0]),
            (col_x[1], row_y[0]),
            (col_x[0], row_y[1]),
            (col_x[1], row_y[1]),
        ]

        cards = []
        for i, lane in enumerate(self._app.inventory.lanes[:4]):
            rect = pygame.Rect(positions[i][0], positions[i][1], card_w, card_h)
            cards.append(PackCard(rect, lane, self._app.image_loader, self._font_large, self._font_small))
        return cards

    def _touch_pos(self, event: pygame.event.Event) -> tuple[int, int]:
        if event.type == pygame.FINGERDOWN:
            return (int(event.x * theme.WIDTH), int(event.y * theme.HEIGHT))
        return event.pos

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            pos = self._touch_pos(event)
            for card in self._cards:
                if card.is_hit(pos):
                    self._app.transition("confirm", lane_id=card.lane.lane_id)
                    return

    def update(self) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(theme.DARK_BG)

        # Title bar
        title = self._font_title.render("POKÉVEND", True, theme.POKEMON_YELLOW)
        surface.blit(title, title.get_rect(centerx=theme.WIDTH // 2, centery=theme.TITLE_BAR_H // 2))
        pygame.draw.line(surface, theme.CARD_BORDER, (0, theme.TITLE_BAR_H), (theme.WIDTH, theme.TITLE_BAR_H))

        # Lane cards
        for card in self._cards:
            card.draw(surface)

        # Stats bar
        bar_y = theme.HEIGHT - theme.STATS_BAR_H
        pygame.draw.line(surface, theme.CARD_BORDER, (0, bar_y), (theme.WIDTH, bar_y))
        total = sum(l.quantity for l in self._app.inventory.lanes)
        label = f"{total} pack{'s' if total != 1 else ''} in stock"
        txt = self._font_small.render(label, True, theme.TEXT_SECONDARY)
        surface.blit(txt, txt.get_rect(centerx=theme.WIDTH // 2, centery=bar_y + theme.STATS_BAR_H // 2))
