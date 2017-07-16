import settings
from constants import *
from server.playerstub import PlayerStub
from server.game import Game
players = []

for uri in settings.players_uris:
    players.append(PlayerStub(uri))

Game(players)
