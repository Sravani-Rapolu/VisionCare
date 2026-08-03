import cv2
import mediapipe as mp
from ultralytics import YOLO
from modules.fall_detection import detect_fall
from modules.bed_motion_detection import detect_rapid_movement

# Load YOLO model
model = YOLO("yolov8n.pt")  # nano model (fast)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils


def classify_posture(landmarks):
    # Get key body landmarks
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]

    # Calculate average positions
    shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
    hip_y = (left_hip.y + right_hip.y) / 2
    knee_y = (left_knee.y + right_knee.y) / 2
    ankle_y = (left_ankle.y + right_ankle.y) / 2
    
    # Calculate vertical distances
    shoulder_to_hip = hip_y - shoulder_y  # Positive when hip is below shoulder
    hip_to_knee = knee_y - hip_y          # Positive when knee is below hip
    knee_to_ankle = ankle_y - knee_y      # Positive when ankle is below knee

    # Lying: shoulders and hips at similar height
    if abs(shoulder_y - hip_y) < 0.1:
        return "Lying"
    
    # Sitting: hip to knee distance is small (knees bent, close to hips)
    # AND shoulder_to_hip is moderate
    elif hip_to_knee < 0.15 and shoulder_to_hip > 0.05:
        return "Sitting"
    
    # Standing: clear separation between hip and knee, and knee and ankle
    elif hip_to_knee > 0.15 and knee_to_ankle > 0.1:
        return "Standing"
    
    else:
        return "Standing"  # Default to standing


def detect_multiple_postures(frame, return_stats=False):
    results = model(frame)
    stats = {"falls": 0, "rapid_movements": 0, "health_status": "normal", 
             "postures": {"Standing": 0, "Sitting": 0, "Lying": 0}}

    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])

            # class 0 = person in COCO dataset
            if cls == 0:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Convert to (x, y, w, h) format for fall detection
                w = x2 - x1
                h = y2 - y1
                fall_box = (x1, y1, w, h)
                
                # Check for fall
                is_fall = detect_fall(fall_box)
                if is_fall:
                    stats["falls"] += 1
                
                # Check for rapid movement on bed
                is_rapid_motion = detect_rapid_movement(fall_box)
                if is_rapid_motion:
                    stats["rapid_movements"] += 1

                person_crop = frame[y1:y2, x1:x2]

                rgb = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
                pose_result = pose.process(rgb)

                posture = "Unknown"
                color = (0, 255, 0)  # Green by default
                status_text = posture

                if pose_result.pose_landmarks:
                    posture = classify_posture(pose_result.pose_landmarks.landmark)
                    stats["postures"][posture] = stats["postures"].get(posture, 0) + 1

                    mp_drawing.draw_landmarks(
                        person_crop,
                        pose_result.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS
                    )

                # Put crop back into frame
                frame[y1:y2, x1:x2] = person_crop

                # Change color based on alerts
                if is_fall:
                    color = (0, 0, 255)  # Red for fall
                    status_text = "🚨 FALL!"
                elif is_rapid_motion:
                    color = (0, 165, 255)  # Orange for rapid movement
                    status_text = "⚠️ RAPID MOVE"
                else:
                    status_text = posture

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, status_text, (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
    # Draw health status on frame
    health_color = (0, 255, 0)
    cv2.putText(frame, f"Monitoring: {stats['rapid_movements']} movements, {stats['falls']} falls", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, health_color, 2)

    if return_stats:
        return frame, stats
    return frame
