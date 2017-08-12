import random
from typing import List, Dict, Tuple


class Card:
    """Represents one card in game"""
    MAX_CARDS: int = 24
    MIN_CARDS: int = 0

    def __init__(self, name: str, count: int, values: tuple, img_src: str) -> None:
        self.name: str = name
        self.count: int = count
        self.values: tuple = values
        self.img_src: str = img_src

    def to_dict(self) -> Dict:
        """Returns Card as dictionary"""
        return {
            "name": self.name,
            "count": self.count,
            "values": self.values,
            "img": self.img_src
        }


class Deck:
    """Represents a deck in game. Can be used for draw deck or discard"""

    def __init__(self) -> None:
        self.cards: List[Card] = []

    def build_deck(self) -> None:
        """Builds deck from standard cards"""
        card_types: Tuple[Tuple[str, int, Tuple[int, int, int, int], str], ...] = (
            ("Cocoa Bean", 4, (Card.MAX_CARDS, 2, 3, 4), "assets/beans/cocoa.jpg"),
            ("Garden Bean", 6, (Card.MAX_CARDS, 2, 3, Card.MAX_CARDS), "assets/beans/garden.jpg"),
            ("Red Bean", 8, (2, 3, 4, 5), "assets/beans/red.jpg"),
            ("Black-eyed Bean", 10, (2, 4, 5, 6), "assets/beans/black-eyed.jpg"),
            ("Soy Bean", 12, (2, 4, 6, 7), "assets/beans/soy.jpg"),
            ("Green Bean", 14, (3, 5, 6, 7), "assets/beans/green.jpg"),
            ("Stink Bean", 16, (3, 5, 7, 8), "assets/beans/stink.jpg"),
            ("Chili Bean", 18, (3, 6, 8, 9), "assets/beans/chili.jpg"),
            ("Blue Bean", 20, (4, 5, 8, 10), "assets/beans/blue.jpg"),
            ("Wax Bean", 22, (4, 7, 9, 11), "assets/beans/wax.jpg"),
            ("Coffee Bean", 24, (4, 7, 10, 12), "assets/beans/coffee.jpg")
        )
        for card_type in card_types:
            for _ in range(card_type[1]):
                new_card: Card = Card(*card_type)
                self.cards.append(new_card)

    def pop(self) -> Card:
        card: Card = self.cards[-1]
        self.cards = self.cards[:-1]
        return card

    def shuffle(self) -> None:
        """Shuffles card in deck"""
        random.shuffle(self.cards)

    def get_length(self) -> int:
        """Returns number of cards in deck"""
        return len(self.cards)


class Field:
    """Represents a field in front of a player"""

    def __init__(self, enabled: bool) -> None:
        self.cards: List[Card] = []
        self.enabled: bool = enabled

    def to_dict(self) -> Dict:
        """Returns card as dictionary"""
        name: str = "Empty"
        if self.cards:
            name = self.get_name()
        return {
            "name": name,
            "count": len(self.cards),
            "enabled": self.enabled
        }

    def get_name(self) -> str:
        return self.cards[0].name

    def add_card(self, card: Card) -> bool:
        if card.name != self.get_name():
            return False
        self.cards.append(card)
        return True

    def get_trade_value(self) -> int:
        """Returns coins gained from cashing in cards"""
        try:
            first_card: Card = self.cards[0]
        except IndexError:
            return 0
        value_ranges: Tuple[List[int], ...] = (
            list(range(first_card.values[0], first_card.values[1])),
            list(range(first_card.values[1], first_card.values[2])),
            list(range(first_card.values[2], first_card.values[3])),
            list(range(first_card.values[3], Card.MAX_CARDS))
        )
        for value, value_range in enumerate(value_ranges):
            if len(self.cards) in value_range:
                return value + 1
        return 0
