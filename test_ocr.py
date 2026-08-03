"""
Test vital signs OCR detection - DEPRECATED
OCR functionality has been removed from the project.
This file is no longer supported.
"""

import cv2
import numpy as np
from modules.vital_signs import VitalSignsMonitor

def test_vital_signs_detection():
    """Test vital signs detection with a sample monitor image - DEPRECATED"""
    
    print("=" * 60)
    print("Testing Vital Signs OCR Detection - DEPRECATED")
    print("OCR functionality has been removed from the project")
    print("=" * 60)
    return
    
    # Add text that resembles monitor display
    cv2.putText(img, "HR: 78", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(img, "SPO2: 98", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(img, "BP: 120/80", (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(img, "TEMP: 37.0", (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(img, "RR: 16", (20, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    print("\n1. Testing OCR on Sample Image...")
    print("-" * 60)
    
    # Save test image
    cv2.imwrite("test_monitor.png", img)
    print("✓ Created test monitor image")
    
    # Test extraction
    ocr_results = monitor.extract_numbers_from_region(img, (0, 0, 200, 300))
    print(f"\nDetected text: {ocr_results.get('text', [])}")
    print(f"Detected numbers: {ocr_results.get('numbers', [])}")
    print(f"Monitor detected: {ocr_results.get('detected', False)}")
    
    print("\n2. Testing Vital Signs Parsing...")
    print("-" * 60)
    
    # Test parsing
    vital_signs = monitor.parse_vital_signs_from_ocr(ocr_results)
    print(f"Parsed vital signs: {vital_signs}")
    
    print("\n3. Testing Full Detection Pipeline...")
    print("-" * 60)
    
    # Full detection
    detection = monitor.detect_from_monitor_display(img)
    print(f"Monitor detected: {detection.get('detected', False)}")
    print(f"Vital signs found: {detection.get('vital_signs', {})}")
    
    print("\n4. Testing Health Status Classification...")
    print("-" * 60)
    
    # Manually add some vitals for testing
    monitor.add_vital_sign("heart_rate", 78)
    monitor.add_vital_sign("spo2", 98)
    monitor.add_vital_sign("temperature", 37.0)
    
    print(f"Vital signs stored: {list(monitor.vital_signs.keys())}")
    print(f"Health status: {monitor.get_health_status().upper()}")
    
    print("\n5. Vital Signs Status Details...")
    print("-" * 60)
    for vital, data in monitor.vital_signs.items():
        status = data["status"][0]
        message = data["status"][1]
        print(f"  {vital}: {data['value']} - Status: {status} - {message}")
    
    print("\n" + "=" * 60)
    print("✓ Vital Signs Detection Test Complete!")
    print("=" * 60)
    print(f"\n✓ EasyOCR is working correctly")
    print(f"✓ The system will detect vital signs from ICU monitor displays")
    print(f"\nTo use in production:")
    print(f"  - Point camera at ICU monitor")
    print(f"  - Monitor must show: HR, SPO2, BP, TEMP, RR")
    print(f"  - System will automatically extract and classify")
    print()

if __name__ == "__main__":
    test_vital_signs_detection()
