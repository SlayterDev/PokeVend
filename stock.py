#!/usr/bin/env python3
"""Interactive stock management CLI for pokevend."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from pokevend.inventory import Inventory, Pack

CATALOG_PATH = "data/packs.json"
INVENTORY_PATH = "data/inventory.json"

# ANSI helpers
B    = "\033[1m"
DIM  = "\033[2m"
YLW  = "\033[33m"
CYN  = "\033[36m"
GRN  = "\033[32m"
RED  = "\033[31m"
RST  = "\033[0m"


# ── Catalog ──────────────────────────────────────────────────────────────────

def load_catalog() -> list[dict]:
    if not os.path.exists(CATALOG_PATH):
        return []
    with open(CATALOG_PATH) as f:
        return json.load(f).get("packs", [])


def save_catalog(packs: list[dict]) -> None:
    with open(CATALOG_PATH, "w") as f:
        json.dump({"packs": packs}, f, indent=2)


# ── UI helpers ────────────────────────────────────────────────────────────────

def pick(prompt: str, options: list[str], extras: dict[str, str] | None = None) -> str:
    """Numbered menu; returns 1-based index string or an extras key."""
    for i, opt in enumerate(options, 1):
        print(f"  {CYN}{i}{RST}. {opt}")
    if extras:
        for key, label in extras.items():
            print(f"  {CYN}{key}{RST}. {label}")
    while True:
        val = input(f"\n{prompt}").strip().lower()
        if val.isdigit() and 1 <= int(val) <= len(options):
            return val
        if extras and val in extras:
            return val
        print(f"  {RED}Invalid choice — try again.{RST}")


def ask_int(prompt: str, min_val: int = 1) -> int:
    while True:
        val = input(prompt).strip()
        if val.isdigit() and int(val) >= min_val:
            return int(val)
        print(f"  {RED}Enter a whole number ≥ {min_val}.{RST}")


# ── Views ─────────────────────────────────────────────────────────────────────

def show_inventory(inv: Inventory) -> None:
    print(f"\n{B}Current inventory:{RST}")
    for lane in inv.lanes:
        if lane.is_empty:
            print(f"  {B}{lane.label}{RST}  {DIM}empty{RST}")
        else:
            counts: dict[str, int] = {}
            names: dict[str, str] = {}
            for p in lane.stack:
                counts[p.pack_id] = counts.get(p.pack_id, 0) + 1
                names[p.pack_id] = p.name
            summary = ", ".join(f"{names[k]} ×{v}" for k, v in counts.items())
            print(f"  {B}{lane.label}{RST}  {lane.quantity} pack{'s' if lane.quantity != 1 else ''}  {DIM}{summary}{RST}")
    print()


def show_catalog(catalog: list[dict]) -> None:
    if not catalog:
        print(f"\n  {DIM}Catalog is empty — use 'Add new pack' to create one.{RST}")
        return
    print(f"\n{B}Known packs ({len(catalog)}):{RST}")
    for p in catalog:
        img = f"  {DIM}{p['image']}{RST}" if p.get("image") else ""
        print(f"  {p['name']}  {DIM}({p['set_code']} · {p['series']}){RST}{img}")


# ── Actions ───────────────────────────────────────────────────────────────────

def add_pack_to_catalog(catalog: list[dict]) -> dict | None:
    print(f"\n{B}Add new pack to catalog{RST}")
    name = input("  Name (or blank to cancel): ").strip()
    if not name:
        return None
    series  = input("  Series (e.g. Scarlet & Violet): ").strip()
    set_code = input("  Set code (e.g. SV9): ").strip()
    image   = input("  Image — local path or URL (blank to skip): ").strip()

    base_id = name.lower().replace(" ", "-").replace("&", "and")
    existing = {p["pack_id"] for p in catalog}
    pack_id = base_id if base_id not in existing else f"{base_id}-{set_code.lower()}"

    entry = {"pack_id": pack_id, "name": name, "series": series,
             "set_code": set_code, "image": image}
    catalog.append(entry)
    save_catalog(catalog)
    print(f"  {GRN}✓ \"{name}\" added to catalog.{RST}")
    return entry


_LANE_KEYS = list("abcd")


def pick_lane(inv: Inventory) -> "Lane":  # type: ignore[name-defined]
    """Lane picker using letter keys (a/b/c/d) to avoid confusion with lane numbers."""
    from pokevend.inventory import Lane  # noqa: F401
    print(f"\n{B}Select lane:{RST}")
    lanes = inv.lanes[:4]
    for key, lane in zip(_LANE_KEYS, lanes):
        if lane.is_empty:
            print(f"  {CYN}{key}{RST}. {B}{lane.label}{RST}  {DIM}empty{RST}")
        else:
            print(f"  {CYN}{key}{RST}. {B}{lane.label}{RST}  —  {lane.quantity} pack{'s' if lane.quantity != 1 else ''}  {DIM}next: {lane.front.name}{RST}")
    valid = set(_LANE_KEYS[:len(lanes)])
    while True:
        val = input("\n> ").strip().lower()
        if val in valid:
            return lanes[_LANE_KEYS.index(val)]
        print(f"  {RED}Type a letter ({'/'.join(_LANE_KEYS[:len(lanes)])}).{RST}")


def add_stock(inv: Inventory, catalog: list[dict]) -> None:
    lane = pick_lane(inv)

    # Choose pack
    print(f"\n{B}Select pack:{RST}")
    if not catalog:
        print(f"  {DIM}(no packs in catalog yet){RST}")
        pack_dict = add_pack_to_catalog(catalog)
        if not pack_dict:
            return
    else:
        labels = [f"{p['name']}  {DIM}({p['set_code']} · {p['series']}){RST}" for p in catalog]
        key = pick("> ", labels, extras={"n": "Add new pack to catalog"})
        if key == "n":
            pack_dict = add_pack_to_catalog(catalog)
            if not pack_dict:
                return
        else:
            pack_dict = catalog[int(key) - 1]

    # Quantity
    qty = ask_int(f"\nHow many × {B}{pack_dict['name']}{RST} to add to {lane.label}? ")

    for _ in range(qty):
        lane.stack.append(Pack(
            pack_id=pack_dict["pack_id"],
            name=pack_dict["name"],
            series=pack_dict["series"],
            set_code=pack_dict["set_code"],
            image=pack_dict["image"],
        ))
    inv.save()
    total = lane.quantity
    print(f"\n  {GRN}✓ Added {qty} × {pack_dict['name']} to {lane.label}.")
    print(f"  {lane.label} now has {total} pack{'s' if total != 1 else ''}.{RST}")


# ── Main loop ─────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"\n{B}{YLW}=== PokéVend Stock Manager ==={RST}")

    catalog = load_catalog()
    inv = Inventory.load(INVENTORY_PATH)

    while True:
        show_inventory(inv)
        print(f"{B}Options:{RST}")
        print(f"  {CYN}1{RST}. Add stock to a lane")
        print(f"  {CYN}2{RST}. Add new pack to catalog")
        print(f"  {CYN}3{RST}. List known packs")
        print(f"  {CYN}q{RST}. Quit")

        choice = input("\n> ").strip().lower()

        if choice == "q":
            print("Bye!")
            break
        elif choice == "1":
            add_stock(inv, catalog)
        elif choice == "2":
            add_pack_to_catalog(catalog)
        elif choice == "3":
            show_catalog(catalog)
        else:
            print(f"  {RED}Unknown option.{RST}")


if __name__ == "__main__":
    main()
