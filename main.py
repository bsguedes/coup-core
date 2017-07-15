
import logger
from constants import *
import settings
from playercommunication import PlayerCommunication
pc = PlayerCommunication()

for player in settings.players:
    pc.send_start(player, [DUKE, DUKE])