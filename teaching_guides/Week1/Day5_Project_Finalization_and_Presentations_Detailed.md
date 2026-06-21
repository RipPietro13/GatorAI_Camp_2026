# Day 5: Project Finalization and Presentations

## Objective
Polish game modifications and present final projects.

## Activities
- **Polish & Personalization** — custom sprites, dialogue, NPCs, settings
- **Testing** — walk through every change and confirm it works
- **Show & Tell** — demonstrate the modified game
- **Reflection & Next Steps**
- **Deliverable**: Push final project to personal GitHub repository

## Code References

> Snippets are copied from the real project files. Search for the quoted code or the
> `@STUDENT-EDIT` marker rather than relying on exact line numbers.

### Polish 1: Custom Player Animation
**File**: [player.py](../../player.py) — `import_assets()`

The animation dictionary already has a marked spot for a custom animation folder:

```python
    def import_assets(self):
        self.animations = {
            "up": [], "down": [], "left": [], "right": [],
            "right_idle": [], "left_idle": [], "up_idle": [], "down_idle": [],
            # ... tool animations ...
            # @STUDENT-EDIT-Day5-2: Add custom animation folder path here (e.g. 'celebrate')
        }

        for animation in self.animations.keys():
            full_path = "graphics/character/" + animation
            self.animations[animation] = import_folder(full_path)
```

**DETAILED WALKTHROUGH:**
- To add a `"celebrate"` animation a student would: (1) add `"celebrate": []` at the
  `@STUDENT-EDIT-Day5-2` marker, (2) create the folder
  `graphics/character/celebrate/` with PNG frames, and (3) set
  `self.status = "celebrate"` somewhere (e.g. after a sale). The existing `for` loop
  loads the new folder automatically — no other code changes needed.

### Polish 2: Personalized Title and Names
**File**: [settings.py](../../settings.py)

These real constants are the easy personalization knobs (no invented settings needed):

```python
TITLE = "PyDew Valley: GAIC 26"   # @STUDENT-EDIT-Day1-2
PLAYER_NAME = "Farmer"            # @STUDENT-EDIT-Day5-1
GREETING = "Hello there!"         # @STUDENT-EDIT-Day5-1
```

**DETAILED WALKTHROUGH:**
- `PLAYER_NAME` and `GREETING` exist specifically for personalization (marker
  `@STUDENT-EDIT-Day5-1`). Students can use f-strings to weave `PLAYER_NAME` into NPC
  dialogue, e.g. returning `f"Welcome back, {PLAYER_NAME}!"` from
  `_get_static_fallback`.

### Polish 3: Loading Dialogue From a File (Stretch Goal)
**File**: [dialogue_system.py](../../dialogue_system.py) — near `_get_static_fallback()`

Marker `@STUDENT-EDIT-Day5-3` suggests replacing the hard-coded dictionary with text
loaded from a file. A minimal, real implementation students can add:

```python
    def _get_static_fallback(self, character_id):
        # @STUDENT-EDIT-Day5-3: load custom dialogue from a text file instead of hardcoding
        try:
            with open(f"dialogue/{character_id}.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            pass  # fall through to the built-in defaults

        fallbacks = {
            "trader": "Welcome, friend! ..."
        }
        return fallbacks.get(character_id, "Hello there! Nice day for farming.")
```

**DETAILED WALKTHROUGH:**
- This teaches **file I/O** (`open`, `with`, reading text) and **error handling**
  (`try/except FileNotFoundError`) using a feature students actually asked for. If the
  file is missing, the game still works with the built-in lines.

### Testing: There's a Real Test Script
**File**: [test_emotions.py](../../test_emotions.py)

The project ships a real, runnable test/demo script. It exercises the emotion deque and
the AI dialogue manager's fallback path without needing the camera:

```python
from collections import deque
from emotion_detector import EmotionDetector
from ai_dialogue_manager import AIDialogueManager

def test_emotion_integration():
    emotions_deque = deque(maxlen=5)
    for emotion in ["happy", "sad", "angry", "surprised", "neutral"]:
        emotions_deque.append(emotion)

    ai_manager = AIDialogueManager()
    for emotion in ["happy", "sad", "angry", "neutral"]:
        dialogue = ai_manager.generate_npc_dialogue(
            character_name="Merchant Pete",
            character_role="friendly trader",
            player_context=f"player seems {emotion}",
            emotion=emotion,
        )
        print(f"{emotion} -> {dialogue}")

if __name__ == "__main__":
    test_emotion_integration()
```

