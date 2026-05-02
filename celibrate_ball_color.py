import cv2
import numpy as np

# CHANGE THIS TO YOUR ESP32-CAM STREAM URL
STREAM_URL = "http://192.168.1.16:81/stream"  # <-- PUT YOUR IP HERE

print("=" * 50)
print("HSV Color Detector for Indigo Blue Ball")
print("=" * 50)
print("Instructions:")
print("1. Place your ball in front of the camera")
print("2. Click on the ball in the window")
print("3. The HSV values will appear in the terminal")
print("4. Press 'q' to quit")
print("-" * 50)

# Connect to camera
cap = cv2.VideoCapture(STREAM_URL)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce lag

# Mouse callback function
def get_hsv(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        hsv_image = param['hsv']
        hsv_value = hsv_image[y, x]
        print(f"\n📍 Pixel at ({x}, {y})")
        print(f"   HSV = [{hsv_value[0]}, {hsv_value[1]}, {hsv_value[2]}]")
        print(f"\nSuggested HSV range for your ball:")
        print(f"   LOWER = np.array([{max(0, hsv_value[0]-10)}, {max(0, hsv_value[1]-50)}, {max(0, hsv_value[2]-50)}])")
        print(f"   UPPER = np.array([{min(179, hsv_value[0]+10)}, 255, 255])")
        print("-" * 50)

# Create window and set mouse callback
cv2.namedWindow('Click on your ball')
cv2.setMouseCallback('Click on your ball', get_hsv, {'hsv': None})

while True:
    ret, frame = cap.read()
    if not ret:
        print("Warning: Failed to grab frame")
        continue
    
    # Convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Update the HSV image in the callback parameter
    cv2.setMouseCallback('Click on your ball', get_hsv, {'hsv': hsv})
    
    # Show the frame
    cv2.imshow('Click on your ball', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()