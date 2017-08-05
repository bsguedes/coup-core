import settings
import requests
import json
import logging
from server.action import Action


class PlayerStub:
    def __init__(self, playeruri):
        self.uri = playeruri

        self.cards = []
        self.coins = 0
        self.id = self.uri

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
        players = list(settings.players_uris)
        payload = {'cards': cards, 'players': players, 'coins': settings.starting_coins}
        r = requests.post(self.uri + "/start/", data=json.dumps(payload))
        return self.__decode_response(r)

    def play(self, must_coup, players):
        logging.info('Player play: {}'.format(must_coup))
        headers = {'Must-Coup': must_coup}
        r = requests.post(self.uri + "/play/", headers=headers)
        return Action.decode_action_from_dict(self.__decode_response(r), players)

    def request_tries_to_block(self, action, opponent):
        headers = {'Action': action.get_identifier(), 'Player': opponent.id}
        r = requests.post(self.uri + "/tries_to_block/", headers=headers)
        return self.__decode_response(r)

    def request_challenge(self, action, opponent, card):
        headers = {'Action': action.get_identifier(), 'Player': opponent.id, 'Card': card}
        r = requests.post(self.uri + "/challenge/", headers=headers)
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

    def request_inquisitor_choose_card_to_return(self, card):
        payload = {'card': card}
        r = requests.post(self.uri + "/inquisitor/choose_card_to_return/", data=payload)
        return self.__decode_response(r)

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

    def signal_action(self, opponent, action, targetted_opponent):
        pass

    #Common interactions

    def lose_influence(self):
        #TODO check if player is not cheating
        card_to_lose = self.request_lose_influence()
        self.remove_card(card_to_lose)
        return card_to_lose

    def send_card_back_to_deck_and_draw_card(self, deck, target_card):
        self.remove_card(target_card)
        self.take_card_from_deck(deck)
        deck.return_card(target_card)

    def change_card(self, deck, card_to_change):
        self.remove_card(card_to_change)
        deck.return_card(card_to_change)
        self.add_card(deck.draw_card())

    def change_cards(self, deck, new_card, removed_card):
        self.remove_card(removed_card)
        self.add_card(new_card)
        deck.return_card(removed_card)

    def give_cards(self, card1, card2):
        self.cards = list()
        self.add_card(card1)
        self.add_card(card2)



    def delta_coins(self, coins):
        self.coins += coins

    def is_alive(self):
        return len(self.cards) > 0

    #private methods

    def remove_card(self, card):
        try:
            self.cards.remove(card)
        except ValueError:
            pass  # do nothing!

    def add_card(self, card):
        self.cards.append(card)

    def take_card_from_deck(self, deck):
        card = deck.draw_card()
        self.add_card(card)

    def has_card(self, card):
        return card in self.cards
