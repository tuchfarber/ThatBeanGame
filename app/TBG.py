from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
from bottle import request, Bottle, abort, response, route, post, run, static_file
import json
from typing import Dict, List

from player import Player
from game import Game, GAME_TYPES
import util

app = Bottle()

games: Dict[str, Game] = {}
clients: Dict[str, str] = {}


def check_valid_request(f):
    '''Decorator. Verifies game exists and client is authorized. Returns game and client'''
    def wrapper(*args, **kwargs):
        try:
            game: Game = games[kwargs['game_id']]
        except KeyError:
            abort(400, util.error('Game does not exist'))

        try:
            player: Player = [player for player in game.players if player.token == request.get_cookie('tbg_token')][0]
        except IndexError:
            abort(400, util.error('Not authorized to view game'))

        return f(game, player)
    return wrapper


def error_check(result: Dict) -> Dict:
    '''Aborts with 400 if result is error'''
    if result.get('error'):
        abort(400, result)
    return result


@app.error(400)
def error400(err):
    return err.body


@app.hook('after_request')
def enable_cors():
    '''Verifies server responds to all requests'''
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, user-agent'


@app.route('/<:re:.*>', method='OPTIONS')
def enable_options():
    '''Enables clients to receive okay from OPTIONS request'''
    return

@app.route('/api/access', method='GET')
def access() -> Dict:
    '''
    Checks if request has a cookie of a logged in user. If cookie exists it
    sends user their game info. If not, it takes them to the login page.
    '''
    cookie: str = request.get_cookie('tbg_token')
    try:
        game_id: str = clients[cookie]
    except KeyError:
        abort(400, util.error('Access denied'))
    if games[game_id].status == 'Completed':
        abort(400, util.error('Game already completed'))
    return {'game': game_id}


@app.route('/api/login', method='POST')
def login() -> Dict:
    '''
    Adds user to the requested game as long as game isn't full or already started,
    game exists, and user name isn't already used in game.
    '''

    try:
        name: str = request.json['name']
        game_id: str = request.json['game']
    except KeyError:
        abort(400, util.error('Incorrect JSON data'))

    # Get first public game
    game: Game = util.shrink([games[game_id] for game_id in games if games[game_id].game_type == 'public'])

    # If game game_id isn't a blank string, use that game
    if game_id in games:
        game = games[game_id]

    if name in [player.name for player in game.players]:
        abort(400, util.error('User already exists with that name'))
    if game.status != 'Awaiting':
        abort(400, util.error('Game has already started or ended'))
    if game.is_full():
        abort(400, util.error('Game is full'))

    player: Player = Player(name)
    game.add_player(player)
    response.set_cookie('tbg_token', player.token, max_age=400)
    clients[player.token] = game_id
    return util.success('Successfully logged into game')

@app.route('/api/create', method='POST')
def create_new_game() -> Dict:
    '''Creates new player and game, returns game id'''
    try:
        player: Player = Player(request.json['name'])
    except KeyError:
        abort(400, util.error('Name not supplied'))

    try:
        if not request.json['game_type'] in GAME_TYPES:
            abort(400, util.error('Invalid game type parameter'))
        game_type: str = request.json['game_type']
    except KeyError:
        abort(400, util.error('Game type not supplied'))

    game: Game = Game(game_type)
    game.add_player(player)
    games[game.id] = game
    clients[player.token] = game.id
    response.set_cookie('tbg_token', player.token, max_age=400)
    return {'game': game.id}

@app.route('/api/game/<game_id>', method='GET')
@check_valid_request
def game_status(game: Game, player: Player) -> Dict:
    '''Returns all game info'''
    result: Dict = game.retrieve_game(player)
    error_check(result)
    return result


@app.route('/api/game/<game_id>/start', method='POST')
@check_valid_request
def start_game(game: Game, player: Player) -> Dict:
    '''Starts requested game if user is host'''
    result: Dict = game.start_game(player)
    error_check(result)
    return result


@app.route('/api/game/<game_id>/play/hand', method='POST')
@check_valid_request
def play_card_from_hand(game: Game, player: Player) -> Dict:
    '''Plays top card from hand to field specified'''
    try:
        field_index: int = request.json['field_index']
    except KeyError:
        abort(400, util.error('Incorrect JSON data'))
    result: Dict = game.hand_to_field(player, field_index)
    error_check(result)
    return result


@app.route('/api/game/<game_id>/play/market', method='POST')
@check_valid_request
def play_card_from_market(game: Game, player: Player) -> Dict:
    '''Places card from market into field'''
    try:
        field_index: int = request.json['field_index']
        card_id: str = request.json['card_id']
    except KeyError:
        abort(400, util.error('Incorrect JSON data'))
    result: Dict = game.market_to_field(player, field_index, card_id)
    error_check(result)
    return result

@app.route('/api/game/<game_id>/play/pending', method='POST')
@check_valid_request
def play_card_from_pending(game: Game, player: Player) -> Dict:
    '''Places card from market into field'''
    try:
        card_id: str = request.json['card_id']
        field_index: int = request.json['field_index']
    except KeyError:
        abort(400, util.error('Incorrect JSON data'))
    result: Dict = game.pending_to_field(player, field_index, card_id)
    error_check(result)
    return result


@app.route('/api/game/<game_id>/draw/market', method='POST')
@check_valid_request
def draw_for_market(game: Game, player: Player) -> Dict:
    '''Draws two cards and places them in market'''
    result: Dict = game.deck_to_market(player)
    error_check(result)
    return result


@app.route('/api/game/<game_id>/draw/hand', method='POST')
@check_valid_request
def draw_for_hand(game: Game, player: Player) -> Dict:
    '''Draws three cards and places them in players hand'''
    result: Dict = game.deck_to_hand(player)
    error_check(result)
    return result

@app.route('/api/game/<game_id>/trade/create', method='POST')
@check_valid_request
def create_trade(game: Game, player: Player) -> Dict:
    '''Creates new trade'''
    try:
        card_ids: List[str] = request.json['card_ids']
        other_player_name: str = request.json['other_player']
        wants: List[str] = request.json['wants'] # List of card names
    except KeyError:
        abort(400, util.error('Incorrect JSON data'))

    result = game.create_trade(player, other_player_name, card_ids, wants)
    error_check(result)
    return result

@app.route('/api/game/<game_id>/trade/accept', method='POST')
@check_valid_request
def accept_trade(game: Game, player: Player) -> Dict:
    '''Accepts a trade'''
    try:
        trade_id: str = request.json['trade_id']
        card_ids: List[str] = request.json['card_ids']
    except KeyError:
        abort(400, util.error('Incorrect JSON data'))
    result = game.accept_trade(player, trade_id, card_ids)
    error_check(result)
    return result

@app.route('/api/game/<game_id>/trade/reject', method='POST')
@check_valid_request
def reject_trade(game: Game, player: Player) -> Dict:
    '''Rejects a trade'''
    try:
        trade_id: str = request.json['trade_id']
    except KeyError:
        abort(400, util.error('Incorrect JSON data'))
    result = game.reject_trade(player, trade_id)
    error_check(result)
    return result

@app.route('/', method='GET')
def index():
    '''Returns webpage'''
    return static_file('tbg.html', './app/static')

@app.route('/<filename:path>', method='GET')
def static_assets(filename):
    print(filename)
    '''Returns asset'''
    return static_file(filename, './app/static')

print("Server starting...")
server = WSGIServer(('0.0.0.0', 8080), app, handler_class=WebSocketHandler)
server.serve_forever()
