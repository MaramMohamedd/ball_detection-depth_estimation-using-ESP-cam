import cv2
import numpy as np
import time

# ESP32-CAM Stream URL - CHANGE THIS TO YOUR IP
STREAM_URL = "http://192.168.1.16:81/stream"  # <-- PUT YOUR IP HERE

# HSV color range for ball detection (RED example)
LOWER_RED1 = np.array([0, 100, 100])
UPPER_RED1 = np.array([10, 255, 255])
LOWER_RED2 = np.array([160, 100, 100])
UPPER_RED2 = np.array([179, 255, 255])

MIN_BALL_RADIUS = 10

def detect_ball(frame):
    """Detect a colored ball in the frame"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Red mask (two ranges)
    mask1 = cv2.inRange(hsv, LOWER_RED1, UPPER_RED1)
    mask2 = cv2.inRange(hsv, LOWER_RED2, UPPER_RED2)
    mask = cv2.bitwise_or(mask1, mask2)
    
    # Remove noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None, None, None
    
    largest_contour = max(contours, key=cv2.contourArea)
    ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)
    
    if radius < MIN_BALL_RADIUS:
        return None, None, None
    
    x, y, w, h = cv2.boundingRect(largest_contour)
    center = (int(x + w/2), int(y + h/2))
    
    return (int(x), int(y), w, h), center, int(radius)


def main():
    print("=" * 50)
    print("ESP32-CAM Ball Detection (Optimized)")
    print("=" * 50)
    print(f"Connecting to: {STREAM_URL}")
    print("Press 'q' to quit")
    print("-" * 50)
    
    # Connect to ESP32-CAM stream
    cap = cv2.VideoCapture(STREAM_URL)
    
    if not cap.isOpened():
        print("ERROR: Could not connect to camera stream!")
        return
    
    print("Connected! Starting detection...")
    
    # CRITICAL: Set buffer size to 1 (no buffering)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        # Read a frame
        ret, frame = cap.read()
        
        if not ret:
            print("Warning: Failed to grab frame")
            time.sleep(0.1)
            continue
        
        # OPTIONAL: Skip frames for better performance
        # Process only every 2nd or 3rd frame
        frame_count += 1
        if frame_count % 2 != 0:  # Process every 2nd frame
            continue
        
        # Detect the ball
        bbox, center, radius = detect_ball(frame)
        
        # Draw results
        if bbox is not None:
            x, y, w, h = bbox
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            cv2.circle(frame, center, radius, (0, 255, 0), 2)
            cv2.putText(frame, "Ball Detected", (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No Ball Detected", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Show FPS for debugging
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Show the frame
        cv2.imshow("Ball Detection - ESP32-CAM", frame)
        
        # Handle quit - use waitKey with small delay
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()