from typing import List, Dict
import uuid
import util
from player import Player
from card import Card

class TradingCard:
    def __init__(self, card: Card, location: List[Card], location_desc: str) -> None:
        self.card: Card = card
        self.location: List[Card] = location
        self.location_desc: str = location_desc
    
    def remove_from_location(self):
        safe_cards = [card for card in self.location if card.id != self.card.id]
        self.location.clear()
        for card in safe_cards:
            self.location.append(card)
    
    def to_dict(self):
        return {"card": self.card.to_dict(), 'location': self.location_desc}

class Trade:
    '''Represents a trade between two players'''
    def __init__(self, p1: Player, p2: Player, p1_trades: List[TradingCard], wants: List[str]) -> None:
        self.id: str = str(uuid.uuid4())[:6] 
        self.p1: Player = p1
        self.p2: Player = p2
        self.p1_trades: List[TradingCard] = p1_trades
        self.p2_trades: List[TradingCard] = []
        self.wants: List[str] = wants

    def accept(self, p2_trades: List[TradingCard]) -> Dict:
        self.p2_trades = p2_trades
        if sorted(self.wants) != sorted([tc.card.name for tc in p2_trades]):
            return util.error("Did not send cards requested")
        # Add cards to temporary pending
        p1_pending: List[Card] = [tc.card for tc in self.p2_trades]
        p2_pending: List[Card] = [tc.card for tc in self.p1_trades]
        # Remove cards from location
        [tc.remove_from_location() for tc in self.p1_trades + self.p2_trades]
        # Add cards to actual pending
        self.p1.pending_cards += p1_pending
        self.p2.pending_cards += p2_pending
        return util.success("Successfully traded cards")
    
    def to_public_dict(self) -> Dict:
        return {
            "id": self.id,
            "player_1": self.p1.name,
            "player_2": self.p2.name,
            "p1_wants": self.wants,
            "p1_has": [str(tc.card.name) for tc in self.p1_trades],
            "p1_trades": [tc.to_dict() for tc in self.p1_trades],
            "p2_trades": [tc.to_dict() for tc in self.p2_trades]
        }

