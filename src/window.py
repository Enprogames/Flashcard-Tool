"""
Handles all windows and displaying of information for flashcard program.

Author: Ethan Posner
Date: July 27, 2021
"""

import os
from pathlib import Path
import random
import time

import tkinter as tk
from text_to_speech import TextToSpeech
from PIL import Image, ImageTk

from database.models import Flashcard


class Root(tk.Tk):
    """
    Main object which handles all frames (current display of widgets) for window
    """

    def __init__(
        self,
        get_flashcard_data_func,
        image_path,
        width=600,
        height=400,
        bg='#263238',
        font_type='consolas',
    ):

        tk.Tk.__init__(self)
        self.width = width
        self.height = height
        self.bg = bg
        self.font_type = font_type
        self.configure(bg=self.bg)
        self.geometry(f"{width}x{height}")
        self.resizable(0, 0)

        self.item_selection_frame = None
        self.flashcard_series_frame = None

        self.get_flashcard_data_func = get_flashcard_data_func
        self.image_path = image_path

    def goto_main(self):
        self.update_list()

    def start_button_press(self):
        cards_to_present: list[Flashcard] = []

        # determine which sets have been selected using check marks and append them to the selected_sets list accordingly
        selected_sets_values: dict[str: bool] = self.item_selection_frame.enable

        for set in self.flashcard_sets:
            if selected_sets_values[set.name].get():
                for card in set.flashcards:
                    if not card.exclude:
                        cards_to_present.append(card)

        # retreive all custom settings. These are retrieved through tkinter Booleanvars which are associated with whether the checkbuttons are checked
        random_order = self.item_selection_frame.randomize
        read_aloud = self.item_selection_frame.read_aloud.get()  # whether or not to read each card out loud when it is presented
        definition_first = self.item_selection_frame.reverse_order.get()
        autoflip = self.item_selection_frame.autoflip.get()
        autoflip_interval = float(self.item_selection_frame.autoflip_interval_box.get())

        # if any sets are selected, present the first card
        if cards_to_present:
            self.start_flashcards(
                cards_to_present,
                random_order=random_order,
                definition_first=definition_first,
                autoflip=autoflip,
                autoflip_interval=autoflip_interval,
                read_aloud=read_aloud
            )

    def start_flashcards(
        self,
        cards_to_present: list[Flashcard],
        random_order=False,
        definition_first=False,
        read_aloud=False,
        autoflip=False,
        autoflip_interval=0
    ):
        self.flashcard_series_frame = FlashcardFrame(
                self,
                cards_to_present,
                random_order=random_order,
                definition_first=definition_first,
                bg=self.bg,
                font_type=self.font_type,
                autoflip=autoflip,
                autoflip_interval=autoflip_interval,
                read_aloud=read_aloud,
                quit_cmd=self.goto_main,
                image_path=self.image_path
        )

        if self.item_selection_frame:
            self.item_selection_frame.pack_forget()

        self.flashcard_series_frame.pack(fill="both", expand=True)
        self.flashcard_series_frame.next()

    def update_list(self):
        """
        Refresh the list of flashcard sets
        """

        self.flashcard_sets = self.get_flashcard_data_func()
        flashcard_set_names = [set.name for set in self.flashcard_sets]

        if self.item_selection_frame is not None:
            self.item_selection_frame.pack_forget()
        if self.flashcard_series_frame is not None:
            self.flashcard_series_frame.pack_forget()

        self.item_selection_frame = ItemSelectionFrame(
            self,
            items=flashcard_set_names,
            start_command=self.start_button_press,
            refresh_command=self.update_list,
            bg=self.bg,
            font_type=self.font_type
        )
        self.item_selection_frame.pack(
            side=tk.LEFT,
            fill="both",
            expand=True
        )


