import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from Classes.ByteStream import ByteStream
from Classes.Commands.Client.LogicStarRoadClaimCommand import LogicStarRoadClaimCommand
from Classes.Commands.Client.LogicStarRoadRewardCommand import LogicStarRoadRewardCommand
from Classes.Commands.Server.LogicStarRoadUpdateCommand import LogicStarRoadUpdateCommand


class StarRoadCommandTests(unittest.TestCase):
    @patch("Classes.Commands.Client.LogicStarRoadClaimCommand.database.claim_star_road", return_value=(True, 160))
    @patch("Classes.Messaging.Messaging.sendMessage")
    def test_claim_delivers_once_and_updates_route(self, send, claim):
        player = SimpleNamespace(ID=[0, 1], reload=Mock(), OwnedBrawlers={0: {}, 8: {}}, Credits=8)
        LogicStarRoadClaimCommand(b"").execute(
            SimpleNamespace(player=player, client=object()), {"BrawlerID": [16, 8]}, object()
        )
        claim.assert_called_once_with(1, 8)
        player.reload.assert_called_once()
        self.assertEqual([203, 227], [call.args[1]["Command"]["ID"] for call in send.call_args_list])
        self.assertEqual(25, send.call_args_list[0].args[1]["Boxes"][0]["Type"])

    @patch("Classes.Commands.Client.LogicStarRoadClaimCommand.database.claim_star_road", return_value=(False, "not-current"))
    @patch("Classes.Messaging.Messaging.sendMessage")
    def test_duplicate_claim_does_not_deliver_again(self, send, claim):
        player = SimpleNamespace(ID=[0, 1], reload=Mock())
        LogicStarRoadClaimCommand(b"").execute(
            SimpleNamespace(player=player), {"BrawlerID": [16, 8]}
        )
        player.reload.assert_not_called()
        send.assert_not_called()

    def test_framed_route_keeps_boolean_after_command_base(self):
        from Classes.Packets.Server.Home.AvailableServerCommandMessage import AvailableServerCommandMessage
        message = AvailableServerCommandMessage(b"")
        message.encode({"Command": {"ID": 227}, "OwnedBrawlers": [0, 8, 2], "Credits": 8})
        reader = ByteStream(message.messagePayload)
        self.assertEqual(227, reader.readVInt())
        self.assertEqual(0xffffffff, reader.readVInt())
        self.assertEqual([0, 0, 0, 0], [reader.readVInt() for _ in range(4)])
        self.assertTrue(reader.readBoolean())

    def test_purchase_decoder_consumes_payment_reference(self):
        stream = ByteStream(b"")
        for value in [12, 13, 0, 1]: stream.writeVInt(value)
        stream.writeDataReference(16, 2)
        stream.writeDataReference(5, 19)
        stream.writeVInt(569)
        reader = ByteStream(stream.messagePayload)
        fields = LogicStarRoadRewardCommand(b"").decode(reader)
        self.assertEqual([5, 19], fields["PaymentResource"])
        self.assertEqual(569, reader.readVInt())

    @patch("Classes.Commands.Client.LogicStarRoadRewardCommand.database.claim_star_road", return_value=(True, 160))
    @patch("Classes.Commands.Client.LogicStarRoadRewardCommand.Messaging.sendMessage")
    def test_purchase_syncs_star_road_without_resending_home(self, send, claim):
        player = SimpleNamespace(ID=[0, 1], reload=Mock(), OwnedBrawlers={0: {}, 2: {}, 8: {}}, Credits=8)
        LogicStarRoadRewardCommand(b"").execute(
            SimpleNamespace(player=player, client=object()),
            {"BrawlerID": [16, 2], "PaymentResource": [5, 19]}, object()
        )
        claim.assert_called_once_with(1, 2)
        self.assertEqual(24111, send.call_args.args[0])
        self.assertEqual({"ID": 227}, send.call_args.args[1]["Command"])

    @patch("Classes.Commands.Client.LogicStarRoadRewardCommand.database.claim_star_road")
    def test_unsupported_payment_cannot_spend_credits(self, claim):
        LogicStarRoadRewardCommand(b"").execute(
            SimpleNamespace(), {"BrawlerID": [16, 2], "PaymentResource": [5, 0]}
        )
        claim.assert_not_called()

    def test_in_session_star_road_update_has_native_base_and_route(self):
        command = LogicStarRoadUpdateCommand(b"")
        command.encode({"OwnedBrawlers": [0, 8, 2], "Credits": 8})
        reader = ByteStream(command.messagePayload)
        self.assertEqual(227, command.getCommandType())
        self.assertEqual(0xffffffff, reader.readVInt())
        self.assertEqual([0, 0, 0, 0], [reader.readVInt() for _ in range(4)])
        self.assertTrue(reader.readBoolean())
        self.assertEqual([0, 0], [reader.readVInt() for _ in range(2)])
        self.assertIsNone(reader.readDataReference())
        self.assertEqual(1, reader.readVInt())
        self.assertEqual([16, 1], reader.readDataReference())
        self.assertEqual([160, 29, 0, 8, 0, 0], [reader.readVInt() for _ in range(6)])


if __name__ == "__main__":
    unittest.main()
