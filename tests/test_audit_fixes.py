import os
import socket
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from Classes.ByteStream import ByteStream
from Classes.Commands.Client.LogicPurchaseOfferCommand import LogicPurchaseOfferCommand
from Classes.Connection import Connection
from Classes.Crypto import Crypto, Nonce
from Classes.Database import GameDatabase
from Classes.GameData import EVENT_LANES, active_events
from Classes.MessageManager import MessageManager
from Classes.Packets.Client.Home.EndClientTurnMessage import EndClientTurnMessage
from Classes.TweetnaclCrypto.tweetnacl import crypto_secretbox_xsalsa20poly1305_tweet


def turn(*commands):
    stream = ByteStream(b"")
    stream.writeBoolean(False)
    for value in (100, 0, len(commands)):
        stream.writeVInt(value)
    for command_id, body in commands:
        stream.writeVInt(command_id)
        body(stream)
    return stream.messagePayload


def select_character(stream):
    for value in (1, 1, 0, 1):  # ticks and executor account
        stream.writeVInt(value)
    stream.writeDataReference(16, 3)
    stream.writeVInt(0)


def garbage(stream):
    stream.writeVInt(525)  # would look like a select-character command if misread
    for value in (1, 1, 0, 1):
        stream.writeVInt(value)
    stream.writeDataReference(16, 9)
    stream.writeVInt(0)


class EndClientTurnTests(unittest.TestCase):
    def test_decode_stops_at_command_without_decoder(self):
        fields = EndClientTurnMessage(turn((525, select_character), (506, garbage), (525, select_character))).decode()
        self.assertEqual([525, 506], [command["ID"] for command in fields["Commands"]])
        self.assertEqual([16, 3], fields["Commands"][0]["Fields"]["BrawlerID"])
        self.assertNotIn("Instance", fields["Commands"][1])

    def test_unknown_command_id_is_not_followed_by_misread_commands(self):
        fields = EndClientTurnMessage(turn((9999, garbage))).decode()
        self.assertEqual(1, len(fields["Commands"]))
        self.assertNotIn("Instance", fields["Commands"][0])


class PurchaseOfferTests(unittest.TestCase):
    @patch("Classes.Commands.Client.LogicPurchaseOfferCommand.Messaging.sendMessage")
    def test_execute_accepts_turn_arguments_and_sends_resync(self, send):
        crypto = object()
        instance = SimpleNamespace(client=object())
        LogicPurchaseOfferCommand(b"").execute(instance, {"Unk1": 0}, crypto)
        message_type, fields, sent_crypto = send.call_args.args
        self.assertEqual(24104, message_type)
        self.assertIs(instance.client, fields["Socket"])
        self.assertIs(crypto, sent_crypto)


class BattleReplayTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.db = GameDatabase(os.path.join(self.directory.name, "replay.sqlite"))
        self.low_id = self.db.login((0, 0), "", "replay-test")[0]["low_id"]

    def test_result_inside_interval_is_rejected_without_rewards(self):
        with patch("Classes.Database.time.time", return_value=1000):
            self.assertEqual(32, self.db.record_battle(self.low_id, 7, 0, 0, 0, 30)["trophy_delta"])
        with patch("Classes.Database.time.time", return_value=1029):
            self.assertEqual({"rejected": "too-soon"}, self.db.record_battle(self.low_id, 7, 0, 0, 0, 30))
        account, _ = self.db.load(self.low_id)
        self.assertEqual((37, 1, 20), (account["trophies"], account["battle_count"], account["credits"]))
        with patch("Classes.Database.time.time", return_value=1030):
            self.assertEqual(32, self.db.record_battle(self.low_id, 7, 0, 0, 0, 30)["trophy_delta"])

    def test_zero_interval_keeps_previous_behavior(self):
        for _ in range(2):
            self.assertNotIn("rejected", self.db.record_battle(self.low_id, 7, 0, 0, 0, 0))


class FakeSocket:
    def __init__(self, chunks):
        self.chunks = list(chunks)
        self.closed = False
        self.timeout = None

    def settimeout(self, value):
        self.timeout = value

    def recv(self, n):
        if not self.chunks:
            return b""
        chunk = self.chunks.pop(0)
        if isinstance(chunk, Exception):
            raise chunk
        if len(chunk) > n:
            self.chunks.insert(0, chunk[n:])
            chunk = chunk[:n]
        return chunk

    def close(self):
        self.closed = True


