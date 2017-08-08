from card import Card, Deck
import uuid
import json
import asyncio

class Game:
    STAGES = (
        "First Card",
        "Second Card",
        "Open Market"
    )
    MAX_PLAYERS = 7
    
    def __init__(self):
        self.players = []
        self.deck = Deck()
        self.playthrough = 0
        self.discards = Deck()
        self.current_player_index = 0
        self.status = "Awaiting" # Awaiting, Running, Completed
        self.id = str(uuid.uuid4())[:6]
        self.stage_index = 0
        self.market = {'0': None, '1': None}

        self.deck.build_deck()
        self.deck.shuffle()

    def add_player(self, player):
        # First player is host
        if not self.players:
            player.is_host = True
        self.players.append(player)
    
    def is_full(self):
        if len(self.players) < Game.MAX_PLAYERS:
            return False
        return True
    
    def start_game(self, player):
        if self.status != "Awaiting":
            return {'status':'error', 'message':'Game has already started'}
        if not player.is_host:
            return {'status':'error', 'message':'Only host can start game'}
        self.deal_cards()
        self.status = "Running"
        return {'status':'success'}

    def retrieve_game(self, player):
        return {
            "player_info": player.to_dict_private(),
            "players": [other_player.to_dict_public() for other_player in self.players],
            "deck_count": self.deck.get_length(),
            "playthrough": self.playthrough,
            "discard_count": self.discards.get_length(),
            "current_player": self.players[self.current_player_index].name,
            "status": self.status,
            "game_id": self.id,
            "stage": Game.STAGES[self.stage_index]
        }


    
    def deck_to_market(self):
        self.add_to_market([self.deck.pop(), self.deck.pop()])
        return {'status':'success', 'message': 'Cards drawn into market'}

    def add_to_market(self, cards):
        self.market['0'] = cards[0]
        self.market['1'] = cards[1]

    def hand_to_field(self, player, field_index):
        """
        Plays card from users hand to field. No confirmation.
        """
        result = self.play_card(player, field_index, Game.STAGES[:2], market_index)
        return result
        return {'status':'success', 'message': 'Card successfully played'}
    
    def market_to_field(self, player, field_index, market_index):
        """
        Plays card from market to field. No confirmation.
        """
        result = self.play_card(player, field_index, [Game.STAGES[2]], market_index)
        return result

    def play_card(self, player, field_index, valid_stages, market_index=None):
        stage_check = self.verify_stage([Game.STAGES[:2]])
        turn_check = self.verify_turn(player)
        field_check = self.verify_field(player, field_index)
        if stage_check or turn_check or field_check:
            return stage_check or turn_check or field_check

        if market_index:
            card = self.market[market_index]
        else:
            card = player.hand[0]

        field = player.fields[field_index]
        if not field.add_card(card):
            field.cash_in(player, self.discards)
            field.add_card(card)
            if market_index:
                self.market[market_index] = None
            else:
                player.hand = player.hand[1:]
                self.go_next_stage()
            return {'status':'success', 'message': 'Field cashed in and card successfully played'}
        if market_index:
            self.market[market_index] = None
        else:
            player.hand = player.hand[1:]
            self.go_next_stage()
        return {'status':'success', 'message': 'Card successfully played'}
    
    def deck_to_hand(self, player):
        stage_check = self.verify_stage([Game.STAGES[2]])
        turn_check = self.verify_turn(player)
        if stage_check or turn_check:
            return stage_check or turn_check

        for _ in range(2):
            player.hand.append(self.deck.pop())
        self.go_next_stage()
        self.go_next_player()
        return {'status':'success', 'message': 'Successfully drew two cards for hand'}

    def trade_from_market(self, params):
        pass

    def trade_from_hand(self, params):
        pass

    def trade_accept(self, params):
        pass
        
    def go_next_stage(self):
        self.stage_index = (self.stage_index + 1) % len(Game.STAGES)

    def go_next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def verify_stage(self, allowed_stages):
        if Game.STAGES[self.stage_index] not in allowed_stages:
            return {'status':'error', 'message': 'Invalid move'}

    def verify_turn(self, player):
        if player != self.players[self.current_player_index]:
            return {'status':'error', 'message': 'It is not your turn'}

    def verify_field(self, player, field_index):
        if field_index in range(0,len(player.fields)):
            return {'status':'error', 'message': 'Invalid field index'}
        if not player.fields[field_index].enabled:
            return {'status':'error', 'message': 'Field not yet bought'}
    
    def deal_cards(self):
        for player in self.players:
            for _ in range(5):
                player.hand.append(self.deck.pop())

    def get_updates(self):
        return