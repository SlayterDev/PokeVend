from __future__ import annotations
import json
import os
from datetime import datetime, timezone

from pokevend.inventory import Pack


class StatsLogger:
    def __init__(self, log_path: str):
        self._path = log_path
        dir_name = os.path.dirname(log_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

    def record_vend(self, lane_id: int, pack: Pack) -> None:
        event = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "lane_id": lane_id,
            "pack_id": pack.pack_id,
            "name": pack.name,
            "series": pack.series,
            "set_code": pack.set_code,
        }
        with open(self._path, "a") as f:
            f.write(json.dumps(event) + "\n")
