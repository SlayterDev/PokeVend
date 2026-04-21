from __future__ import annotations
import hashlib
import os

import pygame


class ImageLoader:
    def __init__(self, cache_dir: str, placeholder_path: str):
        self._cache_dir = cache_dir
        self._placeholder_path = placeholder_path
        self._placeholder: pygame.Surface | None = None
        os.makedirs(cache_dir, exist_ok=True)

    def load(self, image_ref: str, size: tuple[int, int] | None = None) -> pygame.Surface:
        if not image_ref:
            surf = self._get_placeholder()
        elif image_ref.startswith("https://") or image_ref.startswith("http://"):
            surf = self._load_remote(image_ref)
        else:
            surf = self._load_local(image_ref)

        if size is not None and surf.get_size() != size:
            surf = pygame.transform.smoothscale(surf, size)
        return surf

    def _get_placeholder(self) -> pygame.Surface:
        if self._placeholder is not None:
            return self._placeholder
        if os.path.exists(self._placeholder_path):
            try:
                self._placeholder = self._load_via_pil(self._placeholder_path)
                return self._placeholder
            except Exception:
                pass
        surf = pygame.Surface((160, 220), pygame.SRCALPHA)
        surf.fill((45, 45, 65))
        pygame.draw.rect(surf, (70, 70, 100), surf.get_rect(), width=2, border_radius=8)
        self._placeholder = surf
        return surf

    def _load_local(self, path: str) -> pygame.Surface:
        try:
            return self._load_via_pil(path)
        except Exception:
            return self._get_placeholder()

    def _load_remote(self, url: str) -> pygame.Surface:
        cache_path = self._cache_path(url)
        if not os.path.exists(cache_path):
            try:
                import requests
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                with open(cache_path, "wb") as f:
                    f.write(resp.content)
            except Exception:
                return self._get_placeholder()
        return self._load_local(cache_path)

    def _load_via_pil(self, path: str) -> pygame.Surface:
        from PIL import Image
        img = Image.open(path).convert("RGBA")
        return pygame.image.frombuffer(img.tobytes(), img.size, "RGBA").convert_alpha()

    def _cache_path(self, url: str) -> str:
        key = hashlib.sha256(url.encode()).hexdigest()[:16]
        return os.path.join(self._cache_dir, f"{key}.png")
