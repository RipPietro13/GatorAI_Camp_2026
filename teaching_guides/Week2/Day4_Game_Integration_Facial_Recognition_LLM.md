# Day 4: Game Integration — Facial Recognition + LLM

## Objective
Combine the emotion detector (computer vision) and the dialogue manager (LLM) so an NPC
responds to the player's real facial expression.

## Core Concepts
- **Connecting two AI systems** through shared data (the `emotions_deque`)
- **Building a context** from game state + detected emotion
- **Passing that context** into the LLM prompt
- **Showing the result** on screen (emotion icons + AI dialogue)

## Hands-On Exercise
- Ensure the camera is on (Day 1) and the API key is set (Day 3).
- Walk up to the **Trader** and press ENTER. The trader's greeting is generated based on
  your detected emotion and your in-game progress.

## Code References

> Snippets are copied from the real project files.

### Step 1: The Detector Shares a `deque` With the Game
**File**: [main.py](../../main.py) — `Game.__init__` and `restart_emotion_detector`

```python
        # Store the last 5 detected emotions in a shared deque
        self.emotions_deque = deque(maxlen=5)
        self.emotion_detector = None  # created later (camera imports are heavy)
```

```python
    def restart_emotion_detector(self):
        from emotion_detector import EmotionDetector
        self.emotion_detector = EmotionDetector(
            self.emotions_deque, show_camera_preview=False
        )
        self.emotion_detector.start()  # launches the background thread
```

**DETAILED WALKTHROUGH:**
- The same `emotions_deque` object is handed to the detector **and** to the level/overlay.
  The detector writes to it; everyone else reads from it. This shared object is the
  bridge between the vision system and the rest of the game.
- The detector is created lazily (when the camera is enabled via Options) because
  importing `torch`/`cv2` is slow — we don't want to pay that at startup.

### Step 2: Passing the `deque` Into the Level and Overlay
**File**: [level.py](../../level.py) — `Level.__init__`

```python
    def __init__(self, emotions_deque):
        self.emotions_deque = emotions_deque          # keep a reference
        ...
        self.overlay = Overlay(self.player, emotions_deque)   # overlay shows the icons
        self.dialogue_system = DialogueSystem()
```

**DETAILED WALKTHROUGH:**
- `Level` receives the deque and forwards it to the `Overlay`, which draws the bunny
  emotion icons in the corner. So the detector's output is visible immediately, even
  before any dialogue happens.

### Step 3: Building Emotion-Aware Context for the Trader
**File**: [level.py](../../level.py) — `toggle_shop()`

```python
    def toggle_shop(self):
        # Most recent emotion (newest is at the end of the deque); default to neutral
        recent_emotions = list(self.emotions_deque) if self.emotions_deque else []
        current_emotion = recent_emotions[-1] if recent_emotions else "neutral"

        # Context from the player's progress (money)
        if self.player.money > 1000:
            situation = "player has lots of money and is doing well farming"
        elif self.player.money < 100:
            situation = "player is just starting out and has limited funds"
        else:
            situation = "player is making steady progress with their farm"

        player_context = {
            "npc_name": "Merchant Pete",
            "npc_role": "friendly trader",
            "situation": situation,
            "emotion": current_emotion,
            "player_money": self.player.money,
        }

        # Start dialogue; open the shop only after the greeting finishes
        self.dialogue_system.start_dialogue(
            "trader", player_context=player_context, on_finish=self.open_trader_menu
        )
```

**DETAILED WALKTHROUGH:**
- **`recent_emotions[-1]`** reads the *newest* emotion (the deque appends to the end).
- The `if/elif/else` turns the player's **money** into a human-readable `situation`
  string — game state becoming AI context.
- Both pieces (emotion + situation) go into the `player_context` dictionary that the
  dialogue system forwards to the LLM. The `on_finish=self.open_trader_menu` callback
  opens the shop *after* the AI greeting finishes (the Day 3 callback pattern).

