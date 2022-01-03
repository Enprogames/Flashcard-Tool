"""
Handles all windows and displaying of information for flashcard program.

Author: Ethan Posner
Date: July 27, 2021
"""

import tkinter as tk


def resize_font(number_of_characters, max_width):
    return 20
    return round(max_width * 1.6 / number_of_characters)


class Root(tk.Tk):
    """
    Main object which handles all frames (current display of widgets) for window
    """

    def __init__(self, width=600, height=400, background='#263238'):

        tk.Tk.__init__(self)
        self.width = width
        self.height = height
        self.configure(bg=background)
        self.geometry(f"{width}x{height}")
        self.resizable(0, 0)


class ItemSelectionFrame(tk.Frame):
    """
    List of items to check off for selection
    """

    def __init__(self, parent, items=[], start_command=None, width=600, height=600):

        tk.Frame.__init__(self, parent, width=width, height=height, bg='#263238')
        self.parent = parent
        self.width = width
        self.height = height

        self.list_items = items

        # display all flashcard sets for selection
        self.scrollable_item_selection = tk.Frame(self, width=400, height=600, bg='white')
        self.scrollable_canvas = tk.Canvas(self.scrollable_item_selection, bg='#263238', highlightthickness=0, width=400)
        self.item_selection_scrollbar = tk.Scrollbar(self.scrollable_item_selection, orient='vertical',
                                                     command=self.scrollable_canvas.yview, bg='#263238')

        # create a frame for the scrollable items to exist in and bind it to a command which changes their position as the scrollbar moves
        self.scrollable_items_frame = tk.Frame(self.scrollable_canvas, width=0, height=0, bg='#263238')
        self.scrollable_items_frame.bind("<Configure>", lambda e: self.scrollable_canvas.configure(scrollregion=self.scrollable_canvas.bbox("all")))

        # set up the scrolling canvas in the
        self.scrollable_canvas.create_window((0, 0), window=self.scrollable_items_frame, anchor="nw")
        self.scrollable_canvas.config(yscrollcommand=self.item_selection_scrollbar.set)

        self.enable = {}
        for i, list_item in enumerate(self.list_items):
            self.enable[list_item] = tk.BooleanVar(value=False)
            checkbox = tk.Checkbutton(
                self.scrollable_items_frame, text=list_item, variable=self.enable[list_item], foreground='white', bg='#263238',
                onvalue=True, offvalue=False, font=('consolas', 15, 'normal'), selectcolor='black')
            checkbox.grid(row=i, column=0, sticky=tk.W)

        self.item_selection_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollable_canvas.pack(side=tk.LEFT, fill="both", expand=True)
        self.scrollable_item_selection.pack(padx=5, pady=5, side=tk.LEFT, fill="both", expand=True)

        # session customization
        self.options_frame = tk.Frame(self, width=300, height=100, bg='#263238')

        self.read_aloud = tk.BooleanVar()
        self.read_aloud_checkbutton = tk.Checkbutton(self.options_frame, text="Read Text Aloud", variable=self.read_aloud, foreground='white',
                                                     bg='#263238', onvalue=True, offvalue=False, font=('consolas', 15, 'normal'), selectcolor='black')
        self.read_aloud_checkbutton.grid(row=1, column=1, sticky='w')

        self.reverse_order = tk.BooleanVar()
        self.reverse_checkbutton = tk.Checkbutton(self.options_frame, text="Show Definition First", variable=self.reverse_order, foreground='white',
                                                  bg='#263238', onvalue=True, offvalue=False, font=('consolas', 15, 'normal'), selectcolor='black')
        self.reverse_checkbutton.grid(row=2, column=1, sticky='w')

        self.randomize = tk.BooleanVar()
        self.random_checkbutton = tk.Checkbutton(
            self.options_frame, text="Random Order", variable=self.randomize, foreground='white', bg='#263238',
            onvalue=True, offvalue=False, font=('consolas', 15, 'normal'), selectcolor='black')
        self.random_checkbutton.grid(row=3, column=1, sticky='w')
        self.random_checkbutton.toggle()

        self.autoflip = tk.BooleanVar()
        self.autoflip_checkbutton = tk.Checkbutton(
            self.options_frame, text="Autoflip After ", variable=self.autoflip, foreground='white', bg='#263238',
            onvalue=True, offvalue=False, font=('consolas', 15, 'normal'), selectcolor='black')
        self.autoflip_checkbutton.grid(row=4, column=1, sticky='w')

        self.autoflip_interval = tk.IntVar()

        # new frame for autoflip options
        self.autoflip_entry_frame = tk.Frame(self.options_frame)

        self.autoflip_interval_box = tk.Entry(self.autoflip_entry_frame, width=5, foreground='white', bg='#263238',
                                              font=('consolas', 15, 'normal'), textvariable=self.autoflip_interval)
        self.autoflip_interval_box.delete(0, tk.END)
        self.autoflip_interval_box.insert(0, "5")
        self.autoflip_interval_box.pack(side=tk.LEFT)
        self.seconds_label = tk.Label(self.autoflip_entry_frame, text="seconds", foreground='white', bg='#263238', font=('consolas', 15, 'normal'))
        self.seconds_label.pack(side=tk.LEFT)

        self.autoflip_entry_frame.grid(row=5, column=1, sticky='w')

        self.start_button = tk.Button(self.options_frame, text='START', foreground='white',
                                      background='grey25', command=start_command, font=('consolas', 15, 'bold'))
        self.start_button.grid(row=6, column=1, sticky='w')

        self.options_frame.grid_rowconfigure(2, weight=1)

        self.options_frame.place(relx=0.97, rely=1, anchor="se")


