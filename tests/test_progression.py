import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from Classes.Database import GameDatabase
from Classes.GameData import active_events, brawl_pass_claim_masks, star_road_remaining
from Classes.Instances.Classes.Player import Player
from Classes.Packets.Server.Home.OwnHomeDataMessage import OwnHomeDataMessage
from Classes.Packets.Client.Battle.AskForBattleEndMessage import AskForBattleEndMessage


class ProgressionTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db = GameDatabase(os.path.join(self.tempdir.name, "test.sqlite"))
        self.account, self.brawlers = self.db.login((0, 0), "", "test-device")
        self.low_id = self.account["low_id"]

    def tearDown(self):
        self.tempdir.cleanup()

    def test_account_reconnects_with_stable_identity(self):
        account, brawlers = self.db.login((0, 0), "", "test-device")
        self.assertEqual(self.low_id, account["low_id"])
        self.assertEqual(self.account["token"], account["token"])
        self.assertEqual([0], [row["brawler_id"] for row in brawlers])

    def test_star_road_claim_is_transactional_and_idempotent(self):
        target_id, cost, _ = star_road_remaining([0])[0]
        with self.db.connect() as connection:
            connection.execute(
                "UPDATE accounts SET credits = ? WHERE low_id = ?",
                (cost, self.low_id),
            )
        claimed, charged = self.db.claim_star_road(self.low_id, target_id)
        self.assertTrue(claimed)
        self.assertEqual(cost, charged)
        account, brawlers = self.db.load(self.low_id)
        self.assertEqual(0, account["credits"])
        self.assertEqual(10, account["trophies"])
        self.assertIn(target_id, [row["brawler_id"] for row in brawlers])

        claimed_again, _ = self.db.claim_star_road(self.low_id, target_id)
        self.assertFalse(claimed_again)
        account_again, brawlers_again = self.db.load(self.low_id)
        self.assertEqual(0, account_again["credits"])
        self.assertEqual(2, len(brawlers_again))

    def test_battle_rewards_persist_across_reload(self):
        result = self.db.record_battle(self.low_id, 7, 0, 0, 0)
        self.assertEqual(8, result["trophy_delta"])
        self.assertEqual(20, result["tokens"])
        account, brawlers = self.db.load(self.low_id)
        self.assertEqual(13, account["trophies"])
        self.assertEqual(20, account["credits"])
        self.assertEqual(1, account["battle_count"])
        self.assertEqual(13, brawlers[0]["trophies"])

    def test_brawl_pass_credit_claim_is_exact_and_idempotent(self):
        claimed, amount = self.db.claim_brawl_pass_credit(self.low_id, 17, 9, 47)
        self.assertTrue(claimed)
        self.assertEqual(45, amount)
        account, _ = self.db.load(self.low_id)
        self.assertEqual(45, account["credits"])
        self.assertEqual({(17, 9, 47)}, self.db.brawl_pass_credit_claims(self.low_id))

        claimed_again, reason = self.db.claim_brawl_pass_credit(self.low_id, 17, 9, 47)
        self.assertFalse(claimed_again)
        self.assertEqual("already-claimed", reason)
        account_again, _ = self.db.load(self.low_id)
        self.assertEqual(45, account_again["credits"])

    def test_first_star_road_unlock_advances_to_the_next_target(self):
        with self.db.connect() as connection:
            connection.execute(
                "UPDATE accounts SET credits = 160 WHERE low_id = ?", (self.low_id,)
            )

        claimed, cost = self.db.claim_star_road(self.low_id, 8)
        self.assertTrue(claimed)
        self.assertEqual(160, cost)
        account, brawlers = self.db.load(self.low_id)
        self.assertEqual(0, account["credits"])
        self.assertIn(8, {row["brawler_id"] for row in brawlers})
        self.assertEqual(2, star_road_remaining(row["brawler_id"] for row in brawlers)[0][0])

    def test_brawl_pass_claim_mask_marks_the_exact_tier(self):
        premium, free = brawl_pass_claim_masks(17, {(17, 9, 47)})
        self.assertEqual(16383 | (1 << 17), premium[1])
        self.assertEqual(2147483647, free[1])

    def test_offline_battle_result_uses_advertised_map_fallback(self):
        player = Player()
        player.load(self.account, self.brawlers)

        def reload_player():
            player.load(*self.db.load(self.low_id))

        player.reload = reload_player
        calling_instance = type("CallingInstance", (), {
            "player": player,
            "client": object(),
        })()
        fields = {
            "Result": 0,
            "Rank": 0,
            "MapID": None,
            "HeroesCount": 0,
            "Heroes": [],
        }

        with patch(
            "Classes.Packets.Client.Battle.AskForBattleEndMessage.database",
            self.db,
        ), patch("Classes.Messaging.Messaging.sendMessage") as send_message:
            AskForBattleEndMessage.execute(None, calling_instance, fields, object())

        with self.db.connect() as connection:
            recorded_map = connection.execute(
                "SELECT map_id FROM battles WHERE account_low_id = ?",
                (self.low_id,),
            ).fetchone()[0]
        self.assertEqual(active_events()[0]["map_id"], recorded_map)
        self.assertEqual(8, fields["Progression"]["trophy_delta"])
        self.assertEqual(13, player.Trophies)
        send_message.assert_called_once()

    def test_unowned_brawler_cannot_receive_battle_rewards(self):
        self.assertIsNone(self.db.record_battle(self.low_id, 7, 0, 0, 12))
        account, _ = self.db.load(self.low_id)
        self.assertEqual(0, account["battle_count"])

    def test_home_advertises_two_client_proven_events(self):
        events = active_events(0)
        self.assertEqual(2, len(events))
        self.assertEqual([33, 32], [event["event_index"] for event in events])
        self.assertEqual([1, 1], [event["slot"] for event in events])
        self.assertEqual([7, 5], [event["map_id"] for event in events])
        self.assertEqual([0, 3], [event["variation"] for event in events])

    def test_home_data_encodes_database_player(self):
        player = Player()
        player.load(self.account, self.brawlers)
        message = OwnHomeDataMessage(b"")
        message.encode({}, player)
        self.assertGreater(len(message.messagePayload), 500)

    def test_v49_character_ids_keep_disabled_rows_out_of_card_mapping(self):
        from Classes.GameData import BRAWLER_CARD_IDS

        self.assertNotIn(33, BRAWLER_CARD_IDS)
        self.assertNotIn(55, BRAWLER_CARD_IDS)
        self.assertEqual(218, BRAWLER_CARD_IDS[34])
        self.assertEqual(573, BRAWLER_CARD_IDS[69])

    def test_database_integrity(self):
        with self.db.connect() as connection:
            self.assertEqual("ok", connection.execute("PRAGMA integrity_check").fetchone()[0])
            self.assertEqual([], connection.execute("PRAGMA foreign_key_check").fetchall())


if __name__ == "__main__":
    unittest.main()
