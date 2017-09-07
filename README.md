# ThatBeanGame
## A web based version of my favourite bean farming game

**To run the game server:**
1. `make env`
2. `source venv/bin/activate`
3. `make requirements`
4. `make run`

NOTE: For cross domain clients to work, you will need to set the domain and port of the client to the environment variable `TBG_CLIENT_ORIGIN` prior to executing `make run`.
For example if your client is hosted at `http://example.com:9000/tbg_client.html`, you will need to run `export TBG_CLIENT_ORIGIN='http://example.com:9000'`.

This game is also being automatically built on Docker Hub. To run the docker container, run the following command:

`docker run -d -p 8080:8080 -e TBG_CLIENT_ORIGIN='http://example.com:9000' tuchfarber/thatbeangame`

*Current status*: partially working

## Documentation
Documentation (including API) can be found at: http://thatbeangame.readthedocs.io

Currently the game will run and allows the following:
* Creating a game
* Joining a game
* Starting a game
* Playing a card from hand
* Drawing 2 cards from deck to market
* Drawing 3 cards from hand to market
* Display game details
* Display player hand
* Display all players fields and points
* Trading

### TODO
* Implement websocket updates
* Implement audio/video chat in app
* Game cleanup after game ends