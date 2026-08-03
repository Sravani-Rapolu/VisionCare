from datetime import datetime
from modules.database import log_event

def trigger_alert(alert_type, message):
    """
    Trigger different types of alerts based on patient conditions.
    
    alert_type options:
    - 'fall': Patient fall detected
    - 'vital_critical': Critical vital sign (heart rate, SpO2, BP, temp)
    - 'vital_warning': Warning-level vital sign
    - 'rapid_motion': Rapid bed movements
    - 'general': General alert
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    alert_symbols = {
        'fall': '🚨',
        'vital_critical': '🚨',
        'vital_warning': '⚠️',
        'rapid_motion': '⚠️',
        'general': '⚪'
    }
    
    symbol = alert_symbols.get(alert_type, '❓')
    
    alert_msg = f"{symbol} [{timestamp}] {alert_type.upper()}: {message}"
    print(alert_msg)
    
    # Log to database
    log_event(alert_msg)
    
    return alert_msg

def trigger_vital_sign_alert(vital_name, value, status, normal_range):
    """
    Trigger alert for abnormal vital signs.
    """
    if status == "critical":
        msg = f"CRITICAL: {vital_name} = {value} (Normal: {normal_range})"
        trigger_alert('vital_critical', msg)
    elif status == "warning":
        msg = f"WARNING: {vital_name} = {value} (Normal: {normal_range})"
        trigger_alert('vital_warning', msg)

def trigger_fall_alert(details=""):
    """Trigger fall detection alert"""
    msg = f"Fall detected {details}"
    trigger_alert('fall', msg)

def trigger_motion_alert(details=""):
    """Trigger rapid motion alert"""
    msg = f"Rapid bed movement detected {details}"
    trigger_alert('rapid_motion', msg)
