# VisionCare - Vital Signs Monitoring System

## Overview
This system provides comprehensive patient monitoring combining:
- **Body posture detection** (Standing/Sitting/Lying)
- **Fall detection** (when patient collapses)
- **Rapid movement detection** (sudden bed movements indicating distress)
- **Vital signs monitoring** (from ICU monitor display)

---

## Vital Signs Integration

### Supported Vital Signs
The system monitors the following vital signs from ICU monitors:

| Vital Sign | Normal Range | Warning Range | Critical |
|-----------|-------------|---------------|----------|
| **Heart Rate** | 60-100 bpm | 50-120 bpm | <50 or >120 |
| **SpO2 (O2 Sat)** | 95-100% | 90-100% | <90% |
| **Systolic BP** | 90-140 mmHg | 80-160 mmHg | <80 or >160 |
| **Diastolic BP** | 60-90 mmHg | 50-110 mmHg | <50 or >110 |
| **Temperature** | 36.5-37.5°C | 35.5-39.0°C | <35.5 or >39.0°C |
| **Respiratory Rate** | 12-20 breaths/min | 10-30 breaths/min | <10 or >30 |

### How Vital Signs Detection Works

1. **Monitor Recognition**
   - System detects ICU monitor in camera frame (top-right corner by default)
   - Uses image enhancement (CLAHE) to improve readability
   - Blue box drawn around detected monitor

2. **Data Extraction**
   - Currently supports manual vital sign input
   - Ready for OCR integration (Tesseract/EasyOCR)
   - Can read digital displays showing vital signs

3. **Status Classification**
   - **Normal (Green ✓)**: Within normal range
   - **Warning (Orange ⚠️)**: Within warning range
   - **Critical (Red 🚨)**: Outside safe ranges - requires intervention

### Integration with Detection Pipeline

The vital signs module integrates with the posture detection system:

```python
# In detect_multiple_postures()
vital_monitor.detect_from_monitor_display(frame)
health_status = vital_monitor.get_health_status()
```

### Current Status Display

On live monitoring and processed videos:
- **Live Feed**: Shows "Health: NORMAL/WARNING/CRITICAL" overlay
- **Results Page**: Vital signs summary table
- **Dashboard**: Event log shows all vital sign alerts

---

## Alert System

### Alert Types

#### 1. **Fall Alerts** (🚨 CRITICAL)
- Triggered when width/height ratio > 0.6
- Red bounding box with "FALL!" label
- Logged with timestamp

#### 2. **Rapid Movement Alerts** (⚠️ WARNING)
- Triggered when movement > 100 pixels per frame
- Orange bounding box with "RAPID MOVE" label
- Indicates patient distress or seizure-like activity

#### 3. **Vital Sign Alerts** (🚨 CRITICAL / ⚠️ WARNING)
- **Critical**: Heart rate outside safe range, SpO2 <90%, etc.
- **Warning**: Values approaching dangerous levels
- Can trigger automated notifications

---

## System Architecture

### Key Modules

**vital_signs.py**
- `VitalSignsMonitor` class for monitoring
- Normal/warning/critical range definitions
- Alert generation system

**alert.py**
- Enhanced alert system with categorization
- Logging to database
- Support for multiple alert types

**multi_person_posture.py**
- Integrates fall, motion, and vital sign detection
- Color-coded visual feedback
- Statistics collection for analysis

---

## How to Use

### 1. **Live Monitoring**
```
http://localhost:5000/live
```
- See real-time video feed
- Posture detection with color indicators
- Health status overlay
- Vital signs panel (if monitor in view)

### 2. **Video Upload**
```
http://localhost:5000/upload
```
- Upload patient monitoring video
- System analyzes for:
  - Falls
  - Rapid movements
  - Posture changes
  - Vital sign anomalies

### 3. **Results/Analysis**
- Falls counted: 🚨
- Rapid movements: ⚠️
- Frame analysis: ✓
- Vital signs summary table

### 4. **Event Dashboard**
```
http://localhost:5000
```
- Complete event log with timestamps
- Searchable alerts
- Critical events highlighted

---

## Configuration

**config/settings.py:**
```python
FALL_THRESHOLD_RATIO = 0.6          # Person becomes wider when falling
ALERT_COOLDOWN = 5                  # Seconds between fall alerts
RAPID_MOVEMENT_THRESHOLD = 100      # Pixels moved to trigger alert
MOTION_COOLDOWN = 3                 # Seconds between motion alerts
```

---

## Future Enhancements

### 1. **OCR Integration**
```python
# Add to vital_signs.py
import pytesseract  # or EasyOCR
vital_values = pytesseract.image_to_string(monitor_roi)
```

### 2. **Remote Alerts**
- SMS/Push notifications for critical events
- Email reports to medical staff
- Integration with hospital alert systems

### 3. **Data Analysis**
- 24-hour vital sign trends
- Pattern recognition for decline detection
- Machine learning for anomaly detection

### 4. **Multi-Patient Monitoring**
- Track multiple patients in ICU
- Comparative analysis
- Resource allocation optimization

---

## Testing

### Test Fall Detection
```bash
# Upload video of person falling
# Expected: Falls detected: 1
```

### Test Rapid Movement
```bash
# Upload video with sudden bed movements
# Expected: Rapid bed movements detected
```

### Test Vital Signs
```python
# In Python shell
from modules.vital_signs import VitalSignsMonitor
monitor = VitalSignsMonitor()
monitor.add_vital_sign("heart_rate", 75)
print(monitor.get_health_status())  # "normal"
```

---

## Notes

- Monitor position defaults to top-right (640x480 frame)
- Can be adjusted in `multi_person_posture.py`
- System runs on CPU with YOLOv8-Nano for speed
- Requires: OpenCV, MediaPipe, YOLO

---

## Support

For issues or enhancements:
- Check config/settings.py for threshold adjustments
- Review modules/vital_signs.py for vital sign definitions
- Enable debug mode in Flask: `debug=True`
