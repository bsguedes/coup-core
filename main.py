
import logger
from constants import *
import settings
from playerstub import PlayerStub

players = []

for uri in settings.players_uris:
    players.append(PlayerStub(uri))

for player in players:
    player.send_start([DUKE, DUKE])