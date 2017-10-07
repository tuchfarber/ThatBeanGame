from functools import wraps
import json
from json.decoder import JSONDecodeError
from typing import Dict, List
import os
from time import sleep
from flask import Flask, request, abort, jsonify, make_response
import jsonpatch
from flask_socketio import SocketIO, join_room

from player import Player
from game import Game
import util

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

games: Dict[str, Game] = {}
clients: Dict[str, str] = {}

if 'TBG_CLIENT_ORIGIN' in os.environ:
    CLIENT_ORIGIN = os.environ['TBG_CLIENT_ORIGIN']

@socketio.on('login')
def on_login(login_info):
    try:
        game: Game = games[login_info['game']]
        player: Player = [player for player in game.players if player.token == login_info['token']][0]
    except KeyError:
        socketio.emit('error', 'Socket connection must start with sending of token (cookie) and game (id) in JSON format')
        return
    except IndexError:
        socketio.emit('error', 'User does not exist')
        return
    player.socket_sid = request.sid
    socketio.emit('client full', json.dumps(game.retrieve_game(player)), room=player.socket_sid)

def check_valid_request(f):
    '''Decorator. Verifies game exists and client is authorized. Returns game and client'''
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            game: Game = games[kwargs['game_id']]
        except KeyError:
            abort(400, util.error('Game does not exist'))

        try:
            player: Player = [player for player in game.players if player.token == request.cookies.get('tbg_token')][0]
        except IndexError:
            abort(400, util.error('Not authorized to view game'))

        return f(game, player)
    return wrapper

def update_client(game):
    for player in game.players:
        update = game.retrieve_game(player)
        patch = jsonpatch.make_patch(player.last_update, update)
        socketio.emit('client update', patch.to_string(), room=player.socket_sid)
        player.last_update = update

def error_check(result: Dict) -> Dict:
    '''Aborts with 400 if result is error'''
    if result.get('error'):
        abort(400, result)
    return result


@app.errorhandler(400)
def error400(err):
    return jsonify(err.description), 400


@app.after_request
def enable_cors(response):
    '''Verifies server responds to all requests'''
    
    if CLIENT_ORIGIN:
        response.headers['Access-Control-Allow-Origin'] = CLIENT_ORIGIN
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, user-agent'
    return response

@app.route('/api/access', methods=['GET'])
def access() -> Dict:
    '''
    Checks if request has a cookie of a logged in user. If cookie exists it
    sends user their game info. If not, it takes them to the login page.
    '''
    cookie: str = request.cookies.get('tbg_token')
    try:
        game_id: str = clients[cookie]
    except KeyError:
        abort(400, util.error('Access denied'))
    if games[game_id].status == 'Completed':
        abort(400, util.error('Game already completed'))
    player: Player = util.shrink([player for player in games[game_id].players if player.token == request.cookies.get('tbg_token')])
    return jsonify({'game': game_id, "player_name": player.name})


@app.route('/api/login', methods=['POST'])
def login() -> Dict:
    '''
    Adds user to the requested game as long as game isn't full or already started,
    game exists, and user name isn't already used in game.
    '''
    post_data: Dict = request.get_json()
    try:
        name: str = post_data['name']
        game_id: str = post_data['game']
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
    clients[player.token] = game_id
    response = make_response(jsonify(util.success('Successfully logged into game')))
    response.set_cookie('tbg_token', player.token, max_age=6000, domain="")
    update_client(game)
    return response

@app.route('/api/create', methods=['POST'])
def create_new_game():
    '''Creates new player and game, returns game id'''
    post_data: Dict = request.get_json()
    try:
        player: Player = Player(post_data['name'])
    except KeyError:
        abort(400, util.error('Name not supplied'))
    
    try:
        game_type: str = post_data['game_type']
    except KeyError:
        abort(400, util.error('Game type not supplied'))
    if game_type not in ('public', 'private'):
        abort(400, util.error('Invalid game type parameter'))

    game: Game = Game(game_type)
    game.add_player(player)
    games[game.id] = game
    clients[player.token] = game.id
    response = make_response(jsonify({'game': game.id}))
    response.set_cookie('tbg_token', player.token, max_age=6000)
    return response

@app.route('/api/game/<game_id>', methods=['GET'])
@check_valid_request
def game_status(game: Game, player: Player) -> Dict:
    '''Returns all game info'''
    result: Dict = game.retrieve_game(player)
    error_check(result)
    return jsonify(result)