### Step 4: The Dialogue System Calls the LLM With That Context
**File**: [dialogue_system.py](../../dialogue_system.py) — `start_dialogue()` (AI branch)

```python
        elif self.ai_enabled and self.ai_manager and player_context:
            dialogue_line = self.ai_manager.generate_npc_dialogue(
                character_name=player_context.get("npc_name", "NPC"),
                character_role=player_context.get("npc_role", "character"),
                player_context=player_context.get("situation", "meeting you"),
                emotion=player_context.get("emotion", "neutral"),
            )
            self.current_dialogue = self._wrap_text(dialogue_line, self.text_box_rect.width - 40)
```

**DETAILED WALKTHROUGH:**
- This is the branch from Day 3's `generate_npc_dialogue`. The detected `emotion` flows
  all the way from the camera → deque → `toggle_shop` context → here → the LLM prompt.
- If AI is disabled or unavailable, `start_dialogue` falls through to static
  emotion-aware lines instead — the demo still works.

### Step 5: Showing the Detected Emotion On Screen
**File**: [overlay.py](../../overlay.py) — emotion icons

```python
        # Keys MUST match the model's (mapped) labels and the bunny-*.png filenames
        for emotion in ["happy", "sad", "angry", "surprised", "neutral", "fearful"]:
            icon_path = os.path.join(emotions_path, f"bunny-{emotion}.png")
            if os.path.exists(icon_path):
                self.emotion_icons[emotion] = pygame.transform.scale(
                    pygame.image.load(icon_path).convert_alpha(), (64, 64))
```

```python
        # in display(): show the most recent emotion largest, older ones smaller
        if self.emotions_deque:
            emotions_to_display = list(reversed(self.emotions_deque))
            ...
```

**DETAILED WALKTHROUGH:**
- The overlay reads the **same deque** and draws a bunny face per recent emotion. The
  icon keys, the model's mapped labels (`EMOTION_LABEL_MAP`), and the AI's
  `emotion_guidance` keys must all use the same vocabulary
  (`happy/sad/angry/surprised/neutral/fearful`) — the integration only works if these
  three lists agree.

## The Full Data Flow (the key picture for today)

```
Webcam ─▶ EmotionDetector (thread)
            detect face ─▶ crop ─▶ CNN ─▶ EMOTION_LABEL_MAP
              │
              ▼  appends to
        emotions_deque (shared)
         │                 │
         ▼                 ▼
   Overlay (icons)   level.toggle_shop() builds player_context
                            │
                            ▼
              dialogue_system.start_dialogue(player_context)
                            │
                            ▼
        ai_dialogue_manager.generate_npc_dialogue()  ─▶  LLM (mistral-7b-instruct)
                            │
                            ▼
                  text shown in the dialogue box
```

## Key Learning Points
1. **Shared mutable state** (`emotions_deque`) connects independent systems.
2. **Lazy initialization** keeps startup fast despite heavy AI imports.
3. **Game state → context → prompt** is the heart of context-aware AI.
4. **Callbacks** sequence dialogue then shop.
5. **Vocabulary must be consistent** across detector, overlay, and dialogue.

## Extension Activities
1. **Make a custom NPC emotion-aware** by giving it a `player_context` like the trader.
2. **Use more than the latest emotion** — pass the *most common* of the last 5.
3. **Different NPC personalities** reacting to the same emotion (system-prompt changes).
4. **Add an on-screen label** of the current emotion next to the bunny icon.

## Troubleshooting Tips
- **NPC always acts "neutral":** the deque is empty (camera off / no face) or labels
  don't match — verify `EMOTION_LABEL_MAP` and the overlay keys agree.
- **Icons don't appear:** the emotion name has no matching `bunny-*.png`; check spelling
  (`fearful`, not `fear`).
- **Shop opens before the greeting:** make sure `toggle_shop` passes
  `on_finish=self.open_trader_menu` rather than opening the menu directly.
- **Game stutters with camera + AI:** the API call happens when the shop opens, not
  every frame; if it's still slow, confirm the detector's loop keeps its `time.sleep`.
