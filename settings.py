"""
Game Settings and Configuration
==============================
This file contains all the important settings and constants for our game.
In programming, it's good practice to keep all configuration values in one place!

Educational Concepts:
- Constants and global variables
- Dictionaries for organizing data
- Coordinate systems and positioning
- Game design parameters
"""
# @STUDENT-EDIT-Day1-1: Examine datatypes in settings.py (identify strings and integers). Add your own comment describing a variable.

from pygame.math import Vector2

# =============================================================================
# SCREEN AND DISPLAY SETTINGS
# =============================================================================
# These control how big our game window is and how detailed the graphics are

# @STUDENT-EDIT-Day1-3: Change the game window size
SCREEN_WIDTH = 1280  # Width of game window in pixels (Default: 1280)
SCREEN_HEIGHT = 720  # Height of game window in pixels (Default: 720)
# @STUDENT-EDIT-Day1-2: Customize the game window title (TITLE)
TITLE = "Fazenda do Seu Ze: GAIC 26"  # Game window title text (Default: "PyDew Valley: GAIC 26")
# @STUDENT-EDIT-Day1-4: Experiment with different background colors
WATER_COLOR = "#71ddee"  # Hex color code for the water background (Default: "#71ddee")
TILE_SIZE = 64  # Size of each tile in our game world (pixels) (Default: 64)

# @STUDENT-EDIT-Day1-8: Variables can be used in CALCULATIONS! The two values below are
# computed from SCREEN_WIDTH / SCREEN_HEIGHT above (/ means divide; Python follows the
# PEMDAS order of operations). The game centers things on screen with this same math.
# Try changing the screen size and see how these change too.
SCREEN_CENTER_X = SCREEN_WIDTH / 2   # float: horizontal middle of the screen
SCREEN_CENTER_Y = SCREEN_HEIGHT / 2  # float: vertical middle of the screen

# @STUDENT-EDIT-Day1-10: Every value has a TYPE. Try adding a line like
# print(type(SCREEN_WIDTH))     -> int   (a whole number)
# print(type(SCREEN_CENTER_X))  -> float (division always makes a float)
# You can also convert ("cast") between types: int(3.99) -> 3 (it TRUNCATES toward
# zero, it does NOT round!) and float(64) -> 64.0. More casting practice is in scratch.py.

# @STUDENT-EDIT-Day5-1: Customize the player name and greeting variables
PLAYER_NAME = "Seu Ze"  # Name shown for the player (Default: "Farmer")
GREETING = "Hello there!"  # Starter greeting text (Default: "Hello there!")

# =============================================================================
# USER INTERFACE POSITIONS
# =============================================================================
# These dictionaries tell us where to place UI elements on the screen

# Overlay positions for showing tools and seeds
OVERLAY_POSITIONS = {
    "tool": (40, SCREEN_HEIGHT - 15),  # Where to show current tool (Default: (40, SCREEN_HEIGHT - 15))
    "seed": (70, SCREEN_HEIGHT - 5),  # Where to show current seed (Default: (70, SCREEN_HEIGHT - 5))
}

# Tool positioning offsets relative to player
PLAYER_TOOL_OFFSET = {
    "left": Vector2(-50, 40),  # Tool position when facing left (Default: Vector2(-50, 40))
    "right": Vector2(50, 40),  # Tool position when facing right (Default: Vector2(50, 40))
    "up": Vector2(0, -10),  # Tool position when facing up (Default: Vector2(0, -10))
    "down": Vector2(0, 50),  # Tool position when facing down (Default: Vector2(0, 50))
}

# =============================================================================
# GRAPHICS LAYERS SYSTEM
# =============================================================================
# This controls which graphics appear in front of others (like z-depth)
# Lower numbers are drawn first (in the background)

LAYERS = {
    "water": 0,  # Water is drawn first (background) (Default: 0)
    "ground": 1,  # Ground tiles (Default: 1)
    "soil": 2,  # Farmable soil (Default: 2)
    "soil water": 3,  # Wet soil (Default: 3)
    "rain floor": 4,  # Rain effects on ground (Default: 4)
    "house bottom": 5,  # Bottom part of buildings (Default: 5)
    "ground plant": 6,  # Plants growing on ground (Default: 6)
    "main": 7,  # Player and main characters (Default: 7)
    "house top": 8,  # Top part of buildings (roofs) (Default: 8)
    "fruit": 9,  # Harvestable fruits (Default: 9)
    "rain drops": 10,  # Rain drop effects (foreground) (Default: 10)
}

