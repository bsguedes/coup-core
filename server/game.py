import constants
import settings
from deck import Deck

class Game:
    def __init__(self, players):
        self.players = players
        ''' :type: list[PlayerStub] '''
        self.deck = Deck(settings.deckrepetitions)

        self.give_cards_and_two_coins()
        self.signal_status()

        player_index = players[0] #TODO randomize

        current_player = self.players[player_index]
        ''' :type: playerstub.PlayerStub '''

        while not self.is_game_over():
            if current_player.is_alive():

                action = current_player.play(current_player.coins >= 10)

                if action.is_valid(players, player_index):
                    self.signal_new_turn(player_index)
                    if action.is_targetted():
                        self.signal_targetted_action(current_player, action, action.target)
                    else:
                        self.signal_player_action(current_player, action)

                    # resolve
                    action_name = action.name()

                    if action_name == constants.INCOME:
                        action.resolve_action(current_player)
                    elif action_name == constants.COUP:
                        action.resolve_action(current_player)
                    elif action_name == constants.ASSASSINATE or action_name == constants.EXTORTION:
                        self.resolve_assassination_and_extortion(current_player, action)
                    elif action_name == constants.INVESTIGATE:
                        self.resolve_investigate(current_player, action)
                    elif action_name == constants.COLLECT_TAXES or action_name == constants.EXCHANGE:
                        self.resolve_collect_taxes_and_exchange(current_player, action)
                    elif action_name == constants.FOREIGN_AID:
                        self.resolve_foreign_aid(current_player, action)

                    self.signal_status()

                else:
                    # TODO invalid action
                    pass
            else:
                pass
            current_player = (current_player + 1) % len(players)

    def give_cards_and_two_coins(self):
        for player in self.players:
            player.start([self.deck.draw_card(), self.deck.draw_card()])

    def get_global_status(self):
        player_list = []
        for player in self.players:
            player_dict = {"player": player.name(),
                           "cards": player.get_visible_cards(),
                           "coins": player.get_coins()
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
                player.signal_new_turn(self.players[player_index])

    def signal_targetted_action(self, current_player, action, action_target):
        for player in self.players:
            if player.is_alive():
                player.signal_action(current_player, action, action_target)

    def signal_player_action(self, current_player, action):
        for player in self.players:
            if player.is_alive():
                player.signal_action(current_player, action, None)

    def resolve_assassination_and_extortion(self, current_player, action):
        pass

    def resolve_investigate(self, current_player, action):
        pass

    def resolve_collect_taxes_and_exchange(self, current_player, action):
        pass

    def resolve_foreign_aid(self, current_player, action):
        no_block = True
        challenge_won = False
        for player_blocker in random_other_players(current_player):
            payload = player_blocker.request_tries_to_block(action, current_player)
            if payload['attempt_block']:
                self.signal_blocking(current_player, action, player_blocker, payload['card'])
                no_block = False
                if current_player.request_challenge(action, player_blocker, payload['card']):
                    self.signal_challenge(player_blocker, payload['card'], current_player)
                    if player_blocker.has_card(payload['card']):
                        influence = current_player.lose_influence()
                        player_blocker.change_card(self.deck, payload['card'])
                        self.signal_lost_influence(current_player, influence)
                    else:
                        influence = player_blocker.lose_influence()
                        challenge_won = True
                        self.signal_lost_influence(player_blocker, influence)
                else:
                    for spectator in random_other_players(current_player, player_blocker):
                        if spectator.request_challenge(player_blocker, payload['card']):
                            self.signal_challenge(player_blocker, payload['card'], spectator)
                            if player_blocker.has_card(payload['card']):
                                influence = spectator.lose_influence()
                                player_blocker.change_card(self.deck, payload['card'])
                                self.signal_lost_influence(spectator, influence)
                            else:
                                influence = player_blocker.lose_influence()
                                challenge_won = True
                                self.signal_lost_influence(player_blocker, influence)
                            break
                break
        if no_block || challenge_won:
            action.resolve_action(current_player)
