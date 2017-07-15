import settings
import requests
import json
import logging

class PlayerCommunication:
    def __init__(self):
        pass

    def send_start(self, player, cards):
        opponents = list(settings.players)
        opponents.remove(player)

        payload = {'cards': cards, 'players': opponents, 'coins': settings.starting_coins}

        r = requests.post(player + "/start/", data=json.dumps(payload))
        if r.status_code != 200:
            logging.error("Error sending start")
        logging.info(r.text)
        return json.loads(r.text)



