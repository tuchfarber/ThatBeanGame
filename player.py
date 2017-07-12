class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.fields = []
        self.coins = 0

        # Create 3 fields
        self.fields.append(Field(True))
        self.fields.append(Field(True))
        self.fields.append(Field(False))

class Field:
    def __init__(self, enabled):
        self.cards = []
        self.enabled = enabled