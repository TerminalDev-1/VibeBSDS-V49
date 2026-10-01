import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from Classes.ByteStream import ByteStream
from Classes.Database import GameDatabase
from Classes.Instances.Classes.Player import Player
from Classes.Packets.Client.Battle.AskForBattleEndMessage import AskForBattleEndMessage
from Classes.Packets.Server.Battle.BattleEndMessage import BattleEndMessage


class BattleEndTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.db = GameDatabase(os.path.join(self.directory.name, "battle.sqlite"))
        account, brawlers = self.db.login((0, 0), "", "battle-test")
        self.player = Player()
        self.player.load(account, brawlers)
        self.player.reload = lambda: self.player.load(*self.db.load(self.player.ID[1]))

    def tearDown(self):
        self.directory.cleanup()

    def finish(self, team, winner, rank=0):
        fields = {
            "Result": winner, "Rank": rank, "MapID": [15, 5],
            "Heroes": [{"IsPlayer": True, "Team": team, "PlayerName": "Player",
                        "Brawler": {"ID": [16, 0], "SkinID": None}}],
        }
        instance = SimpleNamespace(player=self.player, client=object())
        with patch("Classes.Packets.Client.Battle.AskForBattleEndMessage.database", self.db), \
                patch("Classes.Messaging.Messaging.sendMessage"):
            AskForBattleEndMessage.execute(None, instance, fields, None)
        return fields

    def test_winning_team_is_relative_to_player_on_either_team(self):
        for team in (0, 1):
            for winner in (0, 1):
                with self.subTest(team=team, winner=winner):
                    before = self.player.Trophies
                    fields = self.finish(team, winner)
                    won = team == winner
                    self.assertEqual(0 if won else 1, fields["Result"])
                    self.assertEqual(20 if won else 10, fields["Progression"]["tokens"])
                    self.assertEqual(20 if won else 8, fields["Progression"]["credits"])
                    expected = before + 8 if won else max(5, before - 6)
                    reconnected, _ = self.db.load(self.player.ID[1])
                    self.assertEqual(expected, reconnected["trophies"])
                    with self.db.connect() as connection:
                        battle = connection.execute(
                            "SELECT result, map_id FROM battles WHERE rowid = ?",
                            (fields["Progression"]["battle_id"],),
                        ).fetchone()
                    self.assertEqual((0 if won else 1, 5), tuple(battle))

    def test_draw_and_placement_do_not_become_team_victories(self):
        self.assertEqual(2, self.finish(1, -1)["Result"])
        self.assertEqual(0, self.finish(1, 0, rank=1)["Result"])

    def test_result_header_encodes_defeat_draw_and_placement(self):
        for team, winner, rank, outcome in [(0, 1, 0, 1), (0, -1, 0, 2), (1, 0, 4, 4)]:
            with self.subTest(outcome=outcome):
                fields = self.finish(team, winner, rank)
                message = BattleEndMessage(b"")
                message.encode(fields, self.player)
                reader = ByteStream(message.messagePayload)
                reader.readLong()
                reader.readLong()
                reader.readVInt()
                self.assertEqual(outcome, reader.readVInt())

    def test_v49_native_result_layout_including_default_skins(self):
        fields = self.finish(1, 1)
        fields["Heroes"] += [
            {"IsPlayer": False, "Team": index % 2, "PlayerName": f"Bot {index}",
             "Brawler": {"ID": [16, index], "SkinID": [29, 0] if index == 1 else None}}
            for index in range(1, 6)
        ]
        message = BattleEndMessage(b"")
        message.encode(fields, self.player)
        reader = ByteStream(message.messagePayload)
        self.assertEqual([0, self.player.ID[1]], reader.readLong())
        self.assertEqual([0, fields["Progression"]["battle_id"]], reader.readLong())
        header = [reader.readVInt() for _ in range(11)]
        self.assertEqual([1, 0, 20, 8], header[:4])
        self.assertFalse(reader.readBoolean())
        for _ in range(2): reader.readVInt()
        for _ in range(2): reader.readBoolean()
        for _ in range(6): reader.readVInt()
        for _ in range(7): reader.readBoolean()
        reader.readVInt()
        reader.readBoolean()
        self.assertEqual(6, reader.readVInt())
        # Native hero decoder 0x696d54: byte counts, five arrays, display
        # data with FOUR VInts, two short statistics and two fixed integers.
        for hero in fields["Heroes"]:
            self.assertEqual(hero["IsPlayer"], reader.readBoolean())
            self.assertEqual(hero["Team"] != 1, reader.readBoolean())
            self.assertFalse(reader.readBoolean())
            self.assertEqual(1, reader.readByte())
            self.assertEqual(hero["Brawler"]["ID"], reader.readDataReference())
            self.assertEqual(1, reader.readByte())
            self.assertEqual(hero["Brawler"]["SkinID"], reader.readDataReference())
            for array_index in range(3):
                self.assertEqual(1, reader.readByte())
                value = reader.readVInt()
                if array_index == 0:
                    self.assertEqual(5 if hero["IsPlayer"] else 0, value)
            reader.readVInt()
            reader.readVInt()
            local = reader.readBoolean()
            if local: self.assertEqual(self.player.ID, reader.readLong())
            self.assertEqual(hero["PlayerName"], reader.readString())
            display = [reader.readVInt() for _ in range(4)]
            self.assertEqual(43000000 + (self.player.Namecolor if local else 0), display[2])
            self.assertFalse(reader.readBoolean())
            self.assertEqual(0, reader.readByte())
            self.assertEqual(0, reader.readByte())
            self.assertEqual([0, 0], [reader.readInt16(), reader.readInt16()])
            self.assertEqual([0, 0], [reader.readInt(), reader.readInt()])
            self.assertIsNone(reader.readDataReference())
        self.assertEqual([0, 0, 2], [reader.readVInt() for _ in range(3)])
        self.assertEqual([1, 5, 13, 5, 5, 13], [reader.readVInt() for _ in range(6)])
        self.assertEqual([28, 0], reader.readDataReference())
        for _ in range(3): self.assertFalse(reader.readBoolean())
        for _ in range(2): self.assertEqual(0, reader.readVInt())
        self.assertFalse(reader.readBoolean())
        self.assertEqual(0xFFFFFFFF, reader.readVInt())
        self.assertFalse(reader.readBoolean())
        self.assertEqual(0, reader.readVInt())
        for _ in range(2): self.assertFalse(reader.readBoolean())
        self.assertEqual(0, reader.readVInt())
        for _ in range(3): self.assertFalse(reader.readBoolean())
        self.assertEqual(len(message.messagePayload), reader.offset)
