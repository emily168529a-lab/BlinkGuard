# BlinkGuard: Dry-Eye & Computer Vision Syndrome Preventer

BlinkGuard monitors your eye aspect ratio (EAR) and blink frequency using your local webcam, preventing Computer Vision Syndrome (CVS), dry eyes, and screen fatigue.

## Project Structure
- `main.py` - Core application tracking facial eye landmarks, computing rolling BPM, and rendering a real-time HUD with alerts.
- `app.py` - Optional Flask web monitor that requests webcam access from the browser and analyzes submitted frames.
- `templates/index.html` - Browser camera permission prompt, live preview, and blink metrics.
- `requirements.txt` - Python dependencies.
- `run.sh` / `run.bat` - Quick start scripts.

## Installation & Setup

1. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the desktop monitor:**
   ```bash
   python main.py
   ```

   To run the Flask web monitor instead, start the web app:
   ```bash
   python app.py
   ```
   Then open <http://127.0.0.1:5000> in your browser. The web app uses the
   computer's webcam through the Flask server. If no camera can be opened, the
   page displays camera-access troubleshooting instead of a broken image.
   Click **Allow camera** on the page and grant permission in your browser.
   BlinkGuard sends camera frames from the browser to the local Flask app for
   blink analysis using OpenCV's face and eye detectors, so the browser's
   camera permission prompt is used instead of the server opening the webcam.

## Controls & Demo Notes
- Press **`q`** inside the camera preview window to quit.
- **Stage Demo Calibration:** `STARE_TIMEOUT_SEC` is configured to `8.0s` so you can stare directly on stage without blinking and trigger the live alert box + system notification in front of an audience.
