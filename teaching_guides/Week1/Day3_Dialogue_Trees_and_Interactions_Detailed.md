# Day 3: Dialogue Trees and Interactions

## Objective
Create branching conversations and interactive dialogue systems.

## Core Concepts
- **Introduction to Dialogue Trees**
  - Storing dialogue in data structures (lists / dictionaries)
- **Using Lists and Dictionaries**
- **Loops and Conditionals for Navigating Dialogue**

## Exercise: Implementing a Conversation
The student-facing steps live in
[student_tutorials/Day3_Dialogue.md](../../student_tutorials/Day3_Dialogue.md).
Students edit the fallback dialogue and experiment with branching.
- **Deliverable**: Push project to personal GitHub repository

## Code References

> Snippets are copied from the real project files. Search for the quoted code or the
> `@STUDENT-EDIT` marker rather than relying on exact line numbers.

### The Dialogue System
**File**: [dialogue_system.py](../../dialogue_system.py) — `class DialogueSystem`

The dialogue system shows a text box and steps through pages of text. It can use
**static** lines (Week 1) or **AI-generated** lines (Week 2). Today we focus on the
static path.

```python
import pygame
from settings import *
from timer import Timer
import game_settings

# Try to import AI dialogue manager, fall back gracefully if it fails
try:
    from ai_dialogue_manager import AIDialogueManager
    AI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AI Dialogue Manager not available: {e}")
    AI_AVAILABLE = False


class DialogueSystem:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font("font/LycheeSoda.ttf", 30)
        self.active = False
        self.current_dialogue = []
        self.dialogue_index = 0
        self.on_finish_callback = None
```

**DETAILED WALKTHROUGH:**
1. **The `try/except` import** is *defensive programming*: if the AI library isn't
   installed, the game still runs with static dialogue. `AI_AVAILABLE` records which
   mode we're in. (Students don't need the AI working in Week 1.)
