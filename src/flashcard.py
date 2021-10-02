"""
Manipulation and storage of flashcard data

Author: Ethan Posner
Date: July 27, 2021
"""

import os
import csv
from typing import List, Tuple

class Flashcard:
    """
    Store and manipulate data for flashcard. Flashcards are used for memorization of large amounts of information.
    They typically consist of terms and definitions.

    In the future,
    """

    def __init__(self, term: str, definition: str = "", exclude: bool = False):

        self.term: str = term
        self.definition = definition
        self.exclude = exclude
    
    def __len__(self):
        return len(self.term)


class FlashcardSet:
    """
    
    """

    def __init__(self, name: str, definition_dict: dict = {}, description: str = "", data_tuple_list: List[Tuple[str, str, bool]]=None):
        """
        Load flashcards in one of two ways:
        - data_tuple_list: A list of tuples in the form: (term, definition, exclude)
        - definition_dict: Dictionary of terms and their definitions. Does not allow for some cards to be excluded.
        """

        self.name = name
        self.description = description

        if data_tuple_list:
            self.cards = [Flashcard(str(data_tuple[0]), str(data_tuple[1]), exclude=True if data_tuple[2] == 'True' else False) for data_tuple in data_tuple_list]
        else:
            self.cards = [Flashcard(term, definition) for term, definition in definition_dict.items()]

    def add_card(self, term: str, definition: str = ""):
        self.cards.append(Flashcard(term, definition))
    
    def save_to_csv(self, path="flashcard_data", name=""):

        if name == "":
            name = self.name
        
        if not os.path.exists(path):
            os.mkdir(path)
        
        with open(os.path.join(path, name), 'w', newline='') as f:

            writer = csv.writer(f)

            writer.writerow(['Term', 'Definition', 'Exclude'])

            flashcard_data_rows = []

            for card in self.cards:
                row = [card.term, card.definition, card.exclude]
                flashcard_data_rows.append(row)
                
            writer.writerows(flashcard_data_rows)
    
    def __str__(self):
        card_output = ""
        longest_item_len = len(max(self.cards, key=len))

        for i, card in enumerate(self.cards):
            if i < len(self.cards)-1:
                card_output += f"\t{card.term:{longest_item_len}}: {card.definition}\n"
            else:
                card_output += f"\t{card.term:{longest_item_len}}: {card.definition}"


        return f"{self.name} Flashcard Set. Cards:\n{card_output}"