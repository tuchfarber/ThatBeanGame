import websockets
import asyncio
import json

# GLOBAL CONFIG
MAX_PLAYERS_PER_GAME = 7
ERRORS = {
    "MAX_PLAYER":"This game already has the maximum number of players"
}
games = []

class Client:
    def __init__(self, name, websocket):
        self.name = name
        self.websocket = websocket

def _create_error(error_key):
    obj = {"type":"error","error_key":error_key, "error_text":ERRORS[error_key]}
    return json.dumps(obj)

def _create_notification(message):
    obj = {"type":"notification", "notification_text":message}
    return json.dumps(obj)

def login(introduction, websocket):
    player = Player(introduction["name"], websocket)
    matching_game = [game for game in games if game.id == introduction["game_id"]][0]
    if matching_game:
        if len(matching_game.players) > MAX_PLAYERS_PER_GAME:
            websocket.send(_create_error("MAX_PLAYER"))
            return
        matching_game.players.append(player)
    else:
        new_game = Game()
        new_game.players.append(player)
        websocket.send(_create_notification)
        # Create new game and add user

    # HANDLE USER RETURNING AFTER LOSING CONNECTION (via username and gameid)



async def communication_handler(websocket, path):
    introduction = await websocket.recv()
    login(json.dumps(introduction), websocket)
    client = Client(json.loads(hello_message)["name"], websocket)
    while True:
        message = await websocket.recv()
        print(message)
        message = "{} said {}!".format(client.name, message)
        await websocket.send(message)

if __name__ == "__main__":
    start_server = websockets.serve(communication_handler, 'localhost', 5678)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()