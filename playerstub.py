import settings
import requests
import json
import logging

class PlayerStub:
    def __init__(self, playeruri):
        self.uri = playeruri

    def send_start(self, cards):
        opponents = list(settings.players_uris)
        opponents.remove(self.uri)

        payload = {'cards': cards, 'players': opponents, 'coins': settings.starting_coins}

        r = requests.post(self.uri + "/start/", data=json.dumps(payload))
        if r.status_code != 200:
            logging.error("Error sending start")
        logging.info(r.text)
        try:
            return json.loads(r.text)
        except:
            return r.text

    def request_play(self, must_coup):
        pass

    def request_tries_to_block(self, action, opponent):
        pass

    def request_challenge(self, action, opponent, card):
        pass

    def request_lose_influence(self):
        pass

    def request_give_card_to_inquisitor(self, opponent):
        pass

    def request_show_card_to_inquisitor(self, opponent, card):
        pass

    def request_inquisitor_choose_card_to_return(self):
        pass

    def signal_status(self, global_status):
        pass

    def signal_new_turn(self, opponent):
        pass

    def signal_blocking(self, acting_opponent, blocked_opponent, action, card):
        pass

    def signal_lost_influence(self, opponent, card):
        pass

    def signal_challenge(self, acting_opponent, challenged_opponent):
        pass

    def signal_action(self, opponent, action, targetted_opponent):
        pass