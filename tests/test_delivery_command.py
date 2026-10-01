import unittest

from Classes.ByteStream import ByteStream
from Classes.Packets.Server.Home.AvailableServerCommandMessage import AvailableServerCommandMessage


class DeliveryCommandTests(unittest.TestCase):
    def test_native_delivery_context_and_base_are_complete(self):
        message = AvailableServerCommandMessage(b"")
        message.encode({"Command": {"ID": 203}, "RewardBrawler": [16, 1],
                        "Boxes": [{"Type": 25, "Items": [
                            {"Amount": 1, "DataRef": [16, 1], "RewardID": 1}]}]})
        reader = ByteStream(message.messagePayload)
        self.assertEqual([203, 0, 1, 25, 1, 1], [reader.readVInt() for _ in range(6)])
        self.assertEqual([16, 1], reader.readDataReference())
        self.assertEqual(1, reader.readVInt())
        self.assertEqual([None] * 3, [reader.readDataReference() for _ in range(3)])
        self.assertEqual([0, 0], [reader.readVInt() for _ in range(2)])
        self.assertFalse(reader.readBoolean())
        self.assertEqual([0] * 4, [reader.readVInt() for _ in range(4)])
        self.assertFalse(reader.readBoolean())
        self.assertFalse(reader.readBoolean())
        self.assertEqual([16, 1], reader.readDataReference())
        self.assertEqual([0xffffffff] * 3, [reader.readVInt() for _ in range(3)])
        self.assertEqual([0] * 4, [reader.readVInt() for _ in range(4)])
        self.assertEqual(len(message.messagePayload), reader.offset)


if __name__ == "__main__":
    unittest.main()
