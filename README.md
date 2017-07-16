# coup-core
Coup Core using Django/Python

## Player API

player: a player string IP (e.g. "192.168.0.10")
card: one of five cards ("duke", "contessa", "assassin", "captain", "inquisitor")
action: one of eight actions ("income", "foreign_aid", "collect_taxes", "assassinate", "extortion", "investigate", "exchange", "coup")

player_descriptor: 
Contains public information of a player. 
If a card is hidden it is equal to null.
{
	"player": player
	"card1": card?
	"card2": card?
	"coins": integer
}

actions may be targetted, blockable and/or challengeable

action<targetted>: ("coup", "assassinate", "investigate", "extortion")
action<blockable>: ("assassinate", "extortion", "foreign_aid")
action<challengeable>: ("collect_taxes", "assassinate", "extortion", "investigate", "exchange")

server POST /start

payload
{ 
	"card1": card, 
	"card2": card, 
	"coins": integer,
	"players": [ 
		player
	] 
}

expects 200: OK

server GET /play/

headers
Must-Coup: ("true", "false")

expects 200: OK
payload
{
	"action": action<non_targetted>
}
OR
{
	"action": action<targetted>
	"target": player
}

server GET /tries_to_block/

headers
Action: action<blockable>
Player: player

expects 200: OK
payload
{
	"attempt_block": bool
	"card": card
}

server GET /challenge/

headers
Action: action<challengeable>
Player: player
Card: card

expects 200: OK
payload
{
	"challenges": bool
}

server GET /lose_influence/

expects 200: OK
payload
{ 
"card": card
}


server GET /inquisitor/give_card_to_inquisitor/

headers
Player: player

expects 200: OK
payload
{ 
"card": card
}

server GET /inquisitor/show_card_to_inquisitor

headers
Player: player
Card: card

expects 200: OK
payload
{
	"change_card": bool
}

server GET /inquisitor/choose_card_to_return

expects 200: OK
payload
{ 
"card": card
}

Signals

server POST /signal/status
payload
{
[
	{ player_descriptor }, (...)
]	
}

expects 201: OK



server POST /signal/new_turn
payload
{
"player": player
}

expects 201: OK

server POST /signal/blocking
payload
{
	"player_acting": player,
	"action": action<blockable>
	"player_blocking": player,
	"card": card
}
expects 201: OK

server POST /signal/lost_influence
payload
{
	"player": player,
	"card": card
}
expects 201: OK


server POST /signal/challenge
payload
{
	"challenger": player,
	"challenged": player,
	"card": card
}
expects 201: OK

server POST /signal/action
payload
{
	"player_acting": player,
	"action": action<non_targetted>
}
OR
{
	"player_acting": player,
	"action": action<targetted>,
	"player_targetted": player
}



