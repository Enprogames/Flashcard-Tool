"""
Handles all windows and displaying of information for flashcard program.

Author: Ethan Posner
Date: July 27, 2021
"""

import math
import os
import random
import time
import tkinter as tk
from typing import List, Tuple
import pyttsx3
from PIL import Image, ImageTk

from flashcard import Flashcard


class Root(tk.Tk):
    """
    Main object which handles all frames (current display of widgets) for window
    """

    def __init__(self, width=600, height=400, bg='#263238'):

        tk.Tk.__init__(self)
        self.width = width
        self.height = height
        self.configure(bg=bg)
        self.geometry(f"{width}x{height}")
        self.resizable(0, 0)


class ItemSelectionFrame(tk.Frame):
    """
    List of items to check off for selection
    """

    def __init__(self, parent, items=[], start_command=None, refresh_command=None, width=600, height=600, bg='#263238'):

        tk.Frame.__init__(self, parent, width=width, height=height, bg=bg)
        self.bg = bg
        self.parent = parent
        self.width = width
        self.height = height

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
                onvalue=True, offvalue=False, font=('consolas', 15, 'normal'), selectcolor='black')
            checkbox.grid(row=i, column=0, sticky=tk.W)

        self.item_selection_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollable_canvas.pack(side=tk.LEFT, fill="both", expand=True)
        self.scrollable_item_selection.pack(padx=5, pady=5, side=tk.LEFT, fill="both", expand=True)

        # -- session customization -- #
        self.options_frame = tk.Frame(self, width=300, height=100, bg=self.bg)

        self.read_aloud = tk.BooleanVar()
        self.read_aloud_checkbutton = tk.Checkbutton(self.options_frame, text="Read Text Aloud", variable=self.read_aloud, foreground='white',
                                                     bg=self.bg, onvalue=True, offvalue=False, font=('consolas', 15, 'normal'), selectcolor='black')
        self.read_aloud_checkbutton.grid(row=1, column=1, sticky='w')

        self.reverse_order = tk.BooleanVar()
        self.reverse_checkbutton = tk.Checkbutton(self.options_frame, text="Show Definition First", variable=self.reverse_order, foreground='white',
                                                  bg=self.bg, onvalue=True, offvalue=False, font=('consolas', 15, 'normal'), selectcolor='black')
        self.reverse_checkbutton.grid(row=2, column=1, sticky='w')

        self.randomize = tk.BooleanVar()
        self.random_checkbutton = tk.Checkbutton(
            self.options_frame, text="Random Order", variable=self.randomize, foreground='white', bg=self.bg,
            onvalue=True, offvalue=False, font=('consolas', 15, 'normal'), selectcolor='black')
        self.random_checkbutton.grid(row=3, column=1, sticky='w')
        self.random_checkbutton.toggle()

        self.autoflip = tk.BooleanVar()
        self.autoflip_checkbutton = tk.Checkbutton(
            self.options_frame, text="Autoflip After ", variable=self.autoflip, foreground='white', bg=self.bg,
            onvalue=True, offvalue=False, font=('consolas', 15, 'normal'), selectcolor='black')
        self.autoflip_checkbutton.grid(row=4, column=1, sticky='w')

        self.autoflip_interval = tk.IntVar()

        # new frame for autoflip options
        self.autoflip_entry_frame = tk.Frame(self.options_frame)

        # put autoflip interval box inside of highlighted frame so that its border color can be changed
        self.autoflip_border_color = tk.Frame(self.autoflip_entry_frame, background=self.bg)
        self.autoflip_interval_box = tk.Entry(self.autoflip_border_color, width=5, foreground='white', bg=self.bg,
                                              font=('consolas', 15, 'normal'), textvariable=self.autoflip_interval)
        self.autoflip_interval_box.delete(0, tk.END)
        self.autoflip_interval_box.insert(0, "5")
        self.autoflip_interval_box.pack(padx=1, pady=1)
        self.autoflip_border_color.pack(side=tk.LEFT)
        self.seconds_label = tk.Label(self.autoflip_entry_frame, text="seconds", foreground='white', bg=self.bg, font=('consolas', 15, 'normal'))
        self.seconds_label.pack(side=tk.LEFT)

        self.autoflip_entry_frame.grid(row=5, column=1, sticky='w')

        self.start_button = tk.Button(self.options_frame, text='START', foreground='white',
                                      background='grey25', command=self.start_button_press, font=('consolas', 15, 'bold'))
        self.start_button.grid(row=6, column=1, sticky='w')

        self.options_frame.grid_rowconfigure(2, weight=1)

        self.options_frame.place(relx=0.97, rely=1, anchor="se")

        # used for refreshing list of flashcard sets
        self.refresh_button = tk.Button(self, text="RELOAD", foreground='white',
                                        background='grey25', command=self.refresh_command, font=('consolas', 15, 'bold'))
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

    def __init__(self, parent, cards: List[Flashcard], random_order=False, definition_first=False, quit_cmd=None, read_aloud=False, autoflip=False,
                 autoflip_interval=0, width=600, height=400, bg='#263238', root_dir='', img_dir='img'):

        tk.Frame.__init__(self, parent, width=width, height=height, bg=bg)
        self.parent = parent
        self.width = width
        self.height = height
        self.bg = bg

        self.cards = cards

        self.quit_cmd = quit_cmd
        self.read_aloud = read_aloud
        self.definition_first = definition_first
        self.autoflip = autoflip
        self.autoflip_interval = autoflip_interval
        self.autoflip_job = None
        self.definition_first = definition_first

        self.font_type = 'consolas'

        self.current_text = tk.StringVar(value="")  # term or definition

        self.card_label = tk.Label(self, textvariable=self.current_text, fg='white', bg=self.bg, font=(
            self.font_type, 20, 'bold' if not self.definition_first else 'normal'),
            justify='center', wraplength=800)
        self.card_label.pack(fill="x", expand=True)

        self.back_button = tk.Button(self, text="BACK", command=self.back, font=('consolas', 15, 'bold'))
        self.back_button.place(relx=0.4, rely=0.8, anchor="center")

        self.flip_button = tk.Button(self, text="FLIP", command=self.flip, font=('consolas', 15, 'bold'))
        self.flip_button.place(relx=0.5, rely=0.8, anchor="center")
        self.is_flipped = False  # allows for user to flip back to the term after seeing the definition

        self.next_button = tk.Button(self, text="NEXT", command=self.next, font=('consolas', 15, 'bold'))

        self.num_of_cards = len(self.cards)
        self.current_card_num = -1  # since the presentation of cards hasn't started yet, -1 is the current card
        self.current_card_text = tk.StringVar(value=f"{self.current_card_num}/{self.num_of_cards}")
        self.current_card_label = tk.Label(self, textvariable=self.current_card_text, font=('consolas', 15, 'bold'), fg='white',
                                           bg=self.bg)
        self.current_card_label.pack(side='top', anchor='ne', padx=10, pady=10)

        self.quit_button = tk.Button(self, text="QUIT", foreground='white', background='grey25', command=quit_cmd, font=('consolas', 20, 'bold'))
        self.quit_button.pack(side='top', anchor='ne', padx=10, pady=10)

        self.pause_autoflip = False  # a pause button will be used for pausing autoflipping if enabled
        if autoflip:
            pause_icon = Image.open(os.path.join(root_dir, img_dir, "pause_icon2.png"))
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
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', voices[1].id)
            self.engine.setProperty('rate', 220)
            self.engine.setProperty('volume', 0.5)

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
        self.engine.say(text)
        self.engine.runAndWait()


