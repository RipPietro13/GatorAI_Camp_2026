import pygame
from settings import *


class CharacterScreen:
    """The inventory/stats screen toggled with the I key."""
    def __init__(self, player):
        """Store the player and set up the font; start hidden."""
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font("font/LycheeSoda.ttf", 30)
        self.player = player
        self.visible = False

    def display(self):
        """Draw the player's items, seeds, and money as a list of text lines."""
        self.display_surface.fill("black")
        y_offset = 50
        text_surf = self.font.render("Inventory", True, "White")
        text_rect = text_surf.get_rect(topleft=(50, y_offset))
        self.display_surface.blit(text_surf, text_rect)

        y_offset += 60  # Add some space between the title and the items

        for item, amount in self.player.item_inventory.items():
            text_surf = self.font.render(f"{item}: {amount}", True, "White")
            text_rect = text_surf.get_rect(topleft=(50, y_offset))
            self.display_surface.blit(text_surf, text_rect)
            y_offset += 40

        y_offset += 20  # Add some space between the items and the seeds

        for seed, amount in self.player.seed_inventory.items():
            text_surf = self.font.render(f"{seed} seed: {amount}", True, "White")
            text_rect = text_surf.get_rect(topleft=(50, y_offset))
            self.display_surface.blit(text_surf, text_rect)
            y_offset += 40

        y_offset += 20  # Add some space between the items and the seeds

        text_surf = self.font.render(f"Money: ${self.player.money}", True, "White")
        text_rect = text_surf.get_rect(topleft=(50, y_offset))
        self.display_surface.blit(text_surf, text_rect)

        y_offset += 100  # Add some space after the money display

        text_surf = self.font.render("Press ESC or I to close", True, "White")
        text_rect = text_surf.get_rect(topleft=(50, y_offset))
        self.display_surface.blit(text_surf, text_rect)

    def toggle(self):
        """Show or hide the screen."""
        self.visible = not self.visible

    def update(self):
        """No per-frame logic needed (the screen is static while open)."""
        pass
