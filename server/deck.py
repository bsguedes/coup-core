import constants
import random

class Deck:
    def __init__(self, repetitions):
        self.cards = list()
        for i in range(repetitions):
            self.cards.append(constants.ASSASSIN)
            self.cards.append(constants.CAPTAIN)
            self.cards.append(constants.CONTESSA)
            self.cards.append(constants.DUKE)
            self.cards.append(constants.INQUISITOR)

    def shuffle(self):
        for i in range(1000):
            self.swap(random.randint(len(self.cards)), random.randint(len(self.cards)))

    def swap(self, i, j):
        c = self.cards[i]
        self.cards[i] = self.cards[j]
        self.cards[j] = c

    def draw_card(self):
        self.shuffle()
        c = self.cards[0]
        self.cards.remove(c)
        return c

    def return_card(self, card):
        self.cards.append(card)
