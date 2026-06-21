import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image
import pytorch_lightning as pl
import os
import requests
import threading
import time
import game_settings


# Maps the labels the trained model outputs to the canonical names used by the
# rest of the game (the bunny-*.png icons in overlay.py and the emotion guidance
# in ai_dialogue_manager.py). The model emits e.g. "Fear"/"Surprise", but the
# game uses "fearful"/"surprised", so we translate here. Comparison is done in
# lowercase, so only the spelling differences need entries.
EMOTION_LABEL_MAP = {
    "angry": "angry",
    "fear": "fearful",
    "happy": "happy",
    "neutral": "neutral",
    "sad": "sad",
    "surprise": "surprised",
}


# =============================================================================
# DEFINE THE CNN MODEL ARCHITECTURE
# =============================================================================
# This class must be defined so we can load the saved model weights.
class EmotionCNN(pl.LightningModule):
    """Compact CNN for emotion recognition (must match the training notebook)."""

    def __init__(self, num_classes=6, learning_rate=0.001):
        """Define the three conv blocks and the classifier head."""
        super().__init__()
        self.save_hyperparameters()
        self.learning_rate = learning_rate
        self.num_classes = num_classes
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        self.global_avg_pool = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        """Run an image batch through the network and return per-emotion scores."""
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.global_avg_pool(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x


class EmotionDetector(threading.Thread):
    """
    Runs real-time emotion detection in a separate thread to avoid blocking the game loop.
    """

    def __init__(self, emotions_deque, show_camera_preview=False):
        """Set up the detector thread; results are appended to the shared `emotions_deque`."""
        super().__init__()
        self.daemon = True  # Thread will close when the main program exits
        self._stopper = threading.Event()
        self.emotions_deque = emotions_deque
        self.show_camera_preview = show_camera_preview
        self.model = None
        self.emotion_names = []
        self.face_cascade = None

    def stop(self):
        """Signal the detection loop to exit."""
        self._stopper.set()

    def _load_model(self):
        """Loads the trained emotion recognition model."""
        # @STUDENT-EDIT-Week2_Day2-1: Change the path to point to your captured image folder or model if you trained your own
        model_path = os.path.join("ai_materials", "emotion_model.pth")
        if not os.path.exists(model_path):
            print(f"❌ Error: Model file not found at {model_path}")
            return False

        try:
            checkpoint = torch.load(
                model_path, map_location=torch.device("cpu"), weights_only=False
            )
            self.model = EmotionCNN(num_classes=checkpoint["num_classes"])
            self.model.load_state_dict(checkpoint["model_state_dict"])
            self.model.eval()
            self.emotion_names = checkpoint["emotion_names"]
            print(f"✅ Emotion model loaded successfully.")
            return True
        except Exception as e:
            print(f"❌ Error loading emotion model: {e}")
            return False

    def _load_face_detector(self):
        """Loads the Haar Cascade face detector from OpenCV."""
        HAAR_CASCADE_FILENAME = "haarcascade_frontalface_default.xml"
        if not os.path.exists(HAAR_CASCADE_FILENAME):
            print(f"📥 Downloading face detector: {HAAR_CASCADE_FILENAME}...")
            url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
            response = requests.get(url)
            if response.status_code == 200:
                with open(HAAR_CASCADE_FILENAME, "wb") as f:
                    f.write(response.content)
                print("✅ Download complete.")
            else:
                print(
                    f"❌ Failed to download face detector. Status code: {response.status_code}"
                )
                return False

        self.face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_FILENAME)
        if self.face_cascade.empty():
            print("❌ Face detector could not be loaded.")
            return False

        print(f"✅ Face detector loaded successfully.")
        return True

    def run(self):
        """The main loop for the emotion detection thread."""
        if not self._load_model() or not self._load_face_detector():
            print("⚠️ Emotion detection thread stopping due to loading errors.")
            return

        # Try multiple camera initialization methods for Windows compatibility
        cap = None
        selected_camera_index = game_settings.get_camera_index()
        camera_backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, 0]  # Windows-specific backends

        print(
            f"🎥 Using camera index: {selected_camera_index} ({game_settings.get_camera_name(selected_camera_index)})"
        )

        for backend in camera_backends:
            try:
                if backend == 0:
                    cap = cv2.VideoCapture(selected_camera_index)
                    print("🔍 Trying default camera backend...")
                else:
                    cap = cv2.VideoCapture(selected_camera_index, backend)
                    backend_name = (
                        "DirectShow" if backend == cv2.CAP_DSHOW else "Media Foundation"
                    )
                    print(f"🔍 Trying {backend_name} backend...")

                if cap.isOpened():
                    # Test if camera actually works by reading a frame
                    ret, test_frame = cap.read()
                    if ret and test_frame is not None:
                        print(
                            f"✅ Camera {selected_camera_index} initialized successfully!"
                        )
                        # Set camera properties for better performance
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        cap.set(cv2.CAP_PROP_FPS, 30)
                        break
                    else:
                        cap.release()
                        cap = None
                else:
                    if cap:
                        cap.release()
                    cap = None
            except Exception as e:
                print(f"⚠️ Camera backend failed: {e}")
                if cap:
                    cap.release()
                cap = None

        if cap is None or not cap.isOpened():
            print("❌ Error: Could not open webcam with any available backend.")
            print("💡 Troubleshooting tips:")
            print("   - Make sure no other applications are using the camera")
            print("   - Check Windows privacy settings for camera access")
            print("   - Try running as administrator if needed")
            return

        transform = transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize(mean=[0.5], std=[0.5])]
        )

        print("🚀 Starting emotion detection thread...")
        frame_count = 0
        last_emotion_time = time.time()

        try:
            while not self._stopper.is_set():
                ret, frame = cap.read()
                if not ret:
                    print("⚠️ Failed to read frame from camera")
                    time.sleep(0.1)
                    continue

                frame_count += 1
                current_time = time.time()

                # Keep camera active by continuously reading frames
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray_frame, 1.1, 5)

                # Process emotion detection every 0.5 seconds (not every frame)
                if current_time - last_emotion_time >= 0.5:
                    if len(faces) > 0:
                        # For simplicity, we only process the largest face found
                        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                        x, y, w, h = faces[0]

                        face_roi = gray_frame[y : y + h, x : x + w]

                        if face_roi.size > 0:
                            resized_face = cv2.resize(face_roi, (48, 48))
                            image = Image.fromarray(resized_face)
                            image_tensor = transform(image).unsqueeze(0)

                            with torch.no_grad():
                                output = self.model(image_tensor)
                                # @STUDENT-EDIT-Week2_Day2-2: Adjust the confidence threshold for emotion detection here if needed (e.g. 0.5)
                                # This 6-class model rarely exceeds 0.5 confidence
                                # for natural expressions, so a lower threshold
                                # (0.4) lets real emotions register instead of
                                # always falling back to "neutral".
                                probabilities = torch.nn.functional.softmax(output, dim=1)
                                max_prob, pred_idx = torch.max(probabilities, dim=1)

                                if max_prob.item() >= 0.4:
                                    emotion = self.emotion_names[pred_idx.item()]
                                else:
                                    emotion = "neutral"

                                # Translate the model's label (e.g. "Fear") to the
                                # canonical name the overlay icons and AI dialogue
                                # manager expect (e.g. "fearful").
                                emotion = EMOTION_LABEL_MAP.get(
                                    emotion.lower(), emotion.lower()
                                )
                                self.emotions_deque.append(emotion)

                    last_emotion_time = current_time

                # Optional: Show camera preview for debugging
                if self.show_camera_preview:
                    # Draw rectangles around detected faces
                    for x, y, w, h in faces:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                    cv2.imshow("Camera Preview - Press Q to close", frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        self.show_camera_preview = False
                        cv2.destroyAllWindows()

                # Keep a steady frame rate - this is crucial for keeping camera active
                time.sleep(0.033)  # ~30 FPS

        except Exception as e:
            print(f"❌ Error in emotion detection loop: {e}")
        finally:
            if cap:
                cap.release()
            if self.show_camera_preview:
                cv2.destroyAllWindows()
            print("✅ Emotion detection thread stopped.")
