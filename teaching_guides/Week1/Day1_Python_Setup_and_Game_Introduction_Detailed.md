# Day 1: Python Setup and Game Introduction

## Objective
Set up programming environment and begin coding fundamentals.

## Setup Tasks
1. **Install & Run IDE**: Explain what IDEs are and set up development environment
2. **Install Python**: Walk through Python installation. **Use Python 3.11 or 3.12** — the
   game's libraries (pygame-ce, torch, opencv) have prebuilt wheels for those versions.
   Very new versions (3.14) may not, and will try to compile from source and fail.
3. **GitHub Setup**: Sign-in or sign-up for GitHub account
4. **Download Project**: Clone from [Ian's GitHub Repository](https://github.com/UFResearchComputing/GatorAI_Camp_2026)
5. **Hello World**: Demonstrate running "Hello, World!" in a Python script

## Core Concepts
### Basic Python Syntax
- Simple print statements and comments
- Indentation rules in Python

### Libraries and Importing
- Explain how to import and use external libraries

### Game Environment Overview
- Introduce existing game framework
- Show game file locations and how to run the game (`python main.py`)

### Variables & Data Types (Basic)
- Integers, floats, strings, dictionaries
- Assign simple values (character names, positions, etc.)

## Exercise: Customize the Game
The student-facing steps for today live in
[student_tutorials/Day1_Basics.md](../../student_tutorials/Day1_Basics.md). Students
look for the `@STUDENT-EDIT-Day1-*` markers in the code and edit around them.
- **Deliverable**: Push project to personal GitHub repository

## Code References

> All snippets below are copied from the **actual** project files. Line numbers are
> approximate (the files change as students edit them) — search for the quoted code or
> the `@STUDENT-EDIT` marker rather than trusting an exact line.

### Main Entry Point and Dependency Installation
**File**: [main.py](../../main.py) (top of file)

The game starts in `main.py`. The very first thing it does is make sure the required
libraries are installed, using a small helper from `installer.py`:

```python
# Import required modules for our game
from installer import install

# Install required packages if they're not already installed
install("pygame-ce")  # Game development library (community fork, imports as "pygame")
install("pytmx")  # Map loading library
install("kagglehub")  # Dataset library
install("requests")  # Library for web requests
install("opencv-python")  # Computer vision library
install("pytorch_lightning")
install("openai")  # AI API library for dialogue generation

import pygame  # Main game development library
import sys  # System operations
import os  # Operating system interface

# Import our custom game modules
from settings import *  # Game configuration settings
from main_menu import MainMenu  # Main menu system
import game_settings  # Audio and game settings
from collections import deque
```

**DETAILED WALKTHROUGH:**

1. **`from installer import install`** — imports a custom function from our own
   `installer.py` file. This is an example of *code reuse*: using code we wrote in
   another file.

2. **The `install(...)` calls** — each one checks whether a library is present and
   installs it if not. Note `install("pygame-ce")`: we use the community fork of
   pygame, which still imports as `import pygame`. (Teaching point: a package's
   *install name* and its *import name* can differ.) During Week 1 the heavy AI
   installs can be commented out to make startup faster — students will turn them on
   in Week 2.

3. **Standard library imports (`pygame`, `sys`, `os`)** — `pygame` is the game engine,
   `sys` is used for `sys.exit()`, and `os` is used to work with file paths.

4. **Custom module imports** — note the three import *styles*, which is a great
   discussion point:
   - `from settings import *` pulls in every constant from `settings.py` (handy, but
     use sparingly).
   - `from main_menu import MainMenu` pulls in just one class.
   - `import game_settings` imports the whole module so we call it as
     `game_settings.load_settings()`.
   - `from collections import deque` imports one tool from the standard library — the
     `deque` is later used to remember the last few detected emotions in Week 2.

### Game Class Structure
**File**: [main.py](../../main.py) — `class Game`

```python
class Game:
    """
    Main Game Class - The Heart of Our Game
    ======================================
    This class manages the entire game, including:
    - Starting up pygame and creating the game window
    - Managing the main menu and game screens
    - Running the main game loop
    - Handling user input and events
    """

    def __init__(self):
        # Initialize pygame - this must be done before using pygame features
        pygame.init()
        pygame.mixer.init()  # Initialize audio system for sound effects and music

        # Create the game window with specified dimensions
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)  # Set window title

        # Create a clock to control frame rate (how fast the game runs)
        self.clock = pygame.time.Clock()
```

**DETAILED WALKTHROUGH:**

1. **`class Game:`** — a class is a blueprint. Our `Game` class holds all the logic for
   starting and running the game.

2. **`def __init__(self):`** — the *constructor*, run automatically when we write
   `game = Game()` at the bottom of the file. `self` refers to the specific game object
   being built.

3. **`pygame.init()` and `pygame.mixer.init()`** — turn on the pygame engine and its
   audio system. These must happen before any other pygame call.

4. **`pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))`** — creates the window.
   `SCREEN_WIDTH` and `SCREEN_HEIGHT` are constants imported from `settings.py`
   (currently `1280` and `720`). The returned surface is stored in `self.screen` so we
   can draw on it later.

5. **`pygame.display.set_caption(TITLE)`** — sets the text in the window's title bar.
   `TITLE` is also from `settings.py`.

6. **`self.clock = pygame.time.Clock()`** — a clock used to cap the frame rate so the
   game runs at a steady speed on any computer.

### The Settings File (Variables & Data Types)
**File**: [settings.py](../../settings.py)

This is the best file for today's "variables and data types" lesson. It is full of
clearly-typed values students can read and change:

```python
# @STUDENT-EDIT-Day1-3: Change the game window size
SCREEN_WIDTH = 1280   # integer
SCREEN_HEIGHT = 720   # integer
# @STUDENT-EDIT-Day1-2: Customize the game window title (TITLE)
TITLE = "PyDew Valley: GAIC 26"   # string
# @STUDENT-EDIT-Day1-4: Experiment with different background colors
WATER_COLOR = "#71ddee"   # string holding a hex color code
TILE_SIZE = 64   # integer
```

**DETAILED WALKTHROUGH:**
- `SCREEN_WIDTH` / `SCREEN_HEIGHT` / `TILE_SIZE` are **integers**.
- `TITLE` and `WATER_COLOR` are **strings**.
- Later in the file, `SALE_PRICES` and `GROW_SPEED` are **dictionaries**, and
  `APPLE_POS` is a dictionary of **lists of tuples** — good examples to point at when
  introducing data structures.
- The `@STUDENT-EDIT-Day1-*` comments mark exactly where students should make their
  Day 1 edits (window title, window size, background color).

### The Program Entry Point
**File**: [main.py](../../main.py) (bottom of file)

```python
if __name__ == "__main__":
    game = Game()  # Create a new Game instance
    game.run()     # Start the main game loop
```

**DETAILED WALKTHROUGH:**
- `if __name__ == "__main__":` is a standard Python idiom meaning "only run this when
  the file is executed directly (not imported)."
- `game = Game()` creates a Game object (which runs `__init__`).
- `game.run()` starts the main loop. Today, students just need to know this is where
  the game begins; `run()` is explored on later days.

## Key Learning Points
1. **How a Python program starts** — the `if __name__ == "__main__":` pattern and
   top-to-bottom execution.
2. **Imports** — built-in modules (`sys`, `os`), third-party libraries
   (`pygame`/pygame-ce), and our own modules, plus the different import styles.
3. **Basic class structure** — `class`, `def __init__(self)`, and `self`.
4. **Initializing pygame** — `pygame.init()`, `set_mode`, `set_caption`, the `Clock`.
5. **Variables and data types** — reading and editing the typed constants in
   `settings.py`.

## Extension Activities
1. **Personalize the title** — change `TITLE` in [settings.py](../../settings.py)
   (marker `@STUDENT-EDIT-Day1-2`).
2. **Resize the window** — change `SCREEN_WIDTH` / `SCREEN_HEIGHT`
   (marker `@STUDENT-EDIT-Day1-3`). Note how larger sizes affect what you can see.
3. **Print when the game starts** — add `print("Game starting!")` at the
   `@STUDENT-EDIT-Day1-5` marker in `Game.__init__` and watch the console.
4. **Change the water color** — try `WATER_COLOR = "#FF0000"` (red)
   (marker `@STUDENT-EDIT-Day1-4`).

## Troubleshooting Tips
- **pygame won't install / tries to "build a wheel":** you are probably on a too-new
  Python. Use Python 3.11 or 3.12. The project installs `pygame-ce`, which has wheels
  for those versions.
- **`ModuleNotFoundError`:** make sure you ran `python main.py` from inside the
  `GatorAI_Camp_2026` folder, and that the `install(...)` calls at the top of
  `main.py` are not all commented out.
- **GitHub clone issues:** re-clone with
  `git clone https://github.com/UFResearchComputing/GatorAI_Camp_2026` and confirm you
  can see the `.py` files plus the `graphics/`, `audio/`, `font/`, and `data/` folders.
- **Window opens then closes instantly:** check the console for a Python error — a typo
  in `settings.py` (e.g. a missing quote) is the usual cause.
