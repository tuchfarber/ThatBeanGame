from typing import List, Dict

def shrink(lst: List):
    if lst:
        return lst[0]
    return []


def get_player(game, token: str):
    return shrink([player for player in game.players if player.token == token])


def get_game(game_id: str, games: Dict):
    if game_id not in games:
        return None
    return games[game_id]


def error(message: str) -> Dict[str, str]:
    return {'error': message}


def success(message: str) -> Dict[str, str]:
    return {'success': message}
