import card
import player

class Game:
    def __init__(self):
        self.players = []
        self.id = ""
        self.deck = card.create_deck()
        self.discards = []
        self.current_player = 0

        card.shuffle_deck(self.deck)
    

if __name__ == "__main__":
    game = Game()
    game.players.append(player.Player("John"))
    game.players.append(player.Player("Steve"))
    game.players.append(player.Player("Bill"))
