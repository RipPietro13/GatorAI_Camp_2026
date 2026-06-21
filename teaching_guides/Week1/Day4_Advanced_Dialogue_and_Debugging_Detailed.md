# Day 4: Advanced Dialogue and Debugging

## Objective
Enhance dialogue systems, tie interactions to sprite actions, and learn debugging.

## Core Concepts
- **Refining Dialogue** — multi-page text, wrapping, callbacks
- **Sprite Interaction** — tying an action (like a screen shake) to an event
- **Basic Debugging** — `print()` to track variables, reading error messages

## Exercise: Complex Dialogue
The student-facing steps live in
[student_tutorials/Day4_Advanced.md](../../student_tutorials/Day4_Advanced.md).
- **Deliverable**: Push project to personal GitHub repository

## Code References

> Snippets are copied from the real project files. Search for the quoted code or the
> `@STUDENT-EDIT` marker rather than relying on exact line numbers.

### Multi-Page Dialogue: Text Wrapping
**File**: [dialogue_system.py](../../dialogue_system.py) — `_wrap_text()`

The dialogue box can only fit a few lines, so long text is broken into lines and grouped
into pages. This is a nice example of building up lists with loops and conditionals:

```python
    def _wrap_text(self, text, max_width):
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                if current_line.strip():
                    lines.append(current_line.strip())
                current_line = word + " "

        if current_line.strip():
            lines.append(current_line.strip())

        # Group lines into pages that fit in the dialogue box
        lines_per_page = 4
        pages = []
        for i in range(0, len(lines), lines_per_page):
            pages.append(lines[i : i + lines_per_page])

        return pages if pages else [["No dialogue available."]]
```

**DETAILED WALKTHROUGH:**
1. **`text.split(" ")`** breaks the sentence into words.
2. The `for word in words:` loop adds words to `current_line` until the line would be
   too wide (`self.font.size(test_line)[0] < max_width`), then starts a new line.
3. The second loop groups every 4 lines into a *page* using `range(0, len(lines), 4)`
   and list slicing `lines[i : i + lines_per_page]`.
4. **`return pages if pages else [["..."]]`** guarantees we never return an empty list —
   a small but important "defensive" habit that prevents an index error later.

### Drawing the Dialogue Box
**File**: [dialogue_system.py](../../dialogue_system.py) — `draw()`

```python
    def draw(self):
        if self.active:
            pygame.draw.rect(self.display_surface, "White", self.text_box_rect, 0, 10)
            pygame.draw.rect(self.display_surface, "Black", self.text_box_rect, 4, 10)

            if self.dialogue_index < len(self.current_dialogue):
                current_page = self.current_dialogue[self.dialogue_index]
                line_height = 35
                start_y = self.text_box_rect.y + 20
                for i, line in enumerate(current_page):
                    if line.strip():
                        line_surface = self.font.render(line, True, "Black")
                        self.display_surface.blit(
                            line_surface,
                            (self.text_box_rect.x + 20, start_y + i * line_height),
                        )
```

**DETAILED WALKTHROUGH:**
- Two `pygame.draw.rect` calls draw a white box with a black rounded border.
- **`if self.dialogue_index < len(self.current_dialogue):`** is a bounds check before
  indexing into the list — the kind of guard that prevents crashes.
- The `for i, line in enumerate(current_page):` loop draws each line 35 px lower than
  the last (`start_y + i * line_height`).

### Tying an Action to an Interaction: Screen Shake
**File**: [player.py](../../player.py) — `use_tool()`, and [level.py](../../level.py) — `shake_camera()`

A great "sprite reacts to an event" example already lives in the game: chopping a tree
shakes the screen.

```python
# in player.py use_tool():
if self.selected_tool == "axe":
    for tree in self.tree_sprites.sprites():
        if tree.rect.collidepoint(self.target_pos):
            tree.damage()       # tell the tree it was hit
            self.shake_camera() # trigger a screen shake!
```

```python
# in level.py:
def shake_camera(self):
    self.all_sprites.shake(duration=0.15, intensity=3)
```

**DETAILED WALKTHROUGH:**
- The player doesn't know *how* the camera shakes — it just calls the `shake_camera`
  **callback** it was given. The `CameraGroup` in `level.py` does the actual shaking.