2. **`self.active`** — a boolean flag for "is a conversation showing right now?"
3. **`self.current_dialogue`** — a *list* of pages to show.
4. **`self.dialogue_index`** — an integer tracking which page we're on.
5. **`self.on_finish_callback`** — a function to call when the conversation ends (used
   later so the trader's shop opens after he finishes talking).

### Starting a Conversation
**File**: [dialogue_system.py](../../dialogue_system.py) — `start_dialogue()`

This method shows the three sources of dialogue. The branch we care about today is the
last one (static fallback):

```python
    def start_dialogue(self, character_id, player_context=None,
                       dialogue_lines=None, on_finish=None):
        self.active = True
        self.dialogue_index = 0
        self.on_finish_callback = on_finish
        # @STUDENT-EDIT-Day4-1: Insert print() statements here to debug which branch runs

        if dialogue_lines:
            # Explicit lines passed in (e.g. from a custom NPC in NPC_DATA)
            self.current_dialogue = []
            for paragraph in dialogue_lines:
                pages = self._wrap_text(paragraph, self.text_box_rect.width - 40)
                self.current_dialogue.extend(pages)
        elif self.ai_enabled and self.ai_manager and player_context:
            # AI-generated dialogue (Week 2)
            dialogue_line = self.ai_manager.generate_npc_dialogue(...)
            self.current_dialogue = self._wrap_text(dialogue_line, self.text_box_rect.width - 40)
        else:
            # Static fallback dialogue
            fallback_dialogue = self._get_static_fallback(character_id)
            self.current_dialogue = self._wrap_text(fallback_dialogue, self.text_box_rect.width - 40)
```

**DETAILED WALKTHROUGH:**
- **`if dialogue_lines:`** — if a caller hands in a list of lines (this is how custom
  NPCs from `NPC_DATA` talk), we use those directly. A `for` loop wraps each paragraph
  into pages that fit the box.
- **`elif self.ai_enabled ...`** — the AI path, covered in Week 2.
- **`else:`** — the static fallback, looked up by `character_id`. This is the simplest
  case and the focus of Day 3.

### Storing Dialogue in a Dictionary
**File**: [dialogue_system.py](../../dialogue_system.py) — `_get_static_fallback()`

This is the exact spot students edit today. It's a dictionary lookup with a default:

```python
    def _get_static_fallback(self, character_id):
        # @STUDENT-EDIT-Day5-3: Try loading custom dialogue from a text file here
        # @STUDENT-EDIT-Day3-1: Add a new greeting string to this dialogue dictionary
        fallbacks = {
            "trader": "Welcome, friend! I have many fine goods for a hardworking "
                      "farmer like you. Let's see what you need."
        }
        # @STUDENT-EDIT-Day3-2: Create a branching dialogue option using nested lists/dictionaries
        # @STUDENT-EDIT-Day3-3: Add a dialogue choice that ends the conversation early (self.active = False)
        return fallbacks.get(character_id, "Hello there! Nice day for farming.")
```

**DETAILED WALKTHROUGH:**
- **`fallbacks = { ... }`** — a dictionary mapping a character id (string) to a line
  (string). Marker `@STUDENT-EDIT-Day3-1` is where students add a new entry.
- **`fallbacks.get(character_id, "Hello there! ...")`** — `.get()` returns the matching
  line, or the default if the id isn't in the dictionary. Great teaching moment for
  "dictionary with a default."
- Markers `@STUDENT-EDIT-Day3-2` and `-3` point students toward turning this flat
  lookup into a *branching* structure (nested dictionaries/lists) and adding an option
  that ends the conversation by setting `self.active = False`.

### Advancing and Ending Dialogue (Loops & Index)
**File**: [dialogue_system.py](../../dialogue_system.py) — `next_line()` / `end_dialogue()` / `input()`

```python
    def next_line(self):
        self.dialogue_index += 1
        if self.dialogue_index >= len(self.current_dialogue):
            self.end_dialogue()

    def end_dialogue(self):
        self.active = False
        self.current_dialogue = []
        self.dialogue_index = 0
        if self.on_finish_callback:
            self.on_finish_callback()
            self.on_finish_callback = None

    def input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    # @STUDENT-EDIT-Day4-2: Link a dialogue choice to a sprite action here
                    self.next_line()
                    return True
        return False
```

**DETAILED WALKTHROUGH:**
- **`next_line()`** increments the index and checks `if self.dialogue_index >= len(...)`
  to detect the end — a classic "walk through a list with an index" pattern.
- **`end_dialogue()`** resets everything and fires the optional callback. This is how
  the trader's shop opens *after* his greeting finishes.
- **`input(events)`** loops over events and advances on SPACE/ENTER. Note it loops over
  an `events` list passed in — the game collects events once and shares them, which
  avoids input being "eaten" by the wrong system.

### How an NPC Triggers Dialogue
**File**: [player.py](../../player.py) — interaction in `input()`, and
[level.py](../../level.py) — `trigger_npc_dialogue()`

When the player presses ENTER next to an NPC, the player asks the level to start that
NPC's dialogue:

```python
# in player.py input(), when ENTER is pressed:
collided_npc = pygame.sprite.spritecollide(self, self.npc_sprites, False)
if collided_npc:
    npc = collided_npc[0]
    self.trigger_dialogue(npc.name, npc.dialogue)   # callback into the Level
    self.direction = pygame.math.Vector2()           # stop moving while talking
```

```python
# in level.py:
def trigger_npc_dialogue(self, name, lines):
    self.dialogue_system.start_dialogue(character_id=name, dialogue_lines=lines)
```

**DETAILED WALKTHROUGH:**
- **`pygame.sprite.spritecollide(...)`** checks whether the player overlaps any NPC.
- The NPC's `name` and `dialogue` (set from `NPC_DATA` back on Day 2) are passed via the
  `trigger_dialogue` *callback*. This is a clean way for the player to talk to the level
  without the player needing a direct reference to the dialogue system.
- `start_dialogue(... dialogue_lines=lines)` lands in the first branch we saw above, so
  custom NPCs show exactly the lines from `NPC_DATA`.

## Key Learning Points
1. **Storing dialogue in data structures** — lists of pages, and a dictionary of
   character → line.
2. **Conditionals and `.get()` with a default** — choosing what an NPC says.
3. **Looping through dialogue with an index** — `next_line()` and the end check.
4. **Callbacks** — `trigger_dialogue` and `on_finish_callback` connect systems without
   tangling them together.
5. **Graceful fallbacks** — the `try/except` AI import keeps the game working offline.

## Extension Activities
1. **Add a greeting** — new entry in the `fallbacks` dictionary (`@STUDENT-EDIT-Day3-1`).
2. **Branching dialogue** — replace the flat string with a nested dictionary keyed by
   the player's choice (`@STUDENT-EDIT-Day3-2`).
3. **End early** — add an option that sets `self.active = False`
   (`@STUDENT-EDIT-Day3-3`).
4. **Give your Day-2 NPC more to say** — expand its `dialogue` list in `NPC_DATA`.

## Troubleshooting Tips
- **Dialogue never appears:** the player must be *touching* the NPC when ENTER is
  pressed. Check the NPC's `pos` in `NPC_DATA` and that it's added to `npc_sprites`.
- **`KeyError` looking up dialogue:** use `fallbacks.get(id, default)` (with a default),
  not `fallbacks[id]`, so an unknown character id can't crash the game.
- **Text runs off the box:** `_wrap_text` handles wrapping; if you pass a huge single
  paragraph it becomes multiple pages — press SPACE/ENTER to advance.
- **Shop opens before the greeting finishes (trader):** that's controlled by
  `on_finish_callback` in `end_dialogue()` — don't open the shop directly from the
  trigger.
