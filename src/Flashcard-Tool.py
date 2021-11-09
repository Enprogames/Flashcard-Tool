#!/usr/bin/env python

"""
Handles initialization of all functionality for flashcard program.

Author: Ethan Posner
Date: July 27, 2021
"""

from typing import Dict, List, Tuple
import pyttsx3
import random
import time
import csv
import os
import notion_parse
from flashcard import FlashcardSet
from window import Root, ItemSelectionFrame, FlashcardFrame

current_frame = None
current_frame_index = 0

flashcard_csv_file_folder = "csv_flashcard_files"

flashcard_data_path = os.path.join("src", flashcard_csv_file_folder)
if os.path.exists(os.path.join("src", flashcard_csv_file_folder)):
    flashcard_data_path = os.path.join("src", flashcard_csv_file_folder)
else:
    flashcard_data_path = flashcard_csv_file_folder

current_folder = os.path.basename(os.getcwd())


def text_to_speech(text: str):
    """
    Copied from stackoverflow: https://stackoverflow.com/questions/63044176/how-to-get-pyttsx3-to-read-a-line-but-not-wait
    """
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 220)
    engine.say(text)
    engine.runAndWait()
    del engine

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

    def next_item():
        global current_frame, current_frame_index

        if current_frame_index >= len(cards_to_present)-1:
            next_command = goto_main
        else:
            next_command = next_item

        term = cards_to_present[current_frame_index].term
        definition = cards_to_present[current_frame_index].definition

        new_flashcard = FlashcardFrame(root, term=definition if definition_first else term, definition=term if definition_first else definition,
                                        next_command=next_command, quit_command=goto_main, definition_first=definition_first)

        # change the frame to the new flashcard
        show_frame(new_flashcard)
        current_frame = new_flashcard

        # debug code to make sure the text-to-speech functionality works
        if read_aloud:
            time.sleep(0.2)
            text_to_speech("hello")

        current_frame_index += 1

    cards_to_present = []

    # determine which sets have been selected using check marks and append them to the selected_sets list accordingly
    selected_sets_values = card_set_selection_frame.enable
    for set in flashcard_sets:
        if selected_sets_values[set.name].get():
            for card in set.cards:
                if not card.exclude:
                    cards_to_present.append(card)

    # if the randomize checkbox has been selected, randomize the order of the flashcards
    if card_set_selection_frame.randomize:
        random.shuffle(cards_to_present)

    read_aloud = card_set_selection_frame.read_aloud.get()  # whether or not to read each card out loud when it is presented

    definition_first = card_set_selection_frame.reverse_order.get()

    print(f"number of cards selected: {len(cards_to_present)}")

    # if any sets are selected, present the first card
    if cards_to_present:
        next_item()


root = Root(width=1000, height=600)
root.lift()

flashcard_set_names = []

try:
    #raise ValueError("notion retrieval skipped")
    start = time.perf_counter()

    # get flashcard data from notion databases
    shared_db_ids = notion_parse.get_shared_dbs()
    flashcard_sets = []

    # create the flashcard sets from notion data in each shared database
    for key, value in shared_db_ids.items():
        notion_db_data_tuple = notion_parse.get_flashcard_data_tuples(value)

        flashcard_sets.append(FlashcardSet(key, data_tuple_list=notion_db_data_tuple))

    # save flashcards to csv files
    for card_set in flashcard_sets:
        card_set.save_to_csv(flashcard_data_path)
    print(f"New flashcard data successfully retrieved from notion in {round(time.perf_counter()-start, 2)} seconds")

except Exception as e:
    print(f"Something went wrong when retrieving or parsing flashcard data from notion: {e}")


flashcard_sets = []
# read all csv files and use their data for the flashcards
for csv_file in os.listdir(flashcard_data_path):
    flashcard_tuple_list: List[Tuple[str, str, bool]] = []

    # make sure the file is a csv file
    if csv_file[-4:] == '.csv':
        with open(os.path.join(flashcard_data_path, f'{csv_file}'), 'r') as f:

            reader = csv.reader(f)
            next(reader)
            for line in reader:
                if len(line) >= 2:
                    term = line[0]
                    definition = line[1]
                    exclude = True if len(line) > 2 and line[2] == 'True' else False

                    flashcard_tuple_list.append((term, definition, exclude))

        set_name = os.path.basename(f.name)[:-4]
        flashcard_sets.append(FlashcardSet(set_name, data_tuple_list=flashcard_tuple_list))
        flashcard_set_names.append(set_name)
            

card_set_selection_frame = ItemSelectionFrame(root, flashcard_set_names, start_command=view_sets)
card_set_selection_frame.pack(fill="both", expand=True)
current_frame = card_set_selection_frame

root.mainloop()
