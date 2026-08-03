CAMERA_SOURCE = 0  # 0 for webcam or IP camera URL
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

FALL_THRESHOLD_RATIO = 0.6   # Width/Height ratio to detect fall (lowered from 0.75 for better detection)
ALERT_COOLDOWN = 5            # Seconds between alerts

# Rapid Movement Detection
RAPID_MOVEMENT_THRESHOLD = 100  # Pixels - distance moved to trigger alert
MOTION_COOLDOWN = 3             # Seconds between motion alerts for same person
