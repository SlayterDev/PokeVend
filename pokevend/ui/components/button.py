from __future__ import annotations
import pygame
from pokevend.ui import theme


class Button:
    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        color: tuple,
        text_color: tuple,
        font: pygame.font.Font,
        border_radius: int = theme.BUTTON_RADIUS,
        enabled: bool = True,
    ):
        self.rect = rect
        self.label = label
        self.color = color
        self.text_color = text_color
        self.font = font
        self.border_radius = border_radius
        self.enabled = enabled

    def draw(self, surface: pygame.Surface) -> None:
        color = self.color if self.enabled else theme.CARD_BORDER
        fg = self.text_color if self.enabled else theme.EMPTY_FG
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        text = self.font.render(self.label, True, fg)
        surface.blit(text, text.get_rect(center=self.rect.center))

    def is_hit(self, pos: tuple[int, int]) -> bool:
        return self.enabled and self.rect.collidepoint(pos)
