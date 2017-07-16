import settings
from constants import *
from server.playerstub import PlayerStub

players = []

for uri in settings.players_uris:
    players.append(PlayerStub(uri))
opponent_id = players[1].id

matheus = players[0]
''' :type: PlayerStub '''
matheus.start([DUKE, DUKE])
response = matheus.play(True)
if response['action']:
    pass
