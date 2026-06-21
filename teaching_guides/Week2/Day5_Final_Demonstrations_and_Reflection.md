# Day 5: Final Demonstrations and Reflection

## Objective
Complete the AI-enhanced project, present it, and reflect on what was learned.

## Activities
- **Polish & Prepare** — tidy prompts, fallbacks, and expression-to-dialogue behavior
- **Presentation** — demo expression recognition + AI dialogue
- **Discussion** — real-world AI: bias, privacy, scale, ethics
- **Reflection** — one learning, one challenge, one future interest

## Code References

> Snippets are copied from the real project files.

### Final Prompt Polish
**File**: [ai_dialogue_manager.py](../../ai_dialogue_manager.py)

Two marked spots are meant for last-minute tuning before the demo:

```python
# system prompt — sets the NPC's overall behavior
# @STUDENT-EDIT-Week2_Day5-1: Fine-tune prompt engineering constraints before the demo
{"role": "system", "content": "You are a helpful NPC in a farming simulation game. "
                              "Keep responses brief, friendly, and appropriate for all ages."},
```

```python
# @STUDENT-EDIT-Week2_Day5-2: Want to see what gets sent to the AI? Add print() statements
# here to inspect the character, context, and emotion.
```

**DETAILED WALKTHROUGH:**
- `@STUDENT-EDIT-Week2_Day5-1` is the place to lock in the NPC's tone for the audience.
- `@STUDENT-EDIT-Week2_Day5-2` is where students can temporarily add prints to *show the
  audience* the prompt being sent — then remove them for the clean final run.

### Verifying AI Status Before You Present
There is no built-in status dashboard, but you can write a tiny check from the **real**
objects the game exposes. Drop this into a scratch script or the Python REPL:

```python
from collections import deque
from ai_dialogue_manager import AIDialogueManager

ai = AIDialogueManager()
print("AI online?    ", not ai.fallback_mode)   # True if the API key/connection worked
print("Client built? ", ai.client is not None)
```

And to confirm emotion detection end-to-end, run the shipped script:

```bash
python test_emotions.py
```

**DETAILED WALKTHROUGH:**
- **`ai.fallback_mode`** is the real flag that tells you whether live AI is active. If
  it's `True`, you'll be demoing the (still emotion-aware) static fallbacks — good to
  know *before* you're in front of people.
- `test_emotions.py` exercises the deque + dialogue path without the camera, so it's a
  reliable "is my AI text working?" smoke test.

### Presentation Settings
**File**: [settings.json](../../settings.json) and [game_settings.py](../../game_settings.py)

Runtime settings live in `settings.json` (created/managed by `game_settings.py`):

```json
{
  "master_volume": 0.6,
  "music_volume": 0.0,
  "camera_index": 1,
  "enable_camera": true,
  "enable_ai_dialogue": true
}
```

**DETAILED WALKTHROUGH:**
- For a live demo: set **`enable_camera: true`** and the correct **`camera_index`**, and
  **`enable_ai_dialogue: true`**. You can change camera/AI from the in-game **Options**
  menu, which calls `restart_emotion_detector` so the new camera takes effect without a
  restart.
- Have a backup plan: if the webcam misbehaves, set `enable_camera: false` and present
  the emotion-aware **fallback** dialogue, which still demonstrates the design.

### Toggling the Camera Safely In-Game
**File**: [main.py](../../main.py) — `restart_emotion_detector`

```python
    def restart_emotion_detector(self):
        if self.emotion_detector and self.emotion_detector.is_alive():
            self.emotion_detector.stop()
            self.emotion_detector.join(timeout=2.0)  # wait for the old thread to stop
        from emotion_detector import EmotionDetector
        self.emotion_detector = EmotionDetector(self.emotions_deque, show_camera_preview=False)
        self.emotion_detector.start()
```

**DETAILED WALKTHROUGH:**
- This cleanly **stops** the old detector thread before starting a new one — important
  because two threads grabbing the same camera causes errors. It's the right pattern to
  show when discussing how the game manages the webcam during the demo.

## Discussion: Real-World AI Considerations
Use the actual project to anchor the ethics conversation:
- **Bias:** the emotion model has only 6 classes and was trained on a limited dataset.
  Whose expressions might it read poorly? (Connect to Day 2's `emotion_names` and
  accuracy discussion.)
- **Privacy & consent:** the webcam runs locally and nothing is uploaded or saved — but
  students should still ask permission before turning a camera on someone.
- **Confidence & honesty:** the `>= 0.4` threshold and the `"neutral"` default mean the
  game admits when it isn't sure rather than guessing — a small example of responsible
  AI behavior.

## Key Learning Points
1. **Integrating CV + NLP** into one application.
2. **Checking real status** (`fallback_mode`, `test_emotions.py`) before demoing.
3. **Configuring** the camera and AI via `settings.json` / Options.
4. **Managing hardware** (the camera thread) cleanly.
5. **AI ethics** grounded in this project's actual limitations.

## Extension Activities
1. Write a slide that shows the **data-flow diagram** from Day 4 and narrate it.
2. Add a temporary on-screen readout of `ai.fallback_mode` and the latest emotion for
   the demo.
3. Compare live-AI vs. fallback dialogue for the same emotion and discuss the trade-offs.
4. Draft a one-paragraph "responsible use" note for your game's README.

## Troubleshooting Tips (for presentations)
- **Test the full setup beforehand** — camera index, lighting, and `fallback_mode`.
- **Webcam fails on stage:** flip `enable_camera: false` and demo the fallback dialogue.
- **AI seems offline:** check `ai.fallback_mode`; the key file may be missing or the
  endpoint unreachable from the venue's network.
- **Two camera errors / black preview:** the previous detector thread may still be
  running — `restart_emotion_detector` stops it first; don't start two detectors by hand.

## Resources for Continued Learning
- PyTorch tutorials (pytorch.org)
- OpenCV documentation (docs.opencv.org)
- Prompt-engineering and LLM API guides
- AI ethics & fairness reading (e.g. model cards, dataset documentation)
