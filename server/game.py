import constants
import settings
from deck import Deck
from action import *
import random

class Game:
    def __init__(self, players):
        self.players = players
        ''' :type: list[PlayerStub] '''
        self.deck = Deck(settings.deckrepetitions)

        self.give_cards_and_two_coins()
        self.signal_status()

        player_index = random.randint(0, len(players) - 1)

        current_player = self.players[player_index]
        ''' :type: playerstub.PlayerStub '''

        while not self.is_game_over():
            if current_player.is_alive():

                action = current_player.play(current_player.coins >= 10)

                if action.is_valid(players, player_index):
                    self.signal_new_turn(player_index)
                    if action.target:
                        self.signal_targetted_action(current_player, action, action.target)
                    else:
                        self.signal_player_action(current_player, action)

                    # resolve
                    if isinstance(action, Assassinate) or isinstance(action, Extortion):
                        self.resolve_assassination_and_extortion(current_player, action)
                    elif isinstance(action, CollectTaxes) or isinstance(action, Exchange):
                        self.resolve_collect_taxes_and_exchange(current_player, action)
                    elif isinstance(action, ForeignAid):
                        self.resolve_foreign_aid(current_player, action)
                    elif isinstance(action, Investigate):
                        self.resolve_investigate(current_player, action)
                    else:
                        action.resolve_action(current_player)

                    self.signal_status()

                else:
                    # TODO invalid action
                    pass
            else:
                pass
            current_player = self.players[(player_index + 1) % len(players)]

    def give_cards_and_two_coins(self):
        for player in self.players:
            player.start([self.deck.draw_card(), self.deck.draw_card()])

    def get_global_status(self):
        player_list = []
        for player in self.players:
            player_dict = {"player": player.id,
                           "cards": player.cards,
                           "coins": player.coins
                           }
            player_list += [player_dict]
        return {"players": player_list}

    def signal_status(self):
        for player in self.players:
            if player.is_alive():
                player.signal_status(self.get_global_status())

    def is_game_over(self):
        count = 0
        for player in self.players:
            if player.is_alive():
                count += 1
        return count == 1

    def signal_new_turn(self, player_index):
        for player in self.players:
            if player.is_alive():
                player.signal_new_turn(self.players[player_index].id)

    def signal_targetted_action(self, current_player, action, action_target):
        for player in self.players:
            if player.is_alive():
                player.signal_action(current_player.id, action, action_target)

    def signal_player_action(self, current_player, action):
        for player in self.players:
            if player.is_alive():
                player.signal_action(current_player.id, action, None)

    def resolve_assassination_and_extortion(self, current_player, action):
        pass

    def resolve_investigate(self, current_player, action):
        pass

    def resolve_collect_taxes_and_exchange(self, current_player, action):
        pass

    def resolve_foreign_aid(self, current_player, action):
        pass
