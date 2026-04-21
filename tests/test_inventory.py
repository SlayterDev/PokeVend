import json
import pytest
from pokevend.inventory import Inventory, Lane, Pack


def _write_inventory(path, data):
    path.write_text(json.dumps(data))
    return Inventory.load(str(path))


def _sample_data(*lane_packs):
    lanes = []
    for i, packs in enumerate(lane_packs):
        lanes.append({
            "lane_id": i,
            "label": f"Lane {i + 1}",
            "stack": [
                {"pack_id": p, "name": p, "series": "S", "set_code": "X", "image": ""}
                for p in packs
            ],
        })
    return {"lanes": lanes}


def test_load_missing_file(tmp_path):
    inv = Inventory.load(str(tmp_path / "nonexistent.json"))
    assert len(inv.lanes) == 4
    assert all(l.is_empty for l in inv.lanes)


def test_load_populates_missing_lanes(tmp_path):
    data = {"lanes": [{"lane_id": 0, "label": "L1", "stack": []}]}
    inv = _write_inventory(tmp_path / "inv.json", data)
    assert len(inv.lanes) == 4


def test_vend_pops_front(tmp_path):
    inv = _write_inventory(tmp_path / "inv.json", _sample_data(["a", "b"], [], [], []))
    pack = inv.vend_lane(0)
    assert pack.pack_id == "a"
    assert inv.get_lane(0).quantity == 1
    assert inv.get_lane(0).front.pack_id == "b"


def test_vend_empty_raises(tmp_path):
    inv = _write_inventory(tmp_path / "inv.json", _sample_data([], [], [], []))
    with pytest.raises(IndexError):
        inv.vend_lane(0)


def test_vend_persists_to_disk(tmp_path):
    path = tmp_path / "inv.json"
    inv = _write_inventory(path, _sample_data(["a", "b"], [], [], []))
    inv.vend_lane(0)
    inv2 = Inventory.load(str(path))
    assert inv2.get_lane(0).quantity == 1
    assert inv2.get_lane(0).front.pack_id == "b"


def test_save_is_atomic(tmp_path):
    path = tmp_path / "inv.json"
    inv = _write_inventory(path, _sample_data(["a"], [], [], []))
    inv.vend_lane(0)
    # No .tmp file should remain
    assert not (tmp_path / "inv.json.tmp").exists()


def test_lane_properties():
    lane = Lane(lane_id=0, label="L1", stack=[
        Pack("id1", "Name", "Series", "SET", ""),
        Pack("id2", "Name2", "Series2", "SET2", ""),
    ])
    assert not lane.is_empty
    assert lane.quantity == 2
    assert lane.front.pack_id == "id1"


def test_empty_lane_properties():
    lane = Lane(lane_id=0, label="L1")
    assert lane.is_empty
    assert lane.front is None
    assert lane.quantity == 0