Run it with `python test_emotions.py`.

**DETAILED WALKTHROUGH:**
- This is a good model for "manual testing as a script": it constructs the same
  `deque(maxlen=5)` the game uses and prints the dialogue produced for each emotion.
- Because `AIDialogueManager` falls back to static, emotion-aware lines when no API key
  is present, this script works even offline — students can confirm their Week-1
  dialogue edits behave before any AI is configured.

### A Simple Real UI to Study: The Character Screen
**File**: [character_screen.py](../../character_screen.py)

This is the shortest UI file and a clean capstone read — it loops over the player's
inventory dictionaries to draw text:

```python
    def display(self):
        self.display_surface.fill("black")
        y_offset = 50
        # ... draw "Inventory" title ...
        for item, amount in self.player.item_inventory.items():
            text_surf = self.font.render(f"{item}: {amount}", True, "White")
            self.display_surface.blit(text_surf, (50, y_offset))
            y_offset += 40
```

**DETAILED WALKTHROUGH:**
- Pressing **I** in-game toggles this screen (see `main.py`'s event loop).
- It ties together everything from the week: dictionaries (`item_inventory`), loops
  (`.items()`), f-strings, and drawing text. A great "you now understand this whole
  file" moment for the showcase.

### Sharing: How Dependencies Are Handled
**File**: [installer.py](../../installer.py)

```python
def install(package_name):
    package_import_map = {
        "opencv-python": "cv2",
        "pytorch_lightning": "pytorch_lightning",
        "pygame-ce": "pygame",
    }
    import_name = package_import_map.get(package_name, package_name)
    try:
        importlib.import_module(import_name)
        print(f"{package_name} is already installed.")
    except ImportError:
        print(f"{package_name} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install",
                               "--only-binary", ":all:", package_name])
```

**DETAILED WALKTHROUGH:**
- This is why a friend can clone the repo and just run `python main.py`: missing
  libraries install themselves.
- Teaching points: the **install-name vs import-name** map (`pygame-ce` imports as
  `pygame`), and `--only-binary :all:`, which makes pip use prebuilt wheels and fail
  with a clear message instead of trying to compile from source on an unsupported
  Python version.

## Key Learning Points
1. **Pulling the week together** — sprites, dialogue, data structures, and UI in one
   project.
2. **Personalization** with real constants (`TITLE`, `PLAYER_NAME`, `GREETING`).
3. **File I/O + error handling** as a real, optional upgrade to the dialogue system.
4. **Manual testing** with `test_emotions.py`.
5. **Reproducible setup** via `installer.py` so the project runs on someone else's
   machine.

## Extension Activities
1. **Add a celebrate animation** (`@STUDENT-EDIT-Day5-2`) and trigger it after a sale.
2. **Weave `PLAYER_NAME` into dialogue** with f-strings (`@STUDENT-EDIT-Day5-1`).
3. **Move dialogue into text files** (`@STUDENT-EDIT-Day5-3`).
4. **Write your own tiny test** modeled on `test_emotions.py` that checks your custom
   NPC returns your custom lines.
5. **Record a short demo video** of your changes for the showcase.

## Presentation Guidelines
- **Duration**: 3–5 minutes.
- **Show**: your custom NPC(s), dialogue edits, and any sprite/animation changes.
- **Explain**: one piece of code you wrote and what it does.
- **Reflect**: one thing that was hard, one thing you're proud of.

## Troubleshooting Tips
- **Game won't start after edits:** read the console traceback bottom-up; the last line
  names the error and file. A missing colon or bad indentation is the usual cause.
- **New animation not showing:** confirm the folder name matches the dictionary key and
  that you set `self.status` to it.
- **Dialogue file not found:** paths are relative to where you run `python main.py`; the
  `try/except FileNotFoundError` keeps the game alive while you fix the path.
- **Friend can't run it:** make sure the `install(...)` lines at the top of `main.py`
  aren't all commented out, and that they're on Python 3.11/3.12.
