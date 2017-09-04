===
API
===

access
------

Route: /api/access

Method: GET

Params:

login
------

Route: /api/login

Method: POST

Params:

* name (str)

* game (str)

create new game
------

Route: /api/create

Method: POST

Params:

* name (Player)

* game_type (str)

game status
------

Route: /api/game/<game_id>

Method: GET

Params:

start game
------

Route: /api/game/<game_id>/start

Method: POST

Params:

play card from hand
------

Route: /api/game/<game_id>/play/hand

Method: POST

Params:

* field_index (int)

play card from market
------

Route: /api/game/<game_id>/play/market

Method: POST

Params:

* field_index (int)

* card_id (str)

play card from pending
------

Route: /api/game/<game_id>/play/pending

Method: POST

Params:

* card_id (str)

* field_index (int)

draw for market
------

Route: /api/game/<game_id>/draw/market

Method: POST

Params:

draw for hand
------

Route: /api/game/<game_id>/draw/hand

Method: POST

Params:

create trade
------

Route: /api/game/<game_id>/trade/create

Method: POST

Params:

* card_ids (List[str])

* other_player (str)

* wants (List[str])

accept trade
------

Route: /api/game/<game_id>/trade/accept

Method: POST

Params:

* trade_id (str)

* card_ids (List[str])