class ItemSelectionFrame(tk.Frame):
    """
    List of items to check off for selection
    """

    def __init__(
        self,
        parent,
        items=[], 
        start_command=None,
        refresh_command=None,
        width=600,
        height=600,
        bg='#263238',
        font_type='consolas'
    ):

        tk.Frame.__init__(self, parent, width=width, height=height, bg=bg)
        self.bg = bg
        self.parent = parent
        self.width = width
        self.height = height
        self.font_type = font_type

        self.list_items = items
        self.start_command = start_command
        self.refresh_command = refresh_command

        # display all flashcard sets for selection
        self.scrollable_item_selection = tk.Frame(self, width=400, height=600, bg='white')
        self.scrollable_canvas = tk.Canvas(self.scrollable_item_selection, bg=self.bg, highlightthickness=0, width=400)
        self.item_selection_scrollbar = tk.Scrollbar(self.scrollable_item_selection, orient='vertical',
                                                     command=self.scrollable_canvas.yview, bg=bg)

        # create a frame for the scrollable items to exist in and bind it to a command which changes their position as the scrollbar moves
        self.scrollable_items_frame = tk.Frame(self.scrollable_canvas, width=0, height=0, bg=bg)
        self.scrollable_items_frame.bind("<Configure>", lambda e: self.scrollable_canvas.configure(scrollregion=self.scrollable_canvas.bbox("all")))

        # set up the scrolling canvas in the
        self.scrollable_canvas.create_window((0, 0), window=self.scrollable_items_frame, anchor="nw")
        self.scrollable_canvas.config(yscrollcommand=self.item_selection_scrollbar.set)

        self.enable = {}
        for i, list_item in enumerate(self.list_items):
            self.enable[list_item] = tk.BooleanVar(value=False)
            checkbox = tk.Checkbutton(
                self.scrollable_items_frame, text=list_item, variable=self.enable[list_item], foreground='white', bg=self.bg,
                onvalue=True, offvalue=False, font=(self.font_type, 15, 'normal'), selectcolor='black')
            checkbox.grid(row=i, column=0, sticky=tk.W)

        self.item_selection_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollable_canvas.pack(side=tk.LEFT, fill="both", expand=True)
        self.scrollable_item_selection.pack(padx=5, pady=5, side=tk.LEFT, fill="both", expand=True)

        # -- session customization -- #
        self.options_frame = tk.Frame(self, width=300, height=100, bg=self.bg)

        self.read_aloud = tk.BooleanVar()
        self.read_aloud_checkbutton = tk.Checkbutton(self.options_frame, text="Read Text Aloud", variable=self.read_aloud, foreground='white',
                                                     bg=self.bg, onvalue=True, offvalue=False, font=(self.font_type, 15, 'normal'), selectcolor='black')
        self.read_aloud_checkbutton.grid(row=1, column=1, sticky='w')

        self.reverse_order = tk.BooleanVar()
        self.reverse_checkbutton = tk.Checkbutton(self.options_frame, text="Show Definition First", variable=self.reverse_order, foreground='white',
                                                  bg=self.bg, onvalue=True, offvalue=False, font=(self.font_type, 15, 'normal'), selectcolor='black')
        self.reverse_checkbutton.grid(row=2, column=1, sticky='w')

        self.randomize = tk.BooleanVar()
        self.random_checkbutton = tk.Checkbutton(
            self.options_frame, text="Random Order", variable=self.randomize, foreground='white', bg=self.bg,
            onvalue=True, offvalue=False, font=(self.font_type, 15, 'normal'), selectcolor='black')
        self.random_checkbutton.grid(row=3, column=1, sticky='w')
        self.random_checkbutton.toggle()

        self.autoflip = tk.BooleanVar()
        self.autoflip_checkbutton = tk.Checkbutton(
            self.options_frame, text="Autoflip After ", variable=self.autoflip, foreground='white', bg=self.bg,
            onvalue=True, offvalue=False, font=(self.font_type, 15, 'normal'), selectcolor='black')
        self.autoflip_checkbutton.grid(row=4, column=1, sticky='w')

        self.autoflip_interval = tk.IntVar()

        # new frame for autoflip options
        self.autoflip_entry_frame = tk.Frame(self.options_frame)

        # put autoflip interval box inside of highlighted frame so that its border color can be changed
        self.autoflip_border_color = tk.Frame(self.autoflip_entry_frame, background=self.bg)
        self.autoflip_interval_box = tk.Entry(self.autoflip_border_color, width=5, foreground='white', bg=self.bg,
                                              font=(self.font_type, 15, 'normal'), textvariable=self.autoflip_interval)
        self.autoflip_interval_box.delete(0, tk.END)
        self.autoflip_interval_box.insert(0, "5")
        self.autoflip_interval_box.pack(padx=1, pady=1)
        self.autoflip_border_color.pack(side=tk.LEFT)
        self.seconds_label = tk.Label(self.autoflip_entry_frame, text="seconds", foreground='white', bg=self.bg, font=(self.font_type, 15, 'normal'))
        self.seconds_label.pack(side=tk.LEFT)

        self.autoflip_entry_frame.grid(row=5, column=1, sticky='w')

        self.start_button = tk.Button(self.options_frame, text='START', foreground='white',
                                      background='grey25', command=self.start_button_press, font=(self.font_type, 15, 'bold'))
        self.start_button.grid(row=6, column=1, sticky='w')

        self.options_frame.grid_rowconfigure(2, weight=1)

        self.options_frame.place(relx=0.97, rely=1, anchor="se")

        # used for refreshing list of flashcard sets
        self.refresh_button = tk.Button(self, text="RELOAD", foreground='white',
                                        background='grey25', command=self.refresh_command, font=(self.font_type, 15, 'bold'))
        self.refresh_button.place(relx=0.97, rely=1, anchor="se")

    def start_button_press(self):
        """
        Ran when self.start_button is pressed. Before continuing execution of the
        program, this will make sure user input is legible. If it is, self.start_command
        will be ran.
        """
        try:
            float(self.autoflip_interval_box.get())
            self.autoflip_input_error_reset()
            self.start_command()
        except ValueError:
            self.autoflip_input_error_alert()

    def autoflip_input_error_alert(self):
        """
        Alert the user that the value entered into the autoflip interval entry widget was invalid. Only numbers should be entered
        into the autoflip entry box.
        Right now, the box will be made red
        """
        self.autoflip_border_color.config(background='red')

    def autoflip_input_error_reset(self):
        """
        Remove the alert if the user input has been amended
        """
        self.autoflip_border_color.config(background=self.bg)


