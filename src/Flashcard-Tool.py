#!/usr/bin/env python

"""
Handles initialization of all functionality for flashcard program.

Author: Ethan Posner
Date: July 27, 2021
"""

import notion_parse
from flashcard import Flashcard, FlashcardSet
from window import Root, ItemSelectionFrame, FlashcardFrame, LoginFrame

current_frame = None
current_frame_index = 0

def goto_main():

    global current_frame

    current_frame.pack_forget()
    card_set_selection_frame.pack(fill="both", expand=True)
    current_frame = card_set_selection_frame

def show_frame(frame):

    current_frame.pack_forget()
    frame.pack(fill="both", expand=True)

def view_sets():

    global current_frame, current_frame_index

    current_frame_index = 0

    def next_card():
        global current_frame, current_frame_index

        current_frame_index += 1
        
        if current_frame_index >= len(cards_to_present)-1:
            new_flashcard = FlashcardFrame(root, term=cards_to_present[current_frame_index].term, definition=cards_to_present[current_frame_index].definition, next_command=goto_main, quit_command=goto_main)
        else:
            new_flashcard = FlashcardFrame(root, term=cards_to_present[current_frame_index].term, definition=cards_to_present[current_frame_index].definition, next_command=next_card, quit_command=goto_main)
        show_frame(new_flashcard)
        current_frame = new_flashcard



    cards_to_present = []

    # determine which sets have been selected using check marks and append them to the selected_sets list accordingly
    selected_sets_values = card_set_selection_frame.enable
    for set in flashcard_sets:
        if selected_sets_values[set.name].get():
            for card in set.cards:
                cards_to_present.append(card)

    # if any sets are selected, present the first card
    if cards_to_present:
        if len(cards_to_present) > 1:
            first_card_frame = FlashcardFrame(root, term=cards_to_present[0].term, definition=cards_to_present[0].definition, next_command=next_card, quit_command=goto_main)
        else:
            first_card_frame = FlashcardFrame(root, term=cards_to_present[0].term, definition=cards_to_present[0].definition, next_command=goto_main, quit_command=goto_main)
        show_frame(first_card_frame)
        current_frame = first_card_frame
    

root = Root(width=1000, height=600)
root.lift()

db_id = "2a59b9e1b3b9459eb5fdf64346408b38"
database_items = notion_parse.get_db(db_id)
shared_db_ids = notion_parse.get_shared_dbs()
flashcard_sets = []
for key, value in shared_db_ids.items():
    flashcard_sets.append(FlashcardSet(key, notion_parse.get_flashcard_db_dict(value)))

card_set_selection_frame = ItemSelectionFrame(root, list(shared_db_ids.keys()), start_command=view_sets)
card_set_selection_frame.pack(fill="both", expand=True)
current_frame = card_set_selection_frame

root.mainloop()
