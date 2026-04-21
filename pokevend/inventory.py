from __future__ import annotations
import json
import os
from dataclasses import dataclass, field, asdict


@dataclass
class Pack:
    pack_id: str
    name: str
    series: str
    set_code: str
    image: str  # local path or https:// URL

    @classmethod
    def from_dict(cls, d: dict) -> "Pack":
        return cls(
            pack_id=d["pack_id"],
            name=d["name"],
            series=d["series"],
            set_code=d.get("set_code", ""),
            image=d.get("image", ""),
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Lane:
    lane_id: int
    label: str
    stack: list[Pack] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return len(self.stack) == 0

    @property
    def front(self) -> Pack | None:
        return self.stack[0] if self.stack else None

    @property
    def quantity(self) -> int:
        return len(self.stack)

    @classmethod
    def from_dict(cls, d: dict) -> "Lane":
        return cls(
            lane_id=d["lane_id"],
            label=d.get("label", f"Lane {d['lane_id'] + 1}"),
            stack=[Pack.from_dict(p) for p in d.get("stack", [])],
        )

    def to_dict(self) -> dict:
        return {
            "lane_id": self.lane_id,
            "label": self.label,
            "stack": [p.to_dict() for p in self.stack],
        }


class Inventory:
    def __init__(self, lanes: list[Lane], path: str):
        self.lanes = lanes
        self._path = path

    @classmethod
    def load(cls, path: str) -> "Inventory":
        if not os.path.exists(path):
            lanes = [Lane(lane_id=i, label=f"Lane {i + 1}") for i in range(4)]
            return cls(lanes, path)
        with open(path) as f:
            data = json.load(f)
        lanes = [Lane.from_dict(l) for l in data.get("lanes", [])]
        existing_ids = {l.lane_id for l in lanes}
        for i in range(4):
            if i not in existing_ids:
                lanes.append(Lane(lane_id=i, label=f"Lane {i + 1}"))
        lanes.sort(key=lambda l: l.lane_id)
        return cls(lanes, path)

    def save(self) -> None:
        dir_name = os.path.dirname(self._path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        tmp = self._path + ".tmp"
        with open(tmp, "w") as f:
            json.dump({"lanes": [l.to_dict() for l in self.lanes]}, f, indent=2)
        os.replace(tmp, self._path)

    def get_lane(self, lane_id: int) -> Lane:
        for lane in self.lanes:
            if lane.lane_id == lane_id:
                return lane
        raise KeyError(f"Lane {lane_id} not found")

    def vend_lane(self, lane_id: int) -> Pack:
        lane = self.get_lane(lane_id)
        if lane.is_empty:
            raise IndexError(f"Lane {lane_id} is empty")
        pack = lane.stack.pop(0)
        self.save()
        return pack
