import card
import player
import uuid

class Game:
    def __init__(self):
        self.players = []
        self.deck = card.create_deck()
        self.discards = []
        self.current_player = 0
        self.id = str(uuid.uuid4())[:6]

        card.shuffle_deck(self.deck)
        return self.id

if __name__ == "__main__":
    game = Game()
    game.players.append(player.Player("John"))
    game.players.append(player.Player("Steve"))
    game.players.append(player.Player("Bill"))

