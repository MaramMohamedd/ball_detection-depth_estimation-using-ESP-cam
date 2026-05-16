
# ESP32-CAM Ball Detection & Depth Estimation

Real-time ball detection and distance estimation using ESP32-CAM and computer vision. The system detects an indigo blue ball and calculates its distance from the camera using a calibrated focal length formula.

## 🎯 Features

- **Real-time ball detection** using HSV color filtering
- **Distance estimation** based on known-size formula: `Distance = (Real Diameter × Focal Length) / Pixel Diameter`
- **Low-latency streaming** optimized for ESP32-CAM
- **Interactive calibration tools** for HSV values and focal length
- **Visual feedback** with bounding box and distance display

## 📋 Requirements

### Hardware
- ESP32-CAM module
- Indigo blue ball (or any colored ball of your choice)
- USB-TTL programmer (for initial ESP32 setup)
- Power supply (5V) (optional if not using your laptop port + Micro_USB) for powering esp

### Software
- Arduino IDE (for ESP32-CAM setup)
- Python 3.7+
- OpenCV
- NumPy

## 🚀 Setup & Installation

### 1. ESP32-CAM Setup

1. Install ESP32 board in Arduino IDE
2. Upload the CameraWebServer example sketch
3. Configure WiFi credentials
4. Note the IP address (e.g., `http://192.145.1.16:81/stream`)

### 2. Python Dependencies

```bash
pip install opencv-python numpy
```

### 3. Clone Repository

```bash
git clone https://github.com/yourusername/esp32-ball-detection.git
cd esp32-ball-detection
```

## 🔧 Calibration Process

### Step 1: HSV Color Calibration

Find the optimal HSV range for your ball:

```bash
python hsv_calibration.py
```

- Click on the ball in the video window
- Copy the suggested HSV range values
- Update `LOWER_BLUE` and `UPPER_BLUE` in the main script

### Step 2: Focal Length Calibration

Calibrate your camera's focal length:

```bash
python focal_calibration.py
```

1. Place the ball exactly **20 cm** from the camera
2. Press `SPACE` when ball is detected
3. Copy the calculated focal length value to the main script

## 🔌 Hardware Setup

-> Ensure that you've installed the driver pleasee

### ESP32-CAM with MB Adapter Board

The **ESP32-CAM-MB** is a shield/programmer board that makes everything much simpler:

### Simple Connection (via Micro USB)

- **One cable solution**: Just connect Micro USB to laptop
- **MB board handles**: 
  - 5V to 3.3V regulation
  - USB-to-Serial conversion
  - Automatic reset circuit

### Power Options

1. **Laptop USB** (simplest) and what i have used:
   - Works for most cases
   - May have issues if laptop USB port is weak 
   
2. **USB Wall Charger** (recommended for reliability):
   - 5V, 1A minimum
   - More stable for long-running projects

## 📁 Project Structure

```
ball-detection-depth-estimation-using-ESP-cam/
│
├── depth_estimation_ball_detection.py   # Main application
├── celibrate_ball_color.py              # HSV value finder
├── focal_calibration.py                 # Focal length calibrator
├── ball_detection_final.py              # src code for detection only                    
├── requirements.txt                     
└── README.md                            # This file
```

## 💻 Usage

### Run the Main Application

```bash
python depth_estimation_ball_detection.py
```

**Controls:**
- `q` - Quit application
- Real-time display shows:
  - Bounding box around detected ball
  - Distance in centimeters
  - FPS counter

### Configuration

Edit the following variables in the main script:

```python
# Camera settings
STREAM_URL = "http://192.168.1.16:81/stream"  # Your ESP32-CAM IP

# Ball properties
REAL_BALL_DIAMETER_CM = 7.0    # Your ball's actual diameter
FOCAL_LENGTH = 265.33           # Your calibrated focal length

# HSV range (from calibration)
LOWER_BLUE = np.array([88, 60, 40])
UPPER_BLUE = np.array([108, 255, 255])
```

## 📊 Performance Optimization Tips that really worked with me

From my testing experience:

1. **Frame Size**: Smaller frame sizes reduce latency significantly
   - Recommended: 320x240 or 640x480
   
2. **Quality Setting**: Lower quality values (e.g., 12-15) improve speed
   
3. **Buffer Size**: Set buffer to 1 frame to reduce lag:
   ```python
   cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
   ```

## 🔬 How It Works

### Distance Estimation Formula

```
Distance = (Real Diameter × Focal Length) / Pixel Diameter

Where:
- Real Diameter: Actual ball diameter (cm)
- Focal Length: Calibrated camera constant (pixels)
- Pixel Diameter: Detected ball width in image (pixels)
```

### Ball Detection Pipeline

1. Convert BGR frame to HSV color space
2. Apply HSV mask for ball color
3. Erode/Dilate to remove noise
4. Find contours and select largest
5. Draw bounding box and calculate pixel width
6. Compute distance using calibrated formula

## 🎯 Example Output

```
Ball detected! Width: 45 px
Distance: 41.2 cm

Ball detected! Width: 52 px
Distance: 35.7 cm
```

## ⚠️ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Cannot connect to ESP32-CAM | Check IP address and power cycle the ESP32 |
| Ball not detected | Recalibrate HSV values with different lighting |
| Unstable distance readings | Ensure good lighting and reduce frame size |
| High latency | Lower frame resolution and quality settings |

## 📈 Future Improvements

- [ ] Add object tracking for multiple balls
- [ ] Create GUI interface
- [ ] Support for different colored objects

## 🤝 Contributing

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you'd like to change.

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🙏 Acknowledgments

- ESP32-CAM community
- OpenCV developers
- Arduino team for CameraWebServer example

## 📧 Contact

Maram - marammohamedhanafy@gmail.com

