import settings
import requests
import json
import logging
from server.action import Action


class PlayerStub:
    def __init__(self, playeruri):
        self.uri = playeruri

        self.cards = []
        self.dead_cards = []
        self.coins = 0
        self.id = self.uri

    def __str__(self):
        return "player %s, coins %i, cards [%s]" % (self.id, self.coins, ",".join(self.cards))

    def __decode_response(self, response):
        if response.status_code != 200:
            logging.error("Error receiving response")
        logging.info(response.text)
        try:
            return json.loads(response.text)
        except:
            return response.text

    def start(self, cards):
        logging.info('Player start: {}'.format(cards))
        self.cards = list(cards)
        self.coins = 0
        self.dead_cards = []
        players = list(settings.players_uris)
        payload = {'you': self.id, 'cards': cards, 'players': players, 'coins': settings.starting_coins}
        r = requests.post(self.uri + "/start/", data=json.dumps(payload))
        return self.__decode_response(r)

    def play(self, must_coup, players):
        logging.info('Player play: {}'.format(must_coup))
        headers = {'Must-Coup': 'true' if must_coup else 'false'}
        r = requests.get(self.uri + "/play/", headers=headers)
        return Action.decode_action_from_dict(self.__decode_response(r), players)

    def request_tries_to_block(self, action, opponent):
        headers = {'Action': action.get_identifier(), 'Player': opponent.id}
        r = requests.get(self.uri + "/tries_to_block/", headers=headers)
        payload = self.__decode_response(r)
        return payload

    def request_challenge(self, action, opponent, card):
        headers = {'Action': action.get_identifier(), 'Player': opponent.id, 'Card': card}
        r = requests.get(self.uri + "/challenge/", headers=headers)
        payload = self.__decode_response(r)
        return payload['challenges']

    def request_lose_influence(self):
        r = requests.get(self.uri + "/lose_influence/")
        payload = self.__decode_response(r)
        return payload['card']

    def request_give_card_to_inquisitor(self, opponent):
        headers = {'Player': opponent.id}
        r = requests.get(self.uri + "/inquisitor/give_card_to_inquisitor/", headers=headers)
        payload = self.__decode_response(r)
        return payload['card']

    def request_card_returned_from_investigation(self, opponent, same_card, card):
        payload = {'player': opponent.id, 'same_card': same_card, 'card': card}
        r = requests.post(self.uri + "/inquisitor/card_returned_from_investigation/", data=json.dumps(payload))
        return self.__decode_response(r)

    def request_send_new_card_after_challenge(self, old_card, new_card):
        payload = {'old_card': old_card, 'new_card': new_card}
        r = requests.post(self.uri + "/new_card_from_challenge/", data=json.dumps(payload))
        return self.__decode_response(r)

    def request_show_card_to_inquisitor(self, opponent, card):
        headers = {'Player': opponent.id, 'Card': card}
        r = requests.get(self.uri + "/inquisitor/show_card_to_inquisitor/", headers=headers)
        payload = self.__decode_response(r)
        return payload['change_card']

    def request_inquisitor_choose_card_to_return(self, card):
        headers = {'Card': card}
        r = requests.get(self.uri + "/inquisitor/choose_card_to_return/", headers=headers)
        payload = self.__decode_response(r)
        return payload['card']

    def signal_status(self, global_status):
        pass

    def signal_new_turn(self, opponent):
        pass

    def signal_blocking(self, acting_opponent, blocked_opponent, action, card):
        pass

    def signal_lost_influence(self, opponent, card):
        pass

    def signal_challenge(self, acting_opponent, card, challenged_opponent):
        pass

    def signal_action(self, opponent, action, targeted_opponent):
        pass

    # Common interactions

    def get_coins(self):
        return self.coins

    def lose_influence(self):
        card_to_lose = self.request_lose_influence()
        if card_to_lose in self.cards:
            self.dead_cards.append(card_to_lose)
            self.remove_card(card_to_lose)
            return card_to_lose
        else:
            # this is cheating
            raise ValueError()

    def draw_card_then_send_card_to_deck(self, deck, target_card):
        new_card = self.take_card_from_deck(deck)
        deck.return_card(target_card)
        self.remove_card(target_card)
        return new_card

    def change_card(self, deck, card_to_change):
        self.remove_card(card_to_change)
        deck.return_card(card_to_change)
        new_card = deck.draw_card()
        self.add_card(new_card)
        return new_card

    def change_cards(self, deck, new_card, removed_card):
        self.add_card(new_card)
        self.remove_card(removed_card)
        deck.return_card(removed_card)

    def give_cards(self, card1, card2):
        self.cards = list()
        self.add_card(card1)
        self.add_card(card2)

    def delta_coins(self, coins):
        self.coins += coins

    def is_alive(self):
        return len(self.cards) > 0

    # private methods

    def remove_card(self, card):
        self.cards.remove(card)

    def add_card(self, card):
        self.cards.append(card)

    def take_card_from_deck(self, deck):
        card = deck.draw_card()
        self.add_card(card)
        return card

    def has_card(self, card):
        return card in self.cards
