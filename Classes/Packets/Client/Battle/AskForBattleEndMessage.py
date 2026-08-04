from Classes.Messaging import Messaging
from Classes.Database import database
from Classes.GameData import active_events

from Classes.Packets.PiranhaMessage import PiranhaMessage


class AskForBattleEndMessage(PiranhaMessage):
    def __init__(self, messageData):
        super().__init__(messageData)
        self.messageVersion = 0

    def encode(self, fields):
        pass

    def decode(self):
        fields = {}
        fields["Unk1"] = self.readVInt()
        fields["Result"] = self.readVInt()
        fields["Rank"] = self.readVInt()
        fields["MapID"] = self.readDataReference()
        fields["HeroesCount"] = self.readVInt()
        fields["Heroes"] = []
        for i in range(fields["HeroesCount"]): fields["Heroes"].append({"Brawler": {"ID": self.readDataReference(), "SkinID": self.readDataReference()}, "Team": self.readVInt(), "IsPlayer": self.readBoolean(), "PlayerName": self.readString()})
        super().decode(fields)
        return fields

    def execute(message, calling_instance, fields, cryptoInit):
        brawler_id = calling_instance.player.SelectedBrawlers[0]
        for hero in fields["Heroes"]:
            if hero["IsPlayer"]:
                brawler_id = hero["Brawler"]["ID"][1]
                break
        # V49 offline bot battles omit both the map reference and hero list.
        # The result still belongs to the one event advertised in HomeData, and
        # the selected database brawler is already used when no player hero is
        # supplied.
        map_reference = fields.get("MapID")
        if map_reference and len(map_reference) > 1 and map_reference[1] >= 0:
            map_id = map_reference[1]
        else:
            map_id = active_events()[0]["map_id"]
        progression = database.record_battle(
            calling_instance.player.ID[1],
            map_id,
            fields["Result"],
            fields["Rank"],
            brawler_id,
        )
        if progression is None:
            print(f"Rejected battle result for unowned brawler {brawler_id}")
            return
        calling_instance.player.reload()
        fields["Progression"] = progression
        fields["PlayerBrawlerID"] = brawler_id
        fields["Socket"] = calling_instance.client
        Messaging.sendMessage(23456, fields, cryptoInit, calling_instance.player)

    def getMessageType(self):
        return 14110

    def getMessageVersion(self):
        return self.messageVersion
