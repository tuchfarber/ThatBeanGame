from card import Card, Deck, Field
from player import Player
import uuid
import json
import asyncio
from util import error, success
from typing import List, Dict, Tuple


class Game:
    STAGES: Tuple[str, ...] = (
        'First Card',
        'Second Card',
        'Pre Market Flip',
        'Post Market Flip'
    )
    MAX_PLAYERS: int = 7

    def __init__(self) -> None:
        self.players: List[Player] = []
        self.deck: Deck = Deck()
        self.playthrough: int = 0
        self.discards: Deck = Deck()
        self.current_player_index: int = 0
        self.status: str = 'Awaiting'  # Awaiting, Running, Completed
        self.id: str = str(uuid.uuid4())[:6]
        self.stage_index: int = 0
        self.market: Dict[int, Card] = {0: None, 1: None}

        self.deck.build_deck()
        self.deck.shuffle()

    def add_player(self, player: Player) -> None:
        # First player is host
        if not self.players:
            player.is_host = True
        self.players.append(player)

    def is_full(self) -> bool:
        if len(self.players) < Game.MAX_PLAYERS:
            return False
        return True

    def start_game(self, player: Player) -> Dict[str, str]:
        if self.status != 'Awaiting':
            return error('Game has already started')
        if not player.is_host:
            return error('Only host can start game')
        self.deal_cards()
        self.status = 'Running'
        return success('Successfully started game')

    def retrieve_game(self, player: Player) -> Dict:
        return {
            'player_info': player.to_dict_private(),
            'players': [other_player.to_dict_public() for other_player in self.players],
            'deck_count': self.deck.get_length(),
            'playthrough': self.playthrough,
            'discard_count': self.discards.get_length(),
            'current_player': self.players[self.current_player_index].name,
            'status': self.status,
            'game_id': self.id,
            'stage': Game.STAGES[self.stage_index],
            'market': self.market_to_dict()
        }

    def deck_to_market(self, player: Player) -> Dict[str, str]:
        '''Draws top 2 cards from deck and places them in market'''
        stage_check: Dict = self.verify_stage(Game.STAGES[1:3])
        turn_check: Dict = self.verify_turn(player)
        if stage_check or turn_check:
            return stage_check or turn_check
        self.add_to_market([self.deck.pop(), self.deck.pop()])
        self.go_next_stage()
        return success('Cards drawn into market')

    def add_to_market(self, cards: List[Card]):
        self.market[0] = cards[0]
        self.market[1] = cards[1]

    def hand_to_field(self, player: Player, field_index: int) -> Dict[str, str]:
        '''
        Plays card from users hand to field. No confirmation.
        '''
        result: Dict = self.play_card(player, field_index, Game.STAGES[:2])
        return result

    def market_to_field(self, player: Player, field_index: int, market_index: int) -> Dict[str, str]:
        '''
        Plays card from market to field. No confirmation.
        '''
        result: Dict = self.play_card(player, field_index, tuple([Game.STAGES[3]]), market_index)
        return result

    def play_card(self, player: Player, field_index: int,
                  valid_stages: Tuple[str, ...], market_index: int=None) -> Dict[str, str]:
        stage_check: Dict[str, str] = self.verify_stage(valid_stages)
        turn_check: Dict[str, str] = self.verify_turn(player)
        field_check: Dict[str, str] = self.verify_field(player, field_index)
        if stage_check or turn_check or field_check:
            return stage_check or turn_check or field_check
        card: Card = self.market[market_index] if market_index is not None else player.hand[0]
        if not card:
            return error("No card in that spot")
        field: Field = player.fields[field_index]
        if not field.add_card(card):
            self.cash_in(field, player, self.discards)
            print(field.add_card(card))
            if market_index is not None:
                self.market[market_index] = None
            else:
                player.hand = player.hand[1:]
                self.go_next_stage()
            return success('Field cashed in and card successfully played')
        if market_index is not None:
            self.market[market_index] = None
        else:
            player.hand = player.hand[1:]
            self.go_next_stage()
        return success('Card successfully played')

    def deck_to_hand(self, player: Player) -> Dict[str, str]:
        stage_check: Dict[str, str] = self.verify_stage(tuple([Game.STAGES[3]]))
        turn_check: Dict[str, str] = self.verify_turn(player)
        if stage_check or turn_check:
            return stage_check or turn_check
        if self.market[0] or self.market[1]:
            return error("Cannot draw cards until market is empty")
        for _ in range(2):
            player.hand.append(self.deck.pop())
        self.go_next_stage()
        self.go_next_player()
        return success('Successfully drew two cards for hand')

    def go_next_stage(self) -> None:
        self.stage_index = (self.stage_index + 1) % len(Game.STAGES)

    def go_next_player(self) -> None:
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def verify_stage(self, allowed_stages: Tuple[str, ...]) -> Dict[str, str]:
        if Game.STAGES[self.stage_index] not in allowed_stages:
            return error('Invalid move')
        return None

    def verify_turn(self, player: Player) -> Dict[str, str]:
        if player != self.players[self.current_player_index]:
            return error('It is not your turn')
        return None

    def verify_field(self, player: Player, field_index: int) -> Dict[str, str]:
        if field_index not in range(0, len(player.fields)):
            return error('Invalid field index')
        if not player.fields[field_index].enabled:
            return error('Field not yet bought')
        return None

    def deal_cards(self) -> None:
        for player in self.players:
            for _ in range(5):
                player.hand.append(self.deck.pop())

    def market_to_dict(self) -> Dict:
        obj: Dict[int, Dict] = {0: None, 1: None}
        if self.market[0]:
            obj[0] = self.market[0].to_dict()
        if self.market[1]:
            obj[1] = self.market[1].to_dict()
        return obj

    def cash_in_field(self, player: Player, field: Field):
        value: int = field.get_trade_value()
        player.coins += value
        field.cards = field.cards[:-value]
        for card in field.cards:
            self.discards.cards.append(card)
        field.cards = []

    def cash_in(self, field: Field, player: Player, discards: Deck) -> None:
        '''Adds coins to player and clears field'''
        value: int = field.get_trade_value()
        player.coins += value
        field.cards = field.cards[:-value]
        for card in field.cards:
            discards.cards.append(card)
        field.cards = []

    def draw_cards(self, card_count: int) -> List[Card]:
        '''Draws card for user and shuffles if necessary'''
        cards: List[Card] = []
        for i in range(card_count):
            if self.deck.get_length() == 0:
                if self.playthrough == 2:
                    self.end_game()
                    return None
                self.playthrough += 1
                self.deck.cards = self.discards.take_all()
                self.deck.shuffle()
            cards.append(self.deck.pop())
        return cards 

    def end_game(self):
        '''End the game'''
        pass
            