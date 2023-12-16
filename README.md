# Flashcard-Tool
A simple python program to create and display flashcards. Flashcards can be very useful for memorizing of 
large amounts of information.

At this point in time, this application interfaces with a notion account to create  flashcards based on a 
database table of terms and definitions. Alternatively, csv files can be created in the csv_flashcard_files
folder.

In the future, I aim to create a CRUDL menu to give users the option to create them inside of this program.

![flashcard-tool1.JPG](docs/img/flashcard-tool1.JPG)

![flashcard-tool2.JPG](docs/img/flashcard-tool2.JPG)

## Installation
1. Clone repository:
`git clone https://github.com/Enprogames/Flashcard-Tool.git`

2. Change to root directory of project: `cd Flashcard-Tool`

3. Create new virtual environment using venv
    1. Linux: `python3 -m venv venv --prompt flashcard-tool`
    2. Windows: `python -m venv venv --prompt flashcard-tool`
   
4. Activate the virtual environment:
    1. Linux: `source venv/bin/activate`
    2. Windows: `source venv/Scripts/activate`
   
5. Now that you're in the virtual environment, install the requirements:
`pip install -r requirements.txt`

6. Run setup.sh: `./setup.sh'. This does the following:
    1. Creates a file in src called api_conf.json where a notion API key can be given
    2. Creates a folder in src called csv_flashcard_files. This is where flashcard data is stored.


### Creating CSV flashcard files
Create files ending in ".csv" e.g. "french revolution.csv". These will be your flashcard sets.
The files must follow this structure. Items are separated by commas. For more information about CSV files,
refer to [this](https://www.howtogeek.com/348960/what-is-a-csv-file-and-how-do-i-open-it/) guide.
Term | Definition | Exclude
-----|------------|--------
When did the french revolution start? | May 5, 1789 | False
Where did the french revolution occur? | France | True
...  | ... | ...

Excluded items will not be shown in the flashcard program.

### Setting up notion integration
Coming soon...
   
### Troubleshooting
- If `No module named tkinter` is given when attempting to run main.py:
     1. Linux: Run command in terminal `sudo apt-get install python3-tk`
     2. Windows: Install python through activestate: https://www.activestate.com/products/python/downloads/
   
# Usage
1. Run Flashcard-Tool.pyw from root of project directory by double clicking.
   Alternatively, run through terminal:
    1. Linux: `python3 src/Flashcard-Tool.pyw`
    2. Windows: `python src/Flashcard-Tool.pyw`