# ThatBeanGame
## A web based version of my favourite bean farming game

**NOTICE**: This repo only contains the server side of the code. The client is completed detached from the server and resides in it's own repo here: [https://github.com/tuchfarber/ThatBeanGame-Client](https://github.com/tuchfarber/ThatBeanGame-Client)

**To run the game server:**
1. `make env`
2. `source venv/bin/activate`
3. `make requirements`
4. `make run`

NOTE: For cross domain clients to work, you will need to set the domain and port of the client to the environment variable `TBG_CLIENT_ORIGIN` prior to executing `make run`.
For example if your client is hosted at `http://example.com:9000/tbg_client.html`, you will need to run `export TBG_CLIENT_ORIGIN='http://example.com:9000'`.

This game is also being automatically built on Docker Hub. To run the docker container, run the following command:

`docker run -d -p 8080:8080 -e TBG_CLIENT_ORIGIN='http://example.com:9000' tuchfarber/thatbeangame`

*Current status*: mostly working

## Documentation
Documentation (including API) can be found at: http://thatbeangame.readthedocs.io

The full game can be played currently, assuming the networking is done correctly. 

### Wishlist
* Implement audio or video chat in app
* Game cleanup after game ends
* Game over page
* Make more documentation or automation on the networking side.
* Make the UX way better
* Add a public game listing that users can choose from if they don't have a group of their own.