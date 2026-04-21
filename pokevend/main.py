import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pokevend.config import Config
from pokevend.ui.app import App


def main() -> None:
    parser = argparse.ArgumentParser(description="PokéVend — Pokemon card vending machine")
    parser.add_argument("--mock", action="store_true", help="Force mock servo controller")
    parser.add_argument("--config", default="config/config.toml", help="Path to config file")
    parser.add_argument("--no-fullscreen", action="store_true", help="Run in a window instead of fullscreen")
    parser.add_argument("--screensaver-timeout", type=int, default=None,
                        metavar="SECS", help="Override screensaver idle timeout (useful for testing)")
    args = parser.parse_args()

    cfg = Config.load(args.config)
    if args.no_fullscreen:
        cfg.display.fullscreen = False
    if args.screensaver_timeout is not None:
        cfg.ui.screensaver_timeout_s = args.screensaver_timeout

    app = App(cfg, force_mock=args.mock)
    app.run()


if __name__ == "__main__":
    main()
