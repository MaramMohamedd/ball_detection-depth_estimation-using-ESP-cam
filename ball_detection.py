import cv2
import numpy as np

# ============================================
# CONFIGURATION - CHANGE THESE FOR YOUR BALL
# ============================================

# ESP32-CAM Stream URL
STREAM_URL = "http://192.168.1.16:81/stream"  # <-- CHANGE THIS TO YOUR IP

# HSV color range for ball detection
# Start with RED as an example (common ball color)
# You will need to adjust these values!

# For RED ball (two ranges because red wraps around HSV wheel)
LOWER_RED1 = np.array([0, 100, 100])
UPPER_RED1 = np.array([10, 255, 255])
LOWER_RED2 = np.array([160, 100, 100])
UPPER_RED2 = np.array([179, 255, 255])

# For GREEN ball (uncomment to use green instead)
# LOWER_GREEN = np.array([40, 50, 50])
# UPPER_GREEN = np.array([80, 255, 255])

# For BLUE ball (uncomment to use blue instead)
# LOWER_BLUE = np.array([90, 50, 50])
# UPPER_BLUE = np.array([130, 255, 255])

# Minimum ball size (ignore smaller detections)
MIN_BALL_RADIUS = 10

# ============================================
# MAIN DETECTION LOOP
# ============================================

def detect_ball(frame):
    """Detect a colored ball in the frame and return bounding box and center"""
    
    # Convert frame from BGR (OpenCV default) to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Create mask for the specified color
    # For red (two ranges)
    mask1 = cv2.inRange(hsv, LOWER_RED1, UPPER_RED1)
    mask2 = cv2.inRange(hsv, LOWER_RED2, UPPER_RED2)
    mask = cv2.bitwise_or(mask1, mask2)
    
    # For green/blue single range (uncomment if using green/blue)
    # mask = cv2.inRange(hsv, LOWER_GREEN, UPPER_GREEN)
    # mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)
    
    # Remove noise with morphological operations
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=2)
    
    # Find contours (shapes) in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None, None, None
    
    # Find the largest contour (assumed to be the ball)
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Get enclosing circle
    ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)
    
    # Filter by minimum size
    if radius < MIN_BALL_RADIUS:
        return None, None, None
    
    # Get bounding rectangle
    x, y, w, h = cv2.boundingRect(largest_contour)
    center = (int(x + w/2), int(y + h/2))
    
    return (int(x), int(y), w, h), center, int(radius)


def main():
    print("=" * 50)
    print("ESP32-CAM Ball Detection")
    print("=" * 50)
    print(f"Connecting to: {STREAM_URL}")
    print("Press 'q' to quit")
    print("Press 'h' to see HSV values for calibration")
    print("-" * 50)
    
    # Connect to ESP32-CAM stream
    cap = cv2.VideoCapture(STREAM_URL)
    
    if not cap.isOpened():
        print("ERROR: Could not connect to camera stream!")
        print("Check that:")
        print("  1. Your ESP32-CAM is powered on")
        print("  2. You're on the same Wi-Fi network")
        print(f"  3. The URL is correct: {STREAM_URL}")
        return
    
    print("Connected to camera! Starting detection...")
    
    while True:
        # Read a frame from the stream
        ret, frame = cap.read()
        
        if not ret:
            print("Warning: Failed to grab frame")
            continue
        
        # Detect the ball
        bbox, center, radius = detect_ball(frame)
        
        # Draw results on the frame
        if bbox is not None:
            x, y, w, h = bbox
            
            # Draw bounding box (green rectangle)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw center circle (red)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            
            # Draw circle around ball (green)
            cv2.circle(frame, center, radius, (0, 255, 0), 2)
            
            # Display information
            cv2.putText(frame, f"Ball Detected", (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Size: {w}x{h}px", (x, y + h + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        else:
            cv2.putText(frame, "No Ball Detected", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Show the frame
        cv2.imshow("Ball Detection - ESP32-CAM", frame)
        
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):  # Quit
            print("Exiting...")
            break
        
        elif key == ord('h'):  # Help for HSV calibration
            print("\n--- HSV Calibration Help ---")
            print("To find the right HSV values for your ball:")
            print("1. Place the ball in front of the camera")
            print("2. Run this script and note when it's detected")
            print("3. If not detected, adjust HSV ranges in the code")
            print("\nCommon HSV ranges:")
            print("  RED:   H:0-10 or 160-179, S:100-255, V:100-255")
            print("  GREEN: H:40-80, S:50-255, V:50-255")
            print("  BLUE:  H:90-130, S:50-255, V:50-255")
            print("  YELLOW: H:20-30, S:100-255, V:100-255")
            print("-----------------------------\n")
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()