class LoginFrame(tk.Frame):

    def __init__(self, parent, login_function, back_function, width=600, height=400, bg='#263238'):

        tk.Frame.__init__(self, parent, width=width, height=height, bg="grey25")

        self.width = width
        self.height = height
        self.parent = parent
        self.login_function = login_function
        self.goto_register_function = back_function

        login_message_label = tk.Label(self, text="Login Failed", fg="grey25", bg="grey25",
                                       font=('consolas', 10, 'bold'))
        login_message_label.place(relx=.5, rely=.1, anchor="center")

        login_label = tk.Label(self, text="LOGIN", fg="white", bg="grey25", font=('consolas', 50, 'bold'))
        login_label.place(relx=.5, rely=.3, anchor="center")

        username_label = tk.Label(self, text="Username", font=('consolas', 10, 'bold'), bg="grey25", fg="white")
        username_label.place(relx=.5, rely=.45, anchor="center")
        username_box = tk.Entry(self, width="20")
        username_box.place(relx=.5, rely=.5, anchor="center")

        password_label = tk.Label(self, text="Password", font=('consolas', 10, 'bold'), bg="grey25", fg="white")
        password_label.place(relx=.5, rely=.6, anchor="center")
        password_box = tk.Entry(self, width="20")
        password_box.place(relx=.5, rely=.65, anchor="center")

        back_button = tk.Button(self, text="register", font=('consolas', 10, 'bold'), bg="white", fg="black",
                                command=back_function)
        back_button.place(relx=.45, rely=.85, anchor="center")

        login_button = tk.Button(self, text="login", font=('consolas', 10, 'bold'), bg="white", fg="black",
                                 command=login_function)
        login_button.place(relx=.55, rely=.85, anchor="center")


