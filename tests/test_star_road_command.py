import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from Classes.Commands.Client.LogicStarRoadClaimCommand import LogicStarRoadClaimCommand


class StarRoadCommandTests(unittest.TestCase):
    @patch(
        "Classes.Commands.Client.LogicStarRoadClaimCommand.database.claim_star_road",
        return_value=(True, 160),
    )
    @patch("Classes.Commands.Client.LogicStarRoadClaimCommand.Messaging.sendMessage")
    def test_claim_sends_brawler_delivery(self, send, claim):
        player = SimpleNamespace(ID=[0, 1], reload=Mock())
        connection = SimpleNamespace(player=player, client=object())

        LogicStarRoadClaimCommand(b"").execute(
            connection, {"BrawlerID": [16, 8]}, object()
        )

        claim.assert_called_once_with(1, 8)
        player.reload.assert_called_once_with()
        self.assertEqual(1, send.call_count)
        delivery = send.call_args.args
        self.assertEqual(24111, delivery[0])
        self.assertEqual({"ID": 203}, delivery[1]["Command"])
        self.assertEqual([16, 8], delivery[1]["Boxes"][0]["Items"][0]["DataRef"])


if __name__ == "__main__":
    unittest.main()
