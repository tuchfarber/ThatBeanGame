import random
from typing import List, Dict, Tuple
import uuid
import constants


class Card:
    '''Represents one card in game'''

    def __init__(self, name: str, count: int, values: tuple, img_src: str) -> None:
        self.name: str = name
        self.count: int = count
        self.values: tuple = values
        self.img_src: str = img_src
        self.id: str = str(uuid.uuid4())[:6]

    def to_dict(self) -> Dict:
        '''Returns Card as dictionary'''
        return {
            "name": self.name,
            "count": self.count,
            "values": [val if val != 24 else 0 for val in self.values],
            "img": self.img_src,
            "id": self.id
        }
    


class Deck:
    '''Represents a deck in game. Can be used for draw deck or discard'''

    def __init__(self) -> None:
        self.cards: List[Card] = []

    def build_deck(self) -> None:
        '''Builds deck from standard cards'''
        for card_type in constants.CARD_TYPES:
            for _ in range(card_type[1]):
                new_card: Card = Card(*card_type)
                self.cards.append(new_card)

    def pop(self) -> Card:
        card: Card = self.cards[-1]
        self.cards = self.cards[:-1]
        return card

    def shuffle(self) -> None:
        '''Shuffles card in deck'''
        random.shuffle(self.cards)

    def get_length(self) -> int:
        '''Returns number of cards in deck'''
        return len(self.cards)

    def take_all(self) -> List[Card]:
        '''Removes card from deck and returns them'''
        all_cards: List[Card] = [card for card in self.cards]
        self.cards = []
        return all_cards


class Field:
    '''Represents a field in front of a player'''

    def __init__(self, enabled: bool) -> None:
        self.cards: List[Card] = []
        self.enabled: bool = enabled

    def to_dict(self) -> Dict:
        '''Returns card as dictionary'''
        return {
            "name": self.name,
            "img": self.image,
            "values": self.values,
            "count": len(self.cards),
            "enabled": self.enabled
        }

    @property
    def name(self) -> str:
        try:
            name = self.cards[0].name
        except IndexError:
            name = 'Empty'
        return name

    @property
    def image(self) -> str:
        try:
            img = self.cards[0].img_src
        except IndexError:
            img = ''
        return img

    @property
    def values(self) -> Tuple:
        try:
            values = self.cards[0].values
        except IndexError:
            values = ()
        return values

    def add_card(self, card: Card) -> bool:
        if card.name != self.name and self.name != 'Empty':
            return False
        self.cards.append(card)
        return True

    def get_trade_value(self) -> int:
        '''Returns coins gained from cashing in cards'''
        try:
            first_card: Card = self.cards[0]
        except IndexError:
            return 0
        value_ranges: Tuple[List[int], ...] = (
            list(range(first_card.values[0], first_card.values[1])),
            list(range(first_card.values[1], first_card.values[2])),
            list(range(first_card.values[2], first_card.values[3])),
            list(range(first_card.values[3], constants.MAX_CARDS))
        )
        for value, value_range in enumerate(value_ranges):
            if len(self.cards) in value_range:
                return value + 1
        return 0
