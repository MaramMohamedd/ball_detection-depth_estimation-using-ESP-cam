import cv2
import numpy as np

# ============================================
# CONFIGURATION - CHANGE THESE!
# ============================================
STREAM_URL = "http://192.168.1.16:81/stream"  # Your ESP32-CAM IP
REAL_BALL_DIAMETER_CM = 7.0  # <-- YOUR BALL'S ACTUAL DIAMETER in cm (meadured manually using ruler and found it is = 7cm)
KNOWN_DISTANCE_CM = 20.0     # <-- Place ball exactly 30cm from camera

# Your HSV values for indigo blue ball
LOWER_BLUE = np.array([88, 60, 40])
UPPER_BLUE = np.array([108, 255, 255])

MIN_BALL_RADIUS = 10

# ============================================
# CALIBRATION SCRIPT
# ============================================

def detect_ball_pixel_width(frame):
    """Returns the pixel width of detected ball, or None if not found"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)
    
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=2)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    
    # Filter by minimum size
    if w < MIN_BALL_RADIUS * 2:
        return None
    
    return w  # Return pixel width

def calibrate_focal_length():
    print("=" * 50)
    print("FOCAL LENGTH CALIBRATION")
    print("=" * 50)
    print(f"Ball diameter: {REAL_BALL_DIAMETER_CM} cm")
    print(f"Place ball exactly {KNOWN_DISTANCE_CM} cm from camera")
    print("Press SPACE to capture and calculate focal length")
    print("Press 'q' to quit")
    print("-" * 50)
    
    cap = cv2.VideoCapture(STREAM_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if not cap.isOpened():
        print("ERROR: Cannot connect to camera!")
        return None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Detect ball and get pixel width
        pixel_width = detect_ball_pixel_width(frame)
        
        # Draw status
        if pixel_width:
            cv2.putText(frame, f"Ball detected! Width: {pixel_width} px", (10, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Press SPACE to calibrate", (10, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        else:
            cv2.putText(frame, "No ball detected - adjust position", (10, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        cv2.putText(frame, f"Known distance: {KNOWN_DISTANCE_CM} cm", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow("Calibration - Place ball at known distance", frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        
        elif key == ord(' ') and pixel_width:
            # Calculate focal length
            # Formula: f = (pixel_diameter × distance) / real_diameter
            focal_length = (pixel_width * KNOWN_DISTANCE_CM) / REAL_BALL_DIAMETER_CM
            
            print("\n" + "=" * 50)
            print("✅ CALIBRATION COMPLETE!")
            print(f"   Real ball diameter: {REAL_BALL_DIAMETER_CM} cm")
            print(f"   Known distance: {KNOWN_DISTANCE_CM} cm")
            print(f"   Pixel width: {pixel_width} px")
            print(f"   Calculated focal length: {focal_length:.2f} pixels")
            print("=" * 50)
            print("\nAdd this to your main script:")
            print(f"FOCAL_LENGTH = {focal_length:.2f}")
            print("=" * 50)
            
            cap.release()
            cv2.destroyAllWindows()
            return focal_length
    
    cap.release()
    cv2.destroyAllWindows()
    return None

if __name__ == "__main__":
    focal = calibrate_focal_length()
    if focal:
        print(f"\n✅ Save this value: FOCAL_LENGTH = {focal:.2f}")