# =============================================================================
# GAME WORLD OBJECT POSITIONS
# =============================================================================
# These dictionaries define where special objects (like apples) appear in the world

# Apple tree positions - Small and Large trees have different apple locations
# @STUDENT-EDIT-Day2-9: Each (x, y) pair below is a TUPLE - an ordered, fixed group of
# values written with parentheses. Tuples are how Python bundles things like coordinates.
# You'll also meet tuples when a function returns more than one value at once - see the
# powers() example in scratch.py, and how to "unpack" a tuple into separate variables.
APPLE_POS = {
    "Small": [
        (18, 17),
        (30, 37),
        (12, 50),
        (30, 45),
        (20, 30),
        (30, 10),
    ],  # Small tree apple spots (Default: six preset coordinates)
    "Large": [
        (30, 24),
        (60, 65),
        (50, 50),
        (16, 40),
        (45, 50),
        (42, 70),
    ],  # Large tree apple spots (Default: six preset coordinates)
}

# =============================================================================
# GAME MECHANICS AND TIMING
# =============================================================================
# These settings control how the game plays and feels

# Plant growth speeds (lower numbers = faster growth)
GROW_SPEED = {
    "corn": 0.1,  # Corn grows relatively fast (Default: 0.1)
    "tomato": 1,  # Tomatoes grow a bit slower (Default: 0.07)
}

# How much growth a single night's sleep gives every plant. Sleeping skips a
# full day, so plants advance much more than during a single gameplay frame.
DAY_GROWTH = 10  # Growth added after sleeping one day (Default: 10)

# @STUDENT-EDIT-Day2-2: Change the player's movement speed (PLAYER_SPEED)
PLAYER_SPEED = 500  # Player movement speed (Default: 200)

# =============================================================================
# ECONOMIC SYSTEM - PRICES AND VALUES
# =============================================================================
# These dictionaries control the game's economy

# How much money you get for selling each item (tomato is the most valuable)
SALE_PRICES = {
    "wood": 4,  # Default sale value for wood
    "apple": 2,  # Default sale value for apples
    "corn": 10,  # Default sale value for corn
    "tomato": 10000,  # Default sale value for tomatoes
}

# How much it costs to buy each seed
PURCHASE_PRICES = {
    "corn": 4,  # Default seed purchase price for corn
    "tomato": 5,  # Default seed purchase price for tomatoes
}

# =============================================================================
# NPC CONFIGURATION
# =============================================================================
# Students can easily add new characters to the game here!
# @STUDENT-EDIT-Day2-1: Add your custom sprite image name to the character list
# @STUDENT-EDIT-Day2-6: Good NAMING matters. The key "Robin" below is a name you choose.
# Rules: use letters/digits/underscores, don't start with a digit, and make it meaningful.
# Python is case-sensitive, so "Robin" and "robin" are different names. (Illegal names
# like 1st_npc or my$npc would cause an error.) PEP8 style prefers lower_case_with_underscores.
# For each NPC, define:
# - name: Display name of the character
# - pos: Grid coordinates or pixel coordinates (x, y)
# - graphic: Path to the character's image
# - dialogue: A list of lines/paragraphs the character says when spoken to
NPC_DATA = {
    "Sergio": {
        "pos": (800, 400),  # Default spawn position
        "graphic": "graphics/objects/merchant.png",  # Placeholder using existing asset (Default: "graphics/objects/merchant.png")
        "dialogue": [
            "Hi there! Welcome to the Big Farm Valley! Our farm, my champion!",
            "I'm Sergio, a helper NPC created using Python classes.",
            "Try editing settings.py to change what I say, or create your own custom NPC!"
        ]  # Default starter dialogue lines
    },
    "Flavia": {
        "pos": (900, 800),  # Default spawn position
        "graphic": "graphics/objects/merchant.png",  # Placeholder using existing asset (Default: "graphics/objects/merchant.png")
        "dialogue": [
            "Hi there! Welcome to my Little Farm Valley! It's tiny, but... its cute right? :D",
            "I'm Flavia, a helper NPC created using Python classes.",
            "Try editing settings.py to change what I say, or create your own custom NPC!"
        ]  # Default starter dialogue lines
    },
    "Black_Cat": {
        "pos": (0, 0),  # Default spawn position
        "graphic": "C:\Users\guest.101038\Downloads\gato preto teste 1.webphics/objects/black_cat.png"
        "dialogue": [
            "Meow! I'm the Black Cat, here to help you on your farm adventure!",
            "Keep an eye out for my fellow cats around the farm!"
        ]  # Default starter dialogue lines
    }
}