class ConnectionTests(unittest.TestCase):
    def run_connection(self, chunks):
        client = FakeSocket(chunks)
        connection = Connection(client, ("127.0.0.1", 1))
        with patch("Classes.Connection.MessageManager.receiveMessage") as receive, \
                patch("Classes.Connection.Crypto") as crypto:
            crypto.return_value.decryptClient.side_effect = lambda packet_id, payload: payload
            connection.run()
        return client, receive

    def test_split_header_is_reassembled(self):
        header = (10108).to_bytes(2, "big") + (3).to_bytes(3, "big") + bytes(2)
        client, receive = self.run_connection([header[:3], header[3:], b"abc"])
        receive.assert_called_once()
        self.assertEqual((10108, b"abc"), receive.call_args.args[1:3])
        self.assertTrue(client.closed)
        self.assertEqual(Connection.IDLE_TIMEOUT, client.timeout)

    def test_idle_timeout_and_closed_socket_disconnect(self):
        for chunks in ([socket.timeout()], [], [b"\x27"]):
            with self.subTest(chunks=chunks):
                client, receive = self.run_connection(chunks)
                receive.assert_not_called()
                self.assertTrue(client.closed)


class CryptoAuthenticationTests(unittest.TestCase):
    def encrypted(self, crypto, payload):
        nonce = Nonce(bytes(crypto.decryptNonce))
        nonce.increment()
        plain = bytearray(32) + bytearray(payload)
        boxed = bytearray(len(plain))
        crypto_secretbox_xsalsa20poly1305_tweet(boxed, plain, len(plain), bytes(nonce), crypto.shared_encryption_key)
        return bytes(boxed[16:])

    def test_authentic_packet_decrypts_and_tampered_packet_is_rejected(self):
        crypto = Crypto()
        crypto.decryptNonce = Nonce(bytes(24))
        self.assertEqual(b"laser", bytes(crypto.decryptClient(14102, self.encrypted(crypto, b"laser"))))

        crypto = Crypto()
        crypto.decryptNonce = Nonce(bytes(24))
        packet = bytearray(self.encrypted(crypto, b"laser"))
        packet[-1] ^= 1
        self.assertIsNone(crypto.decryptClient(14102, bytes(packet)))


class LobbyInfoTests(unittest.TestCase):
    def receive(self, execute):
        message = MagicMock()
        message.isServerToClient.return_value = False
        message.execute.side_effect = execute
        instance = SimpleNamespace(client=object(), player=object())
        with patch("Classes.MessageManager.LogicLaserMessageFactory.createMessageByType", return_value=message), \
                patch("Classes.MessageManager.Messaging.sendMessage") as send:
            MessageManager.receiveMessage(instance, 10108, b"", None)
        return send

    def test_lobby_info_follows_handled_messages_only(self):
        self.assertEqual(23457, self.receive(None).call_args.args[0])
        self.receive(RuntimeError("handler failed")).assert_not_called()

    def test_unknown_message_gets_no_lobby_info(self):
        with patch("Classes.MessageManager.LogicLaserMessageFactory.createMessageByType", return_value=None), \
                patch("Classes.MessageManager.Messaging.sendMessage") as send:
            MessageManager.receiveMessage(SimpleNamespace(client=object(), player=object()), 14999, b"", None)
        send.assert_not_called()


class StringTests(unittest.TestCase):
    def test_null_string_is_empty_text_and_stream_stays_aligned(self):
        stream = ByteStream(b"")
        stream.writeInt(-1)
        stream.writeString("next")
        stream.writeString("ref")
        reader = ByteStream(stream.messagePayload)
        self.assertEqual("", reader.readString())
        self.assertEqual("next", reader.readString())
        self.assertEqual("ref", reader.readStringReference())


class EventOverrideTests(unittest.TestCase):
    def test_override_uses_advertised_variations(self):
        for _, _, map_id, variation in EVENT_LANES:
            with self.subTest(map_id=map_id), patch.dict(os.environ, {
                    "VIBEBSDS_EVENT_SLOT": "1", "VIBEBSDS_EVENT_MAP": str(map_id)}):
                self.assertEqual(variation, active_events()[0]["variation"])


if __name__ == "__main__":
    unittest.main()
