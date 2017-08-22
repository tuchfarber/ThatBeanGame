# ThatBeanGame
## A web based version of my favourite bean farming game

**To run the game server:**
1. `make env`
2. `source env/bin/activate`
3. `make requirements`
4. `make run`

This game is also being automatically built on Docker Hub. To run the docker container, run the following command:

`docker run -d -p 8080:8080 tuchfarber/thatbeangame`

*Current status*: partially working

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