# Flashcard-Tool
A simple python program to create and display flashcards. Very useful for memorization of 
large amounts of information.

To begin with, this application will interface with your notion account and create 
flashcards based on a database table of terms and definitions, but also give you the
option to create them using this program, and save them to the notion database.

In the future, I also want to create functionality for note-taking so that all
functionality will exist in one place.

## Installation
1. Clone repository:
`git clone https://github.com/Enprogames/Flashcard-Tool.git`
   
2. Create new virtual environment using venv
    1. Linux: `python3 -m venv venv --prompt flashcard-tool`
    2. Windows: `python -m venv venv --prompt flashcard-tool`
   
3. Activate the virtual environment:
    1. Linux: `source venv/bin/activate`
    2. Windows: `source venv/Scripts/activate`
   
4. Now that you're in the virtual environment, install the requirements:
`pip install -r requirements.txt`
   
5. Run main.py from root of project directory by double clicking.
   Alternatively, run through terminal: 
    1. Linux: `python3 src/main.py`
    2. Windows: `python src/main.py`
   
### Troubleshooting
- If `No module named tkinter` is given when attempting to run main.py:
     1. Linux: Run command in terminal `sudo apt-get install python3-tk`
     2. Windows: Install python through activestate: https://www.activestate.com/products/python/downloads/
   
