# Tray status detection with TensorFlow + OpenCV + webcam

import tensorflow as tf
import numpy as np
import cv2
import requests
import datetime
from collections import deque

model = tf.keras.models.load_model("buffet_tray_model.h5")
class_names = ['empty', 'full', 'low', 'medium']
IMG_SIZE = (224, 224)

CONFIDENCE_THRESHOLD = 0.7
STABILITY_FRAMES = 5
FALLBACK_CROP = False  # set True if tray is always in same place on screen
FALLBACK_RECT = (100, 100, 400, 300)  # x, y, w, h fallback crop

last_sent_status = None
recent_predictions = deque(maxlen=STABILITY_FRAMES)

cap = cv2.VideoCapture(0)
print("Tray detection started. Press Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    detected = False
    tray_crop = None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)
    blurred = cv2.GaussianBlur(contrast, (5, 5), 0)
    edged = cv2.Canny(blurred, 30, 150)

    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
# look for rectangle-shaped contour that could be the tray
    for cnt in contours:
        area = cv2.contourArea(cnt)
        approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)

        if len(approx) == 4 and area > 10000:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w) / h
            if 0.5 < aspect_ratio < 2.5:
                tray_crop = frame[y:y + h, x:x + w]
                detected = True
                break  # use only first match

    if not detected and FALLBACK_CROP:  # enable if tray is fixed in view
        x, y, w, h = FALLBACK_RECT
        tray_crop = frame[y:y + h, x:x + w]

    if tray_crop is None:
        cv2.imshow("Tray Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue
# process the tray image and make a prediction

    try:
        img = cv2.resize(tray_crop, IMG_SIZE)
        img_array = tf.keras.utils.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        predictions = model.predict(img_array, verbose=0)
        confidence = np.max(predictions)
        predicted_index = np.argmax(predictions)
        predicted_class = class_names[predicted_index]

# if low confidence, skip this frame
        if confidence < CONFIDENCE_THRESHOLD: 
            continue

        override_applied = False
        if predicted_class == "empty":
            tray_gray = cv2.cvtColor(tray_crop, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(tray_gray, 80, 255, cv2.THRESH_BINARY_INV)
            contours2, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours2:
                if cv2.contourArea(c) > 500:
                    predicted_class = "low"
                    override_applied = True
                    break

        tray_id = "Tray 1"
        recent_predictions.append(predicted_class)

        if (len(recent_predictions) == STABILITY_FRAMES and
            all(p == predicted_class for p in recent_predictions) and
            predicted_class != last_sent_status):

            tray_data = {
                "tray_id": tray_id,
                "status": predicted_class,
                "confidence": float(round(confidence * 100, 1)),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "override": override_applied
            }

            try:
                response = requests.post("http://127.0.0.1:1880/tray-status", json=tray_data)
                print("Sent:", tray_data)
                last_sent_status = predicted_class
            except Exception as e:
                print("Send error:", e)

        label = f"{tray_id}: {predicted_class.upper()} ({confidence*100:.1f}%)"
        if override_applied:
            label += " [OVERRIDE]"
        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        if detected:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    except Exception as e:
        print("Detection error:", e)

    cv2.imshow("Tray Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
