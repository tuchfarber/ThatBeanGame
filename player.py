from card import Field
import uuid
class Player:
    """Represents a player in the game"""
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.fields = []
        self.coins = 0
        self.is_host = False
        self.token = str(uuid.uuid4())

        # Create 3 fields
        self.fields.append(Field(True))
        self.fields.append(Field(True))
        self.fields.append(Field(False))

    def get_first_card(self):
        """Removes first card from hand and returns it"""
        first_card = self.hand[0]
        self.hand = self.hand[1:]
        return first_card

    def to_dict_public(self):
        """Returns all public knowledge as dictionary"""
        return {
            "name": self.name,
            "hand_count": len(self.hand),
            "fields": [field.to_dict() for field in self.fields],
            "coins": self.coins,
            "is_host": self.is_host
        }

    def to_dict_private(self):
        """Returns all private knowledge as dictionary"""
        knowledge = self.to_dict_public()
        knowledge["hand"] = [card.to_dict() for card in self.hand]
        return knowledge
