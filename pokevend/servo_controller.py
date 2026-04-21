from __future__ import annotations
import platform
import time

from pokevend.config import Config, ServoLaneConfig


class ServoControllerBase:
    def __init__(self, cfg: Config):
        self._cfg = cfg

    def vend(self, lane_id: int) -> None:
        raise NotImplementedError

    def _lane_cfg(self, lane_id: int) -> ServoLaneConfig:
        return self._cfg.servo.get(lane_id, ServoLaneConfig(channel=lane_id))


class RealServoController(ServoControllerBase):
    def __init__(self, cfg: Config):
        super().__init__(cfg)
        from adafruit_extended_bus import ExtendedI2C
        from adafruit_pca9685 import PCA9685
        from adafruit_motor.servo import Servo

        i2c = ExtendedI2C(cfg.i2c.bus)
        self._pca = PCA9685(i2c)
        self._pca.frequency = 50

        self._servos: dict[int, object] = {}
        for lane_id, lc in cfg.servo.items():
            servo = Servo(self._pca.channels[lc.channel], actuation_range=180)
            servo.angle = lc.neutral_angle
            self._servos[lane_id] = servo

    def vend(self, lane_id: int) -> None:
        lc = self._lane_cfg(lane_id)
        servo = self._servos[lane_id]
        servo.angle = lc.neutral_angle
        time.sleep(0.05)
        servo.angle = lc.vend_angle
        time.sleep(lc.vend_hold_ms / 1000.0)
        servo.angle = lc.neutral_angle
        time.sleep(lc.return_ms / 1000.0)


class MockServoController(ServoControllerBase):
    def vend(self, lane_id: int) -> None:
        lc = self._lane_cfg(lane_id)
        total_ms = 50 + lc.vend_hold_ms + lc.return_ms
        print(f"[MOCK] vend lane={lane_id}  simulating {total_ms}ms")
        time.sleep(total_ms / 1000.0)


def make_servo_controller(cfg: Config, force_mock: bool = False) -> ServoControllerBase:
    if force_mock or platform.machine() not in ("aarch64", "armv7l"):
        return MockServoController(cfg)
    try:
        return RealServoController(cfg)
    except Exception as e:
        print(f"[WARN] Hardware servo unavailable ({e}), falling back to mock")
        return MockServoController(cfg)
