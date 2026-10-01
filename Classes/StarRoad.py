from Classes.GameData import star_road_remaining


def encode_star_road(stream, owned_brawlers, credits):
    """Encode the optional V49 StarRoadData used by HomeData and command 227."""
    star_road = star_road_remaining(owned_brawlers)
    stream.writeBoolean(bool(star_road)) # Star Road
    if star_road:
        # V49.194 StarRoadData::decode. The first two candidate lists and
        # selected reference are unused by this linear progression path.
        stream.writeVInt(0)
        stream.writeVInt(0)
        stream.writeDataReference(0)

        current_entry = star_road[:1]
        stream.writeVInt(len(current_entry))
        for brawler_id, cost, gems in current_entry:
            stream.writeDataReference(16, brawler_id)
            stream.writeVInt(cost)
            stream.writeVInt(gems)
            stream.writeVInt(0)
            stream.writeVInt(credits)
            stream.writeVInt(0)
            stream.writeVInt(0)

        # The route contains only the nodes after the active unlock. On the
        # next HomeData decode (including reconnect), its first node becomes
        # the next active Star Road target.
        queued_entries = star_road[1:]
        stream.writeVInt(len(queued_entries))
        for brawler_id, cost, gems in queued_entries:
            stream.writeDataReference(16, brawler_id)
            stream.writeVInt(cost)
            stream.writeVInt(gems)
            stream.writeVInt(0)
            stream.writeVInt(0)
            stream.writeVInt(brawler_id)
            stream.writeVInt(0)

        stream.writeVInt(0)
        stream.writeVInt(0)