class FlashcardFrame(tk.Frame):
    """
    Frame which is used for presenting multiple flashcard frames
    """

    def __init__(
        self,
        parent,
        cards: list[Flashcard],
        image_path: os.PathLike,
        random_order=False,
        definition_first=False,
        quit_cmd=None,
        read_aloud=False,
        autoflip=False,
        autoflip_interval=0,
        width=600,
        height=400,
        bg='#263238',
        font_type='consolas',
        root_dir='',
        img_dir='img'
    ):

        tk.Frame.__init__(self, parent, width=width, height=height, bg=bg)
        self.parent = parent
        self.width = width
        self.height = height
        self.bg = bg
        self.font_type = font_type
        self.image_path = image_path

        self.cards = cards

        self.quit_cmd = quit_cmd
        self.read_aloud = read_aloud
        self.definition_first = definition_first
        self.autoflip = autoflip
        self.autoflip_interval = autoflip_interval
        self.autoflip_job = None
        self.definition_first = definition_first

        self.current_text = tk.StringVar(value="")  # term or definition

        self.card_label = tk.Label(self, textvariable=self.current_text, fg='white', bg=self.bg, font=(
            self.font_type, 20, 'bold' if not self.definition_first else 'normal'),
            justify='center', wraplength=800)
        self.card_label.pack(fill="x", expand=True)

        self.back_button = tk.Button(self, text="BACK", command=self.back, font=(self.font_type, 15, 'bold'))
        self.back_button.place(relx=0.4, rely=0.8, anchor="center")

        self.flip_button = tk.Button(self, text="FLIP", command=self.flip, font=(self.font_type, 15, 'bold'))
        self.flip_button.place(relx=0.5, rely=0.8, anchor="center")
        self.is_flipped = False  # allows for user to flip back to the term after seeing the definition

        self.next_button = tk.Button(self, text="NEXT", command=self.next, font=(self.font_type, 15, 'bold'))

        self.num_of_cards = len(self.cards)
        self.current_card_num = -1  # since the presentation of cards hasn't started yet, -1 is the current card
        self.current_card_text = tk.StringVar(value=f"{self.current_card_num}/{self.num_of_cards}")
        self.current_card_label = tk.Label(self, textvariable=self.current_card_text, font=(self.font_type, 15, 'bold'), fg='white',
                                           bg=self.bg)
        self.current_card_label.pack(side='top', anchor='ne', padx=10, pady=10)

        self.quit_button = tk.Button(self, text="QUIT", foreground='white', background='grey25', command=quit_cmd, font=(self.font_type, 20, 'bold'))
        self.quit_button.pack(side='top', anchor='ne', padx=10, pady=10)

        self.pause_autoflip = False  # a pause button will be used for pausing autoflipping if enabled
        if autoflip:
            pause_icon = Image.open(Path(self.image_path) / 'pause_icon2.png')
            pause_icon = ImageTk.PhotoImage(pause_icon.resize((50, 50)))
            label = tk.Label(image=pause_icon)
            label.image = pause_icon  # keep a reference of the image in the label
            self.autoflip_pause_button = tk.Button(self, image=pause_icon, command=self.toggle_pause_autoflip,
                                                   relief='raised', bd=3, background='grey25', compound='center', width=60, height=60)
            self.autoflip_pause_button.pack(side='top', anchor='nw', padx=10, pady=10)

            # used to keep track of how much longer to wait after pausing and unpausing
            self.autoflip_schedule_start = 0
            self.autoflip_schedule_elapsed = 0

        if random_order:
            random.shuffle(self.cards)

        if self.read_aloud:
            self.engine = TextToSpeech()
            # voices = self.engine.getProperty('voices')
            # self.engine.setProperty('voice', voices[1].id)
            # self.engine.setProperty('rate', 220)
            # self.engine.setProperty('volume', 0.5)

    def back(self):
        """
        Go to previous card. Activated if self.back_button is pressed
        """
        if self.autoflip_job:  # if a previously created autoflip event still exists, cancel and delete it
            self.winfo_toplevel().after_cancel(self.autoflip_job)
            self.autoflip_job = None

        if self.current_card_num > 0:  # don't want to go back on first card
            self.is_flipped = False
            self.next_button.place_forget()
            self.current_card_num -= 1
            self.current_card_text.set(f"{self.current_card_num+1}/{self.num_of_cards}")  # e.g. show that value with show as 1 instead of 0
            self.card_label.config(font=(self.font_type, 20,  'bold' if not self.definition_first else 'normal'))

            self.current_card = self.cards[self.current_card_num]
            self.current_text.set(self.current_card.term if not self.definition_first else self.current_card.definition)
            if self.read_aloud:
                self.parent.update()
                self.speak_text(self.current_card.term)

            # set an event for flipping the card after the set interval if autoflip is enabled
            if self.autoflip and not self.pause_autoflip:
                self.autoflip_job = self.winfo_toplevel().after(int(self.autoflip_interval*1000), self.flip if not self.is_flipped else self.next)
                self.autoflip_schedule_start = time.time() * 1000
                self.autoflip_schedule_elapsed = 0

    def flip(self):
        """
        Handles packing and pack_forgetting of various widgets, as well as changing text.

        Also handles text to speech of the current card, as well as cancelling an autoflip event if the user flipped before it was issued
        """

        if not self.is_flipped:
            self.is_flipped = True
            self.current_text.set(self.current_card.definition if not self.definition_first else self.current_card.term)
            self.card_label.config(font=(self.font_type, 20, 'normal' if not self.definition_first else 'bold'))

            self.next_button.place(relx=0.6, rely=0.8, anchor="center")  # insert the "next card" button

            if self.autoflip_job:  # see if the autoflip job exists. If so, cancel it
                self.winfo_toplevel().after_cancel(self.autoflip_job)
                self.autoflip_job = None

            if self.autoflip and not self.pause_autoflip:  # if autoflip is enabled, schedule another autoflip event
                self.autoflip_job = self.winfo_toplevel().after(int(self.autoflip_interval*1000), self.next)
                self.autoflip_schedule_start = time.time() * 1000
                self.autoflip_schedule_elapsed = 0
        else:  # if the card has already been flipped, flip back to the term
            self.is_flipped = False
            self.current_text.set(self.current_card.term if not self.definition_first else self.current_card.definition)
            self.card_label.config(font=(self.font_type, 20, 'bold' if not self.definition_first else 'normal'))

        if self.read_aloud:
            self.parent.update()
            self.speak_text(self.current_card.definition)

    def next(self):

        if self.autoflip_job:  # if a previously created autoflip event still exists, cancel and delete it
            self.winfo_toplevel().after_cancel(self.autoflip_job)
            self.autoflip_job = None

        # Quit if no more cards are left
        if self.current_card_num+1 >= len(self.cards):
            self.quit_cmd()
        else:  # Otherwise, prepare the next card
            self.is_flipped = False
            self.next_button.place_forget()
            self.current_card_num += 1
            self.current_card_text.set(f"{self.current_card_num+1}/{self.num_of_cards}")  # e.g. show that value with show as 1 instead of 0
            self.card_label.config(font=(self.font_type, 20,  'bold' if not self.definition_first else 'normal'))

            self.current_card = self.cards[self.current_card_num]
            self.current_text.set(self.current_card.term if not self.definition_first else self.current_card.definition)
            if self.read_aloud:
                self.parent.update()
                self.speak_text(self.current_card.term)

            # set an event for flipping the card after the set interval if autoflip is enabled
            if self.autoflip and not self.pause_autoflip:
                self.autoflip_job = self.winfo_toplevel().after(int(self.autoflip_interval*1000), self.flip if not self.is_flipped else self.next)
                self.autoflip_schedule_start = time.time() * 1000
                self.autoflip_schedule_elapsed = 0

    def toggle_pause_autoflip(self):
        if not self.pause_autoflip:
            self.autoflip_pause_button.config(relief="sunken")
            self.pause_autoflip = True
            if self.autoflip_job:  # see if the autoflip job exists. If so, cancel it
                self.winfo_toplevel().after_cancel(self.autoflip_job)
                self.autoflip_job = None
                self.autoflip_schedule_elapsed = time.time() * 1000 - self.autoflip_schedule_start
        else:
            self.autoflip_pause_button.config(relief="raised")
            self.pause_autoflip = False
            # start a new autoflip job starting where the last one left off
            self.autoflip_job = self.winfo_toplevel().after(int(self.autoflip_interval*1000-self.autoflip_schedule_elapsed), self.flip)
            self.autoflip_schedule_start = time.time() * 1000
            self.autoflip_schedule_elapsed = 0

    def speak_text(self, text):
        self.engine.play(text)


