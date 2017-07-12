import random

class Card:
    MAX_CARDS = 24
    MIN_CARDS = 0
    def __init__(self, name, count, values, img_src):
        self.name = name
        self.count = count
        self.values = values
        self.img_src = img_src
    
    def get_trade_value(self, amount):
        value_ranges = (
            list(range(self.values[0], self.values[1])),
            list(range(self.values[1], self.values[2])),
            list(range(self.values[2], self.values[3])),
            list(range(self.values[3], Card.MAX_CARDS))
        )
        for value, value_range in enumerate(value_ranges):
            if amount in value_range:
                return value + 1
        return 0

def create_deck():
    card_types = (
        ("Cocoa Bean", 4, (Card.MAX_CARDS, 2, 3, 4), "assets/beans/cocoa.jpg"),
        ("Garden Bean", 6, (Card.MAX_CARDS, 2, 3, Card.MAX_CARDS), "assets/beans/garden.jpg"),
        ("Red Bean", 8, (2, 3, 4, 5), "assets/beans/red.jpg"),
        ("Black-eyed Bean", 10, (2, 4, 5, 6), "assets/beans/black-eyed.jpg"),
        ("Soy Bean", 12, (2, 4, 6, 7), "assets/beans/soy.jpg"),
        ("Grean Bean", 14, (3, 5, 6, 7), "assets/beans/green.jpg"),
        ("Stink Bean", 16, (3, 5, 7, 8), "assets/beans/stink.jpg"),
        ("Chili Bean", 18, (3, 6, 8, 9), "assets/beans/chili.jpg"),
        ("Blue Bean", 20, (4, 5, 8, 10), "assets/beans/blue.jpg"),
        ("Wax Bean", 22, (4, 7, 9, 11), "assets/beans/wax.jpg"),
        ("Coffee Bean", 24, (4, 7, 10, 12), "assets/beans/coffee.jpg")
    )
    deck = []
    for card_type in card_types:
        for i in range(card_type[1]):
            new_card = Card(*card_type)
            deck.append(new_card)
    return deck

def shuffle_deck(deck):
    random.shuffle(deck)
    
