import collections
import threading
import time

import cv2
from flask import Flask, jsonify, render_template, request
import numpy as np

app = Flask(__name__)

# ----------------- CONFIGURATION -----------------
HEALTHY_BPM_MIN = 12
STARE_TIMEOUT_SEC = 8.0
WINDOW_SECONDS = 60

analysis_lock = threading.Lock()
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
frame_counter = 0
total_blinks = 0
blink_timestamps = collections.deque()
last_blink_time = time.time()


def analyze_frame(frame):
  global frame_counter, total_blinks, last_blink_time

  with analysis_lock:
    current_time = time.time()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.2, minNeighbors=5, minSize=(100, 100)
    )
    face_detected = len(faces) > 0
    eyes_open = False

    if face_detected:
      for x, y, width, height in faces[:1]:
        upper_face = gray[y : y + int(height * 0.6), x : x + width]
        eyes = eye_cascade.detectMultiScale(
            upper_face, scaleFactor=1.15, minNeighbors=4, minSize=(25, 25)
        )
        eyes_open = len(eyes) >= 1

      if not eyes_open:
        frame_counter += 1
      else:
        if 1 <= frame_counter <= 6:
          total_blinks += 1
          blink_timestamps.append(current_time)
          last_blink_time = current_time
        frame_counter = 0
    else:
      frame_counter = 0

    while (
        blink_timestamps
        and current_time - blink_timestamps[0] > WINDOW_SECONDS
    ):
      blink_timestamps.popleft()

    stare_sec = current_time - last_blink_time if face_detected else 0.0
    return {
        "eyes_open": eyes_open,
        "bpm": len(blink_timestamps),
        "total_blinks": total_blinks,
        "stare_sec": round(stare_sec, 1),
        "face_detected": face_detected,
        "warning": face_detected and stare_sec >= STARE_TIMEOUT_SEC,
    }


@app.route("/")
def index():
  return render_template("index.html")


@app.route("/analyze_frame", methods=["POST"])
def analyze_video_frame():
  image = cv2.imdecode(
      np.frombuffer(request.get_data(), dtype=np.uint8), cv2.IMREAD_COLOR
  )
  if image is None:
    return jsonify(error="Could not read the camera frame."), 400
  return jsonify(analyze_frame(image))


if __name__ == "__main__":
  app.run(host="127.0.0.1", port=5000, debug=False)