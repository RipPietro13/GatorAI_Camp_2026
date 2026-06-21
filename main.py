"""
PyDew Valley - Educational Game for Learning Python
==================================================
This is the main game file that starts and runs our farming simulation game.
We will learn Python concepts through game development!

Educational Concepts Covered:
- Classes and Object-Oriented Programming
- Game loops and event handling
- Pygame library usage
- Module imports and organization
"""

# [1] Main game entry point with module imports and installation

# Import required modules for our game
from installer import install

# Install required packages if they're not already installed
# install("pygame-ce")  # Game development library (community fork, imports as "pygame")
# install("pytmx")  # Map loading library
# install("kagglehub")  # Dataset library
# install("requests")  # Library for web requests
# install("opencv-python")  # Computer vision library
# install("torchvision")
# install("pytorch_lightning")
# install("openai")  # AI API library for dialogue generation

import pygame  # Main game development library
import sys  # System operations
import os  # Operating system interface

# Import our custom game modules
from settings import *  # Game configuration settings
from main_menu import MainMenu  # Main menu system
import game_settings  # Audio and game settings
from collections import deque


class Game:
    """
    Main Game Class - The Heart of Our Game
    ======================================
    This class manages the entire game, including:
    - Starting up pygame and creating the game window
    - Managing the main menu and game screens
    - Running the main game loop
    - Handling user input and events

    Think of this as the "manager" that coordinates everything!
    """

    # [2] Game class structure; shows class definition, initialization with pygame setup

    def __init__(self):
        """Start pygame, open the window, and set up the menu and game-state flags."""
        # pygame.init() must run before any other pygame call
        pygame.init()
        pygame.mixer.init()  # audio system for sound effects and music

        # Create the game window and title it
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)

        # Clock caps the frame rate so the game runs at a steady speed
        self.clock = pygame.time.Clock()

        # Change to the directory where our game files are located
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # Load game settings (like volume levels) from file
        game_settings.load_settings()

        # Show a quick loading screen before the menu is fully built
        self.show_loading_screen("Loading menu...")

        # Initialize game components
        self.level = None  # The game world (will be created when game starts)
        self.main_menu = MainMenu(
            self.start_game, self.restart_emotion_detector
        )  # Main menu screen
        self.character_screen = None  # Player stats screen (created when game starts)
        self.show_main_menu = True  # Flag to control which screen to show
        self.show_settings_during_game = False  # Flag for in-game settings menu
        self.settings_menu = None  # Settings menu (created when first needed)

        # Emotion Detection Setup
        # Defer until actually needed in the game (not at startup to avoid heavy imports)
        self.emotions_deque = deque(maxlen=5)  # Store the last 5 detected emotions
        self.emotion_detector = None
        # Don't import EmotionDetector at startup - too slow
        # It will be created later when start_game() is called if camera is enabled

        # @STUDENT-EDIT-Day1-5: Insert a print("Game starting!") statement here to see when the game starts

    def show_loading_screen(self, message="Loading...", delay_ms=250):
        """Display a loading screen with game title and animated loading bar."""
        self.screen.fill("black")
        try:
            game_title_font = pygame.font.Font("font/LycheeSoda.ttf", 80)
            message_font = pygame.font.Font("font/LycheeSoda.ttf", 36)
            info_font = pygame.font.Font("font/LycheeSoda.ttf", 24)
        except Exception:
            game_title_font = pygame.font.SysFont(None, 80)
            message_font = pygame.font.SysFont(None, 36)
            info_font = pygame.font.SysFont(None, 24)

        # Draw game title at top
        game_title = game_title_font.render("PyDew Valley", True, "White")
        subtitle = info_font.render("GAIC 26", True, (100, 200, 100))
        title_rect = game_title.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 120)
        )
        subtitle_rect = subtitle.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40)
        )

        self.screen.blit(game_title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)

        # Draw current loading message
        message_surface = message_font.render(message, True, "White")
        message_rect = message_surface.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40)
        )
        self.screen.blit(message_surface, message_rect)

        # Draw loading bar with simple progress
        bar_width = 400
        bar_height = 20
        bar_x = (SCREEN_WIDTH - bar_width) / 2
        bar_y = SCREEN_HEIGHT / 2 + 110

        # Background bar
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (50, 50, 50), bg_rect)
        pygame.draw.rect(self.screen, "White", bg_rect, 2)

        # Fill bar partially
        fill_width = int(bar_width * 0.7)
        if fill_width > 0:
            fill_rect = pygame.Rect(
                bar_x + 2, bar_y + 2, fill_width - 4, bar_height - 4
            )
            pygame.draw.rect(self.screen, (100, 200, 100), fill_rect)

        pygame.display.update()
        pygame.time.delay(delay_ms)

    def start_game(self):
        """
        Start the Main Game - Called When Player Clicks "Start Game"
        ==========================================================
        This method creates the game world and player character screen.
        """
        self.show_loading_screen("Loading world...")
        from level import Level
        from character_screen import CharacterScreen

        self.level = Level(self.emotions_deque)  # Create the game world
        self.character_screen = CharacterScreen(
            self.level.player
        )  # Create player info screen
        self.show_main_menu = False  # Hide main menu and show game
        self.show_settings_during_game = False  # Reset settings menu flag

    def restart_emotion_detector(self):
        """Restart the emotion detector with new camera settings"""
        if self.emotion_detector and self.emotion_detector.is_alive():
            print("🔄 Restarting emotion detector with new camera settings...")
            self.emotion_detector.stop()
            self.emotion_detector.join(timeout=2.0)  # Wait for thread to stop

        # Create new emotion detector with updated settings
        from emotion_detector import EmotionDetector

        self.emotion_detector = EmotionDetector(
            self.emotions_deque, show_camera_preview=False
        )
        self.emotion_detector.start()

    def run(self):
        """The main game loop: every frame, handle input, update state, then draw.

        Runs forever until the player quits. This input -> update -> draw cycle is
        a fundamental game-programming concept.
        """
        # Start the emotion detector thread once the main loop begins
        if self.emotion_detector and not self.emotion_detector.is_alive():
            self.emotion_detector.start()

        # Main game loop - runs until player quits
        while True:
            # Cap the frame rate to reduce CPU usage and keep game timing stable
            delta_time = self.clock.tick(60) / 1000  # Convert milliseconds to seconds

            # EVENT HANDLING - Check what the player is doing
            events = pygame.event.get()
            for event in events:
                # Check if player clicked the X button to close the window
                if event.type == pygame.QUIT:
                    if self.emotion_detector:
                        self.emotion_detector.stop()  # Signal the thread to stop
                    pygame.quit()  # Close pygame
                    sys.exit()  # Exit the program

                # Check if player pressed 'I' key to open inventory/character screen
                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_i
                    and self.character_screen
                    and not self.show_settings_during_game
                ):
                    self.character_screen.toggle()  # Show/hide character screen

                # Check if player pressed ESC to close submenus or open settings
                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                    and not self.show_main_menu
                    and not self.show_settings_during_game
                ):
                    if self.character_screen and self.character_screen.visible:
                        self.character_screen.toggle()  # Close inventory screen
                    elif self.level and (
                        self.level.shop_active or self.level.dialogue_system.active
                    ):
                        # Let level run/events handle closing dialogue or shop (avoid opening settings)
                        pass
                    else:
                        self.show_settings_during_game = True

            # UPDATE GAME STATE - Decide what to update based on current screen
            if self.show_main_menu:
                # We're showing the main menu
                self.main_menu.update()
            else:
                # We're in the main game
                if self.show_settings_during_game:
                    # Settings menu is open - create it if needed and handle it
                    if self.settings_menu is None:
                        from settings_menu import SettingsMenu

                        self.settings_menu = SettingsMenu(self.restart_emotion_detector)

                    # Process input for settings menu
                    # The input_timer in settings_menu prevents immediate processing of the opening ESC
                    result = self.settings_menu.update()
                    if result == "back":
                        self.show_settings_during_game = False
                        self.settings_menu = None
                else:
                    # Normal gameplay - pass events for proper input handling
                    self.level.run(delta_time, events)  # Update game world

                    # If character screen is visible, update it too
                    if self.character_screen and self.character_screen.visible:
                        self.character_screen.update()

            # RENDER - Draw everything to the screen
            if self.show_main_menu:
                # Draw the main menu (it fills the screen with black and draws menu items)
                self.main_menu.display()
            elif self.level is not None:
                # Draw the game level
                self.level.display()
                # If character screen is visible, draw it on top
                if self.character_screen and self.character_screen.visible:
                    self.character_screen.display()
                # If settings menu is open, draw it on top of the game with an overlay
                if self.show_settings_during_game and self.settings_menu is not None:
                    # Draw a semi-transparent overlay to dim the game world
                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    overlay.set_alpha(128)
                    overlay.fill((0, 0, 0))
                    self.screen.blit(overlay, (0, 0))
                    # Draw the settings menu on top
                    self.settings_menu.display()

            pygame.display.update()  # Actually display what we've drawn


# PROGRAM ENTRY POINT - This runs when we start the program
if __name__ == "__main__":
    """
    This special condition checks if this file is being run directly
    (not imported as a module). If so, create and start the game!
    """
    game = Game()  # Create a new Game instance
    game.run()  # Start the main game loop
