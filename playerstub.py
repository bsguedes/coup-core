import settings
import requests
import json
import logging

class PlayerStub:
    def __init__(self, playeruri):
        self.uri = playeruri
        self.cards = list()
        self.coins = 0

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

    #private methods

    def remove_card(self, card):
        self.cards.remove(card)

    def add_card(self, card):
        self.cards.append(card)

    def take_card_from_deck(self, deck):
        card = deck.draw_card()
        self.add_card(card)