@app.route('/api/game/<game_id>/start', methods=['POST'])
@check_valid_request
def start_game(game: Game, player: Player) -> Dict:
    '''Starts requested game if user is host'''
    result: Dict = game.start_game(player)
    error_check(result)
    update_client(game)
    return jsonify(result)


@app.route('/api/game/<game_id>/play/hand', methods=['POST'])
@check_valid_request
def play_card_from_hand(game: Game, player: Player) -> Dict:
    '''Plays top card from hand to field specified'''
    post_data: Dict = request.get_json()
    try:
        field_index: int = post_data['field_index']
    except KeyError:
        abort(400, util.error('Incorrect JSON data'))
    result: Dict = game.hand_to_field(player, field_index)
    error_check(result)
    update_client(game)
    return jsonify(result)


@app.route('/api/game/<game_id>/play/market', methods=['POST'])
@check_valid_request
def play_card_from_market(game: Game, player: Player) -> Dict:
    '''Places card from market into field'''
    post_data: Dict = request.get_json()
    try:
        field_index: int = post_data['field_index']
        card_id: str = post_data['card_id']
    except KeyError:
        abort(400, util.error('Incorrect JSON data'))
    result: Dict = game.market_to_field(player, field_index, card_id)
    error_check(result)
    update_client(game)
    return jsonify(result)

@app.route('/api/game/<game_id>/play/pending', methods=['POST'])
@check_valid_request
def play_card_from_pending(game: Game, player: Player) -> Dict:
    '''Places card from market into field'''
    post_data: Dict = request.get_json()
    try:
        card_id: str = post_data['card_id']
        field_index: int = post_data['field_index']
    except KeyError:
        abort(400, util.error('Incorrect JSON data'))
    result: Dict = game.pending_to_field(player, field_index, card_id)
    error_check(result)
    update_client(game)
    return jsonify(result)


@app.route('/api/game/<game_id>/draw/market', methods=['POST'])
@check_valid_request
def draw_for_market(game: Game, player: Player) -> Dict:
    '''Draws two cards and places them in market'''
    result: Dict = game.deck_to_market(player)
    error_check(result)
    update_client(game)
    return jsonify(result)


@app.route('/api/game/<game_id>/draw/hand', methods=['POST'])
@check_valid_request
def draw_for_hand(game: Game, player: Player) -> Dict:
    '''Draws three cards and places them in players hand'''
    result: Dict = game.deck_to_hand(player)
    error_check(result)
    update_client(game)
    return jsonify(result)

@app.route('/api/game/<game_id>/trade/create', methods=['POST'])
@check_valid_request
def create_trade(game: Game, player: Player) -> Dict:
    '''Creates new trade'''
    post_data: Dict = request.get_json()
    try:
        card_ids: List[str] = post_data['card_ids']
        other_player_name: str = post_data['other_player']
        wants: List[str] = post_data['wants'] # List of card names
    except KeyError:
        abort(400, util.error('Incorrect JSON data'))

    result = game.create_trade(player, other_player_name, card_ids, wants)
    error_check(result)
    update_client(game)
    return jsonify(result)

@app.route('/api/game/<game_id>/trade/accept', methods=['POST'])
@check_valid_request
def accept_trade(game: Game, player: Player) -> Dict:
    '''Accepts a trade'''
    post_data: Dict = request.get_json()
    try:
        trade_id: str = post_data['trade_id']
        card_ids: List[str] = post_data['card_ids']
    except KeyError:
        abort(400, util.error('Incorrect JSON data'))
    result = game.accept_trade(player, trade_id, card_ids)
    error_check(result)
    update_client(game)
    return jsonify(result)

@app.route('/api/game/<game_id>/trade/reject', methods=['POST'])
@check_valid_request
def reject_trade(game: Game, player: Player) -> Dict:
    '''Rejects a trade'''
    post_data: Dict = request.get_json()
    try:
        trade_id: str = post_data['trade_id']
    except KeyError:
        abort(400, util.error('Incorrect JSON data'))
    result = game.reject_trade(player, trade_id)
    error_check(result)
    update_client(game)
    return jsonify(result)

@app.route('/api/game/<game_id>/buy', methods=['POST'])
@check_valid_request
def buy_field(game: Game, player: Player) -> Dict:
    '''Buys third field for 3 coins'''
    result = game.buy_field(player)
    error_check(result)
    update_client(game)
    return jsonify(result)

print("Server starting...")
socketio.run(app, '0.0.0.0', 8080)