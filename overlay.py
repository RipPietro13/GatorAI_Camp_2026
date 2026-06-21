"""
PyDew Valley - UI Overlay System
================================
This module manages the game's user interface (UI) overlay that appears on top
of the game world. It shows the player's currently selected tools, seeds,
keyboard controls, and inventory access.

Educational Concepts Covered:
- User Interface (UI) design and implementation
- Image loading and manipulation
- Surface positioning and blitting
- File path management
- Dictionary comprehensions
- Coordinate system for UI positioning
- Visual feedback for user interactions

This file demonstrates how games create informative and intuitive user interfaces
that help players understand what they can do and what they have available.
"""

import pygame
from settings import *
import os
import game_settings


class Overlay:
    """Draws the on-screen HUD: current tool/seed, keyboard hints, inventory, and emotions."""

    def __init__(self, player, emotions_deque):
        """Load all UI graphics (tool/seed/key icons, emotion icons) and set positions."""
        # BASIC SETUP
        # Get the main game display surface
        self.display_surface = pygame.display.get_surface()
        self.player = player  # Reference to player for current tool/seed info
        self.emotions_deque = emotions_deque

        # GRAPHICS LOADING
        # Construct the path to overlay graphics folder
        base_path = os.path.dirname(os.path.abspath(__file__))
        overlay_path = os.path.join(base_path, "graphics/overlay/")

        # Load tool icons using dictionary comprehension
        # This creates a dictionary mapping tool names to their images
        self.tools_surf = {
            tool: pygame.image.load(
                os.path.join(overlay_path, f"{tool}.png")
            ).convert_alpha()  # convert_alpha() optimizes the image format
            for tool in player.tools
        }

        # Load seed icons the same way
        self.seeds_surf = {
            seed: pygame.image.load(
                os.path.join(overlay_path, f"{seed}.png")
            ).convert_alpha()
            for seed in player.seeds
        }

        # SPECIAL UI GRAPHICS
        # Load and scale the rotation indicator graphic
        rotate_graphic = pygame.image.load(
            os.path.join(overlay_path, "rotate-32.png")
        ).convert_alpha()
        self.rotate_surf = pygame.transform.scale(rotate_graphic, (20, 20))

        # Load and scale the inventory icon
        inventory_icon = pygame.image.load(
            os.path.join(overlay_path, "backpack.png")
        ).convert_alpha()
        self.inventory_surf = pygame.transform.scale(inventory_icon, (64, 64))

        # KEYBOARD KEY GRAPHICS
        # Load keyboard sprite sheets for showing key controls
        keyboard_extras = pygame.image.load(
            os.path.join(overlay_path, "Keyboard Extras.png")
        ).convert_alpha()

        keyboard_letters = pygame.image.load(
            os.path.join(overlay_path, "Keyboard Letters and Symbols.png")
        ).convert_alpha()

        # Extract and scale specific keys from the sprite sheets
        # Spacebar key (for tool usage)
        spacebar_original = keyboard_extras.subsurface(
            pygame.Rect(64, 32, 32, 16)  # (x, y, width, height) in pixels
        )
        self.spacebar_surf = pygame.transform.scale(spacebar_original, (64, 32))

        # Ctrl key (for seed planting)
        ctrl_key_original = keyboard_extras.subsurface(
            pygame.Rect(0, 32, 32, 16)  # (x, y, width, height) in pixels
        )
        self.ctrl_key_surf = pygame.transform.scale(ctrl_key_original, (64, 32))

        # Q key (for tool switching)
        q_key_original = keyboard_letters.subsurface(
            pygame.Rect(0, 64, 16, 16)  # (x, y, width, height) in pixels
        )
        self.q_key_surf = pygame.transform.scale(q_key_original, (32, 32))

        # E key (for seed switching)
        e_key_original = keyboard_letters.subsurface(
            pygame.Rect(64, 32, 16, 16)  # (x, y, width, height) in pixels
        )
        self.e_key_surf = pygame.transform.scale(e_key_original, (32, 32))

        # I key (for inventory)
        i_key_original = keyboard_letters.subsurface(
            pygame.Rect(0, 48, 16, 16)  # (x, y, width, height) in pixels
        )
        self.i_key_surf = pygame.transform.scale(i_key_original, (32, 32))

        # Register this overlay globally for audio updates
        game_settings.set_current_overlay(self)

        # Emotion icons
        # These keys MUST match the lowercase labels the emotion model emits and
        # the keys used in ai_dialogue_manager.py, as well as the bunny-*.png
        # filenames on disk. Keep all three in sync or icons won't appear.
        emotions_path = os.path.join(base_path, "graphics/emotions/")
        self.emotion_icons = {}
        for emotion in ["happy", "sad", "angry", "surprised", "neutral", "fearful"]:
            icon_path = os.path.join(emotions_path, f"bunny-{emotion}.png")
            if os.path.exists(icon_path):
                icon_surf = pygame.image.load(icon_path).convert_alpha()
                # Scale emotion icons to match the inventory icon size (64x64)
                self.emotion_icons[emotion] = pygame.transform.scale(
                    icon_surf, (64, 64)
                )

    def display(self):
        """Draw the tool/seed indicators, keyboard hints, inventory icon, and emotion icons."""
        # TOOL DISPLAY
        tool_surf = self.tools_surf[self.player.selected_tool]
        tool_rect = tool_surf.get_rect(midbottom=OVERLAY_POSITIONS["tool"])
        self.display_surface.blit(tool_surf, tool_rect)

        # SEED DISPLAY
        seed_surf = self.seeds_surf[self.player.selected_seed]
        seed_rect = seed_surf.get_rect(midbottom=OVERLAY_POSITIONS["seed"])
        self.display_surface.blit(seed_surf, seed_rect)

        # INVENTORY AND KEYBOARD HINTS
        tool_pos = pygame.math.Vector2(tool_rect.topleft)
        seed_pos = pygame.math.Vector2(seed_rect.topleft)

        self.display_surface.blit(
            self.q_key_surf, tool_pos + pygame.math.Vector2(-10, -60)
        )
        self.display_surface.blit(
            self.rotate_surf, tool_pos + pygame.math.Vector2(30, -55)
        )
        self.display_surface.blit(
            self.e_key_surf, seed_pos + pygame.math.Vector2(70, 0)
        )
        self.display_surface.blit(
            self.rotate_surf, seed_pos + pygame.math.Vector2(110, 5)
        )
        self.display_surface.blit(self.spacebar_surf, (tool_pos.x, tool_pos.y - 35))
        self.display_surface.blit(
            self.ctrl_key_surf, (seed_pos.x + 70, seed_pos.y + 25)
        )

        self.display_surface.blit(self.inventory_surf, (SCREEN_WIDTH - 80, 10))
        self.display_surface.blit(self.i_key_surf, (SCREEN_WIDTH - 48, 80))

        # EMOTION DISPLAY
        if self.emotions_deque:
            emotions_to_display = list(reversed(self.emotions_deque))
            main_emotion_size = 64
            old_emotion_size = 48
            padding = 6
            current_x = SCREEN_WIDTH - padding

            for i, emotion in enumerate(emotions_to_display):
                icon = self.emotion_icons.get(emotion)
                if not icon:
                    continue

                if i == 0:  # Most recent emotion
                    size = main_emotion_size
                    scaled_icon = icon
                    current_x -= size
                    x_pos = current_x
                    y_pos = SCREEN_HEIGHT - size - padding
                    box_rect = pygame.Rect(x_pos - 4, y_pos - 4, size + 8, size + 8)
                    pygame.draw.rect(
                        self.display_surface,
                        (255, 20, 147),
                        box_rect,
                        3,
                        border_radius=8,
                    )
                    self.display_surface.blit(scaled_icon, (x_pos, y_pos))
                    current_x -= padding
                else:  # Older emotions
                    size = old_emotion_size
                    scaled_icon = pygame.transform.scale(icon, (size, size))
                    current_x -= size
                    x_pos = current_x
                    y_pos = SCREEN_HEIGHT - size - padding
                    self.display_surface.blit(scaled_icon, (x_pos, y_pos))
                    current_x -= padding
