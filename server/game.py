import constants
import settings

class Game:
    def __init__(self, players):
        self.players = players
        self.deck = Deck(len(players))

        self.give_cards_and_two_coins()
        self.signal_status()

        player_index = players[0] #TODO randomize

        current_player = self.players[player_index]
        while not self.is_game_over():
            if current_player.is_alive():

                action = current_player.play(current_player.Coins >= 10)

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
        for player in players:
            player.setAlive(True)
            player.send_start([self.deck.draw_card(), self.deck.draw_card()])

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
            if player.isAlive():
                player.signal_status(self.get_global_status())

    def is_game_over(self):
        count = 0
        for player in self.players:
            if player.isAlive():
                count += 1
        return count == 1

    def signal_new_turn(self, player_index):
        for player in self.players:
            if player.isAlive():
                player.signal_new_turn(self.players[player_index].name())

    def signal_targetted_action(self, current_player, action, action_target):
        for player in self.players:
            if player.isAlive():
                player.signal_action(current_player.name(), action, action_target.name())

    def signal_player_action(self, current_player, action):
        for player in self.players:
            if player.isAlive():
                player.signal_action(current_player.name(), action, None)

    def resolve_assassination_and_extortion(self, current_player, action):
        pass

    def resolve_investigate(self, current_player, action):
        pass

    def resolve_collect_taxes_and_exchange(self, current_player, action):
        pass

    def resolve_foreign_aid(self, current_player, action):
        pass
