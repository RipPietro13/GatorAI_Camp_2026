# Day 2: Facial Recognition Model Training

## Objective
Understand the machine-learning workflow and how the trained emotion model is used in
the game.

## Core Concepts
- **ML workflow**: data → model → training → evaluation → save → use
- **Convolutional Neural Networks (CNNs)** for image classification
- **Image preprocessing**: grayscale, resize to 48×48, normalize
- **Confidence and thresholds**
- **Saving/loading** a PyTorch model (`.pth`)

> **Framework:** PyTorch + PyTorch Lightning. The saved model is
> `ai_materials/emotion_model.pth`, a checkpoint dictionary (not a Keras `.h5`).

## Hands-On Exercise
Work through the notebooks (Colab or locally):
- [ai_materials/01_full_of_emotion.ipynb](../../ai_materials/01_full_of_emotion.ipynb) —
  builds and **trains** the CNN, evaluates it, even compares against transfer learning,
  and saves `emotion_model.pth`.
- [ai_materials/02_real_time_emotion_detection.ipynb](../../ai_materials/02_real_time_emotion_detection.ipynb) —
  loads the saved model and runs it on webcam frames.

Then look at how the game uses the result in `emotion_detector.py`.

## Code References

> Snippets are copied from the real project files / notebooks.

### The CNN Architecture
**File**: [emotion_detector.py](../../emotion_detector.py) — `class EmotionCNN`
(identical to the one in `01_full_of_emotion.ipynb`)

```python
class EmotionCNN(pl.LightningModule):
    """Compact CNN for emotion recognition (must match the training notebook)."""

    def __init__(self, num_classes=6, learning_rate=0.001):
        super().__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2, 2),
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2, 2),
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128), nn.ReLU(), nn.MaxPool2d(2, 2),
        )
        self.global_avg_pool = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Sequential(
            nn.Dropout(0.5), nn.Linear(128, 128), nn.ReLU(),
            nn.Dropout(0.3), nn.Linear(128, num_classes),
        )
```

**DETAILED WALKTHROUGH:**
- **`nn.Conv2d(1, 32, ...)`** — the first conv layer takes **1** channel (grayscale)
  and produces 32 feature maps. Each conv block is Conv → BatchNorm → ReLU → MaxPool,
  the standard CNN building block.
- The three conv blocks progressively learn richer features (edges → shapes →
  expression-like patterns).
- **`AdaptiveAvgPool2d(1)`** collapses each feature map to a single number, and the
  **`classifier`** (with `Dropout` for regularization) outputs one score per emotion.
- **`num_classes=6`** — the model knows 6 emotions. The exact names are stored *in the
  saved file* (see below).

### Why the Architecture Is Duplicated in the Game
The class must be defined in `emotion_detector.py` so PyTorch can rebuild the model
before loading the saved weights. The comment in the file says exactly this: *"This
class must be defined so we can load the saved model weights."* This is a common
gotcha — point it out so students understand the notebook and the game must agree.

### Loading the Trained Model
**File**: [emotion_detector.py](../../emotion_detector.py) — `_load_model()`

```python
    def _load_model(self):
        # @STUDENT-EDIT-Week2_Day2-1: Change the path to point to your own trained model
        model_path = os.path.join("ai_materials", "emotion_model.pth")
        ...
        checkpoint = torch.load(model_path, map_location=torch.device("cpu"),
                                weights_only=False)
        self.model = EmotionCNN(num_classes=checkpoint["num_classes"])
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()
        self.emotion_names = checkpoint["emotion_names"]
        return True
```

**DETAILED WALKTHROUGH:**
- **`torch.load(...)`** reads the checkpoint *dictionary*. It contains
  `model_state_dict` (the learned weights), `num_classes`, and `emotion_names`.
- **`load_state_dict(...)`** pours the saved weights into a fresh `EmotionCNN`.
- **`self.model.eval()`** switches the model to evaluation mode (turns off Dropout).
- **`self.emotion_names = checkpoint["emotion_names"]`** — the saved label list. For the
  provided model this is `['Angry', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']`.
- Marker `@STUDENT-EDIT-Week2_Day2-1` lets students point this at a model **they**
  trained in the notebook.

