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

    def __init__(self, term, definition=None):

        self.term: str = term
        self.definition = definition

    def pickle(self):
        if not os.path.exists('/flashcards'):
            os.mkdir('/flashcards')

        with open(os.path.join('flashcards', self.term), 'wb') as pickle_file:
            pickle.dump(self, pickle_file)
