import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import cv2
import mediapipe as mp
import urllib.request

# Download the required model file if it doesn't exist
MODEL_PATH = 'pose_landmarker_lite.task'
if not os.path.exists(MODEL_PATH):
    url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
    urllib.request.urlretrieve(url, MODEL_PATH)

# Initialize the modern MediaPipe Tasks API
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.IMAGE
)
landmarker = PoseLandmarker.create_from_options(options)

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except (AttributeError, ImportError):
    DEEPFACE_AVAILABLE = False

def analyze_posture_and_emotion(frame):
    # MediaPipe Tasks require a special Image object
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    detection_result = landmarker.detect(mp_image)
    
    posture_status = "Good"
    
    # Posture Calculation using the new data structure
    if detection_result.pose_landmarks:
        # We take the first person detected [0]
        landmarks = detection_result.pose_landmarks[0]
        
        # Index 11 is Left Shoulder, Index 12 is Right Shoulder in the new API
        left_shoulder_y = landmarks[11].y
        right_shoulder_y = landmarks[12].y
        
        if abs(left_shoulder_y - right_shoulder_y) > 0.05:
            posture_status = "Slouching / Unaligned"

    # Emotion Calculation
    emotion = "Neutral"
    if DEEPFACE_AVAILABLE:
        try:
            analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            if isinstance(analysis, list):
                emotion = analysis[0]['dominant_emotion']
            else:
                emotion = analysis['dominant_emotion']
        except Exception:
            pass
    else:
        emotion = "Unavailable"
        
    return posture_status, emotion