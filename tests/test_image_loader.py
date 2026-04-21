import os
import pytest
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
pygame.init()
pygame.display.set_mode((1, 1))

from pokevend.image_loader import ImageLoader


def test_empty_ref_returns_surface(tmp_path):
    loader = ImageLoader(str(tmp_path / "cache"), str(tmp_path / "placeholder.png"))
    surf = loader.load("")
    assert isinstance(surf, pygame.Surface)


def test_missing_local_returns_placeholder(tmp_path):
    loader = ImageLoader(str(tmp_path / "cache"), str(tmp_path / "placeholder.png"))
    surf = loader.load("does_not_exist.png")
    assert isinstance(surf, pygame.Surface)


def test_local_image_loads_and_scales(tmp_path):
    from PIL import Image
    img = Image.new("RGBA", (200, 300), (255, 0, 0, 255))
    img_path = str(tmp_path / "test.png")
    img.save(img_path)

    loader = ImageLoader(str(tmp_path / "cache"), str(tmp_path / "placeholder.png"))
    surf = loader.load(img_path, (100, 150))
    assert surf.get_size() == (100, 150)


def test_cache_dir_created(tmp_path):
    cache = str(tmp_path / "deep" / "cache")
    loader = ImageLoader(cache, str(tmp_path / "placeholder.png"))
    assert os.path.isdir(cache)
