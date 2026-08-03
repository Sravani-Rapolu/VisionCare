import time
from config.settings import FALL_THRESHOLD_RATIO, ALERT_COOLDOWN

# Track last alert time for each person (by bounding box ID)
person_alerts = {}

def detect_fall(box):
    """
    Detects if a person has fallen based on bounding box aspect ratio.
    
    A fall is detected when width/height ratio > FALL_THRESHOLD_RATIO
    (person becomes wider and shorter when lying down)
    """
    (x, y, w, h) = box
    
    # Avoid division by zero
    if h == 0:
        return False
    
    ratio = w / float(h)
    
    # Generate a unique ID for this person based on position
    person_id = f"{x}_{y}"
    current_time = time.time()
    
    # Check if this person's bounding box matches the fall pattern
    if ratio > FALL_THRESHOLD_RATIO:
        # Check cooldown for this specific person
        last_alert = person_alerts.get(person_id, 0)
        if current_time - last_alert > ALERT_COOLDOWN:
            person_alerts[person_id] = current_time
            return True
    else:
        # Reset cooldown when person is no longer in fall position
        if person_id in person_alerts:
            person_alerts[person_id] = 0
    
    return False
