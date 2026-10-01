import os
import tempfile
import unittest

from Classes.ByteStream import ByteStream
from Classes.Commands.Client.LogicClaimMasteryTrackRewardCommand import LogicClaimMasteryTrackRewardCommand
from Classes.Database import GameDatabase
from Classes.Mastery import MAX_POINTS, battle_mastery, mastery_reward


class MasteryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.db = GameDatabase(os.path.join(self.directory.name, "mastery.sqlite"))
        self.account, _ = self.db.login((0, 0), "", "mastery-test")
        self.low = self.account["low_id"]

    def tearDown(self):
        self.directory.cleanup()

    def points(self, amount):
        with self.db.connect() as db:
            db.execute("UPDATE brawlers SET mastery_points = ? WHERE account_low_id = ?", (amount, self.low))

    def test_win_award_uses_pre_battle_trophies_and_stays_separate(self):
        result = self.db.record_battle(self.low, 7, 0, 0, 0)
        self.assertEqual((32, 5, 0), (result["trophy_delta"], result["mastery_delta"], result["previous_mastery"]))
        result = self.db.record_battle(self.low, 7, 1, 0, 0)
        self.assertEqual(0, result["mastery_delta"])
        result = self.db.record_battle(self.low, 7, 0, 0, 0)
        self.assertEqual(5, result["mastery_delta"])
        self.assertEqual(10, self.db.load(self.low)[1][0]["mastery_points"])

    def test_thresholds_cap_and_draw(self):
        self.assertEqual(5, battle_mastery(49, True, 0))
        self.assertEqual(7, battle_mastery(50, True, 0))
        self.assertEqual(100, battle_mastery(2000, True, 0))
        self.points(MAX_POINTS - 2)
        self.assertEqual(2, self.db.record_battle(self.low, 7, 0, 0, 0)["mastery_delta"])
        self.assertEqual(0, self.db.record_battle(self.low, 7, 0, 0, 0)["mastery_delta"])
        self.assertEqual(0, self.db.record_battle(self.low, 7, 2, 0, 0)["mastery_delta"])

    def test_claim_requires_owned_earned_sequential_reward(self):
        self.assertFalse(self.db.claim_mastery(self.low, 0, 2)[0])
        self.points(1500)
        self.assertFalse(self.db.claim_mastery(self.low, 0, 3)[0])
        self.assertFalse(self.db.claim_mastery(self.low, 1, 2)[0])
        self.assertTrue(self.db.claim_mastery(self.low, 0, 2)[0])
        self.assertFalse(self.db.claim_mastery(self.low, 0, 2)[0])
        self.assertTrue(self.db.claim_mastery(self.low, 0, 3)[0])
        self.assertTrue(self.db.claim_mastery(self.low, 0, 4)[0])
        account, heroes = self.db.load(self.low)
        self.assertEqual(1750, account["coins"])
        self.assertEqual(75, account["credits"])
        self.assertEqual(100, account["power_points"])
        self.assertEqual(3, heroes[0]["mastery_claimed"])

    def test_cosmetics_and_claims_survive_reopen(self):
        self.points(MAX_POINTS)
        for level in range(2, 11):
            self.assertTrue(self.db.claim_mastery(self.low, 0, level)[0])
        reopened = GameDatabase(self.db.path)
        account, heroes = reopened.load(self.low)
        self.assertEqual(9, heroes[0]["mastery_claimed"])
        self.assertEqual(3, len(account["cosmetics"]))
        self.assertEqual(mastery_reward(0, 8)["reference"], next(ref for ref in account["cosmetics"] if ref[0] == 52))
        self.assertFalse(reopened.claim_mastery(self.low, 0, 10)[0])

    def test_claim_decoder_consumes_all_fields_before_next_command(self):
        stream = ByteStream(b"")
        for value in [12, 13, 0, 1]: stream.writeVInt(value)
        stream.writeDataReference(16, 0)
        stream.writeVInt(2)
        stream.writeBoolean(True)
        stream.writeVInt(525)
        reader = ByteStream(stream.messagePayload)
        fields = LogicClaimMasteryTrackRewardCommand(b"").decode(reader)
        self.assertEqual(2, fields["RewardLevel"])
        self.assertTrue(fields["Fallback"])
        self.assertEqual(525, reader.readVInt())


if __name__ == "__main__":
    unittest.main()
