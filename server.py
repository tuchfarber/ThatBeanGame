import websockets
import asyncio
import json
from player import Player
from game import Game
from message import Message

json.
# GLOBAL CONFIG
MAX_PLAYERS_PER_GAME = 7
ERRORS = {
    "MAX_PLAYER": "This game already has the maximum number of players",
    "TOO_LATE": "This game has already started"
}
all_games = []

def _create_error(error_key):
    obj = {"type":"error","error_key":error_key, "error_text":ERRORS[error_key]}
    return json.dumps(obj)

def _create_notification(message):
    obj = {"type":"notification", "notification_text":message}
    return json.dumps(obj)



def login(intro, websocket):
    # Find existing game
    game = _shrink([game for game in all_games if game.id == intro["game_id"]])

    if game:
        # Check if player is returning to game
        old_player = _shrink([x for x in game.players if x.name == intro["name"]])

        if old_player:
            # Update player to new websocket connection
            old_player.websocket = websocket
        else:
            # Check if game is maxed out
            if len(game.players) > MAX_PLAYERS_PER_GAME:
                websocket.send(_create_error("MAX_PLAYER"))
            # Make sure game isn't running or already over
            elif game.status != "Awaiting":
                websocket.send(_create_error("TOO_LATE"))
            elif intro["name"] 
            # Add player to game
            else:
                player = Player(intro["name"], websocket)
                game.add_player(player)
    else:
        # Create new game and add new player to it
        game = Game()
        all_games.append(game)
        player = Player(intro["name"], websocket)
        game.add_player(player)
        #websocket.send(_create_notification("New game created"))
    return (game, player)


async def communication_handler(websocket, path):
    # First communication must be in format {"game_id":"", "name":""}
    while True:
        intro = await websocket.recv()
        intro = Message.validate_intro()
        if not intro:
            await websocket.send("Invalid introduction. Please try again")
        break
    (game, player) = login(intro, websocket)    
    await websocket.send("Welcome to game {}".format(game.id))
    if player.is_host:
        await websocket.send("You are the host. You determine when game starts")
    # Notify other players that player has joined
    await asyncio.wait(
        [a_player.websocket.send("{} has joined the game".format(player.name)) for a_player in game.players]
    )
    
    while True:
        message = await websocket.recv()
        # result should be dict
        result = game.do_action(player, message)
        if result:
            result = json.dumps(result)
            await websocket.send(result)

if __name__ == "__main__":
    start_server = websockets.serve(communication_handler, 'localhost', 5678)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()