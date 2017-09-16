from typing import List, Dict, Tuple

STAGES: Tuple[str, ...] = (
    'First Card',
    'Second Card',
    'Pre Market Flip',
    'Post Market Flip'
)
MAX_PLAYERS: int = 7
MAX_CARDS: int = 24
MIN_CARDS: int = 0
CARD_TYPES: Tuple[Tuple[str, int, Tuple[int, int, int, int], str], ...] = (
    ("Cocoa Bean", 4, (MAX_CARDS, 2, 3, 4), "assets/beans/cocoa.png"),
    ("Garden Bean", 6, (MAX_CARDS, 2, 3, MAX_CARDS), "assets/beans/garden.png"),
    ("Red Bean", 8, (2, 3, 4, 5), "assets/beans/red.png"),
    ("Black Bean", 10, (2, 4, 5, 6), "assets/beans/black.png"),
    ("Soy Bean", 12, (2, 4, 6, 7), "assets/beans/soy.png"),
    ("Green Bean", 14, (3, 5, 6, 7), "assets/beans/green.png"),
    ("Stink Bean", 16, (3, 5, 7, 8), "assets/beans/stink.png"),
    ("Chili Bean", 18, (3, 6, 8, 9), "assets/beans/chili.png"),
    ("Blue Bean", 20, (4, 5, 8, 10), "assets/beans/blue.png"),
    ("Wax Bean", 22, (4, 7, 9, 11), "assets/beans/wax.png"),
    ("Coffee Bean", 24, (4, 7, 10, 12), "assets/beans/coffee.png")
)