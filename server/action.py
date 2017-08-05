import constants


class Action:
    target = None
    blockers = None
    card = None

    def __init__(self):
        pass

    def get_identifier(self):
        pass

    def resolve_action(self, current_player=None, deck=None):
        pass

    def is_valid(self, players, player_index):
        # TODO validation
        return True

    @staticmethod
    def decode_action_from_dict(dict, players):
        if dict['action'] == constants.INCOME:
            return Income()
        elif dict['action'] == constants.FOREIGN_AID:
            return ForeignAid()
        elif dict['action'] == constants.COLLECT_TAXES:
            return CollectTaxes()
        elif dict['action'] == constants.ASSASSINATE:
            return Assassinate(get_player_by_name(players, dict['target']))
        elif dict['action'] == constants.EXTORTION:
            return Extortion(get_player_by_name(players, dict['target']))
        elif dict['action'] == constants.INVESTIGATE:
            return Investigate(get_player_by_name(players, dict['target']))
        elif dict['action'] == constants.EXCHANGE:
            return Exchange()
        elif dict['action'] == constants.COUP:
            return CoupDEtat(get_player_by_name(players, dict['target']))


class CoupDEtat(Action):
    def __init__(self, target):
        Action.__init__(self)
        self.target = target

    def get_identifier(self):
        return constants.COUP

    def resolve_action(self, current_player=None, deck=None):
        current_player.delta_coins(-7)
        return self.target.lose_influence()


class ForeignAid(Action):
    def __init__(self):
        Action.__init__(self)
        self.blockers = [constants.DUKE]

    def get_identifier(self):
        return constants.FOREIGN_AID

    def resolve_action(self, current_player=None, deck=None):
        current_player.delta_coins(2)


class Income(Action):
    def __init__(self):
        Action.__init__(self)

    def get_identifier(self):
        return constants.INCOME

    def resolve_action(self, current_player=None, deck=None):
        current_player.delta_coins(1)


class CollectTaxes(Action):
    def __init__(self):
        Action.__init__(self)
        self.card = constants.DUKE

    def get_identifier(self):
        return constants.COLLECT_TAXES

    def resolve_action(self, current_player=None, deck=None):
        current_player.delta_coins(3)


class Investigate(Action):
    def __init__(self, target):
        Action.__init__(self)
        self.target = target
        self.card = constants.INVESTIGATE

    def get_identifier(self):
        return constants.INVESTIGATE

    def resolve_action(self, current_player=None, deck=None):
        target_card = self.target.request_give_card_to_inquisitor(current_player)
        if current_player.request_show_card_to_inquisitor(self.target, target_card):
            self.target.send_card_back_to_deck_and_draw_card(deck, target_card)


class Exchange(Action):
    def __init__(self):
        Action.__init__(self)
        self.card = constants.EXCHANGE

    def get_identifier(self):
        return constants.EXCHANGE

    def resolve_action(self, current_player=None, deck=None):
        new_card = deck.draw_card()
        removed_card = current_player.request_inquisitor_choose_card_to_return(new_card)
        current_player.change_cards(deck, new_card, removed_card)


class Assassinate(Action):
    def __init__(self, target):
        Action.__init__(self)
        self.target = target
        self.card = constants.ASSASSIN
        self.blockers = [constants.CONTESSA]

    def get_identifier(self):
        return constants.ASSASSINATE

    def resolve_action(self, current_player=None, deck=None):
        current_player.delta_coins(-3)
        return self.target.lose_influence()


class Extortion(Action):
    def __init__(self, target):
        Action.__init__(self)
        self.target = target
        self.card = constants.CAPTAIN
        self.blockers = [constants.CAPTAIN, constants.INQUISITOR]

    def get_identifier(self):
        return constants.EXTORTION

    def resolve_action(self, current_player=None, deck=None):
        if self.target.get_coins() >= 2:
            current_player.delta_coins(2)
            self.target.delta_coins(-2)
        elif self.target.get_coins() == 1:
            current_player.delta_coins(1)
            self.target.delta_coins(-1)


def get_player_by_name(players, player_name):
    for player in players:
        if player.id == player_name:
            return player
    return None


