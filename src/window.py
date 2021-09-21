"""
Handles all windows and displaying of information for flashcard program.

Author: Ethan Posner
Date: July 27, 2021
"""

import tkinter as tk


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
    def __init__(self, parent, items=[], start_command=None, width=600, height=400):

        tk.Frame.__init__(self, parent, width=width, height=height, bg='#263238', highlightthickness=2, highlightbackground="black")
        self.parent = parent
        self.width = width
        self.height = height

        self.list_items = items

        self.enable = {}
        
        for list_item in self.list_items:
            self.enable[list_item] = tk.Variable()
            checkbox = tk.Checkbutton(self, text=list_item, variable=self.enable[list_item], foreground='white', bg='#263238', onvalue=True, offvalue=False, font=('consolas', 15, 'normal'))
            checkbox.pack()

        self.start_button = tk.Button(self, text='START', foreground='white', background='grey25', command=start_command)
        self.start_button.pack()


class FlashcardTermFrame(tk.Frame):
    """
    Display term to memorize, as well as options to go back or repeat card. This frame will follow or be
    followed by a definition.
    """
    def __init__(self, parent, text, flip_command=None, width=600, height=400):
        
        tk.Frame.__init__(self, parent, width=width, height=height, bg='#263238', highlightthickness=2, highlightbackground="black")
        self.parent = parent
        self.width = width
        self.height = height

        self.text = text
        self.text_label = tk.Label(self, text=self.text, foreground='white', background='#263238', font=('consolas', 20, 'bold'))
        self.text_label.place(relx=0.5, rely=0.5, anchor="center")

        self.flip_button = tk.Button(self, text="FLIP", command=flip_command, font=('consolas', 15, 'bold'))
        self.flip_button.place(relx=0.5, rely=0.8, anchor="center")


class FlashcardDefinitionFrame(tk.Frame):
    """
    Display definition for term to memorize, as well as options to go back or repeat card. This frame will follow or
    be followed by a term.
    """
    def __init__(self, parent, text, next_command=None, width=600, height=400):

        tk.Frame.__init__(self, parent, width=width, height=height, bg='#263238', highlightthickness=2, highlightbackground="black")
        self.parent = parent
        self.width = width
        self.height = height

        self.text = text
        self.text_label = tk.Label(self, text=self.text, foreground='white', background='#263238', font=('consolas', 10, 'bold'), wraplength=400, justify=tk.CENTER)
        self.text_label.place(relx=0.5, rely=0.5, anchor="center")

        self.next_button = tk.Button(self, text="NEXT", command=next_command, font=('consolas', 15, 'bold'))
        self.next_button.place(relx=0.5, rely=0.8, anchor="center")



class FlashcardFrame(tk.Frame):
    """
    Made up of two frames: the term and definition frames. When clicking on the first frame which shows up, the other
    frame should be shown. When clicking on that frame, the next flashcard should be displayed. There should also
    be buttons for repeating the flashcard now or later in the list.
    """
    def __init__(self, parent, term, definition = "", next_command=None, quit_command=None, width=600, height=400):

        tk.Frame.__init__(self, parent, width=width, height=height, bg='#263238')
        self.parent = parent
        self.width = width
        self.height = height

        self.term_frame = FlashcardTermFrame(self, text=term, flip_command=self.flip_card, width=self.width, height=self.height)
        self.definition_frame = FlashcardDefinitionFrame(self, text=definition, next_command=next_command, width=self.width, height=self.height)

        quit_button = tk.Button(self, text="QUIT", foreground='white', background='grey25', command=quit_command, font=('consolas', 20, 'bold'))
        quit_button.place(relx=0.9, rely=0.9, anchor="se")

        self.term_frame.pack(fill="both", expand=True)


    def flip_card(self):
        self.term_frame.pack_forget()
        self.definition_frame.pack(fill="both", expand=True)


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
