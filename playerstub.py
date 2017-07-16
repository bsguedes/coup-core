import settings
import requests
import json
import logging

class PlayerStub:
    def __init__(self, playeruri):
        self.uri = playeruri
        self.id = self.uri

    def __decode_response(self, response):
        if response.status_code != 200:
            logging.error("Error receiving response")
        logging.info(response.text)
        try:
            return json.loads(response.text)
        except:
            return response.text

    def send_start(self, cards):
        logging.info('Player start: {}'.format(cards))
        opponents = list(settings.players_uris)
        opponents.remove(self.id)
        payload = {'cards': cards, 'players': opponents, 'coins': settings.starting_coins}
        r = requests.post(self.uri + "/start/", data=json.dumps(payload))
        return self.__decode_response(r)

    def request_play(self, must_coup):
        logging.info('Player play: {}'.format(must_coup))
        payload = {'must_coup': must_coup}
        r = requests.post(self.uri + "/play/", data=json.dumps(payload))
        return self.__decode_response(r)

    def request_tries_to_block(self, action, opponent):
        payload = {'action': action, 'opponent': opponent.id}
        r = requests.post(self.uri + "/tries_to_block/", data=json.dumps(payload))
        return self.__decode_response(r)

    def request_challenge(self, action, opponent, card):
        payload = {'action': action, 'opponent': opponent.id, 'card': card}
        r = requests.post(self.uri + "/challenge/", data=json.dumps(payload))
        return self.__decode_response(r)

    def request_lose_influence(self):
        r = requests.post(self.uri + "/lose_influence/", data=None)
        return self.__decode_response(r)

    def request_give_card_to_inquisitor(self, opponent):
        payload = {'opponent': opponent.id}
        r = requests.post(self.uri + "/inquisitor/give_card_to_inquisitor/", data=payload)
        return self.__decode_response(r)

    def request_show_card_to_inquisitor(self, opponent, card):
        payload = {'opponent': opponent.id, 'card': card}
        r = requests.post(self.uri + "/inquisitor/show_card_to_inquisitor/", data=payload)
        return self.__decode_response(r)

    def request_inquisitor_choose_card_to_return(self):
        r = requests.post(self.uri + "/inquisitor/show_card_to_inquisitor/", data=None)
        return self.__decode_response(r)

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