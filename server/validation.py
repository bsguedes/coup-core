import constants


class Validation:
    @staticmethod
    def check_table_correctness(players, deck):
        cards = list()
        for i in range(3):
            cards.append(constants.ASSASSIN)
            cards.append(constants.CAPTAIN)
            cards.append(constants.CONTESSA)
            cards.append(constants.DUKE)
            cards.append(constants.INQUISITOR)
        for player in players:
            for card in player.cards:
                cards.remove(card)
            for card in player.dead_cards:
                cards.remove(card)
        for card in deck.cards:
            cards.remove(card)
        return len(cards) == 0
