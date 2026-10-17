import collections
import time
import cv2
from plyer import notification

HEALTHY_BPM_MIN = 12
STARE_TIMEOUT_SEC = 8.0
WINDOW_SECONDS = 60

# Load built-in OpenCV Haar Cascades
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye.xml"
)


def send_alert(title, message):
  try:
    notification.notify(
        title=title, message=message, app_name="BlinkGuard", timeout=3
    )
  except Exception:
    pass


def main():
  cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
  if not cap.isOpened():
    cap = cv2.VideoCapture(0)
  if not cap.isOpened():
    print("[ERROR] Could not access webcam.")
    return

  blink_count = 0
  eyes_detected_prev = True
  closed_frame_count = 0
  blink_timestamps = collections.deque()
  last_blink_time = time.time()
  last_alert_time = 0.0

  print("[INFO] BlinkGuard running with OpenCV Cascade.")
  print("[INFO] Press 'q' to exit.")

  while True:
    ret, frame = cap.read()
    if not ret:
      break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    current_time = time.time()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.2, minNeighbors=5, minSize=(100, 100)
    )
    face_found = len(faces) > 0
    eyes_detected = False

    for x, y, fw, fh in faces:
      cv2.rectangle(frame, (x, y), (x + fw, y + fh), (255, 180, 0), 1)
      roi_gray = gray[y : y + int(fh * 0.6), x : x + fw]
      roi_color = frame[y : y + int(fh * 0.6), x : x + fw]

      eyes = eye_cascade.detectMultiScale(
          roi_gray, scaleFactor=1.15, minNeighbors=4, minSize=(25, 25)
      )
      if len(eyes) >= 1:
        eyes_detected = True
        for ex, ey, ew, eh in eyes:
          cv2.rectangle(
              roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 1
          )
      break

    # Blink logic: Eyes were open, disappeared briefly (blink), then reopened
    if face_found:
      if not eyes_detected:
        closed_frame_count += 1
      else:
        if 1 <= closed_frame_count <= 6:
          blink_count += 1
          blink_timestamps.append(current_time)
          last_blink_time = current_time
        closed_frame_count = 0

    while (
        blink_timestamps
        and current_time - blink_timestamps[0] > WINDOW_SECONDS
    ):
      blink_timestamps.popleft()

    current_bpm = len(blink_timestamps)
    stare_duration = (
        current_time - last_blink_time if face_found else 0.0
    )

    # Trigger stare alert
    if face_found and stare_duration >= STARE_TIMEOUT_SEC:
      cv2.putText(
          frame,
          "STARE WARNING: BLINK NOW!",
          (w // 2 - 200, h - 35),
          cv2.FONT_HERSHEY_SIMPLEX,
          0.8,
          (0, 0, 255),
          2,
      )
      if current_time - last_alert_time > 5.0:
        send_alert(
            "BlinkGuard Alert", "You haven't blinked in a while! Blink now."
        )
        last_alert_time = current_time

    bpm_color = (
        (0, 0, 255) if current_bpm < HEALTHY_BPM_MIN else (0, 255, 0)
    )

    # HUD overlay
    overlay = frame.copy()
    cv2.rectangle(overlay, (15, 15), (320, 130), (25, 25, 25), -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    cv2.putText(
        frame,
        f"Rolling BPM: {current_bpm} (Target: >{HEALTHY_BPM_MIN})",
        (25, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        bpm_color,
        2,
    )
    cv2.putText(
        frame,
        f"Total Blinks: {blink_count}",
        (25, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        f"Stare Duration: {stare_duration:.1f}s",
        (25, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 165, 255) if stare_duration > 4 else (200, 200, 200),
        1,
    )

    cv2.imshow("BlinkGuard - Live Monitor", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
      break

  cap.release()
  cv2.destroyAllWindows()


if __name__ == "__main__":
  main()