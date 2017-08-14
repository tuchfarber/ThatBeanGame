from card import Card, Deck, Field
from player import Player
import uuid
import json
import asyncio
import util
from typing import List, Dict, Tuple
from trade import Trade, TradingCard


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
        self.market: List[Card] = []
        self.trades: List[Trade] = []

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
            return util.error('Game has already started')
        if not player.is_host:
            return util.error('Only host can start game')
        self.deal_cards()
        self.status = 'Running'
        return util.success('Successfully started game')

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
        self.market += self.draw_cards(2)
        self.go_next_stage()
        return util.success('Cards drawn into market')

    def add_to_market(self, cards: List[Card]):
        self.market += cards

    def hand_to_field(self, player: Player, field_index: int) -> Dict[str, str]:
        '''
        Plays card from users hand to field. No confirmation.
        '''
        result: Dict = self.play_card(player, field_index, Game.STAGES[:2])
        return result

    def market_to_field(self, player: Player, field_index: int, card_id: int) -> Dict[str, str]:
        '''
        Plays card from market to field. No confirmation.
        '''
        result: Dict = self.play_card(player, field_index, tuple([Game.STAGES[3]]), card_id)
        return result

    def play_card(self, player: Player, field_index: int,
                  valid_stages: Tuple[str, ...], card_id: int=None) -> Dict[str, str]:
        stage_check: Dict[str, str] = self.verify_stage(valid_stages)
        turn_check: Dict[str, str] = self.verify_turn(player)
        field_check: Dict[str, str] = self.verify_field(player, field_index)
        if stage_check or turn_check or field_check:
            return stage_check or turn_check or field_check
        if card_id:
            card: Card = util.shrink([card for card in self.market if card.id == card_id])
        else:
            card = player.hand[0]
        if not card:
            return util.error("Incorrect card id")
        field: Field = player.fields[field_index]
        if not field.add_card(card):
            self.cash_in(field, player, self.discards)
            print(field.add_card(card))
            if card_id:
                self.market = [card for card in self.market if card.id != card_id]
            else:
                player.hand = player.hand[1:]
                self.go_next_stage()
            return util.success('Field cashed in and card successfully played')
        if card_id:
            self.market = [card for card in self.market if card.id != card_id]
        else:
            player.hand = player.hand[1:]
            self.go_next_stage()
        return util.success('Card successfully played')

    def deck_to_hand(self, player: Player) -> Dict[str, str]:
        stage_check: Dict[str, str] = self.verify_stage(tuple([Game.STAGES[3]]))
        turn_check: Dict[str, str] = self.verify_turn(player)
        if stage_check or turn_check:
            return stage_check or turn_check
        if self.market:
            return util.error("Cannot draw cards until market is empty")
        player.hand = player.hand + self.draw_cards(3)
        self.go_next_stage()
        self.go_next_player()
        return util.success('Successfully drew two cards for hand')

    def go_next_stage(self) -> None:
        self.stage_index = (self.stage_index + 1) % len(Game.STAGES)

    def go_next_player(self) -> None:
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def verify_stage(self, allowed_stages: Tuple[str, ...]) -> Dict[str, str]:
        if Game.STAGES[self.stage_index] not in allowed_stages:
            return util.error('Invalid move')
        return None

    def verify_turn(self, player: Player) -> Dict[str, str]:
        if player != self.players[self.current_player_index]:
            return util.error('It is not your turn')
        return None

    def verify_field(self, player: Player, field_index: int) -> Dict[str, str]:
        if field_index not in range(0, len(player.fields)):
            return util.error('Invalid field index')
        if not player.fields[field_index].enabled:
            return util.error('Field not yet bought')
        return None

    def deal_cards(self) -> None:
        for player in self.players:
            for _ in range(5):
                player.hand.append(self.deck.pop())

    def market_to_dict(self) -> List[Dict]:
        return [card.to_dict() for card in self.market]

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

    def ids_to_tcs(self, player: Player, card_ids: List[int]) -> List[TradingCard]:
        '''Call with a player and the ids they want to trade'''
        tcs: List[TradingCard] = []
        market_cards = [card for card in self.market if card.id in  card_ids]
        hand_cards = [card for card in player.hand if card.id in card_ids]
        tcs += [TradingCard(card, self.market) for card in market_cards]
        tcs += [TradingCard(card, player.hand) for card in hand_cards]
        return tcs
    
    def create_trade(self, p1: Player, p2_name: str, card_ids: List[int], wants: List[str]):
        tcs: List[TradingCard] = self.ids_to_tcs(p1, card_ids)
        trade: List[Trade] = []
        if p2_name:
            p2: Player = util.shrink([player for player in self.players if player.name == p2_name])
            trade += [Trade(p1, p2, tcs, wants)]
        else:
            # If p2 is blank, create a global request
            trade += [Trade(p1, _p2, tcs, wants) for _p2 in self.players if _p2 != p1]
        self.trades += trade