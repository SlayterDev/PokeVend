import pytest
from pokevend.config import Config, ServoLaneConfig
from pokevend.servo_controller import MockServoController, make_servo_controller


def _cfg():
    cfg = Config()
    for i in range(4):
        cfg.servo[i] = ServoLaneConfig(channel=i, neutral_angle=90.0, vend_angle=170.0,
                                        vend_hold_ms=10, return_ms=10)
    return cfg


def test_mock_vend_completes():
    ctrl = MockServoController(_cfg())
    ctrl.vend(0)  # must not raise


def test_make_returns_mock_when_forced():
    ctrl = make_servo_controller(_cfg(), force_mock=True)
    assert isinstance(ctrl, MockServoController)


def test_mock_fallback_lane_defaults():
    # No lanes configured — should use ServoLaneConfig defaults
    ctrl = MockServoController(Config())
    ctrl.vend(0)  # must not raise