class FlashcardFrame(tk.Frame):
    """
    Made up of two frames: the term and definition frames. When clicking on the first frame which shows up, the other
    frame should be shown. When clicking on that frame, the next flashcard should be displayed. There should also
    be buttons for repeating the flashcard now or later in the list.
    """

    def __init__(self, parent, term, definition="", definition_first=False, next_command=None, flip_command=None, quit_command=None,
                 num_of_cards=None, width=600, height=400, bg='#263238'):

        tk.Frame.__init__(self, parent, width=width, height=height, bg='#263238')
        self.parent = parent
        self.width = width
        self.height = height
        self.bg = bg

        self.flip_command = flip_command
        self.next_command = next_command

        self.term = term
        self.definition = definition
        self.definition_first = definition_first
        self.current_text = term if not self.definition_first else definition  # term or definition

        self.card_label = tk.Label(self, text=self.current_text, foreground='white', background=self.bg, font=(
            'consolas', resize_font(len(self.current_text), 500), 'bold' if not self.definition_first else 'normal'),
            wraplength=600, justify=tk.CENTER)
        self.card_label.place(relx=0.5, rely=0.5, anchor='center')

        self.flip_button = tk.Button(self, text="FLIP", command=self.flip_card, font=('consolas', 15, 'bold'))
        self.flip_button.place(relx=0.45, rely=0.8, anchor="center")

        self.next_button = tk.Button(self, text="NEXT", command=next_command, font=('consolas', 15, 'bold'))

        if num_of_cards is not None:
            self.num_of_cards = num_of_cards
            self.current_card_num = 1
            self.num_of_cards = num_of_cards
            self.current_card_label = tk.Label(self, text=f"{self.current_card_num}/{self.num_of_cards}", font=('consolas', 15, 'bold'), fg='white',
                                               bg=self.bg)
            self.current_card_label.pack(side='top', anchor='ne', padx=10, pady=10)

        self.quit_button = tk.Button(self, text="QUIT", foreground='white', background='grey25', command=quit_command, font=('consolas', 20, 'bold'))
        self.quit_button.place(relx=0.9, rely=0.9, anchor="se")

    def flip_card(self):
        self.current_text = self.definition if not self.definition_first else self.term
        self.card_label.config(text=self.current_text, font=(
            'consolas', resize_font(len(self.current_text), 500), 'bold' if self.definition_first else 'normal'))

        self.flip_button.place_forget()
        self.next_button.place(relx=0.55, rely=0.8, anchor="center")

        if self.flip_command is not None:
            self.flip_command()

    def set_current_card_num(self, num: int):
        """
        Allows for another module to pass in the current flashcard number
        """
        self.current_card_num = num
        self.current_card_label.config(text=f"{self.current_card_num}/{self.num_of_cards}")
        self.current_card_label.pack(side='top', anchor='ne', padx=10, pady=10)


class LoginFrame(tk.Frame):

    def __init__(self, parent, login_function, back_function, width=600, height=400):

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
