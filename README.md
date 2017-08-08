# coup-core
Coup Core using Django/Python

## How to run

This project contains the engine for Coup. It runs as a server that accepts clients through a REST API interface, described on the next sections.

To launch this engine, just run `main.py` via a Python interpreter. You'll need to have the clients up and running.

To config which players will play the game, simply enter their URLs on `settings.py`. Do not enter more than 6 players. 

A client must implement and respond to all Server Calls via GET or POST. All Status calls are optional and do not need to be responded.

## Game Rules

From BoardGameGeek game description: https://boardgamegeek.com/boardgame/131357/coup

In Coup, you want to be the last player with influence in the game, with influence being represented by face-down character cards in your playing area.

Each player starts the game with two coins and two influence – i.e., two face-down character cards; the fifteen card deck consists of three copies of five different characters, each with a unique set of powers:

* **Duke**: Take three coins from the treasury. Block someone from taking foreign aid.

* **Assassin**: Pay three coins and try to assassinate another player's character.

* **Contessa**: Block an assassination attempt against yourself.

* **Captain**: Take two coins from another player, or block someone from stealing coins from you.

* **Inquisitor**: Draw one character card from the Court deck and choose whether or not to exchange it with one of your face-down characters. OR Force an opponent to show you one of their character cards (their choice which). If you wish it, you may then force them to draw a new card from the Court deck. They then shuffle the old card into the Court deck. Block someone from stealing coins from you.

On your turn, you can take any of the actions listed above, regardless of which characters you actually have in front of you, or you can take one of three other actions:

* **Income**: Take one coin from the treasury.

* **Foreign aid**: Take two coins from the treasury.

* **Coup**: Pay seven coins and launch a coup against an opponent, forcing that player to lose an influence. (If you have ten coins or more, you must take this action.)

When you take one of the character actions – whether actively on your turn, or defensively in response to someone else's action – that character's action automatically succeeds unless an opponent challenges you. In this case, if you can't (or don't) reveal the appropriate character, you lose an influence, turning one of your characters face-up. Face-up characters cannot be used, and if both of your characters are face-up, you're out of the game.

If you do have the character in question and choose to reveal it, the opponent loses an influence, then you shuffle that character into the deck and draw a new one, perhaps getting the same character again and perhaps not.

The last player to still have influence – that is, a face-down character – wins the game!

## Defined Types

* **player:** a player string IP (e.g. `"192.168.0.10"`)

* **card:** one of five cards `("duke", "contessa", "assassin", "captain", "inquisitor")`

* **action**: one of eight actions `("income", "foreign_aid", "collect_taxes", "assassinate", "extortion", "investigate", "exchange", "coup")`

* **player_descriptor:** 
Contains public information of a player. 
If a card is hidden it is equal to null.
```
{
    "player": player
    "card1": card?
    "card2": card?
    "coins": integer
}
```
Actions may be targeted, blockable and/or challengeable:

`action<targeted>: ("coup", "assassinate", "investigate", "extortion")`

`action<blockable>: ("assassinate", "extortion", "foreign_aid")`

`action<challengeable>: ("collect_taxes", "assassinate", "extortion", "investigate", "exchange")`


## Server Calls (cannot be ignored)

### server POST /start

##### request payload
```
{ 
    "you": player,
    "cards": [ 
        card
    ],
    "coins": integer,
    "players": [ 
        player
    ] 
}
```

##### response status

201: OK

### server GET /play/

##### request headers

`Must-Coup: ("true", "false")`

##### response status

200: OK

##### response payload
```
{
    "action": action<non_targetted>
}
```
OR

```
{
    "action": action<targetted>
    "target": player
}
```

### server GET /tries_to_block/

##### request headers

`Action: action<blockable>`

`Player: player`

##### response status

200: OK

##### response payload
```
{
    "attempt_block": bool
    "card": card
}
```

### server GET /challenge/

##### request headers

`Action: action<challengeable>`

`Player: player`

`Card: card`

##### response status

200: OK

##### response payload
```
{
    "challenges": bool
}
```

### server POST /new_card_from_challenge/

##### request payload
```
{
	"old_card": card,
	"new_card": card
}
```

##### response status

201: OK

### server GET /lose_influence/

##### response status

200: OK

##### response payload
```
{ 
    "card": card
}
```

### server GET /inquisitor/give_card_to_inquisitor/

##### request headers

`Player: player`

##### response status

200: OK

##### response payload
```
{ 
    "card": card
}
```

### server GET /inquisitor/show_card_to_inquisitor/

##### request headers

`Player: player`

`Card: card`

##### response status

200: OK

##### response payload
```
{
    "change_card": bool
}
```

### server POST /inquisitor/card_returned_from_investigation/

##### request payload
```
{
    "player": player,
    "same_card": bool
    "card": card
}
```

##### response status

201: OK

### server GET /inquisitor/choose_card_to_return/

##### request headers

`Card: card`

##### response status

200: OK

##### response payload
```
{ 
    "card": card
}
```

## Server Signals (can be ignored)

### server POST /signal/status

##### request payload
```
{
    [
        { player_descriptor }, (...)
    ]	
}
```

### server POST /signal/new_turn

##### request payload
```
{
    "player": player
}
```

### server POST /signal/blocking

##### request payload
```
{
    "player_acting": player,
    "action": action<blockable>
    "player_blocking": player,
    "card": card
}
```

### server POST /signal/lost_influence

##### request payload
```
{
    "player": player,
    "card": card
}
```

### server POST /signal/challenge

##### request payload
```
{
    "challenger": player,
    "challenged": player,
    "card": card
}
```

### server POST /signal/action

##### request payload
```
{
    "player_acting": player,
    "action": action<non_targeted>
}
```

OR (if targeted)

```
{
    "player_acting": player,
    "action": action<targeted>,
    "player_targeted": player
}
```
