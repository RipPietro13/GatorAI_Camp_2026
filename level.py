"""
PyDew Valley - Level Manager Module
==================================
This module manages the entire game world including map loading, sprite management,
and game systems coordination. This is one of the most complex files in our game!

Educational Concepts Covered:
- File I/O and map loading from external files
- Sprite group management and organization
- Camera systems for following the player
- Game state management
- Audio system integration
- Weather and environmental systems
- Collision detection systems
- Object-oriented design patterns

This file demonstrates advanced game programming concepts and shows how
different game systems work together to create a complete game experience.
"""

import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from random import randint
from trader_menu import TraderMenu
import game_settings
import os
from dialogue_system import DialogueSystem


class Level:
    """The Game World Manager.

    Responsible for the entire game world: loading the map, organizing sprite
    groups, the camera, coordinating systems (weather, audio, shop, dialogue),
    and day/night state transitions.
    """

    def __init__(self, emotions_deque):
        """Build the whole game world: sprite groups, map, UI, weather, and audio."""
        # Get the main display surface (the game window)
        self.display_surface = pygame.display.get_surface()

        # Store emotions for AI dialogue context
        self.emotions_deque = emotions_deque

        # SPRITE GROUP ORGANIZATION
        # Different sprite groups help us organize and manage game objects efficiently
        self.all_sprites = CameraGroup()  # Custom camera-following sprite group
        self.collision_sprites = pygame.sprite.Group()  # Objects that block movement
        self.tree_sprites = pygame.sprite.Group()  # Trees that can be chopped
        self.npc_sprites = pygame.sprite.Group()  # Custom NPCs
        self.interaction_sprites = (
            pygame.sprite.Group()
        )  # Objects player can interact with

        # GAME SYSTEMS INITIALIZATION
        # Create the soil system for farming mechanics
        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)

        # Load the game map and create all game objects
        self.setup()

        # Create the UI overlay (shows player inventory, tools, etc.)
        self.overlay = Overlay(self.player, emotions_deque)

        # Create the day/night transition system
        self.transition = Transition(self.reset, self.player)

        # Register this level globally for audio updates
        game_settings.set_current_level(self)

        # WEATHER SYSTEM
        # Create rain and sky systems for environmental variety
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0, 10) > 7  # 30% chance of rain
        self.soil_layer.raining = self.raining  # Tell soil system about rain
        self.sky = Sky()  # Day/night color overlay

        # SHOP AND DIALOGUE SYSTEM - trading menu plus the dialogue box
        self.menu = TraderMenu(self.player, self.open_trader_menu)
        self.shop_active = False
        self.dialogue_system = DialogueSystem()

        # AUDIO SYSTEM
        # Load and set up game sounds and music
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.success = pygame.mixer.Sound(os.path.join(base_path, "audio/success.wav"))
        self.music = pygame.mixer.Sound(os.path.join(base_path, "audio/music.mp3"))

        # Apply volume settings from game settings and start background music
        self.update_audio_volumes()
        self.music.play(loops=-1)  # -1 means loop forever

    def setup(self):
        """Load the TMX map and turn each layer into sprites (house, fence, water, trees...)."""
        # Load the map data from an external TMX file
        # TMX is a standard format for tile-based game maps
        tmx_data = load_pygame("data/map.tmx")

        # HOUSE LAYERS - Create house floor and furniture
        # We process different layers separately to control rendering order
        for layer in ["HouseFloor", "HouseFurnitureBottom"]:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic(
                    (
                        x * TILE_SIZE,
                        y * TILE_SIZE,
                    ),  # Convert tile coordinates to pixels
                    surf,  # The image/surface for this tile
                    self.all_sprites,  # Add to main sprite group
                    LAYERS["house bottom"],  # Set rendering layer
                )

        # House walls and top furniture (rendered above the player)
        for layer in ["HouseWalls", "HouseFurnitureTop"]:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)

        # FENCE OBJECTS - Create fence barriers
        # These are both visual and collision objects
        for x, y, surf in tmx_data.get_layer_by_name("Fence").tiles():
            Generic(
                (x * TILE_SIZE, y * TILE_SIZE),
                surf,
                [self.all_sprites, self.collision_sprites],  # Add to multiple groups
            )

        # WATER OBJECTS - Create animated water tiles
        water_frames = import_folder("graphics/water")  # Load water animation frames
        for x, y, surf in tmx_data.get_layer_by_name("Water").tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

        # TREE OBJECTS - Create interactive trees
        for obj in tmx_data.get_layer_by_name("Trees"):
            Tree(
                pos=(obj.x, obj.y),
                surf=obj.image,
                groups=[self.all_sprites, self.collision_sprites, self.tree_sprites],
                name=obj.name,
                player_add=self.player_add,  # Callback for when player gets items
            )

        # DECORATIVE WILDFLOWERS
        for obj in tmx_data.get_layer_by_name("Decoration"):
            WildFlower(
                (obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites]
            )

        # INVISIBLE COLLISION TILES - Create invisible barriers
        for x, y, surf in tmx_data.get_layer_by_name("Collision").tiles():
            Generic(
                (x * TILE_SIZE, y * TILE_SIZE),
                pygame.Surface((TILE_SIZE, TILE_SIZE)),  # Invisible surface
                self.collision_sprites,
            )

        # PLAYER AND INTERACTION OBJECTS
        # Find special objects like player start position and interactive areas
        for obj in tmx_data.get_layer_by_name("Player"):
            if obj.name == "Start":
                # Create the player at the starting position
                self.player = Player(
                    pos=(obj.x, obj.y),
                    group=self.all_sprites,
                    collision_sprites=self.collision_sprites,
                    tree_sprites=self.tree_sprites,
                    interaction=self.interaction_sprites,
                    soil_layer=self.soil_layer,
                    toggle_shop=self.toggle_shop,
                    npc_sprites=self.npc_sprites,
                    trigger_dialogue=self.trigger_npc_dialogue,
                    shake_camera=self.shake_camera,
                )

            if obj.name == "Bed":
                # Create bed interaction area for sleeping
                Interaction(
                    (obj.x, obj.y),
                    (obj.width, obj.height),
                    self.interaction_sprites,
                    obj.name,
                )

            if obj.name == "Trader":
                # Create trader interaction area for shopping
                Interaction(
                    (obj.x, obj.y),
                    (obj.width, obj.height),
                    self.interaction_sprites,
                    obj.name,
                )

        # BACKGROUND GROUND TILE
        # Create the base ground that covers the entire map
        Generic(
            pos=(0, 0),
            surf=pygame.image.load("graphics/world/ground.png").convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS["ground"],  # Put it at the bottom layer
        )

        # Spawn custom NPCs configured in settings.py
        self.spawn_npcs()

    def spawn_npcs(self):
        """Spawn custom NPCs defined in settings.py NPC_DATA configuration."""
        from sprites import NPC
        for npc_name, data in NPC_DATA.items():
            NPC(
                pos=data["pos"],
                surf=pygame.image.load(data["graphic"]).convert_alpha(),
                name=npc_name,
                dialogue=data["dialogue"],
                groups=[self.all_sprites, self.collision_sprites, self.npc_sprites]
            )

    def trigger_npc_dialogue(self, name, lines):
        """Callback to start custom static dialogue."""
        self.dialogue_system.start_dialogue(
            character_id=name,
            dialogue_lines=lines
        )

    def shake_camera(self):
        """Callback to trigger a subtle screen shake."""
        self.all_sprites.shake(duration=0.15, intensity=3)

    def update_audio_volumes(self):
        """Apply the current volume settings to this level's music and sfx."""
        # Get current volume settings from the game settings
        master_vol = game_settings.get("master_volume")
        music_vol = game_settings.get("music_volume")
        sfx_vol = game_settings.get("sfx_volume")

        # Apply volumes - music uses master * music volume
        self.music.set_volume(master_vol * music_vol)
        # SFX uses master * sfx volume
        self.success.set_volume(master_vol * sfx_vol)

    def player_add(self, item):
        """Add one of `item` to the player's inventory and play the success sound."""
        # Add the item to the player's inventory
        self.player.item_inventory[item] += 1

        # Update volume before playing sound
        self.update_audio_volumes()
        self.success.play()

    def toggle_shop(self):
        """Greet the player with emotion-aware trader dialogue, then open the shop."""
        # Get the most recent emotion for context-aware dialogue. When no emotion
        # has been detected (camera off, or no face seen yet) we default to
        # "neutral" so the AI still has valid context to work with.
        recent_emotions = list(self.emotions_deque) if self.emotions_deque else []
        current_emotion = recent_emotions[-1] if recent_emotions else "neutral"

        # Determine player context based on their money and progress
        if self.player.money > 1000:
            situation = "player has lots of money and is doing well farming"
        elif self.player.money < 100:
            situation = "player is just starting out and has limited funds"
        else:
            situation = "player is making steady progress with their farm"

        # Create context dictionary for AI dialogue generation
        player_context = {
            "npc_name": "Merchant Pete",
            "npc_role": "friendly trader",
            "situation": situation,
            "emotion": current_emotion,
            "player_money": self.player.money,
        }

        # Start dialogue with trader using new system
        self.dialogue_system.start_dialogue(
            "trader", player_context=player_context, on_finish=self.open_trader_menu
        )

    def open_trader_menu(self):
        """Open the trading interface (called after the trader's greeting finishes)."""
        self.shop_active = True

    def reset(self):
        """Start a new day after sleeping: grow plants, reroll weather, refresh trees."""
        # Reset plant growth in the soil system
        self.soil_layer.update_plants()

        # Reset soil watering and determine new weather
        self.soil_layer.remove_water()
        self.raining = randint(0, 10) > 7  # New random weather
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()  # Rain waters all soil

        # Reset apples on trees
        for tree in self.tree_sprites.sprites():
            # Remove old apples
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            # Create new apples
            tree.create_fruit()

        # Reset sky color to daylight
        self.sky.start_color = [255, 255, 255]

    def plant_collision(self):
        """Auto-harvest any ripe plant the player is standing on."""
        # Check if there are any plants to harvest
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                # Check if plant is ready and player is touching it
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    # Add the plant to player's inventory
                    self.player_add(plant.plant_type)

                    # Create a visual particle effect
                    Particle(
                        plant.rect.topleft,
                        plant.image,
                        self.all_sprites,
                        z=LAYERS["main"],
                    )

                    # Remove the plant from the game
                    plant.kill()

                    # Update the soil grid data
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][
                        plant.rect.centerx // TILE_SIZE
                    ].remove("P")

    def run(self, dt, events=None):
        """Update one frame. `dt` is seconds since last frame; `events` is this frame's input.

        Only one of dialogue / shop / normal gameplay updates at a time (priority order).
        """
        if events is None:
            events = []

        # Handle ESC key for shop closure
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.shop_active:
                    self.shop_active = False

        # Update camera shake
        if self.all_sprites.shake_timer > 0:
            self.all_sprites.shake_timer -= dt

        # GAME LOGIC UPDATES - Priority order is important!
        if self.dialogue_system.active:
            # If dialogue is active, only update dialogue logic and consume events
            if events:
                self.dialogue_system.input(events)
            # Don't process other game logic while dialogue is active
        elif self.shop_active:
            # If shop is open, only update the shop menu
            self.menu.update()
        else:
            # Normal gameplay updates
            self.all_sprites.update(dt)
            self.plant_collision()
            self.soil_layer.update_plants(dt)

        # Weather effects (only during normal gameplay)
        if self.raining and not self.shop_active and not self.dialogue_system.active:
            self.rain.update()

        # Sky color transitions (day/night cycle)
        self.sky.update(dt)

        # TRANSITION EFFECTS
        if self.player.sleep:
            self.transition.update()

    def display(self):
        """Draw the world, then any active UI (dialogue/shop), overlay, sky, and transition."""
        # RENDERING - Draw the world
        self.display_surface.fill("black")
        self.all_sprites.custom_draw(self.player)

        # Draw active interface elements on top of the world
        if self.dialogue_system.active:
            self.dialogue_system.draw()
        elif self.shop_active:
            self.menu.display()

        # UI AND VISUAL EFFECTS
        self.overlay.display()

        # Sky color transitions (day/night cycle)
        self.sky.display()

        # TRANSITION EFFECTS
        if self.player.sleep:
            self.transition.display()


