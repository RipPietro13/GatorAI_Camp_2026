import pygame
from settings import *
from timer import Timer
import game_settings


class SettingsMenu:
    """In-game/options settings screen: volumes, camera, and AI toggles."""
    def __init__(self, camera_change_callback=None):
        """Build the list of settings rows and set up fonts, state, and the indicator."""
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font("font/LycheeSoda.ttf", 32)
        self.title_font = pygame.font.Font("font/LycheeSoda.ttf", 60)
        self.instruction_font = pygame.font.Font("font/LycheeSoda.ttf", 20)
        self.camera_change_callback = camera_change_callback

        # Settings options
        self.setting_options = [
            {"name": "Master Volume", "type": "volume", "key": "master_volume"},
            {"name": "Music Volume", "type": "volume", "key": "music_volume"},
            {"name": "Sound Effects", "type": "volume", "key": "sfx_volume"},
            {"name": "Camera", "type": "camera", "key": "camera_index"},
            {"name": "Enable Camera", "type": "toggle", "key": "enable_camera"},
            {
                "name": "Enable AI Dialogue",
                "type": "toggle",
                "key": "enable_ai_dialogue",
            },
            {"name": "Back to Menu", "type": "action", "key": "back"},
        ]

        self.selected_index = 0
        self.input_timer = Timer(150)
        self.input_timer.activate()  # Activate timer immediately to prevent processing the opening ESC

        # Camera detection will only run when the player interacts with camera settings
        self.available_cameras = None
        self.cameras_loaded_once = False  # Prevent camera detection on first frame

        # Load corn graphic for selection indicator
        import os

        base_path = os.path.dirname(os.path.abspath(__file__))
        self.corn_surf = pygame.image.load(
            os.path.join(base_path, "graphics/overlay/corn.png")
        ).convert_alpha()

    def display(self):
        """Draw the title, every settings row with its control, and the instructions."""
        # Don't fill with black - let the caller handle the background
        # This allows the menu to be drawn on top of the game world

        # Title
        title_surf = self.title_font.render("Settings", True, "White")
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, 90))
        self.display_surface.blit(title_surf, title_rect)

        # Settings options
        start_y = 180
        for i, option in enumerate(self.setting_options):
            y_pos = start_y + i * 60

            # Option name
            color = "White" if i == self.selected_index else "Gray"
            name_surf = self.font.render(option["name"], True, color)
            name_rect = name_surf.get_rect(center=(SCREEN_WIDTH / 2 - 100, y_pos))
            self.display_surface.blit(name_surf, name_rect)

            # Option value/control
            if option["type"] == "volume":
                self.draw_volume_control(option, y_pos, i == self.selected_index)
            elif option["type"] == "camera":
                self.draw_camera_control(option, y_pos, i == self.selected_index)
            elif option["type"] == "toggle":
                self.draw_toggle_control(option, y_pos, i == self.selected_index)
            elif option["type"] == "action":
                # For "Back to Menu", just show the text
                pass

            # Selection indicator
            if i == self.selected_index:
                corn_rect = self.corn_surf.get_rect(
                    midright=(name_rect.left - 10, name_rect.centery)
                )
                self.display_surface.blit(self.corn_surf, corn_rect)

        # Instructions
        instructions = [
            "Use UP/DOWN arrows to navigate",
            "Use LEFT/RIGHT arrows to adjust volume or change camera",
            "Press ENTER to select, ESC to go back",
        ]

        instr_y = SCREEN_HEIGHT - 80
        for i, instruction in enumerate(instructions):
            instr_surf = self.instruction_font.render(instruction, True, "Yellow")
            instr_rect = instr_surf.get_rect(
                center=(SCREEN_WIDTH / 2, instr_y + i * 24)
            )
            self.display_surface.blit(instr_surf, instr_rect)

    def draw_volume_control(self, option, y_pos, is_selected):
        """Draw volume slider and percentage"""
        volume_percent = game_settings.get_volume_percentage(option["key"])

        # Volume bar background
        bar_width = 300
        bar_height = 20
        bar_x = SCREEN_WIDTH / 2 + 50
        bar_y = y_pos - bar_height // 2

        bg_color = "White" if is_selected else "Gray"
        fill_color = "Green" if is_selected else "DarkGreen"

        # Background bar
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.display_surface, bg_color, bg_rect, 2)

        # Fill bar based on volume
        fill_width = int((volume_percent / 100) * (bar_width - 4))
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x + 2, bar_y + 2, fill_width, bar_height - 4)
            pygame.draw.rect(self.display_surface, fill_color, fill_rect)

        # Volume percentage text
        percent_text = f"{volume_percent}%"
        percent_surf = self.font.render(percent_text, True, bg_color)
        percent_rect = percent_surf.get_rect(center=(bar_x + bar_width + 60, y_pos))
        self.display_surface.blit(percent_surf, percent_rect)

    def load_available_cameras(self):
        """Load available cameras lazily when the player opens camera settings."""
        if self.available_cameras is not None:
            return self.available_cameras

        if not game_settings.get("enable_camera", True):
            self.available_cameras = [
                {
                    "index": game_settings.get_camera_index(),
                    "name": game_settings.get_camera_name(
                        game_settings.get_camera_index()
                    ),
                }
            ]
        else:
            self.available_cameras = game_settings.detect_available_cameras()

        if not self.available_cameras:
            self.available_cameras = [
                {
                    "index": game_settings.get_camera_index(),
                    "name": game_settings.get_camera_name(
                        game_settings.get_camera_index()
                    ),
                }
            ]

        return self.available_cameras

    def draw_camera_control(self, option, y_pos, is_selected):
        """Draw camera selection control"""
        current_camera_index = game_settings.get_camera_index()
        
        # Skip loading cameras on the very first frame to prevent hangs
        if not self.cameras_loaded_once:
            cameras = [
                {
                    "index": current_camera_index,
                    "name": game_settings.get_camera_name(current_camera_index),
                }
            ]
            self.cameras_loaded_once = True
        else:
            cameras = self.load_available_cameras()
        
        current_camera = next(
            (
                cam
                for cam in cameras
                if cam["index"] == current_camera_index
            ),
            {"name": f"Camera {current_camera_index}"},
        )

        # Camera name display
        color = "White" if is_selected else "Gray"
        camera_text = current_camera["name"]
        camera_surf = self.font.render(camera_text, True, color)
        camera_rect = camera_surf.get_rect(center=(SCREEN_WIDTH / 2 + 150, y_pos))
        self.display_surface.blit(camera_surf, camera_rect)

        # Show arrows if more than one camera available
        if len(cameras) > 1 and is_selected:
            arrow_color = "Yellow" if is_selected else "Gray"
            # Left arrow
            left_arrow = self.font.render("<", True, arrow_color)
            left_rect = left_arrow.get_rect(
                midright=(camera_rect.left - 10, camera_rect.centery)
            )
            self.display_surface.blit(left_arrow, left_rect)

            # Right arrow
            right_arrow = self.font.render(">", True, arrow_color)
            right_rect = right_arrow.get_rect(
                midleft=(camera_rect.right + 10, camera_rect.centery)
            )
            self.display_surface.blit(right_arrow, right_rect)

    def draw_toggle_control(self, option, y_pos, is_selected):
        """Draw toggle (on/off) control for boolean settings"""
        enabled = game_settings.get(option["key"], True)
        color = "White" if is_selected else "Gray"
        toggle_text = "ON" if enabled else "OFF"
        toggle_color = "Green" if enabled else "Red"
        toggle_surf = self.font.render(toggle_text, True, toggle_color)
        toggle_rect = toggle_surf.get_rect(center=(SCREEN_WIDTH / 2 + 150, y_pos))
        self.display_surface.blit(toggle_surf, toggle_rect)

    def input(self):
        """Handle navigation and edits; return "back" when leaving, else None."""
        keys = pygame.key.get_pressed()
        self.input_timer.update()

        if self.input_timer.active:
            return None

        # Navigation
        if keys[pygame.K_UP]:
            self.selected_index = (self.selected_index - 1) % len(self.setting_options)
            self.input_timer.activate()
        elif keys[pygame.K_DOWN]:
            self.selected_index = (self.selected_index + 1) % len(self.setting_options)
            self.input_timer.activate()

        # Volume adjustment and toggle
        elif keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            current_option = self.setting_options[self.selected_index]
            if current_option["type"] == "volume":
                current_volume = game_settings.get_volume_percentage(
                    current_option["key"]
                )
                if keys[pygame.K_LEFT]:
                    new_volume = max(0, current_volume - 5)
                else:  # RIGHT
                    new_volume = min(100, current_volume + 5)
                game_settings.set_volume_percentage(current_option["key"], new_volume)
                self.input_timer.activate()
            elif current_option["type"] == "camera":
                current_index = game_settings.get_camera_index()
                # Load cameras when player tries to change them
                self.cameras_loaded_once = True
                camera_indices = [cam["index"] for cam in self.load_available_cameras()]
                if current_index in camera_indices:
                    current_pos = camera_indices.index(current_index)
                else:
                    current_pos = 0
                if keys[pygame.K_LEFT]:
                    new_pos = (current_pos - 1) % len(camera_indices)
                else:  # RIGHT
                    new_pos = (current_pos + 1) % len(camera_indices)
                new_camera_index = camera_indices[new_pos]
                old_camera_index = game_settings.get_camera_index()
                game_settings.set_camera_index(new_camera_index)
                if old_camera_index != new_camera_index and self.camera_change_callback:
                    self.camera_change_callback()
                self.input_timer.activate()
            elif current_option["type"] == "toggle":
                # Toggle the boolean value
                current_value = game_settings.get(current_option["key"], True)
                game_settings.set(current_option["key"], not current_value)
                if current_option["key"] == "enable_camera":
                    self.available_cameras = None
                self.input_timer.activate()

        # Selection
        elif keys[pygame.K_RETURN]:
            current_option = self.setting_options[self.selected_index]
            if current_option["key"] == "back":
                return "back"
            self.input_timer.activate()

        # Back to menu
        elif keys[pygame.K_ESCAPE]:
            return "back"

        return None

    def update(self):
        """Process input and return its result ("back" or None); drawing is done by the caller."""
        result = self.input()
        return result
