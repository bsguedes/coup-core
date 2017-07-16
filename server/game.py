import constants
import settings
from deck import Deck
from action import *
import random
from random import shuffle

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

    def signal_blocking(self, blocked_player, action, blocker_player, card):
        for player in self.players:
            if player.is_alive():
                player.signal_blocking(blocker_player, blocked_player, action, card)

    def signal_challenge(self, challenged_player, card, challenger_player):
        for player in self.players:
            if player.is_alive():
                player.signal_challenge(self, challenger_player, challenged_player)

    def random_other_players(self, player1):
        other_players = list(self.players)
        other_players.remove(player1)
        return shuffle(other_players)

    def random_other_players(self, player1, player2):
        other_players = list(self.players)
        other_players.remove(player1)
        other_players.remove(player2)
        return shuffle(other_players)

    def resolve_assassination_and_extortion(self, current_player, action):
        pass

    def resolve_investigate(self, current_player, action):
        no_challenge = True
        challenge_won = False
        card = action.card
        target = action.target
        if target.request_challenge(action, current_player, card):
            self.signal_challenge(current_player, card, target)
            no_challenge = False
            if current_player.has_card(card):
                influence = target.lose_influence()
                current_player.change_card(self.deck, card)
                challenge_won = True
                self.signal_lost_influence(target, influence)
            else:
                influence = current_player.lose_influence()
                self.signal_lost_influence(current_player, influence)
        else:
            for spectator in self.random_other_players(current_player, target):
                if spectator.request_challenge(action, current_player, card):
                    self.signal_challenge(current_player, card, spectator)
                    no_challenge = False
                    if current_player.has_card(card):
                        influence = spectator.lose_influence()
                        current_player.change_card(self.deck, card)
                        challenge_won = True
                        self.signal_lost_influence(spectator, influence)
                    else:
                        influence = current_player.lose_influence()
                        self.signal_lost_influence(current_player, influence)
                    break
        if no_challenge or challenge_won:
            action.resolve_action(current_player, self.deck)

    def resolve_collect_taxes_and_exchange(self, current_player, action):
        no_challenge = True
        challenge_won = False
        card = action.card
        for challenger in random_other_players(current_player):
            if challenger.request_challenge(action, current_player, card):
                self.signal_challenge(current_player, card, challenger)
                no_challenge = False
                if current_player.has_card(card):
                    influence = challenger.lose_influence()
                    current_player.change_card(self.deck, card)
                    challenge_won = True
                    self.signal_lost_influence(challenger, influence)
                else:
                    influence = current_player.lose_influence()
                    self.signal_lost_influence(current_player, influence)
                break
        if no_challenge or challenge_won:
            action.resolve_action(current_player, self.deck)

    def resolve_foreign_aid(self, current_player, action):
        no_block = True
        challenge_won = False
        for player_blocker in random_other_players(current_player):
            payload = player_blocker.request_tries_to_block(action, current_player)
            card = payload['card']
            if payload['attempt_block']:
                self.signal_blocking(current_player, action, player_blocker, card)
                no_block = False
                if current_player.request_challenge(action, player_blocker, card):
                    self.signal_challenge(player_blocker, card, current_player)
                    if player_blocker.has_card(card):
                        influence = current_player.lose_influence()
                        player_blocker.change_card(self.deck, card)
                        self.signal_lost_influence(current_player, influence)
                    else:
                        influence = player_blocker.lose_influence()
                        challenge_won = True
                        self.signal_lost_influence(player_blocker, influence)
                else:
                    for spectator in random_other_players(current_player, player_blocker):
                        if spectator.request_challenge(action, player_blocker, card):
                            self.signal_challenge(player_blocker, card, spectator)
                            if player_blocker.has_card(card):
                                influence = spectator.lose_influence()
                                player_blocker.change_card(self.deck, card)
                                self.signal_lost_influence(spectator, influence)
                            else:
                                influence = player_blocker.lose_influence()
                                challenge_won = True
                                self.signal_lost_influence(player_blocker, influence)
                            break
                break
        if no_block || challenge_won:
            action.resolve_action(current_player)

