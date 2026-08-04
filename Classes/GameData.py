import os


# Character IDs are not contiguous: IDs 33 and 55 are disabled development
# characters in the V49.194 asset set. Keep the real character/card pairing
# instead of renumbering the remaining entries with enumerate().
BRAWLER_CARD_IDS = dict(zip(
    (*range(0, 33), *range(34, 55), *range(56, 70)),
    (
        0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60,
        64, 68, 72, 95, 100, 105, 110, 115, 120, 125, 130, 177, 182, 188,
        194, 200, 206, 218, 224, 230, 236, 279, 296, 303, 320, 327, 334,
        341, 358, 365, 372, 379, 386, 393, 410, 417, 427, 434, 448, 466,
        474, 491, 499, 507, 515, 523, 531, 539, 547, 557, 565, 573,
    ),
))

# V49's credits path. Chromatic brawlers deliberately remain outside this list.
STAR_ROAD = (
    ((8, 2, 1, 3, 6, 10, 13, 24), 160, 29),
    ((7, 9, 22, 27, 4, 18, 19, 20, 25, 34, 61), 430, 79),
    ((14, 15, 16, 26, 29, 30, 36, 43, 45, 48, 50, 58), 925, 169),
    ((11, 17, 21, 31, 32, 37, 42, 47, 64, 67), 1900, 349),
    ((5, 12, 23, 28, 40, 52, 63), 3400, 699),
)

STAR_ROAD_ENTRIES = tuple(
    (brawler_id, credits, gems)
    for brawlers, credits, gems in STAR_ROAD
    for brawler_id in brawlers
)

# Keep the live event on the client-proven offline slot. Other slot values open
# the APK's unfinished event roulette instead of starting a playable battle.
EVENT_LANES = (
    (1, 33, 7, 0),               # Gem Grab: Hard Rock Mine
    (1, 32, 5, 3),               # Bounty: Shooting Star
)


def active_events(now=None):
    override_slot = os.environ.get("VIBEBSDS_EVENT_SLOT")
    override_map = os.environ.get("VIBEBSDS_EVENT_MAP")
    if override_slot and override_map:
        map_id = int(override_map)
        return [{
            "event_index": int(override_slot),
            "slot": int(override_slot),
            "map_id": map_id,
            "seconds_left": 72292,
            "variation": {24: 5, 5: 3, 7: 0}.get(map_id, 0),
        }]
    return [
        {
            "event_index": event_index,
            "slot": slot,
            "map_id": map_id,
            "seconds_left": 72292,
            "variation": variation,
        }
        for slot, event_index, map_id, variation in EVENT_LANES
    ]


def star_road_remaining(owned_brawlers):
    owned = set(owned_brawlers)
    return [entry for entry in STAR_ROAD_ENTRIES if entry[0] not in owned]


def trophy_delta(result, rank):
    if rank > 0:
        return {1: 10, 2: 8, 3: 6, 4: 4, 5: 2, 6: -1, 7: -2,
                8: -4, 9: -6, 10: -8}.get(rank, 0)
    # V49 uses 0 for victory, 1 for defeat and 2 for draw in team modes.
    return {0: 8, 1: -6, 2: 0}.get(result, 0)
