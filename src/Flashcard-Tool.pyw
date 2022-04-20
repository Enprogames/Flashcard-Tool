#!/usr/bin/env python

"""
Handles initialization of all functionality for flashcard program.

Author: Ethan Posner
Date: July 27, 2021
"""

import os
import sys

skip_notion_retrieval = False
debug = False

ROOT_DIR = ''
if os.path.basename(os.getcwd()) == 'src':
    ROOT_DIR = ''
else:
    ROOT_DIR = 'src'

if not debug:
    # clear file contents frm previous sessions
    open(os.path.join(ROOT_DIR, 'console.log'), '+w')
    sys.stdout = open(os.path.join(ROOT_DIR, 'console.log'), 'a')
    sys.stderr = open(os.path.join(ROOT_DIR, 'console.log'), 'a')


from typing import Dict, List, Tuple
import time
import csv
import notion_parse
from flashcard import FlashcardSet, Flashcard
from window import Root, ItemSelectionFrame, FlashcardFrame
import tkinter as tk
from threading import Thread

BACKGROUND_COLOR = "#191919"
# BACKGROUND_COLOR = "#24292e"
# BACKGROUND_COLOR = '#946b46'

current_frame = None
current_frame_index = 0

flashcard_csv_file_folder = "csv_flashcard_files"

flashcard_data_path = os.path.join(ROOT_DIR, flashcard_csv_file_folder)

current_folder = os.path.basename(os.getcwd())


class AsyncDataRetriever(Thread):
    """
    Asynchronously downloads flashcard data from notion databases. This allows the program to continue running while data is being retrieved.
    """
    def __init__(self):
        super().__init__()

    def run(self):
        try:

            start = time.perf_counter()

            # get flashcard data from notion databases
            shared_db_ids = notion_parse.get_shared_dbs()
            flashcard_sets: List[FlashcardSet] = []

            # create the flashcard sets from notion data in each shared database
            for key, value in shared_db_ids.items():
                notion_db_data_tuple = notion_parse.get_flashcard_data_tuples(value)

                flashcard_sets.append(FlashcardSet(key, data_tuple_list=notion_db_data_tuple))

            # save flashcards to csv files
            for card_set in flashcard_sets:
                card_set.save_to_csv(flashcard_data_path)

        except Exception as e:
            print(f"Something went wrong while retrieving flashcard data from notion: {e}")

        print(f"New flashcard data successfully retrieved from notion in {round(time.perf_counter()-start, 2)} seconds")


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


def get_new_notion_data():
    global flashcard_sets, card_set_selection_frame, current_frame, flashcard_set_names

    # retrieve new flashcard data from notion and save it in csv files
    if not skip_notion_retrieval:
        try:

            downloader = AsyncDataRetriever()
            downloader.daemon = True
            downloader.start()

        except Exception as e:
            print(f"Something went wrong when retrieving or parsing flashcard data from notion: {e}")

    else:
        print("notion retrieval skipped")

    def wait():
        global flashcard_sets, card_set_selection_frame, current_frame, flashcard_set_names
        if downloader.is_alive():
            root.after(500, wait)
        else:  # Once the downloader is finished, load flashcard data from csv files
            flashcard_set_names = []
            flashcard_sets = get_flashcard_data(flashcard_data_path)
            card_set_selection_frame = ItemSelectionFrame(root, flashcard_set_names, start_command=view_sets,
                                                          refresh_command=get_new_notion_data, bg=BACKGROUND_COLOR)
            show_frame(card_set_selection_frame)

    wait()


def goto_main():

    global current_frame

    current_frame.pack_forget()
    card_set_selection_frame.pack(fill="both", expand=True)
    current_frame = card_set_selection_frame


def show_frame(frame):
    global current_frame

    current_frame.pack_forget()
    frame.pack(fill="both", expand=True)
    current_frame = frame


def view_sets():

    cards_to_present: List[Flashcard] = []

    # determine which sets have been selected using check marks and append them to the selected_sets list accordingly
    selected_sets_values: Dict[str: bool] = card_set_selection_frame.enable
    for set in flashcard_sets:
        if selected_sets_values[set.name].get():
            for card in set.cards:
                if not card.exclude:
                    cards_to_present.append(card)

    # retreive all custom settings. These are retrieved through tkinter Booleanvars which are associated with whether the checkbuttons are checked
    random_order = card_set_selection_frame.randomize
    read_aloud = card_set_selection_frame.read_aloud.get()  # whether or not to read each card out loud when it is presented
    definition_first = card_set_selection_frame.reverse_order.get()
    autoflip = card_set_selection_frame.autoflip.get()
    autoflip_interval = float(card_set_selection_frame.autoflip_interval_box.get())

    # if any sets are selected, present the first card
    if cards_to_present:
        flashcard_series = FlashcardFrame(root, cards_to_present, random_order=random_order, definition_first=definition_first, bg=BACKGROUND_COLOR,
                                          autoflip=autoflip, autoflip_interval=autoflip_interval, read_aloud=read_aloud, quit_cmd=goto_main,
                                          root_dir=ROOT_DIR)
        show_frame(flashcard_series)
        flashcard_series.next()


# initialize the root window
root = Root(width=1000, height=600)
root.lift()

loading_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
loading_label = tk.Label(loading_frame, text='Loading New Flashcard Data...', font=('consolas', 20, 'bold'), fg='white', bg=BACKGROUND_COLOR)
loading_label.place(relx=.5, rely=.5, anchor="c")
loading_frame.pack(fill="both", expand=True)
root.update()

flashcard_set_names = []


flashcard_sets = get_flashcard_data(flashcard_data_path)

loading_frame.pack_forget()
# Present the flashcard sets as selectable items
card_set_selection_frame = ItemSelectionFrame(root, flashcard_set_names, start_command=view_sets,
                                              refresh_command=get_new_notion_data, bg=BACKGROUND_COLOR)
card_set_selection_frame.pack(fill="both", expand=True)
current_frame = card_set_selection_frame

get_new_notion_data()

root.mainloop()