### From Camera Frame to Emotion
**File**: [emotion_detector.py](../../emotion_detector.py) — inside `run()`

```python
# detect → crop → preprocess → classify
gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
faces = self.face_cascade.detectMultiScale(gray_frame, 1.1, 5)
...
face_roi = gray_frame[y : y + h, x : x + w]
resized_face = cv2.resize(face_roi, (48, 48))
image_tensor = transform(Image.fromarray(resized_face)).unsqueeze(0)

with torch.no_grad():
    output = self.model(image_tensor)
    # @STUDENT-EDIT-Week2_Day2-2: Adjust the confidence threshold here if needed
    probabilities = torch.nn.functional.softmax(output, dim=1)
    max_prob, pred_idx = torch.max(probabilities, dim=1)

    if max_prob.item() >= 0.4:
        emotion = self.emotion_names[pred_idx.item()]
    else:
        emotion = "neutral"

    # Translate the model's label (e.g. "Fear") to the game's canonical name ("fearful")
    emotion = EMOTION_LABEL_MAP.get(emotion.lower(), emotion.lower())
    self.emotions_deque.append(emotion)
```

**DETAILED WALKTHROUGH:**
1. Convert to grayscale, **detect** faces, **crop** the largest one, **resize** to
   48×48 (the size the model expects), and turn it into a tensor.
2. **`softmax`** turns raw scores into probabilities that sum to 1; **`torch.max`** picks
   the most likely emotion and its confidence.
3. **The threshold** (`>= 0.4`, marker `@STUDENT-EDIT-Week2_Day2-2`): if the model isn't
   confident enough, we report `"neutral"` instead of guessing. This 6-class model
   rarely exceeds 0.5 on natural expressions, which is why the threshold is 0.4 — a great
   discussion of precision vs. recall.
4. **`EMOTION_LABEL_MAP`** translates the model's labels (`Fear`, `Surprise`) into the
   names the rest of the game uses (`fearful`, `surprised`) so the overlay icons and AI
   dialogue match. Keeping these vocabularies in sync is a real engineering lesson.

### The Label Map
**File**: [emotion_detector.py](../../emotion_detector.py) (top of file)

```python
EMOTION_LABEL_MAP = {
    "angry": "angry",
    "fear": "fearful",
    "happy": "happy",
    "neutral": "neutral",
    "sad": "sad",
    "surprise": "surprised",
}
```

If a student trains a model whose `emotion_names` differ, this is where they reconcile
the model's vocabulary with the game's icons (`graphics/emotions/bunny-*.png`) and the
AI guidance keys in `ai_dialogue_manager.py`.

## Key Learning Points
1. **CNNs** classify images via stacked conv blocks.
2. **The model file stores both weights and metadata** (`num_classes`,
   `emotion_names`).
3. **Preprocessing must match training** (grayscale, 48×48, normalized).
4. **Confidence thresholds** trade false positives against missed detections.
5. **Vocabulary consistency** across model, icons, and dialogue matters.

## Extension Activities
1. **Train your own** model in `01_full_of_emotion.ipynb` and point
   `@STUDENT-EDIT-Week2_Day2-1` at it.
2. **Tune the threshold** at `@STUDENT-EDIT-Week2_Day2-2` and observe how often emotions
   register vs. how jittery they are.
3. **Add emotion smoothing**: since the game keeps the last 5 emotions in a `deque`,
   compute the most common of the last few instead of the single latest.
4. **Print confidence** to the console to see how sure the model is per frame.

## Troubleshooting Tips
- **`Model file not found`:** confirm `ai_materials/emotion_model.pth` exists, or update
  the path at `@STUDENT-EDIT-Week2_Day2-1`.
- **Loads but predicts only "neutral":** the threshold may be too high, or the camera is
  dark/no face is detected. Lower the threshold and check lighting.
- **Wrong icon / always neutral in dialogue:** the model's `emotion_names` don't map to
  the game's names — fix `EMOTION_LABEL_MAP`.
- **State-dict load error:** the `EmotionCNN` in `emotion_detector.py` must match the
  one used to train (same layers). Keep them identical.