class LoginFrame(tk.Frame):

    def __init__(self, parent, login_function, back_function, width=600, height=400, bg='#263238'):

        tk.Frame.__init__(self, parent, width=width, height=height, bg="grey25")

        self.width = width
        self.height = height
        self.parent = parent
        self.login_function = login_function
        self.goto_register_function = back_function
        self.font_type = 'consolas'

        login_message_label = tk.Label(self, text="Login Failed", fg="grey25", bg="grey25",
                                       font=(self.font_type, 10, 'bold'))
        login_message_label.place(relx=.5, rely=.1, anchor="center")

        login_label = tk.Label(self, text="LOGIN", fg="white", bg="grey25", font=(self.font_type, 50, 'bold'))
        login_label.place(relx=.5, rely=.3, anchor="center")

        username_label = tk.Label(self, text="Username", font=(self.font_type, 10, 'bold'), bg="grey25", fg="white")
        username_label.place(relx=.5, rely=.45, anchor="center")
        username_box = tk.Entry(self, width="20")
        username_box.place(relx=.5, rely=.5, anchor="center")

        password_label = tk.Label(self, text="Password", font=(self.font_type, 10, 'bold'), bg="grey25", fg="white")
        password_label.place(relx=.5, rely=.6, anchor="center")
        password_box = tk.Entry(self, width="20")
        password_box.place(relx=.5, rely=.65, anchor="center")

        back_button = tk.Button(self, text="register", font=(self.font_type, 10, 'bold'), bg="white", fg="black",
                                command=back_function)
        back_button.place(relx=.45, rely=.85, anchor="center")

        login_button = tk.Button(self, text="login", font=(self.font_type, 10, 'bold'), bg="white", fg="black",
                                 command=login_function)
        login_button.place(relx=.55, rely=.85, anchor="center")
