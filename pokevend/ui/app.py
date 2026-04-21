from __future__ import annotations
import time
import pygame

from pokevend.config import Config
from pokevend.inventory import Inventory
from pokevend.image_loader import ImageLoader
from pokevend.servo_controller import make_servo_controller
from pokevend.stats import StatsLogger

_ACTIVITY_EVENTS = {pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN, pygame.KEYDOWN}


class App:
    def __init__(self, cfg: Config, force_mock: bool = False):
        self.cfg = cfg
        pygame.init()

        flags = pygame.FULLSCREEN if cfg.display.fullscreen else 0
        self.screen = pygame.display.set_mode(
            (cfg.display.width, cfg.display.height), flags
        )
        pygame.display.set_caption("PokéVend")

        self.clock = pygame.time.Clock()
        self.inventory = Inventory.load(cfg.paths.inventory)
        self.image_loader = ImageLoader(cfg.paths.pack_cache, cfg.paths.placeholder)
        self.servo_controller = make_servo_controller(cfg, force_mock)
        self.stats_logger = StatsLogger(cfg.paths.vend_log)

        self._running = False
        self._current_screen = None
        self._current_state: str = ""
        self._last_activity = time.monotonic()
        self.transition("home")

    def transition(self, state: str, **kwargs) -> None:
        from pokevend.ui.screens.home import HomeScreen
        from pokevend.ui.screens.confirm import ConfirmScreen
        from pokevend.ui.screens.dispensing import DispensingScreen
        from pokevend.ui.screens.screensaver import ScreensaverScreen

        self._current_state = state
        if state == "home":
            self._last_activity = time.monotonic()
            self._current_screen = HomeScreen(self)
        elif state == "confirm":
            self._current_screen = ConfirmScreen(self, kwargs["lane_id"])
        elif state == "dispensing":
            self._current_screen = DispensingScreen(self, kwargs["lane_id"])
        elif state == "screensaver":
            self._current_screen = ScreensaverScreen(self)

    def run(self) -> None:
        self._running = True
        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._running = False
                else:
                    if event.type in _ACTIVITY_EVENTS:
                        self._last_activity = time.monotonic()
                    if self._current_screen is not None:
                        self._current_screen.handle_event(event)

            # Trigger screensaver after idle timeout (home screen only)
            if (self._current_state == "home"
                    and time.monotonic() - self._last_activity
                    >= self.cfg.ui.screensaver_timeout_s):
                self.transition("screensaver")

            if self._current_screen is not None:
                self._current_screen.update()
                self._current_screen.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(self.cfg.display.fps)

        pygame.quit()
