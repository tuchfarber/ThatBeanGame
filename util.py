def shrink(lst):
    if lst:
        return lst[0]
    return []


def get_player(game, token):
    return shrink([player for player in game.players if player.token == token])


def get_game(game_id, games):
    if game_id not in games:
        return None
    return games[game_id]


def error(message):
    return {'error': message}


def success(message):
    return {'success': message}
