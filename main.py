import settings
from constants import *
from server.playerstub import PlayerStub

players = []

for uri in settings.players_uris:
    players.append(PlayerStub(uri))

for player in players:
    player.send_start([DUKE, DUKE])