- This is the pattern students should copy to make an NPC react to a dialogue choice:
  pass a small callback (or call a method) when a branch is chosen. Marker
  `@STUDENT-EDIT-Day4-2` in `dialogue_system.py`'s `input()` is the suggested place to
  link a choice to an action.

### Debugging with `print()`
**File**: [dialogue_system.py](../../dialogue_system.py) and [ai_dialogue_manager.py](../../ai_dialogue_manager.py)

The codebase leaves explicit markers for adding debug prints rather than shipping noisy
output:

- `@STUDENT-EDIT-Day4-1` in `start_dialogue()` — add a print to see *which* dialogue
  branch runs (explicit lines vs AI vs fallback):

  ```python
  def start_dialogue(self, character_id, player_context=None, dialogue_lines=None, on_finish=None):
      self.active = True
      self.dialogue_index = 0
      self.on_finish_callback = on_finish
      print(f"[DEBUG] start_dialogue for '{character_id}', "
            f"explicit_lines={dialogue_lines is not None}, context={player_context}")
  ```

- `@STUDENT-EDIT-Week2_Day5-2` in `ai_dialogue_manager.py` — a marked spot to print the
  character, context, and emotion being sent to the AI (used more in Week 2).

**DETAILED WALKTHROUGH:**
- **Reading the console** is the core skill: a print like the one above immediately
  tells you whether your new NPC is using your custom lines or silently falling back.
- Teach students to read tracebacks bottom-up: the last line names the error
  (`KeyError`, `IndexError`, `AttributeError`), and the lines above show the path of
  calls that led there.
- Common errors to demo on purpose: an `IndentationError` (mis-indent a line inside an
  `if`), a `KeyError` (look up a missing dictionary key — then fix it with `.get()`),
  and a `NameError` (typo a variable name).

### Animation State as a Mini State-Machine
**File**: [player.py](../../player.py) — `get_status()` and `animate()`

The player's *status* string (like `"down_idle"` or `"right_axe"`) decides which
animation plays. This is worth showing as "string manipulation driving behavior":

```python
    def get_status(self):
        # If not moving, switch to the idle version of the current direction
        if self.direction.magnitude() == 0:
            self.status = self.status.split("_")[0] + "_idle"

        # If using a tool, switch to the tool version
        if self.timers["tool use"].active:
            self.status = self.status.split("_")[0] + "_" + self.selected_tool
```

**DETAILED WALKTHROUGH:**
- **`self.status.split("_")[0]`** takes the direction part of a status: `"right_axe"` →
  `"right"`. Then we append `"_idle"` or `"_" + tool`.
- `animate()` uses `self.status` to pick the right list of frames from the
  `self.animations` dictionary — connecting today's string work back to Day 2's sprites.

## Key Learning Points
1. **Building lists with loops + conditionals** — text wrapping and paging.
2. **Bounds checks** prevent index/key crashes (`if index < len(...)`, `.get(...)`).
3. **Callbacks tie actions to events** — screen shake on chop; choice → reaction.
4. **Debugging with `print()`** and reading tracebacks.
5. **State machines via strings** — `get_status()` choosing animations.

## Extension Activities
1. **Link a dialogue choice to an action** — at `@STUDENT-EDIT-Day4-2`, call a method
   (e.g. `shake_camera`, or change an NPC sprite) when a branch is selected.
2. **Add a debug print** — at `@STUDENT-EDIT-Day4-1`, print the chosen dialogue branch.
3. **Multi-branch conversation** — extend Day 3's nested-dictionary dialogue to 3+
   branches and confirm each path with your debug print.
4. **Deliberately break it, then fix it** — remove a colon or mis-indent a line, read
   the error message, and repair it. (Builds error-reading confidence.)

## Troubleshooting Tips
- **`IndexError: list index out of range` in `draw`:** you advanced past the last page;
  the `if self.dialogue_index < len(...)` guard is what prevents this — keep it.
- **Debug prints never show:** make sure you're running from a terminal (`python
  main.py`) where you can see stdout, and that the line is actually reached (add it at
  the top of the method).
- **Screen shake does nothing:** confirm the tool is the `axe` and `target_pos` is over
  a tree; `shake_camera` only fires on a successful hit.
- **Wrong animation plays:** print `self.status` inside `animate()` — it must match a
  key in `self.animations`.
