from __future__ import annotations
import os
from dataclasses import dataclass, field

import toml


@dataclass
class DisplayConfig:
    width: int = 480
    height: int = 800
    fps: int = 30
    fullscreen: bool = True


@dataclass
class I2CConfig:
    bus: int = 10


@dataclass
class ServoLaneConfig:
    channel: int = 0
    neutral_angle: float = 90.0
    vend_angle: float = 170.0
    sweep_ms: int = 500
    vend_hold_ms: int = 400
    return_ms: int = 300


@dataclass
class PathsConfig:
    inventory: str = "data/inventory.json"
    vend_log: str = "data/vend_log.jsonl"
    pack_cache: str = "assets/packs/cache"
    placeholder: str = "assets/ui/placeholder_pack.png"


@dataclass
class UIConfig:
    dispensing_display_ms: int = 3000
    screensaver_timeout_s: int = 60


@dataclass
class Config:
    display: DisplayConfig = field(default_factory=DisplayConfig)
    i2c: I2CConfig = field(default_factory=I2CConfig)
    servo: dict[int, ServoLaneConfig] = field(default_factory=dict)
    paths: PathsConfig = field(default_factory=PathsConfig)
    ui: UIConfig = field(default_factory=UIConfig)

    @classmethod
    def load(cls, path: str = "config/config.toml") -> "Config":
        if not os.path.exists(path):
            return cls()
        raw = toml.load(path)
        cfg = cls()

        if "display" in raw:
            d = raw["display"]
            cfg.display = DisplayConfig(
                width=d.get("width", 480),
                height=d.get("height", 800),
                fps=d.get("fps", 30),
                fullscreen=d.get("fullscreen", True),
            )

        if "i2c" in raw:
            cfg.i2c = I2CConfig(bus=raw["i2c"].get("bus", 10))

        for key, val in raw.get("servo", {}).items():
            if key.startswith("lane_"):
                lane_id = int(key.split("_")[1])
                cfg.servo[lane_id] = ServoLaneConfig(
                    channel=val.get("channel", lane_id),
                    neutral_angle=float(val.get("neutral_angle", 90.0)),
                    vend_angle=float(val.get("vend_angle", 170.0)),
                    sweep_ms=int(val.get("sweep_ms", 500)),
                    vend_hold_ms=int(val.get("vend_hold_ms", 400)),
                    return_ms=int(val.get("return_ms", 300)),
                )

        if "paths" in raw:
            p = raw["paths"]
            cfg.paths = PathsConfig(
                inventory=p.get("inventory", "data/inventory.json"),
                vend_log=p.get("vend_log", "data/vend_log.jsonl"),
                pack_cache=p.get("pack_cache", "assets/packs/cache"),
                placeholder=p.get("placeholder", "assets/ui/placeholder_pack.png"),
            )

        if "ui" in raw:
            cfg.ui = UIConfig(
                dispensing_display_ms=raw["ui"].get("dispensing_display_ms", 3000),
                screensaver_timeout_s=raw["ui"].get("screensaver_timeout_s", 60),
            )

        return cfg
