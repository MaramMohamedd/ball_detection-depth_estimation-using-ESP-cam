import cv2
import numpy as np
import time

# ============================================
# CONFIGURATION - CHANGE THESE
# ============================================
STREAM_URL = "http://10.65.189.32:81/stream"  # Your ESP32-CAM IP

# Your ball's real diameter (MEASURE THIS!)
REAL_BALL_DIAMETER_CM = 7.0  # <-- CHANGE to your ball's actual size

# calibrated focal length (FROM STEP 2) after setting the object 20 cm away from camera 
FOCAL_LENGTH = 91.43  

#HSV values for my blue ball (got through calibration also)
LOWER_BLUE = np.array([88, 60, 40])
UPPER_BLUE = np.array([108, 255, 255])

MIN_BALL_RADIUS = 10

# ============================================
# DEPTH ESTIMATION FUNCTION
# ============================================

def estimate_distance(pixel_width):
    """
    Estimate distance using known-size formula:
    Distance = (Real Diameter × Focal Length) / Pixel Diameter
    """
    if pixel_width <= 0:
        return None
    
    distance = (REAL_BALL_DIAMETER_CM * FOCAL_LENGTH) / pixel_width
    return distance


def detect_ball_with_depth(frame):
    """Detect ball and return bounding box, center, pixel width, and distance"""
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)
    
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=2)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None, None, None, None
    
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Filter by minimum size
    if w < MIN_BALL_RADIUS * 2:
        return None, None, None, None
    
    center = (int(x + w/2), int(y + h/2))
    pixel_width = w
    
    # Estimate distance
    distance_cm = estimate_distance(pixel_width)
    
    return (int(x), int(y), w, h), center, pixel_width, distance_cm


# ============================================
# MAIN LOOP WITH DEPTH DISPLAY
# ============================================

def main():
    print("=" * 50)
    print("BALL DETECTION + DEPTH ESTIMATION")
    print("=" * 50)
    print(f"Ball diameter: {REAL_BALL_DIAMETER_CM} cm")
    print(f"Focal length: {FOCAL_LENGTH:.2f} pixels")
    print(f"HSV Range: H:88-108, S:60-255, V:40-255")
    print("Press 'q' to quit")
    print("-" * 50)
    
    cap = cv2.VideoCapture(STREAM_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if not cap.isOpened():
        print("ERROR: Cannot connect to camera!")
        return
    
    print("Connected! Detecting ball and estimating distance...")
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        frame_count += 1
        if frame_count % 2 != 0:
            continue
        
        # Detect ball and get depth
        bbox, center, pixel_width, distance_cm = detect_ball_with_depth(frame)
        
        # Draw results
        if bbox is not None:
            x, y, w, h = bbox
            
            # Draw bounding box (green)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw center dot (red)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            
            # Display detection info
            cv2.putText(frame, "BALL DETECTED", (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Display distance (the key result for your assignment!)
            if distance_cm:
                cv2.putText(frame, f"DISTANCE: {distance_cm:.1f} cm", (x, y + h + 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Display pixel size
            cv2.putText(frame, f"Size: {w} px", (x, y + h + 45),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        else:
            cv2.putText(frame, "NO BALL DETECTED", (50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Show FPS
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Show the frame
        cv2.imshow("Ball Detection + Depth Estimation", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Done!")


if __name__ == "__main__":
    main()
