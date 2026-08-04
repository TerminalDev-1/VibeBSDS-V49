from Classes.Packets.PiranhaMessage import PiranhaMessage


class PlayerProfileMessage(PiranhaMessage):
    def __init__(self, messageData):
        super().__init__(messageData)
        self.messageVersion = 0

    def encode(self, fields, player):
        self.writeVLong(fields["PlayerHighID"], fields["PlayerLowID"])
        self.writeDataReference(0)
        self.writeVInt(len(player.OwnedBrawlers))
        for brawler_id, brawler in player.OwnedBrawlers.items():
            self.writeDataReference(16, brawler_id)
            self.writeDataReference(0)
            self.writeVInt(brawler["Trophies"])
            self.writeVInt(brawler["HighestTrophies"])
            self.writeVInt(brawler["PowerLevel"])
        
        self.writeVInt(17)

        self.writeVInt(1) 
        self.writeVInt(player.WinCount) # 3v3 victories

        self.writeVInt(2)
        self.writeVInt(player.Experience) # total exp

        self.writeVInt(3)
        self.writeVInt(player.Trophies) # current trophies

        self.writeVInt(4)
        self.writeVInt(player.HighestTrophies) # highest trophies

        self.writeVInt(5) 
        self.writeVInt(len(player.OwnedBrawlers)) # unlocked brawlers

        self.writeVInt(8)
        self.writeVInt(6) # solo victories

        self.writeVInt(11) 
        self.writeVInt(7) # duo victories

        self.writeVInt(9) 
        self.writeVInt(8) # highest level robo rumble

        self.writeVInt(12) 
        self.writeVInt(9) # highest level boss fight

        self.writeVInt(13)
        self.writeVInt(10) # highest power league points

        self.writeVInt(14)
        self.writeVInt(11) # some power league stuff

        self.writeVInt(15)
        self.writeVInt(12) # most challenge win

        self.writeVInt(16) #highest level city rampage
        self.writeVInt(13)

        self.writeVInt(18) #highest solo power league rank
        self.writeVInt(14)

        self.writeVInt(17) #highest team power league rank
        self.writeVInt(15)

        self.writeVInt(19) # highest Club league rank
        self.writeVInt(16)

        self.writeVInt(20) # number fame
        self.writeVInt(player.Fame)

        self.writeString(player.Name)  # PlayerInfo
        self.writeVInt(100)
        self.writeVInt(28000000 + player.Thumbnail)
        self.writeVInt(43000000 + player.Namecolor)
        self.writeVInt(14)

        self.writeBoolean(True)
        self.writeVInt(0)

        self.writeString("VibeBSDS V49 player")
        self.writeVInt(0)
        self.writeVInt(0)

        self.writeBoolean(False) # alliance
        

        self.writeDataReference(25, 1) #alliance role

    def decode(self):
        pass
        # fields = {}
        # fields["PlayerCount"] = self.readVInt()
        # fields["Text"] = self.readString()
        # fields["Unk1"] = self.readVInt()
        # super().decode(fields)
        return {}

    def execute(message, calling_instance, fields):
        pass

    def getMessageType(self):
        return 24113

    def getMessageVersion(self):
        return self.messageVersion
