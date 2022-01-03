#!/usr/bin/env python

"""
Handles initialization of all functionality for flashcard program.

Author: Ethan Posner
Date: July 27, 2021
"""

from typing import List, Tuple
import pyttsx3
import random
import time
import csv
import os
import notion_parse
from flashcard import FlashcardSet
from window import Root, ItemSelectionFrame, FlashcardFrame
import tkinter as tk

current_frame = None
current_frame_index = 0

flashcard_csv_file_folder = "csv_flashcard_files"

flashcard_data_path = os.path.join("src", flashcard_csv_file_folder)
if os.path.exists(os.path.join("src", flashcard_csv_file_folder)):
    flashcard_data_path = os.path.join("src", flashcard_csv_file_folder)
else:
    flashcard_data_path = flashcard_csv_file_folder

current_folder = os.path.basename(os.getcwd())


def get_flashcard_data(data_path: str):
    "read all csv files and use their data for the flashcards"

    flashcard_sets = []

    for csv_file in os.listdir(data_path):
        flashcard_tuple_list: List[Tuple[str, str, bool]] = []

        # make sure the file is a csv file
        if csv_file[-4:] == '.csv':
            with open(os.path.join(data_path, f'{csv_file}'), 'r') as f:

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

    return flashcard_sets


def text_to_speech(text: str):
    """
    Copied from stackoverflow: https://stackoverflow.com/questions/63044176/how-to-get-pyttsx3-to-read-a-line-but-not-wait
    """
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 220)
    engine.setProperty('volume', 0.5)
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

    global current_frame, current_frame_index, term, definition

    current_frame_index = 0

    def card_flip():
        global term, definition

        if read_aloud:
            root.update()

            text_to_speech(definition if not definition_first else term)

    def next_item():
        global current_frame, current_frame_index, term, definition

        # the next button on the card frame should go to the next card, unless it is the last card
        if current_frame_index >= len(cards_to_present)-1:
            next_command = goto_main
        else:
            next_command = next_item

        term = cards_to_present[current_frame_index].term
        definition = cards_to_present[current_frame_index].definition

        new_flashcard = FlashcardFrame(root, term=term, definition=definition, flip_command=card_flip,
                                       next_command=next_command, quit_command=goto_main, definition_first=definition_first,
                                       num_of_cards=len(cards_to_present))
        new_flashcard.set_current_card_num(current_frame_index+1)

        # change the frame to the new flashcard
        show_frame(new_flashcard)
        current_frame = new_flashcard

        current_frame_index += 1
        root.update()

        # debug code to make sure the text-to-speech functionality works
        if read_aloud:
            text_to_speech(term)

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


# initialize the root window
root = Root(width=1000, height=600)
root.lift()

loading_frame = tk.Frame(root, bg='#263238')
loading_label = tk.Label(loading_frame, text='Loading New Flashcard Data...', font=('consolas', 20, 'bold'), fg='white', bg='#263238')
loading_label.place(relx=.5, rely=.5, anchor="c")
loading_frame.pack(fill="both", expand=True)
root.update()

flashcard_set_names = []

# retrieve new flashcard data from notion and save it in csv files
try:
    raise ValueError("notion retrieval skipped")
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


# Load flashcard data from csv files

flashcard_sets = get_flashcard_data(flashcard_data_path)

loading_frame.pack_forget()

# Present the flashcard sets as selectable items

card_set_selection_frame = ItemSelectionFrame(root, flashcard_set_names, start_command=view_sets)
card_set_selection_frame.pack(fill="both", expand=True)
current_frame = card_set_selection_frame

root.mainloop()
