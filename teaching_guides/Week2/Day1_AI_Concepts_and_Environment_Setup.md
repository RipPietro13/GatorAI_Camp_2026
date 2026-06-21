# Day 1: AI Concepts and Environment Setup

## Objective
Learn AI fundamentals and prepare the development environment for Week 2.

## Core Concepts
- **What Is AI / ML / DL?** — differentiate Artificial Intelligence, Machine Learning,
  and Deep Learning; real-world examples (image recognition, chatbots).
- **Computer Vision Overview** — face *detection* (where is a face?) vs. expression
  *recognition* (what emotion?). We use **OpenCV** for detection and a small
  **PyTorch** neural network for emotion recognition.
- **Setting Up the AI Environment** — installing `opencv-python`, `torch`,
  `pytorch_lightning`; CPU is fine for this model.
- **Ethics** — privacy and consent when using a webcam and facial data.

> **Important framework note:** this project uses **PyTorch / PyTorch Lightning**, not
> TensorFlow/Keras. The model file is `ai_materials/emotion_model.pth` (a PyTorch
> checkpoint), loaded with `torch.load`. There is no `.h5` / `load_model` here.

## Hands-On Exercise
- Turn the Week-2 installs back **on** in [main.py](../../main.py) (they may have been
  commented out for Week 1):
  ```python
  install("opencv-python")
  install("pytorch_lightning")
  install("openai")
  ```
- Confirm imports work: `python -c "import cv2, torch, pytorch_lightning"`.
- In `settings.json`, set `"enable_camera": true` (and pick the right
  `"camera_index"`). Enable the camera from the in-game **Options** menu.

## Code References

> Snippets are copied from the real project files.

### The Emotion Detector: A Background Thread
**File**: [emotion_detector.py](../../emotion_detector.py)

Unlike a simple polling loop, the real detector runs on its own **thread** so the game
never freezes while reading the camera. It writes results into a shared `deque`:

```python
import cv2
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import pytorch_lightning as pl
import threading, time
import game_settings


class EmotionDetector(threading.Thread):
    """Runs real-time emotion detection in a separate thread."""

    def __init__(self, emotions_deque, show_camera_preview=False):
        super().__init__()
        self.daemon = True            # closes automatically when the game exits
        self._stopper = threading.Event()
        self.emotions_deque = emotions_deque
        self.model = None
        self.emotion_names = []
        self.face_cascade = None
```

**DETAILED WALKTHROUGH:**
1. **`class EmotionDetector(threading.Thread):`** — it *is* a thread. Calling
   `.start()` runs its `run()` method in the background.
2. **`self.daemon = True`** — a daemon thread shuts down when the main program exits, so
   closing the game also stops the camera.
3. **`self._stopper = threading.Event()`** — a clean on/off switch so the game can ask
   the thread to stop.
4. **`self.emotions_deque`** — the shared `deque(maxlen=5)` created in `main.py`. The
   detector *appends* emotions here; the overlay and dialogue system *read* from it.
   This is how two parts of the program safely share data.

### Face Detection with OpenCV (Haar Cascade)
**File**: [emotion_detector.py](../../emotion_detector.py) — `_load_face_detector()`

```python
    def _load_face_detector(self):
        HAAR_CASCADE_FILENAME = "haarcascade_frontalface_default.xml"
        ...
        self.face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_FILENAME)
        if self.face_cascade.empty():
            print("❌ Face detector could not be loaded.")
            return False
        print("✅ Face detector loaded successfully.")
        return True
```

**DETAILED WALKTHROUGH:**
- A **Haar cascade** is a classic, fast face *detector* that ships with OpenCV (the XML
  file is included in the repo). It finds *where* faces are — it does not know emotions.
- Detecting the face first, then cropping just that region for the neural network, is a
  standard computer-vision pipeline: **detect → crop → classify**.

### The AI Dialogue Manager (Preview)
**File**: [ai_dialogue_manager.py](../../ai_dialogue_manager.py)

The other half of Week 2 is the Large Language Model dialogue. It also degrades
gracefully if the library or key is missing:

```python
try:
    import openai
except ImportError:
    print("⚠️ OpenAI library not installed. AI dialogue will use fallback mode.")
    openai = None


class AIDialogueManager:
    def __init__(self, key_file_path: str = "ai_materials/navigator_api_key.json"):
        self.client = None
        self.fallback_mode = True
        if openai is None:
            print("🔄 AI Manager initialized in offline mode (OpenAI not available).")
            return
        # @STUDENT-EDIT-Week2_Day3-1: Add your API key in ai_materials/navigator_api_key.json
        self.credentials = self._load_api_credentials(key_file_path)
        ...
```

**DETAILED WALKTHROUGH:**
- The `try/except ImportError` and the `fallback_mode` flag mean the game *always*
  runs, even with no internet or no API key — it just uses static, emotion-aware lines.
- We'll wire up the actual API on Day 3. Today, just note that emotion detection
  (computer vision) and dialogue generation (NLP) are two separate AI systems we'll
  combine on Day 4.

## Key Learning Points
1. **AI vs ML vs DL** — and where this project's two AI systems fit (CV + NLP).
2. **detect → crop → classify** — the face-to-emotion pipeline.
3. **Threads and shared data** — the detector runs in the background and shares a
   `deque` with the rest of the game.
4. **Graceful degradation** — both AI systems fall back safely when unavailable.
5. **Ethics** — webcam consent and privacy.

## Extension Activities
1. Run a tiny standalone OpenCV face-detection test on a static image.
2. Inspect the model checkpoint: print `torch.load("ai_materials/emotion_model.pth",
   map_location="cpu", weights_only=False).keys()` to see what's stored.
3. Discuss: what could go wrong if an emotion model is trained on a narrow group of
   faces? (bias, fairness)

## Troubleshooting Tips
- **`ModuleNotFoundError: cv2 / torch`:** the Week-2 installs are still commented out in
  `main.py`, or you're on a Python version without wheels (use 3.11/3.12).
- **Camera doesn't open:** check `"enable_camera": true` and the correct
  `"camera_index"` in `settings.json`; a black/empty camera is often a different index.
- **Game feels laggy with the camera on:** the detector throttles to a few predictions
  per second on purpose; make sure you didn't remove the `time.sleep(...)` in its loop.
- **Privacy:** the webcam feed is processed locally and not saved or uploaded — make
  this explicit to students and get consent before turning the camera on.
