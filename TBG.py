from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
from bottle import request, Bottle, abort, response, route, post, run, static_file
import json

from player import Player
from game import Game
import util

#from game import Game

app = Bottle()

games = {}
clients = {}

# Decorators
def check_valid_request(f):
    def decorate(*args, **kwargs):
        game = util.get_game(kwargs['game_id'], games)
        if not game:
            return {'status':'error', 'message':'GameD does not exist'}
        player = util.get_player(game, request.get_cookie('tbg_token'))
        if not player:
            return {'status':'error', 'message':'Not authorized to view game'}
        return f(game, player)
    return decorate



@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, user-agent'

@app.route('/<:re:.*>', method='OPTIONS')
def enable_options():
    return

@app.route('/home', method='GET')
def home():
    return static_file('tbg.html', './')

@app.route('/access', method='POST')
def access():
    '''
    Checks if request has a cookie of a logged in user. If cookie exists it
    sends user their game info. If not, it takes them to the login page.
    '''
    cookie = request.get_cookie('tbg_token')
    if cookie and cookie in clients:
        game_id = clients[cookie]
        return {'access':'granted', 'game': game_id}
    return {'access':'denied'}

@app.route('/login', method='POST')
def login():
    '''
    Adds user to the requested game as long as game isn't full or already started,
    game exists, and user name isn't already used in game.
    '''
    login_data = request.json
    if 'game' not in login_data or 'name' not in login_data:
        return {'status':'error', 'message':'Please supply name and game ID'}
    if login_data['game'] not in games:
        return {'status':'error', 'message':'Game does not exist'}
    if login_data['name'] in [player.name for player in games[login_data['game']].players]:
        return {'status':'error', 'message':'User already exists with that name'}
    if games[login_data['game']].status != "Awaiting":
        return {'status':'error', 'message':'Game has already started or ended'}
    if games[login_data['game']].is_full():
        return {'status':'error', 'message':'Game is full'}
    player = Player(login_data['name'])
    games[login_data['game']].add_player(player)
    response.set_cookie('tbg_token', player.token, max_age=400)
    clients[player.token] = login_data['game']
    return {'status':'success', 'data':{'game':login_data['game']}}

@app.route('/create', method='POST')
def create_new_game():
    '''
    Creates new player and game, returns game id
    '''
    login_data = request.json
    if 'name' not in login_data:
        return {'status':'error', 'message':'Please supply name'}
    player = Player(login_data['name'])
    game = Game()
    game.add_player(player)
    games[game.id] = game
    clients[player.token] = game.id
    response.set_cookie('tbg_token', player.token, max_age=400)
    return {'status':'success', 'data':{'game':game.id}}

@app.route('/game/<game_id>', method='GET')
@check_valid_request
def game_index(game, player):
    return game.retrieve_game(player)

@app.route('/game/<game_id>/start', method='POST')
@check_valid_request
def start_game(game, player):
    result = game.start_game(player)
    return result

@app.route('/game/<game_id>/actions', method='GET')
def list_actions(game_id):
    return {
        "actions": [
            "play/hand",
            "play/market",
            "draw/hand",
            "draw/market",
            "trade/hand",
            "trade/market",
            "trade/accept"
        ]
    }

@app.route('/game/<game_id>/play', method='GET')
def list_plays(game_id):
    return {"play": ["hand", "market"]}

@app.route('/game/<game_id>/draw', method='GET')
def list_draws(game_id):
    return {"draw": ["hand", "market"]}

@app.route('/game/<game_id>/trade', method='GET')
def list_trades(game_id):
    return {"trade": ["hand", "market", "accept"]}

@app.route('/game/<game_id>/play/hand', method='POST')
@check_valid_request
def play_card_from_hand(game, player):
    '''
    Accept {'field_index': int}. Plays top card from hand to field specified
    '''
    data = request.json
    result = game.hand_to_field(player, data['field_index'])
    return result

@app.route('/game/<game_id>/play/hand', method='POST')
@check_valid_request
def play_card_from_hand(game, player):
    '''
    Accept {'field_index': int}. Plays top card from hand to field specified
    '''
    data = request.json
    result = game.hand_to_field(player, data['field_index'])
    return result

@app.route('/game/<game_id>/play/market', method='POST')
@check_valid_request
def play_card_from_market(game, player):
    '''
    Accept {'field_index': int, 'market_index': int}. Places card from market into field
    '''
    data = request.json
    result = game.market_to_field(player, data['field_index'], data['market_index'])
    return result

@app.route('/game/<game_id>/draw/market', method='POST')
@check_valid_request
def draw_for_market(game, player):
    '''
    Accept {}. Draws two cards and places them in market
    '''
    result = game.deck_to_market()
    return result

@app.route('/game/<game_id>/draw/hand', method='POST')
@check_valid_request
def draw_for_hand(game, player):
    '''
    Accept {}. Draws three cards and places them in players hand
    '''
    result = game.deck_to_hand(player)
    return result







server = WSGIServer(('0.0.0.0', 8080), app, handler_class=WebSocketHandler)
server.serve_forever()