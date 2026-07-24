import pygame
from settings import *
from timer import Timer


class TraderMenu:
    """The buy/sell shop UI: lists items to sell and seeds to buy."""
    def __init__(self, player, open_menu_callback):
        """Set up the menu options from the player's inventory and the layout."""
        # general setup
        self.player = player
        self.open_menu_callback = open_menu_callback  # Changed from toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font("font/LycheeSoda.ttf", 30)

        # options
        self.width = 500  # Increase the width of the text boxes
        self.space = 10
        self.padding = 8

        # entries
        self.options = list(self.player.item_inventory.keys()) + [
            f"{seed} seed" for seed in self.player.seed_inventory.keys()
        ]
        self.sell_border = len(self.player.item_inventory) - 1
        self.setup()

        # movement
        self.index = 0
        self.timer = Timer(200)

        # quantity entry state
        self.quantity_mode = False
        self.quantity_text = ""
        self.pending_action = None
        self.pending_item = None
        self.prompt_message = ""
        self.close_button_rect = None

    def display_money(self):
        """Draw the player's current money at the bottom of the screen."""
        text_surf = self.font.render(f"${self.player.money}", False, "Black")
        text_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))

        pygame.draw.rect(self.display_surface, "White", text_rect.inflate(10, 10), 0, 4)
        self.display_surface.blit(text_surf, text_rect)

    def setup(self):
        """Pre-render each menu row's text and compute the menu's size/position."""
        # create the text surfaces
        self.text_surfs = []
        self.total_height = 0

        for item in self.options:
            text_surf = self.font.render(item, False, "Black")
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)

        self.total_height += (len(self.text_surfs) - 1) * self.space
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(
            SCREEN_WIDTH / 2 - self.width / 2,
            self.menu_top,
            self.width,
            self.total_height,
        )

        # buy / sell text surface
        self.buy_text = self.font.render("buy", False, "Black")
        self.sell_text = self.font.render("sell", False, "Black")

    def start_quantity_entry(self):
        """Open a numeric prompt for buying or selling a chosen amount."""
        self.quantity_mode = True
        self.quantity_text = ""
        self.prompt_message = ""
        self.pending_action = "sell" if self.index <= self.sell_border else "buy"
        self.pending_item = self.options[self.index]

    def cancel_quantity_entry(self):
        """Close the quantity prompt without applying any changes."""
        self.quantity_mode = False
        self.quantity_text = ""
        self.prompt_message = ""
        self.pending_action = None
        self.pending_item = None

    def confirm_quantity_entry(self):
        """Apply the entered amount to the selected buy/sell action."""
        if not self.quantity_text:
            self.prompt_message = "Enter a number"
            return

        quantity = int(self.quantity_text)
        if quantity <= 0:
            self.prompt_message = "Use a number above 0"
            return

        if self.pending_action == "sell":
            current_item = self.pending_item
            available = self.player.item_inventory[current_item]
            amount_to_sell = min(quantity, available)
            if amount_to_sell > 0:
                self.player.item_inventory[current_item] -= amount_to_sell
                self.player.money += SALE_PRICES[current_item] * amount_to_sell
            else:
                self.prompt_message = "You have none to sell"
                self.quantity_mode = False
                self.quantity_text = ""
                self.pending_action = None
                self.pending_item = None
                return
        else:
            seed_name = self.pending_item.split()[0]
            seed_price = PURCHASE_PRICES[seed_name]
            max_affordable = self.player.money // seed_price if seed_price > 0 else 0
            amount_to_buy = min(quantity, max_affordable)
            if amount_to_buy > 0:
                self.player.seed_inventory[seed_name] += amount_to_buy
                self.player.money -= seed_price * amount_to_buy
            else:
                self.prompt_message = "Not enough money"
                self.quantity_mode = False
                self.quantity_text = ""
                self.pending_action = None
                self.pending_item = None
                return

        self.quantity_mode = False
        self.quantity_text = ""
        self.prompt_message = ""
        self.pending_action = None
        self.pending_item = None

    def get_prompt_rect(self):
        """Return the rectangle used for the quantity popup."""
        return pygame.Rect(SCREEN_WIDTH / 2 - 220, SCREEN_HEIGHT / 2 - 90, 440, 180)

    def get_close_button_rect(self):
        """Return the rectangle for the popup's close button."""
        prompt_rect = self.get_prompt_rect()
        return pygame.Rect(prompt_rect.right - 36, prompt_rect.top + 10, 24, 24)

    def handle_quantity_events(self, events):
        """Process keyboard and mouse input while the quantity prompt is active."""
        self.close_button_rect = self.get_close_button_rect()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.close_button_rect.collidepoint(event.pos):
                    self.cancel_quantity_entry()
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.cancel_quantity_entry()
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.confirm_quantity_entry()
                elif event.key == pygame.K_BACKSPACE:
                    self.quantity_text = self.quantity_text[:-1]
                elif event.unicode.isdigit():
                    self.quantity_text += event.unicode
                    if len(self.quantity_text) > 4:
                        self.quantity_text = self.quantity_text[:4]

    def input(self, events):
        """Handle navigation and open a quantity prompt for buy/sell actions."""
        keys = pygame.key.get_pressed()
        self.timer.update()

        if self.quantity_mode:
            self.handle_quantity_events(events)
            return

        if keys[pygame.K_ESCAPE]:
            pass

        if not self.timer.active:
            if keys[pygame.K_UP]:
                self.index -= 1
                self.timer.activate()

            if keys[pygame.K_DOWN]:
                self.index += 1
                self.timer.activate()

            if keys[pygame.K_SPACE]:
                self.timer.activate()
                self.start_quantity_entry()

        # clamp the values
        if self.index < 0:
            self.index = len(self.options) - 1
        if self.index > len(self.options) - 1:
            self.index = 0

    def show_entry(self, text_surf, amount, top, selected, item_index):
        """Draw one menu row: name, amount owned, price, and buy/sell highlight."""
        # background
        bg_rect = pygame.Rect(
            self.main_rect.left,
            top,
            self.width,
            text_surf.get_height() + (self.padding * 2),
        )
        pygame.draw.rect(self.display_surface, "White", bg_rect, 0, 4)

        # text
        text_rect = text_surf.get_rect(
            midleft=(self.main_rect.left + 20, bg_rect.centery)
        )
        self.display_surface.blit(text_surf, text_rect)

        # amount
        amount_surf = self.font.render(str(amount), False, "Black")
        amount_rect = amount_surf.get_rect(
            midright=(self.main_rect.right - 20, bg_rect.centery)
        )
        self.display_surface.blit(amount_surf, amount_rect)

        # price
        if item_index <= self.sell_border:
            price = SALE_PRICES[self.options[item_index]]
        else:
            seed_name = self.options[item_index].split()[0]
            price = PURCHASE_PRICES[seed_name]
        price_surf = self.font.render(f"${price}", False, "Black")
        price_rect = price_surf.get_rect(
            midright=(self.main_rect.right - 100, bg_rect.centery)
        )
        self.display_surface.blit(price_surf, price_rect)

        # selected
        if selected:
            pygame.draw.rect(self.display_surface, "black", bg_rect, 4, 4)
            if item_index <= self.sell_border:  # sell
                pos_rect = self.sell_text.get_rect(
                    midleft=(self.main_rect.left + 200, bg_rect.centery)
                )  # Adjust position
                self.display_surface.blit(self.sell_text, pos_rect)
            else:  # buy
                pos_rect = self.buy_text.get_rect(
                    midleft=(self.main_rect.left + 200, bg_rect.centery)
                )  # Adjust position
                self.display_surface.blit(self.buy_text, pos_rect)

    def update(self, events=None):
        """Process shop input each frame."""
        self.input(events or [])

    def display(self):
        """Draw the money total and every buyable/sellable row."""
        self.display_money()

        for text_index, text_surf in enumerate(self.text_surfs):
            top = self.main_rect.top + text_index * (
                text_surf.get_height() + (self.padding * 2) + self.space
            )
            amount_list = list(self.player.item_inventory.values()) + list(
                self.player.seed_inventory.values()
            )
            amount = amount_list[text_index]
            self.show_entry(
                text_surf, amount, top, self.index == text_index, text_index
            )

        if self.quantity_mode:
            prompt_rect = self.get_prompt_rect()
            pygame.draw.rect(self.display_surface, "White", prompt_rect, 0, 8)
            pygame.draw.rect(self.display_surface, "Black", prompt_rect, 4, 8)

            self.close_button_rect = self.get_close_button_rect()
            pygame.draw.rect(self.display_surface, "Red", self.close_button_rect, 0, 6)
            close_text = self.font.render("X", False, "White")
            close_rect = close_text.get_rect(center=self.close_button_rect.center)
            self.display_surface.blit(close_text, close_rect)

            title_surf = self.font.render("How many?", False, "Black")
            title_rect = title_surf.get_rect(midtop=(prompt_rect.centerx, prompt_rect.top + 20))
            self.display_surface.blit(title_surf, title_rect)

            item_label = self.pending_item if self.pending_item else "item"
            action_label = "sell" if self.pending_action == "sell" else "buy"
            info_surf = self.font.render(f"{action_label.title()} {item_label}", False, "Black")
            info_rect = info_surf.get_rect(midtop=(prompt_rect.centerx, prompt_rect.top + 60))
            self.display_surface.blit(info_surf, info_rect)

            input_rect = pygame.Rect(prompt_rect.centerx - 90, prompt_rect.top + 100, 180, 45)
            pygame.draw.rect(self.display_surface, "LightGray", input_rect, 0, 6)
            pygame.draw.rect(self.display_surface, "Black", input_rect, 2, 6)

            value_surf = self.font.render(self.quantity_text or "0", False, "Black")
            value_rect = value_surf.get_rect(center=input_rect.center)
            self.display_surface.blit(value_surf, value_rect)

            hint_surf = self.font.render("Enter to confirm • Esc to cancel", False, "Black")
            hint_rect = hint_surf.get_rect(midtop=(prompt_rect.centerx, prompt_rect.top + 150))
            self.display_surface.blit(hint_surf, hint_rect)

            if self.prompt_message:
                error_surf = self.font.render(self.prompt_message, False, "Red")
                error_rect = error_surf.get_rect(midtop=(prompt_rect.centerx, prompt_rect.top + 130))
                self.display_surface.blit(error_surf, error_rect)
