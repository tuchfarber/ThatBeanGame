from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
from bottle import request, Bottle, abort, response, route, post, run, static_file
import json

from player import Player
from game import Game
import util
#from util import error, success
import util

# from game import Game

app = Bottle()

games = {}
clients = {}


def check_valid_request(f):
    '''Decorator. Verifies game exists and client is authorized. Returns game and client'''
    def decorate(*args, **kwargs):
        game = util.get_game(kwargs['game_id'], games)
        if not game:
            abort(400, util.error('Game does not exist'))
        player = util.get_player(game, request.get_cookie('tbg_token'))
        if not player:
            abort(400, util.error('Not authorized to view game'))
        return f(game, player)
    return decorate


def error_check(result):
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


@app.route('/', method='GET')
def home():
    '''Returns webpage'''
    return static_file('tbg.html', './')


@app.route('/access', method='GET')
def access():
    '''
    Checks if request has a cookie of a logged in user. If cookie exists it
    sends user their game info. If not, it takes them to the login page.
    '''
    cookie = request.get_cookie('tbg_token')
    if cookie and cookie in clients:
        game_id = clients[cookie]
        return {'game': game_id}
    abort(400, util.error('Access denied'))


@app.route('/login', method='POST')
def login():
    '''
    Adds user to the requested game as long as game isn't full or already started,
    game exists, and user name isn't already used in game.
    '''
    login_data = request.json
    if 'game' not in login_data or 'name' not in login_data:
        abort(400, util.error('Please supply name and game ID'))
    if login_data['game'] not in games:
        abort(400, util.error('Game does not exist'))
    if login_data['name'] in [player.name for player in games[login_data['game']].players]:
        abort(400, util.error('User already exists with that name'))
    if games[login_data['game']].status != 'Awaiting':
        abort(400, util.error('Game has already started or ended'))
    if games[login_data['game']].is_full():
        abort(400, util.error('Game is full'))
    player = Player(login_data['name'])
    games[login_data['game']].add_player(player)
    response.set_cookie('tbg_token', player.token, max_age=400)
    clients[player.token] = login_data['game']
    return util.success('Successfully logged into game')


@app.route('/create', method='POST')
def create_new_game():
    '''Creates new player and game, returns game id'''
    login_data = request.json
    if 'name' not in login_data:
        abort(400, util.error('Name not supplied'))
    player = Player(login_data['name'])
    game = Game()
    game.add_player(player)
    games[game.id] = game
    clients[player.token] = game.id
    response.set_cookie('tbg_token', player.token, max_age=400)
    return {'game': game.id}


@app.route('/game/<game_id>', method='GET')
@check_valid_request
def game_status(game, player):
    '''Returns all game info'''
    result = game.retrieve_game(player)
    error_check(result)
    return result


@app.route('/game/<game_id>/start', method='POST')
@check_valid_request
def start_game(game, player):
    '''Starts requested game if user is host'''
    result = game.start_game(player)
    error_check(result)
    return result


@app.route('/game/<game_id>/play/hand', method='POST')
@check_valid_request
def play_card_from_hand(game, player):
    '''Plays top card from hand to field specified'''
    data = request.json
    result = game.hand_to_field(player, data['field_index'])
    error_check(result)
    return result


@app.route('/game/<game_id>/play/market', method='POST')
@check_valid_request
def play_card_from_market(game, player):
    '''Places card from market into field'''
    data = request.json
    result = game.market_to_field(player, data['field_index'], data['market_index'])
    error_check(result)
    return result


@app.route('/game/<game_id>/draw/market', method='POST')
@check_valid_request
def draw_for_market(game, player):
    '''Draws two cards and places them in market'''
    result = game.deck_to_market(player)
    error_check(result)
    return result


@app.route('/game/<game_id>/draw/hand', method='POST')
@check_valid_request
def draw_for_hand(game, player):
    '''Draws three cards and places them in players hand'''
    result = game.deck_to_hand(player)
    error_check(result)
    return result


server = WSGIServer(('0.0.0.0', 8080), app, handler_class=WebSocketHandler)
server.serve_forever()