class CameraGroup(pygame.sprite.Group):
    """A sprite group that follows the player and draws sprites in layer + depth order."""

    def __init__(self):
        """Set up the camera offset and screen-shake state."""
        super().__init__()  # Initialize the parent sprite group
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()  # Camera offset from world origin
        self.shake_duration = 0
        self.shake_intensity = 0
        self.shake_timer = 0

    def shake(self, duration=0.15, intensity=3):
        """Start a screen shake of the given length and strength."""
        self.shake_duration = duration
        self.shake_intensity = intensity
        self.shake_timer = duration

    def custom_draw(self, player):
        """Center the camera on `player` and blit every sprite by layer, then Y position."""
        # CAMERA POSITIONING
        # Center the camera on the player
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        # Apply screen shake if active
        if self.shake_timer > 0:
            import random
            self.offset.x += random.randint(-self.shake_intensity, self.shake_intensity)
            self.offset.y += random.randint(-self.shake_intensity, self.shake_intensity)

        # LAYERED RENDERING
        # Draw sprites in layer order for proper visual layering
        for layer in LAYERS.values():
            # Sort sprites by their Y position for proper depth
            for sprite in sorted(
                self.sprites(), key=lambda sprite: sprite.rect.centery
            ):
                # Only draw sprites that belong to this layer
                if sprite.z == layer:
                    # Calculate sprite position relative to camera
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset

                    # Draw the sprite at the offset position
                    self.display_surface.blit(sprite.image, offset_rect)

                    # DEBUG VISUALIZATION (commented out)
                    # Uncomment these lines to see collision boxes and tool ranges
                    # if sprite == player:
                    #     pygame.draw.rect(self.display_surface,'red',offset_rect,5)
                    #     hitbox_rect = player.hitbox.copy()
                    #     hitbox_rect.center = offset_rect.center
                    #     pygame.draw.rect(self.display_surface,'green',hitbox_rect,5)
                    #     target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
                    #     pygame.draw.circle(self.display_surface,'blue',target_pos,5)
