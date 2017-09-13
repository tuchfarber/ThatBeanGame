from card import Field, Card
import uuid
from typing import Dict, List, Optional


class Player:
    '''Represents a player in the game'''

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.hand: List[Card] = []
        self.fields: List[Field] = []
        self.coins: int = 0
        self.is_host: bool = False
        self.token: str = str(uuid.uuid4())
        self.pending_cards: List[Card] = []
        self.socket_sid: str = ""
        self.last_update: Dict = {}

        # Create 3 fields
        self.fields.append(Field(True))
        self.fields.append(Field(True))
        self.fields.append(Field(False))

    def get_first_card(self) -> Card:
        '''Removes first card from hand and returns it'''
        first_card: Card = self.hand[0]
        self.hand = self.hand[1:]
        return first_card

    def to_dict_public(self) -> Dict:
        '''Returns all public knowledge as dictionary'''
        return {
            "name": self.name,
            "hand_count": len(self.hand),
            "fields": [field.to_dict() for field in self.fields],
            "coins": self.coins,
            "is_host": self.is_host
        }

    def to_dict_private(self) -> Dict:
        '''Returns all private knowledge as dictionary'''
        knowledge: Dict = self.to_dict_public()
        knowledge["hand"] = [card.to_dict() for card in self.hand]
        knowledge["pending_cards"] = [card.to_dict() for card in self.pending_cards]
        return knowledge
