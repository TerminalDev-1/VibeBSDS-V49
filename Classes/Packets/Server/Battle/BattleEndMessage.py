from Classes.Packets.PiranhaMessage import PiranhaMessage

class BattleEndMessage(PiranhaMessage):
    def __init__(self, messageData):
        super().__init__(messageData)
        self.messageVersion = 0

    def encode(self, fields, player):
        progression = fields.get("Progression", {})
        trophy_change = progression.get("trophy_delta", 0)
        tokens = progression.get("tokens", 0)
        player_brawler_id = fields.get("PlayerBrawlerID", player.SelectedBrawlers[0])
        player_brawler = player.OwnedBrawlers.get(player_brawler_id, {})
        self.writeLong(0, 1) # Battle UUID High
        self.writeLong(0, 1) # Battle UUID Low
        self.writeVInt(1) # Battle End Game Mode (gametype)
        self.writeVInt(fields["Rank"]) # Result (Victory/Defeat/Draw/Rank Score)
        self.writeVInt(tokens) # Tokens Gained (Gained Keys)
        self.writeVInt(trophy_change) # Trophies Result (Metascore change)
        self.writeVInt(0) # Power Play Points Gained (Pro League Points)
        self.writeVInt(0) # Doubled Tokens (Double Keys)
        self.writeVInt(0) # Double Token Event (Double Event Keys)
        self.writeVInt(0) # Token Doubler Remaining (Double Keys Remaining)
        self.writeVInt(0) # game Lenght In Seconds
        self.writeVInt(0) # Epic Win Power Play Points Gained (op Win Points)
        self.writeVInt(0) # Championship Level Reached (CC Wins)
        self.writeBoolean(False)
        self.writeVInt(0)
        self.writeVInt(0)
        self.writeBoolean(False)
        self.writeVInt(0)
        self.writeVInt(0)
        self.writeVInt(0)
        self.writeVInt(0)
        self.writeVInt(0)
        self.writeBoolean(False)
        self.writeBoolean(False)
        self.writeBoolean(False)
        self.writeBoolean(False)
        self.writeBoolean(True)
        self.writeBoolean(False)
        self.writeBoolean(False)
        self.writeVInt(-1)
        self.writeBoolean(False)

        self.writeVInt(fields["HeroesCount"])
        for heroEntry in fields["Heroes"]:
            self.writeBoolean(heroEntry["IsPlayer"])
            self.writeBoolean(bool(heroEntry["Team"]))
            self.writeBoolean(bool(heroEntry["Team"]))
            self.writeVInt(1)
            for i in range(1):
                self.writeDataReference(heroEntry["Brawler"]["ID"][0], heroEntry["Brawler"]["ID"][1])
            self.writeVInt(1)
            for i in range(1):
                self.writeDataReference(heroEntry["Brawler"]["SkinID"][0], heroEntry["Brawler"]["SkinID"][1])
            self.writeVInt(1)
            for i in range(1):
                self.writeVInt(player_brawler.get("Trophies", 0) if heroEntry["IsPlayer"] else 0)
            self.writeVInt(1)
            for i in range(1):
                self.writeVInt(player_brawler.get("PowerLevel", 1) if heroEntry["IsPlayer"] else 1)
            self.writeVInt(1)
            for i in range(1):
                self.writeVInt(0)
            self.writeVInt(0)
            self.writeVInt(0)
            self.writeBoolean(heroEntry["IsPlayer"])
            if heroEntry["IsPlayer"]:
                self.writeLong(player.ID[0], player.ID[1])
            self.writeString(heroEntry["PlayerName"])
            self.writeVInt(100)
            self.writeVInt(28000000)
            self.writeVInt(43000000)
            self.writeVInt(46000000)
            if heroEntry["IsPlayer"]:
                self.writeBoolean(True)
                self.writeVLong(5, 4181497)
                self.writeString('Orange eSPORT')
                self.writeDataReference(8, 16)

        self.writeVInt(0)

        self.writeVInt(0)

        self.writeVInt(0)

        self.writeVInt(2)

        self.writeVInt(1)
        current_trophies = player_brawler.get("Trophies", 0)
        self.writeVInt(max(0, current_trophies - trophy_change))
        self.writeVInt(current_trophies)

        self.writeVInt(5)
        self.writeVInt(player.Trophies - trophy_change)
        self.writeVInt(player.Trophies)

        self.writeDataReference(28, 0)
        self.writeBoolean(False)
        self.writeBoolean(False)
        self.writeVInt(0)
        self.writeVInt(0)
        self.writeBoolean(False)
        self.writeVInt(-1)
        self.writeBoolean(False)


    def decode(self):
        fields = {}
        return {}

    def execute(message, calling_instance, fields):
        pass

    def getMessageType(self):
        return 23456

    def getMessageVersion(self):
        return self.messageVersion
