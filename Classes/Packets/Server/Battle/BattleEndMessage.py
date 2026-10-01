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
        current_trophies = player_brawler.get("Trophies", 0)
        previous_trophies = current_trophies - trophy_change
        player_team = next((hero["Team"] for hero in fields["Heroes"]
                            if hero["IsPlayer"]), 0)
        self.writeLong(player.ID[0], player.ID[1])
        self.writeLong(0, progression.get("battle_id", 0))
        self.writeVInt(1) # Battle End Game Mode (gametype)
        self.writeVInt(fields["Rank"] if fields["Rank"] > 0 else fields["Result"])
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
        self.writeBoolean(False) # V49 result flag at native offset 0xa5
        self.writeVInt(0)
        self.writeVInt(0)
        self.writeVInt(0)
        self.writeVInt(0)
        self.writeVInt(0)
        self.writeVInt(0) # V49 result value at native offset 0xc0
        self.writeBoolean(False)
        self.writeBoolean(False)
        self.writeBoolean(False)
        self.writeBoolean(False)
        self.writeBoolean(True)
        self.writeBoolean(False)
        self.writeBoolean(False)
        self.writeVInt(-1)
        self.writeBoolean(False)

        self.writeVInt(len(fields["Heroes"]))
        for heroEntry in fields["Heroes"]:
            self.writeBoolean(heroEntry["IsPlayer"])
            self.writeBoolean(heroEntry["Team"] != player_team)
            self.writeBoolean(False) # no MVP supplied by the offline result
            self.writeByte(1)
            self.writeDataReference(*heroEntry["Brawler"]["ID"])
            self.writeByte(1)
            skin = heroEntry["Brawler"].get("SkinID")
            if skin:
                self.writeDataReference(*skin)
            else:
                self.writeDataReference(0)
            self.writeByte(1)
            self.writeVInt(previous_trophies if heroEntry["IsPlayer"] else 0)
            self.writeByte(1)
            self.writeVInt(player_brawler.get("PowerLevel", 1) if heroEntry["IsPlayer"] else 1)
            self.writeByte(1)
            # V49 hero scoreChanges reports this hero's trophy award.
            self.writeVInt(trophy_change if heroEntry["IsPlayer"] else 0)
            self.writeVInt(0)
            self.writeVInt(0)
            self.writeBoolean(heroEntry["IsPlayer"])
            if heroEntry["IsPlayer"]:
                self.writeLong(player.ID[0], player.ID[1])
            self.writeString(heroEntry["PlayerName"])
            self.writeVInt(player.Level if heroEntry["IsPlayer"] else 1)
            self.writeVInt(28000000 + player.Thumbnail if heroEntry["IsPlayer"] else 28000000)
            self.writeVInt(43000000 + player.Namecolor if heroEntry["IsPlayer"] else 43000000)
            self.writeVInt(46000000)
            self.writeBoolean(False) # no static upstream club attached to the player
            self.writeByte(1) # masteryPoints before this battle
            self.writeVInt(progression.get("previous_mastery", 0) if heroEntry["IsPlayer"] else 0)
            self.writeByte(1) # masteryPointChanges from this battle
            self.writeVInt(progression.get("mastery_delta", 0) if heroEntry["IsPlayer"] else 0)
            self.writeInt16(0)
            self.writeInt16(0)
            self.writeInt(0)
            self.writeInt(0)
            self.writeDataReference(0)

        self.writeVInt(0)

        self.writeVInt(0)

        self.writeVInt(2)

        self.writeVInt(1)
        self.writeVInt(previous_trophies)
        # Native 0x49c220 interprets these as score and previous high score,
        # not before/after scores. Supplying the new total suppresses rank-ups.
        self.writeVInt(progression.get("previous_highest_trophies", previous_trophies))

        self.writeVInt(5)
        self.writeVInt(player.Trophies - trophy_change)
        self.writeVInt(progression.get("previous_account_highest_trophies", player.Trophies - trophy_change))

        self.writeDataReference(28, 0)
        self.writeBoolean(False)
        self.writeBoolean(False)
        self.writeBoolean(False) # V49 flag at 0xf8
        self.writeVInt(0)
        self.writeVInt(0)
        self.writeBoolean(False)
        self.writeVInt(-1)
        self.writeBoolean(False)
        self.writeVInt(0) # result value at 0xc4
        self.writeBoolean(False)
        self.writeBoolean(False)
        self.writeVInt(0)
        self.writeBoolean(False)
        self.writeBoolean(False)
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