class PrettyLabel(tk.Canvas):
    """
    Incomplete. Doesn't work properly. Text doesn't appear entirely inside of the canvas
    Label with a background. If the foreground is light, the background will be black. Otherwise, it will be white.
    """
    def __init__(self, parent, text, fg='white', font=("Arial", 20, "normal"), outline_width=2, **kwargs):
        # the foreground label will be the main one for this object
        super(PrettyLabel, self).__init__(parent, **kwargs)
        self.parent = parent
        self.text = text

        self.fg = fg
        self.outline_width = outline_width

        self.bg_text_color = 'black' if self.is_light(self.parent.winfo_rgb(self.fg)) else 'white'

        self.text_bg_id = self.create_text(2, 50+self.outline_width, text=self.text, fill=self.bg_text_color, font=font)
        self.text_id = self.create_text(0, 50, text=self.text, fill=self.fg, font=font)

        self.move(self.text_bg_id, self.findXCenter(self.text_bg_id), 0)
        self.move(self.text_id, self.findXCenter(self.text_id), 0)

        # print(f"canvas pos: ({self.winfo_x()}, {self.winfo_y()}), size: ({self.winfo_width()}, {self.winfo_height()})")
        # print(f"text size and position: {self.bbox(self.text_id)}")

    def config(self, text=None, fg=None, font=None, **kwargs):
        """
        Change certain aspects of the labels and canvas
        """
        if text is not None:
            self.itemconfig(self.text_bg_id, text=text)
            self.itemconfig(self.text_id, text=text)
            self.move(self.text_bg_id, self.findXCenter(self.text_bg_id), 0)
            self.move(self.text_id, self.findXCenter(self.text_id), 0)

        if font is not None:
            self.itemconfig(self.text_bg_id, font=font)
            self.itemconfig(self.text_id, font=font)

        prev_fg = self.fg

        if fg is not None and not prev_fg == fg:
            self.fg = fg
            self.bg_text_color = 'black' if self.is_light(self.winfo_rgb(self.fg)) else 'white'
        super(PrettyLabel, self).config(**kwargs)  # apply any other canvas configuration settings
        self.itemconfig(self.text_bg_id, **kwargs)

    def is_light(self, rgbColor: Tuple[float, float, float]):
        """
        Return true if a color is light, else false.
        Copied from stackoverflow https://stackoverflow.com/questions/22603510/is-this-possible-to-detect-a-colour-is-a-light-or-dark-colour
        """
        [r, g, b] = rgbColor
        hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
        if (hsp > 127.5):
            return True
        else:
            return False

    def findXCenter(self, item):
        coords = self.bbox(item)
        xOffset = (self.winfo_reqwidth() / 2) - ((coords[2] - coords[0]) / 2)
        print(f"window size: {self.winfo_reqwidth()}, text location: {coords[2] - coords[0]}")
        return xOffset
