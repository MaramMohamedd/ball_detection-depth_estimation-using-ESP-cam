import cv2
import numpy as np
import time

# ============================================
# YOUR ESP32-CAM STREAM URL
# ============================================
STREAM_URL = "http://192.168.1.16:81/stream"  

# ============================================
# YOUR INDiGO BLUE BALL HSV VALUES
# ============================================
LOWER_BLUE = np.array([88, 60, 40])    # From your calibration
UPPER_BLUE = np.array([108, 255, 255]) # From your calibration

# Minimum ball size (ignore smaller detections)
MIN_BALL_RADIUS = 10

# ============================================
# BALL DETECTION FUNCTION
# ============================================

def detect_ball(frame):
    """Detect the indigo blue ball in the frame"""
    
    # Convert frame from BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Create mask for your blue ball
    mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)
    
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


# ============================================
# MAIN LOOP
# ============================================

def main():
    print("=" * 50)
    print("Indigo Blue Ball Detection - ESP32-CAM")
    print("=" * 50)
    print(f"HSV Range: H:88-108, S:60-255, V:40-255")
    print(f"Stream URL: {STREAM_URL}")
    print("Press 'q' to quit")
    print("-" * 50)
    
    # Connect to ESP32-CAM stream
    cap = cv2.VideoCapture(STREAM_URL)
    
    if not cap.isOpened():
        print("ERROR: Could not connect to camera stream!")
        print("Check your IP address and that ESP32-CAM is powered on")
        return
    
    # Reduce buffer to prevent lag
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    print("Connected! Starting detection...")
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        # Read a frame
        ret, frame = cap.read()
        
        if not ret:
            print("Warning: Failed to grab frame")
            continue
        
        # Skip every other frame for better performance
        frame_count += 1
        if frame_count % 2 != 0:
            continue
        
        # Detect the ball
        bbox, center, radius = detect_ball(frame)
        
        # Draw results on the frame
        if bbox is not None:
            x, y, w, h = bbox
            
            # Draw bounding box (green)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw center dot (red)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            
            # Draw circle around ball (green)
            cv2.circle(frame, center, radius, (0, 255, 0), 2)
            
            # Display ball info
            cv2.putText(frame, "Ball Detected!", (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Size: {w}x{h}px", (x, y + h + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        else:
            cv2.putText(frame, "No Ball Detected", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Calculate and show FPS
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Show the frame
        cv2.imshow("Indigo Blue Ball Detection", frame)
        
        # Quit on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("Done!")


if __name__ == "__main__":
    main()