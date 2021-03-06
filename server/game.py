import settings
import random
from server.deck import Deck
from server.action import *
from server.validation import Validation

class Game:
    def __init__(self, players):
        self.scores = {}
        self.players = players

        for player in self.players:
            self.scores[player.id] = 0

        for i in range(0, 100):
            ''' :type: list[PlayerStub] '''
            self.deck = Deck(settings.deckrepetitions)

            self.give_cards_and_two_coins()
            self.signal_status()

            player_index = random.randint(0, len(players) - 1)

            current_player = self.players[player_index]
            ''' :type: playerstub.PlayerStub '''

            while not self.is_game_over():
                if current_player.is_alive():
                    if not Validation.check_table_correctness(self.players, self.deck):
                        print('Invalid Status!')
                        print(str([str(p) for p in self.players]))
                        raise ValueError()
                    action = current_player.play(current_player.coins >= 10, players)
                    if action.is_valid(players, player_index):
                        self.signal_new_turn(player_index)
                        if action.target:
                            self.signal_targeted_action(current_player, action, action.target)
                            if not action.target.is_alive():
                                raise ValueError()  # targeting an elimitated player
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
                        elif isinstance(action, CoupDEtat):
                            influence = action.resolve_action(current_player)
                            self.signal_lost_influence(action.target, influence)
                        else:
                            action.resolve_action(current_player)
                        self.signal_status()
                    else:
                        # TODO invalid action
                        pass
                else:
                    pass
                player_index = (player_index + 1) % len(players)
                current_player = self.players[player_index]
            for winner in self.players:
                if len(winner.cards) > 0:
                    self.scores[winner.id] += 1
                    break
        print('SCORES: ' + str(self.scores))

    def give_cards_and_two_coins(self):
        for player in self.players:
            player.start([self.deck.draw_card(), self.deck.draw_card()])
            player.delta_coins(2)

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
        print('status')
        for player in self.players:
            if player.is_alive():
                print(str(player))
                player.signal_status(self.get_global_status())

    def is_game_over(self):
        count = 0
        for player in self.players:
            if player.is_alive():
                count += 1
        return count <= 1

    def signal_lost_influence(self, player, card):
        print(player.id + ' lost ' + card)
        for p in self.players:
            if p.is_alive():
                player.signal_lost_influence(player.id, card)

    def signal_new_turn(self, player_index):
        print('player ' + str(player_index) + ' is playing.')
        for player in self.players:
            if player.is_alive():
                player.signal_new_turn(self.players[player_index].id)

    def signal_targeted_action(self, current_player, action, action_target):
        print(current_player.id + ' is targeting ' + action_target.id + ' with ' + action.get_identifier())
        for player in self.players:
            if player.is_alive():
                player.signal_action(current_player.id, action, action_target)

    def signal_player_action(self, current_player, action):
        print(current_player.id + ' is doing ' + action.get_identifier())
        for player in self.players:
            if player.is_alive():
                player.signal_action(current_player.id, action, None)

    def signal_blocking(self, blocked_player, action, blocker_player, card):
        print('Player %s block %s\'s %s with %s.' %
              (blocker_player.id, blocked_player.id, action.get_identifier(), card))
        for player in self.players:
            if player.is_alive():
                player.signal_blocking(blocker_player, blocked_player, action, card)

    def signal_challenge(self, challenged_player, card, challenger_player):
        print('Player %s challenges %s\'s %s' % (challenger_player.id, challenged_player.id, card))
        for player in self.players:
            if player.is_alive():
                player.signal_challenge(challenger_player, card, challenged_player)

    def random_other_players(self, player1, player2=None):
        other_players = list(self.players)
        other_players.remove(player1)
        if player2:
            other_players.remove(player2)
        return other_players

    def resolve_assassination_and_extortion(self, current_player, action):
        no_challenge = True
        challenge_won = False
        no_block = True
        card = action.card
        target = action.target

        if target.request_challenge(action, current_player, card):
            self.signal_challenge(current_player, card, target)
            no_challenge = False
            if current_player.has_card(card):
                influence = target.lose_influence()
                new_card = current_player.change_card(self.deck, card)
                current_player.request_send_new_card_after_challenge(card, new_card)
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
                        new_card = current_player.change_card(self.deck, card)
                        current_player.request_send_new_card_after_challenge(card, new_card)
                        challenge_won = True
                        self.signal_lost_influence(spectator, influence)
                    else:
                        influence = current_player.lose_influence()
                        self.signal_lost_influence(current_player, influence)
                    break
        if no_challenge:
            payload = target.request_tries_to_block(action, current_player)
            card = payload['card']
            if payload['attempt_block'] and card in action.blockers:
                self.signal_blocking(current_player, action, target, card)
                no_block = False
                if current_player.request_challenge(action, target, card):
                    self.signal_challenge(target, card, current_player)
                    if target.has_card(card):
                        influence = current_player.lose_influence()
                        new_card = target.change_card(self.deck, card)
                        target.request_send_new_card_after_challenge(card, new_card)
                        self.signal_lost_influence(current_player, influence)
                    else:
                        influence = target.lose_influence()
                        challenge_won = True
                        self.signal_lost_influence(target, influence)
                else:
                    for spectator in self.random_other_players(current_player, target):
                        if spectator.request_challenge(action, target, card):
                            self.signal_challenge(target, card, spectator)
                            if target.has_card(card):
                                influence = spectator.lose_influence()
                                new_card = target.change_card(self.deck, card)
                                target.request_send_new_card_after_challenge(card, new_card)
                                self.signal_lost_influence(spectator, influence)
                            else:
                                influence = target.lose_influence()
                                challenge_won = True
                                self.signal_lost_influence(target, influence)
                            break
        if (no_block and no_challenge) or challenge_won:
            influence = action.resolve_action(current_player)
            if influence:
                self.signal_lost_influence(target, influence)

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
                new_card = current_player.change_card(self.deck, card)
                current_player.request_send_new_card_after_challenge(card, new_card)
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
                        new_card = current_player.change_card(self.deck, card)
                        current_player.request_send_new_card_after_challenge(card, new_card)
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
        for challenger in self.random_other_players(current_player):
            if challenger.request_challenge(action, current_player, card):
                self.signal_challenge(current_player, card, challenger)
                no_challenge = False
                if current_player.has_card(card):
                    influence = challenger.lose_influence()
                    new_card = current_player.change_card(self.deck, card)
                    current_player.request_send_new_card_after_challenge(card, new_card)
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
        for player_blocker in self.random_other_players(current_player):
            payload = player_blocker.request_tries_to_block(action, current_player)
            card = payload['card']
            if payload['attempt_block'] and card in action.blockers:
                self.signal_blocking(current_player, action, player_blocker, card)
                no_block = False
                if current_player.request_challenge(action, player_blocker, card):
                    self.signal_challenge(player_blocker, card, current_player)
                    if player_blocker.has_card(card):
                        influence = current_player.lose_influence()
                        new_card = player_blocker.change_card(self.deck, card)
                        player_blocker.request_send_new_card_after_challenge(card, new_card)
                        self.signal_lost_influence(current_player, influence)
                    else:
                        influence = player_blocker.lose_influence()
                        challenge_won = True
                        self.signal_lost_influence(player_blocker, influence)
                else:
                    for spectator in self.random_other_players(current_player, player_blocker):
                        if spectator.request_challenge(action, player_blocker, card):
                            self.signal_challenge(player_blocker, card, spectator)
                            if player_blocker.has_card(card):
                                influence = spectator.lose_influence()
                                new_card = player_blocker.change_card(self.deck, card)
                                player_blocker.request_send_new_card_after_challenge(card, new_card)
                                self.signal_lost_influence(spectator, influence)
                            else:
                                influence = player_blocker.lose_influence()
                                challenge_won = True
                                self.signal_lost_influence(player_blocker, influence)
                            break
                break
        if no_block or challenge_won:
            action.resolve_action(current_player)

