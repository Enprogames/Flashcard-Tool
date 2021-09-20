"""
Manipulation and storage of flashcard data

Author: Ethan Posner
Date: July 27, 2021
"""

import os
import pickle

class Flashcard:
    """
    Store and manipulate data for flashcard. Flashcards are used for memorization of large amounts of information.
    They typically consist of terms and definitions.

    In the future,
    """

    def __init__(self, term: str, definition: str = ""):

        self.term: str = term
        self.definition = definition

    def pickle(self):
        if not os.path.exists('/flashcards'):
            os.mkdir('/flashcards')

        with open(os.path.join('flashcards', self.term), 'wb') as pickle_file:
            pickle.dump(self, pickle_file)
    
    def __len__(self):
        return len(self.term)


class FlashcardSet:
    """
    
    """

    def __init__(self, name: str, flashcard_data: dict = {}, description: str = ""):

        self.name = name
        self.description = description

        self.cards = [Flashcard(term, definition) for term, definition in flashcard_data.items()]

    def add_card(self, term: str, definition: str = ""):
        self.cards.append(Flashcard(term, definition))
    
    def __str__(self):
        card_output = ""
        longest_item_len = len(max(self.cards, key=len))

        for i, card in enumerate(self.cards):
            if i < len(self.cards)-1:
                card_output += f"\t{card.term:{longest_item_len}}: {card.definition}\n"
            else:
                card_output += f"\t{card.term:{longest_item_len}}: {card.definition}"


        return f"{self.name} Flashcard Set. Cards:\n{card_output}"