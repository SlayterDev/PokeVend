from __future__ import annotations
import pygame
from pokevend.ui import theme
from pokevend.inventory import Lane
from pokevend.image_loader import ImageLoader


class PackCard:
    def __init__(
        self,
        rect: pygame.Rect,
        lane: Lane,
        image_loader: ImageLoader,
        font_large: pygame.font.Font,
        font_small: pygame.font.Font,
    ):
        self.rect = rect
        self.lane = lane
        self._image_loader = image_loader
        self._font_large = font_large
        self._font_small = font_small
        self._art: pygame.Surface | None = None
        self._art_ref: str = ""

    def _ensure_art(self) -> None:
        ref = self.lane.front.image if self.lane.front else ""
        if ref != self._art_ref:
            self._art = self._image_loader.load(ref, theme.HOME_ART_SIZE)
            self._art_ref = ref

    def draw(self, surface: pygame.Surface) -> None:
        bg = theme.CARD_BG if not self.lane.is_empty else (22, 22, 34)
        pygame.draw.rect(surface, bg, self.rect, border_radius=12)
        pygame.draw.rect(surface, theme.CARD_BORDER, self.rect, width=1, border_radius=12)

        cx = self.rect.centerx
        top = self.rect.top + theme.CARD_PADDING

        if self.lane.is_empty:
            label = self._font_small.render(self.lane.label, True, theme.EMPTY_FG)
            surface.blit(label, label.get_rect(centerx=cx, top=top))
            empty = self._font_large.render("EMPTY", True, theme.EMPTY_FG)
            surface.blit(empty, empty.get_rect(center=self.rect.center))
            return

        self._ensure_art()

        # Lane label
        label = self._font_small.render(self.lane.label, True, theme.TEXT_SECONDARY)
        surface.blit(label, label.get_rect(centerx=cx, top=top))
        top += label.get_height() + 4

        # Pack art
        if self._art:
            art_rect = self._art.get_rect(centerx=cx, top=top)
            surface.blit(self._art, art_rect)
            top = art_rect.bottom + 6

        # Pack name (truncate if needed)
        name = self.lane.front.name
        name_surf = self._font_large.render(name, True, theme.TEXT_PRIMARY)
        max_w = self.rect.width - 8
        while name_surf.get_width() > max_w and len(name) > 3:
            name = name[:-1]
            name_surf = self._font_large.render(name + "…", True, theme.TEXT_PRIMARY)
        surface.blit(name_surf, name_surf.get_rect(centerx=cx, top=top))
        top += name_surf.get_height() + 2

        # Series
        series = self._font_small.render(self.lane.front.series, True, theme.TEXT_SECONDARY)
        surface.blit(series, series.get_rect(centerx=cx, top=top))
        top += series.get_height() + 4

        # Quantity badge
        qty_surf = self._font_small.render(f"×{self.lane.quantity}", True, theme.POKEMON_YELLOW)
        qty_rect = qty_surf.get_rect(centerx=cx, top=top)
        pygame.draw.rect(surface, (60, 50, 10), qty_rect.inflate(14, 6), border_radius=8)
        surface.blit(qty_surf, qty_rect)

    def is_hit(self, pos: tuple[int, int]) -> bool:
        return not self.lane.is_empty and self.rect.collidepoint(pos)
