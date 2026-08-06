import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from Classes.Commands.Client.LogicClaimRankUpRewardCommand import (
    LogicClaimRankUpRewardCommand,
)


class BrawlPassCommandTests(unittest.TestCase):
    @patch(
        "Classes.Commands.Client.LogicClaimRankUpRewardCommand.database.claim_brawl_pass_credit",
        return_value=(True, 45),
    )
    @patch("Classes.Commands.Client.LogicClaimRankUpRewardCommand.Messaging.sendMessage")
    def test_credit_claim_sends_delivery_item_acknowledgement(self, send, claim):
        player = SimpleNamespace(ID=[0, 1], reload=Mock())
        connection = SimpleNamespace(player=player, client=object())

        LogicClaimRankUpRewardCommand(b"").execute(
            connection,
            {
                "BrawlPassSeason": 17,
                "RewardTrack": 9,
                "Tier": 47,
            },
        )

        claim.assert_called_once_with(1, 17, 9, 47)
        player.reload.assert_called_once_with()
        self.assertEqual(24111, send.call_args.args[0])
        fields = send.call_args.args[1]
        self.assertEqual({"ID": 203}, fields["Command"])
        self.assertEqual(45, fields["Boxes"][0]["Items"][0]["Amount"])
        self.assertEqual(22, fields["Boxes"][0]["Items"][0]["RewardID"])


if __name__ == "__main__":
    unittest.main()
