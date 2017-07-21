import websockets
import asyncio
import json

games = []

class Client:
    def __init__(self, name, websocket):
        self.name = name
        self.websocket = websocket

def manage_introductions(introduction, websocket):
    player = Player(introduction["name"], websocket)
    matching_game = [game for game in games if game.id == introduction["game_id"]]
    if matching_game:
        if len(matching_game.players) > 7:
            # No new players!
            return
        # Add player to existing game
    else:
        # Create new game and add user

    # HANDLE USER RETURNING AFTER LOSING CONNECTION (via username and gameid)



async def communication_handler(websocket, path):
    introduction = await websocket.recv()
    manage_introductions(json.dumps(introduction), websocket)
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