import constants

class Action:
    def __init__(self):
        pass

    def is_valid(self, players, player_index):
        #TODO validation
        return True

class CoupDEtat(Action):
    def __init__(self, target):
        Action.__init__(self)
        self.target = target

    def resolve_action(self, current_player):
        current_player.delta_coins(-7)
        self.target.lose_influence()

class ForeignAid(Action):
    def __init__(self):
        Action.__init__(self)
        self.blockers = [constants.DUKE]

    def resolve_action(self, current_player):
        current_player.delta_coins(2)

class Income(Action):
    def __init__(self):
        Action.__init__(self)

    def resolve_action(self, current_player):
        current_player.delta_coins(1)


class CollectTaxes(Action):
    def __init__(self):
        Action.__init__(self)
        self.card = constants.DUKE

    def resolve_action(self, current_player):
        current_player.delta_coins(3)

class Investigate(Action):
    def __init__(self, target):
        Action.__init__(self)
        self.target = target
        self.card = constants.INQUISITOR

    def resolve_action(self, current_player, deck):
        target_card = self.target.give_card_to_inquisitor(current_player)
        if current_player.should_target_change_card(self.target, target_card):
            self.target.send_card_back_to_deck_and_draw_card(deck, target_card)

class Exchange(Action):
    def __init__(self):
        Action.__init__(self)
        self.card = constants.INQUISITOR

    def resolve_action(self, current_player, deck):
        new_card = deck.draw_card()
        removed_card = current_player.choose_one_to_remove(new_card)
        current_player.change_cards(deck, new_card, removed_card)

class Assassinate(Action):
    def __init__(self, target):
        Action.__init__(self)
        self.target = target
        self.card = constants.ASSASSIN
        self.blockers = [constants.CONTESSA]

    def resolve_action(self, current_player):
        current_player.delta_coins(-3)
        self.target.lose_influence()


class Extortion(Action):
    def __init__(self, target):
        Action.__init__(self)
        self.target = target
        self.card = constants.CAPTAIN
        self.blockers = [constants.CAPTAIN, constants.INQUISITOR]

    def resolve_action(self, current_player):
        if self.target.get_coins() >= 2:
            current_player.delta_coins(2)
            self.target.delta_coins(-2)
        elif self.target.get_coins() == 1:
            current_player.delta_coins(1)
            self.target.delta_coins(-1)