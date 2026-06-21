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
# @STUDENT-EDIT-Day1-1: Examine datatypes in settings.py (identify strings, integers, lists). Add your own comment describing a variable.

from pygame.math import Vector2

# =============================================================================
# SCREEN AND DISPLAY SETTINGS
# =============================================================================
# These control how big our game window is and how detailed the graphics are

# @STUDENT-EDIT-Day1-3: Change the game window size
SCREEN_WIDTH = 1280  # Width of game window in pixels
SCREEN_HEIGHT = 720  # Height of game window in pixels
# @STUDENT-EDIT-Day1-2: Customize the game window title (TITLE)
TITLE = "PyDew Valley: GAIC 26"
# @STUDENT-EDIT-Day1-4: Experiment with different background colors
WATER_COLOR = "#71ddee"  # Hex color code for the water background
TILE_SIZE = 64  # Size of each tile in our game world (pixels)

# @STUDENT-EDIT-Day5-1: Customize the player name and greeting variables
PLAYER_NAME = "Farmer"
GREETING = "Hello there!"

# =============================================================================
# USER INTERFACE POSITIONS
# =============================================================================
# These dictionaries tell us where to place UI elements on the screen

# Overlay positions for showing tools and seeds
OVERLAY_POSITIONS = {
    "tool": (40, SCREEN_HEIGHT - 15),  # Where to show current tool
    "seed": (70, SCREEN_HEIGHT - 5),  # Where to show current seed
}

# Tool positioning offsets relative to player
PLAYER_TOOL_OFFSET = {
    "left": Vector2(-50, 40),  # Tool position when facing left
    "right": Vector2(50, 40),  # Tool position when facing right
    "up": Vector2(0, -10),  # Tool position when facing up
    "down": Vector2(0, 50),  # Tool position when facing down
}

# =============================================================================
# GRAPHICS LAYERS SYSTEM
# =============================================================================
# This controls which graphics appear in front of others (like z-depth)
# Lower numbers are drawn first (in the background)

LAYERS = {
    "water": 0,  # Water is drawn first (background)
    "ground": 1,  # Ground tiles
    "soil": 2,  # Farmable soil
    "soil water": 3,  # Wet soil
    "rain floor": 4,  # Rain effects on ground
    "house bottom": 5,  # Bottom part of buildings
    "ground plant": 6,  # Plants growing on ground
    "main": 7,  # Player and main characters
    "house top": 8,  # Top part of buildings (roofs)
    "fruit": 9,  # Harvestable fruits
    "rain drops": 10,  # Rain drop effects (foreground)
}

# =============================================================================
# GAME WORLD OBJECT POSITIONS
# =============================================================================
# These dictionaries define where special objects (like apples) appear in the world

# Apple tree positions - Small and Large trees have different apple locations
APPLE_POS = {
    "Small": [
        (18, 17),
        (30, 37),
        (12, 50),
        (30, 45),
        (20, 30),
        (30, 10),
    ],  # Small tree apple spots
    "Large": [
        (30, 24),
        (60, 65),
        (50, 50),
        (16, 40),
        (45, 50),
        (42, 70),
    ],  # Large tree apple spots
}

# =============================================================================
# GAME MECHANICS AND TIMING
# =============================================================================
# These settings control how the game plays and feels

# Plant growth speeds (lower numbers = faster growth)
GROW_SPEED = {
    "corn": 0.1,  # Corn grows relatively fast
    "tomato": 0.07,  # Tomatoes grow a bit slower
}

# How much growth a single night's sleep gives every plant. Sleeping skips a
# full day, so plants advance much more than during a single gameplay frame.
DAY_GROWTH = 10

# @STUDENT-EDIT-Day2-2: Change the player's movement speed (PLAYER_SPEED)
PLAYER_SPEED = 200

# =============================================================================
# ECONOMIC SYSTEM - PRICES AND VALUES
# =============================================================================
# These dictionaries control the game's economy

# How much money you get for selling each item (tomato is the most valuable)
SALE_PRICES = {
    "wood": 4,
    "apple": 2,
    "corn": 10,
    "tomato": 20,
}

# How much it costs to buy each seed
PURCHASE_PRICES = {
    "corn": 4,
    "tomato": 5,
}

# =============================================================================
# NPC CONFIGURATION
# =============================================================================
# Students can easily add new characters to the game here!
# @STUDENT-EDIT-Day2-1: Add your custom sprite image name to the character list
# For each NPC, define:
# - name: Display name of the character
# - pos: Grid coordinates or pixel coordinates (x, y)
# - graphic: Path to the character's image
# - dialogue: A list of lines/paragraphs the character says when spoken to
NPC_DATA = {
    "Robin": {
        "pos": (800, 400),
        "graphic": "graphics/objects/merchant.png",  # Placeholder using existing asset
        "dialogue": [
            "Hi there! Welcome to PyDew Valley!",
            "I'm Robin, a helper NPC created using Python classes.",
            "Try editing settings.py to change what I say, or create your own custom NPC!"
        ]
    }
}

