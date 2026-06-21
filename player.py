"""
Player Character Class - The Heart of Our Game Character
=======================================================
This file defines the Player class, which represents the main character
that the player controls in the game.

Educational Concepts Covered:
- Object-Oriented Programming (Classes, Methods, Inheritance)
- Sprite-based graphics and animation
- Input handling and movement
- Game state management
- Inventory systems
- Timer-based actions
"""

import pygame  # Main game library
from settings import *  # Game configuration
from support import *  # Helper functions
from timer import Timer  # Custom timer class
import os  # File system operations
import game_settings  # Audio and settings management


class Player(pygame.sprite.Sprite):
    """
    Player Class - Represents Our Main Character
    ===========================================
    This class handles everything about the player character:
    - Movement and animation
    - Using tools (hoe, axe, watering can)
    - Planting and harvesting crops
    - Managing inventory and money
    - Interacting with the game world

    It inherits from pygame.sprite.Sprite, which gives us built-in
    functionality for graphics and collision detection.
    """

    def __init__(
        self,
        pos,  # Starting position (x, y coordinates)
        group,  # Sprite group this player belongs to
        collision_sprites,  # Objects the player can't walk through
        tree_sprites,  # Trees the player can interact with
        interaction,  # Function to handle interactions
        soil_layer,  # Farming/soil system
        toggle_shop,  # Function to open/close shop
        npc_sprites,  # Custom NPCs
        trigger_dialogue,  # Callback to trigger dialogue
        shake_camera,  # Callback to shake camera
    ):
        """Set up the player's graphics, movement, tools, inventory, and callbacks.

        The parameters are documented inline in the signature above.
        """
        super().__init__(group)  # pygame.sprite.Sprite setup

        # GRAPHICS AND ANIMATION SETUP
        self.import_assets()  # Load all animation frames
        # @STUDENT-EDIT-Day2-3: Modify the player's starting direction ('down' -> 'left', etc.)
        self.status = "down_idle"  # Start facing down and not moving
        self.frame_index = 0  # Which animation frame to show

        # Set up the visual representation
        self.image = self.animations[self.status][
            self.frame_index
        ]  # Current sprite image
        self.rect = self.image.get_rect(center=pos)  # Position rectangle
        self.z = LAYERS["main"]  # Which layer to draw on

        # MOVEMENT SYSTEM
        self.direction = pygame.math.Vector2()  # Which direction player is moving
        self.pos = pygame.math.Vector2(
            self.rect.center
        )  # Precise position (can have decimals)
        self.speed = PLAYER_SPEED  # How fast the player moves (pixels per second)

        # COLLISION DETECTION
        self.hitbox = self.rect.copy().inflate((-126, -70))  # Smaller box for collision
        self.collision_sprites = collision_sprites  # Objects that block movement

        # TIMER SYSTEM - Controls how often player can do actions
        self.timers = {
            "tool use": Timer(350, self.use_tool),  # How often tools can be used
            "tool switch": Timer(200),  # Delay between switching tools
            "seed use": Timer(350, self.use_seed),  # How often seeds can be planted
            "seed switch": Timer(200),  # Delay between switching seeds
        }
        # TOOL SYSTEM - Different tools for different tasks
        self.tools = ["hoe", "axe", "water"]  # Available tools
        self.tool_index = 0  # Which tool is currently selected
        self.selected_tool = self.tools[self.tool_index]  # Currently equipped tool

        # SEED SYSTEM - Different crops player can plant
        self.seeds = ["corn", "tomato"]  # Available seed types
        self.seed_index = 0  # Which seed is currently selected
        self.selected_seed = self.seeds[self.seed_index]  # Currently selected seed

        # INVENTORY SYSTEM - What the player is carrying
        self.item_inventory = {  # Items collected from the world
            "wood": 20,  # Wood from chopping trees
            "apple": 20,  # Apples from trees
            "corn": 20,  # Harvested corn
            "tomato": 20,  # Harvested tomatoes
        }
        self.seed_inventory = {  # Seeds available for planting
            "corn": 5,  # Corn seeds
            "tomato": 5,  # Tomato seeds
        }
        self.money = 200  # Player's money/coins

        # WORLD INTERACTION SYSTEMS
        self.tree_sprites = tree_sprites  # Trees that can be chopped
        self.interaction = interaction  # Function for interacting with objects
        self.sleep = False  # Is the player sleeping?
        self.soil_layer = soil_layer  # Farming system reference
        self.toggle_shop = toggle_shop  # Function to open/close shop
        self.npc_sprites = npc_sprites  # Custom NPCs group
        self.trigger_dialogue = trigger_dialogue  # Callback to start NPC dialogue
        self.shake_camera = shake_camera  # Callback to shake camera

        # AUDIO SYSTEM - Sound effects for player actions
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.watering = pygame.mixer.Sound(os.path.join(base_path, "audio/water.mp3"))
        self.update_audio_volumes()  # Set initial volume levels
        # Register this player globally for audio updates
        game_settings.set_current_player(self)

    def update_audio_volumes(self):
        """Apply the current master/sfx volume settings to the watering sound."""
        master_vol = game_settings.get("master_volume")
        sfx_vol = game_settings.get("sfx_volume")
        # Final volume is master * sfx
        self.watering.set_volume(master_vol * sfx_vol)

    def use_tool(self):
        """Run the selected tool's action (hoe tills, axe chops, water waters)."""
        # Hoe: till the soil at the target position
        if self.selected_tool == "hoe":
            self.soil_layer.get_hit(self.target_pos)

        # Axe: chop any tree under the target position (and shake the screen)
        if self.selected_tool == "axe":
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
                    self.shake_camera()

        # Water: water the soil and play the watering sound
        if self.selected_tool == "water":
            self.soil_layer.water(self.target_pos)
            self.update_audio_volumes()  # ensure correct volume before playing
            self.watering.play()

    def get_target_pos(self):
        """Work out where the tool is aimed: player center + a per-direction offset."""
        # Get just the facing direction from the status (e.g. "down_hoe" -> "down")
        direction = self.status.split("_")[0]
        # Offset the player's center by the direction's tool offset (vector addition)
        tool_offset = PLAYER_TOOL_OFFSET[direction]
        self.target_pos = self.rect.center + tool_offset

    def use_seed(self):
        """Plant the selected seed if the player still has some in their inventory."""
        # Only plant if we actually have that seed (prevents going negative)
        if self.seed_inventory[self.selected_seed] > 0:
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
            self.seed_inventory[self.selected_seed] -= 1  # use one up

    def import_assets(self):
        """Load every animation into a dict keyed by state (e.g. "down_hoe")."""
        # Each key matches a folder in graphics/character/; the list holds its frames
        self.animations = {
            # Walking
            "up": [], "down": [], "left": [], "right": [],
            # Standing still
            "right_idle": [], "left_idle": [], "up_idle": [], "down_idle": [],
            # Using the hoe
            "right_hoe": [], "left_hoe": [], "up_hoe": [], "down_hoe": [],
            # Using the axe
            "right_axe": [], "left_axe": [], "up_axe": [], "down_axe": [],
            # Using the watering can
            "right_water": [], "left_water": [], "up_water": [], "down_water": [],
            # @STUDENT-EDIT-Day5-2: Add custom animation folder path here (e.g. 'celebrate')
        }

        # Fill each list by loading the matching graphics/character/<state> folder
        for animation in self.animations.keys():
            full_path = "graphics/character/" + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        """Advance the current animation by one time-step and show that frame."""
        # Advance the frame; *4 sets the speed, *dt keeps it framerate-independent
        self.frame_index += 4 * dt

        # Loop back to the start once we pass the last frame
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        # Pick the current frame (int() because list indices must be whole numbers)
        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        """Read the keyboard and turn key presses into movement and actions."""
        keys = pygame.key.get_pressed()  # True/False for every key

        # Ignore input while using a tool or sleeping
        if not self.timers["tool use"].active and not self.sleep:

            # MOVEMENT CONTROLS (vertical)
            # @STUDENT-EDIT-Day2-5: Amend input controls to allow WASD movement using the logical 'or'
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = "up"
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = "down"
            else:
                self.direction.y = 0

            # MOVEMENT CONTROLS (horizontal)
            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = "right"
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = "left"
            else:
                self.direction.x = 0

            # TOOL USAGE - use the current tool (stop moving, restart its animation)
            if keys[pygame.K_SPACE]:
                self.timers["tool use"].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # TOOL SWITCHING - cycle to the next tool, wrapping at the end
            if keys[pygame.K_q] and not self.timers["tool switch"].active:
                self.timers["tool switch"].activate()
                self.tool_index += 1
                self.tool_index = (
                    self.tool_index if self.tool_index < len(self.tools) else 0
                )
                self.selected_tool = self.tools[self.tool_index]

            # SEED PLANTING - plant with Ctrl (stop moving, restart animation)
            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                self.timers["seed use"].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            # SEED SWITCHING - cycle to the next seed, wrapping at the end
            if keys[pygame.K_e] and not self.timers["seed switch"].active:
                self.timers["seed switch"].activate()
                self.seed_index += 1
                self.seed_index = (
                    self.seed_index if self.seed_index < len(self.seeds) else 0
                )
                self.selected_seed = self.seeds[self.seed_index]

            # INTERACTION (Enter) - talk to an NPC, else open shop / sleep in bed
            if keys[pygame.K_RETURN]:
                # NPCs take priority
                collided_npc = pygame.sprite.spritecollide(self, self.npc_sprites, False)
                if collided_npc:
                    npc = collided_npc[0]
                    self.trigger_dialogue(npc.name, npc.dialogue)
                    self.direction = pygame.math.Vector2()  # freeze while talking
                else:
                    # Otherwise check for a Bed/Trader interaction zone we're touching
                    collided_interaction_sprite = pygame.sprite.spritecollide(
                        self, self.interaction, False
                    )
                    if collided_interaction_sprite:
                        if collided_interaction_sprite[0].name == "Trader":
                            self.toggle_shop()
                        else:  # bed -> sleep
                            self.status = "left_idle"
                            self.sleep = True

    def get_status(self):
        """Pick the animation state from movement/tool use (e.g. "right" -> "right_idle")."""
        # Not moving -> idle version of the current facing direction
        if self.direction.magnitude() == 0:
            self.status = self.status.split("_")[0] + "_idle"

        # Using a tool -> tool version (e.g. "right" + "hoe" -> "right_hoe")
        if self.timers["tool use"].active:
            self.status = self.status.split("_")[0] + "_" + self.selected_tool

    def update_timers(self):
        """Tick every timer so its cooldown counts down."""
        for timer in self.timers.values():
            timer.update()

    def collision(self, direction):
        """Stop the player at any solid sprite, one axis at a time so we can slide walls."""
        for sprite in self.collision_sprites.sprites():
            # Skip sprites without a collision box, and any we aren't overlapping
            if hasattr(sprite, "hitbox") and sprite.hitbox.colliderect(self.hitbox):

                # Horizontal: snap to the side of the obstacle we ran into
                if direction == "horizontal":
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right
                    self.rect.centerx = self.hitbox.centerx
                    self.pos.x = self.hitbox.centerx

                # Vertical: same idea, top/bottom
                if direction == "vertical":
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.hitbox.bottom
                    self.rect.centery = self.hitbox.centery
                    self.pos.y = self.hitbox.centery

    def move(self, dt):
        """Move by direction*speed*dt, checking collisions per axis."""
        # Normalize so diagonal isn't faster than straight movement
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # Horizontal: move, sync hitbox/rect, then resolve collisions
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision("horizontal")

        # Vertical: same again
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision("vertical")

        # @STUDENT-EDIT-Day2-4: Add a simple boundary check 'if' statement to prevent the player from leaving the screen.

    def update(self, dt):
        """Run one frame of the player: input -> status -> timers -> aim -> move -> animate."""
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        self.move(dt)
        self.animate(dt)
