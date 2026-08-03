import time
import math
from config.settings import RAPID_MOVEMENT_THRESHOLD, MOTION_COOLDOWN

# Track person positions and last alert times
person_tracking = {}  # {person_id: {"position": (x, y), "last_alert": time}}

def calculate_distance(pos1, pos2):
    """Calculate Euclidean distance between two positions"""
    if pos1 is None or pos2 is None:
        return 0
    x1, y1 = pos1
    x2, y2 = pos2
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

def detect_rapid_movement(box):
    """
    Detects rapid/sudden movements of a person on bed.
    Returns True if person moved more than RAPID_MOVEMENT_THRESHOLD pixels.
    """
    (x, y, w, h) = box
    
    # Center of bounding box
    center = (x + w//2, y + h//2)
    
    # Generate person ID based on current position
    person_id = f"{x}_{y}"
    current_time = time.time()
    
    if person_id not in person_tracking:
        # First detection of this person
        person_tracking[person_id] = {
            "position": center,
            "last_alert": 0
        }
        return False
    
    # Calculate distance moved from last frame
    prev_position = person_tracking[person_id]["position"]
    distance = calculate_distance(prev_position, center)
    
    # Update position
    person_tracking[person_id]["position"] = center
    
    # Check if movement is rapid and cooldown has passed
    last_alert = person_tracking[person_id]["last_alert"]
    
    if distance > RAPID_MOVEMENT_THRESHOLD:
        if current_time - last_alert > MOTION_COOLDOWN:
            person_tracking[person_id]["last_alert"] = current_time
            return True
    
    # Cleanup old entries to avoid memory leaks
    if current_time - last_alert > 30:  # Remove if not tracked for 30 seconds
        del person_tracking[person_id]
    
    return False

def get_movement_info(box):
    """Get detailed movement information"""
    (x, y, w, h) = box
    center = (x + w//2, y + h//2)
    person_id = f"{x}_{y}"
    
    if person_id in person_tracking:
        prev_position = person_tracking[person_id]["position"]
        distance = calculate_distance(prev_position, center)
        return {"distance": distance, "threshold": RAPID_MOVEMENT_THRESHOLD}
    
    return {"distance": 0, "threshold": RAPID_MOVEMENT_THRESHOLD}
