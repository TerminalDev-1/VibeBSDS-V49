"""V49.194 mastery thresholds, rewards and normal-battle point awards."""
import json
from pathlib import Path


DATA = json.loads((Path(__file__).parent / "data" / "v49_mastery.json").read_text())
MAX_POINTS = DATA["levels"][-1]["threshold"]


def battle_mastery(trophies, won, points):
    award = 0
    if won:
        for threshold, amount in DATA["points"]:
            if trophies < threshold:
                break
            award = amount
    return min(award, max(0, MAX_POINTS - points))


def mastery_reward(brawler_id, level):
    hero = DATA["heroes"].get(str(brawler_id))
    if hero is None or not 2 <= level <= 10:
        return None
    entry = DATA["levels"][level - 2]
    kind, amount = entry["rewards"][hero["rarity"]]
    return {
        "threshold": entry["threshold"], "kind": kind, "amount": amount,
        "reference": hero["cosmetics"].get(kind),
        "fallback_coins": entry["fallback_coins"],
    }
