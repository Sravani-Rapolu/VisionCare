"""
VisionCare Vital Signs Monitoring - Demo Script - DEPRECATED
OCR functionality has been removed from the project.
This file is no longer supported.
"""

# from modules.vital_signs import VitalSignsMonitor, VITAL_SIGNS_NORMAL_RANGES
# from modules.alert import trigger_vital_sign_alert

def demo_normal_vitals():
    """Demo with normal vital signs - DEPRECATED"""
    print("=" * 60)
    print("DEMO 1: Patient with Normal Vital Signs - DEPRECATED")
    print("OCR and Vital Signs functionality has been removed")
    print("=" * 60)
    return
        "diastolic": 80,
        "temperature": 37.0,
        "respiratory_rate": 16
    }
    
    for vital, value in normal_readings.items():
        monitor.add_vital_sign(vital, value)
    
    print("\nVital Signs:")
    for vital, data in monitor.vital_signs.items():
        status = data["status"][0]
        message = data["status"][1]
        print(f"  {vital}: {data['value']} - {message}")
    
    print(f"\nOverall Health Status: {monitor.get_health_status().upper()}")
    print()

def demo_warning_vitals():
    """Demo with warning-level vital signs"""
    print("=" * 60)
    print("DEMO 2: Patient with Warning Vital Signs")
    print("=" * 60)
    
    monitor = VitalSignsMonitor()
    
    warning_readings = {
        "heart_rate": 115,      # High but not critical
        "spo2": 92,             # Low but not critical
        "systolic": 155,        # Elevated
        "diastolic": 85,        # Normal
        "temperature": 38.5,    # Slight fever
        "respiratory_rate": 22  # Elevated
    }
    
    for vital, value in warning_readings.items():
        monitor.add_vital_sign(vital, value)
    
    print("\nVital Signs:")
    for vital, data in monitor.vital_signs.items():
        status = data["status"][0]
        message = data["status"][1]
        print(f"  {vital}: {data['value']} - {message}")
    
    print(f"\nOverall Health Status: {monitor.get_health_status().upper()}")
    print()

def demo_critical_vitals():
    """Demo with critical vital signs"""
    print("=" * 60)
    print("DEMO 3: Patient with CRITICAL Vital Signs")
    print("=" * 60)
    
    monitor = VitalSignsMonitor()
    
    critical_readings = {
        "heart_rate": 145,      # Tachycardia (CRITICAL)
        "spo2": 85,             # Severe hypoxemia (CRITICAL)
        "systolic": 175,        # Hypertensive crisis (CRITICAL)
        "diastolic": 95,        # Elevated
        "temperature": 39.8,    # High fever
        "respiratory_rate": 28  # Tachypnea
    }
    
    for vital, value in critical_readings.items():
        monitor.add_vital_sign(vital, value)
    
    print("\nVital Signs:")
    for vital, data in monitor.vital_signs.items():
        status = data["status"][0]
        message = data["status"][1]
        print(f"  {vital}: {data['value']} - {message}")
    
    print(f"\nOverall Health Status: {monitor.get_health_status().upper()}")
    print("\n⚠️ IMMEDIATE MEDICAL INTERVENTION REQUIRED!")
    print()

def demo_alerts():
    """Demo alert generation system"""
    print("=" * 60)
    print("DEMO 4: Alert Generation System")
    print("=" * 60)
    
    # Example: Detecting critical heart rate
    print("\nTriggering alerts for critical vital sign:")
    trigger_vital_sign_alert(
        vital_name="Heart Rate",
        value=152,
        status="critical",
        normal_range="60-100 bpm"
    )
    
    print("\nTriggering alerts for warning vital sign:")
    trigger_vital_sign_alert(
        vital_name="SpO2",
        value=92,
        status="warning",
        normal_range="95-100%"
    )
    print()

def demo_vital_ranges():
    """Display all normal vital sign ranges"""
    print("=" * 60)
    print("Vital Signs Reference Table")
    print("=" * 60)
    print("\nNormal Ranges:")
    print("-" * 60)
    for vital, range_data in VITAL_SIGNS_NORMAL_RANGES.items():
        unit = range_data["unit"]
        min_val = range_data["min"]
        max_val = range_data["max"]
        print(f"{vital:20s}: {min_val:6.1f} - {max_val:6.1f} {unit}")
    print()

def main():
    """Run all demos"""
    print("\n")
    print("█" * 60)
    print("█  VisionCare - Vital Signs Monitoring System  █")
    print("█" * 60)
    print()
    
    # Run demos
    demo_vital_ranges()
    demo_normal_vitals()
    demo_warning_vitals()
    demo_critical_vitals()
    demo_alerts()
    
    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\nTo integrate real vital sign readings:")
    print("1. Add OCR library: pip install easyocr")
    print("2. Update vital_signs.py extract_numbers_from_region()")
    print("3. Connect to monitor's data source (HDMI, network, API)")
    print()

if __name__ == "__main__":
    main()
