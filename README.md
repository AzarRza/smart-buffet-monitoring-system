# Smart Buffet Monitoring & Hygiene Alert System

---

## Overview

This project was developed by Azar during a course in Digitalisation in Sustainable Production Development at KTH, between March and June 2025.

The idea came from a simple problem: in buffet settings, kitchen staff often don't know when a tray is running low or when the environment around the food has become unsafe. This system tries to solve that by combining a camera, environmental sensors, and a real-time dashboard to give staff the information they need without having to constantly check manually.

The system detects tray fill levels using a camera and a trained neural network, monitors temperature and humidity through an Arduino sensor, and routes everything through Node-RED into Firebase and a Power BI dashboard.

---

## Prototype Demo

Watch the system in action: [https://youtu.be/i4Smz0XSJ2A](https://youtu.be/i4Smz0XSJ2A)

---

## System Architecture

```
[USB Webcam]
     |
     v
[tray_detect_and_send.py]  -->  [buffet_tray_model.h5 (CNN)]
     |
     v (HTTP POST → /tray-status)
[Node-RED: Buffet_Monitoring_Flow]
     |                        |
     v                        v
[firebase_server.js]    [WebSocket /tray-feed]
     |                        |
     v                        v
[Firebase Realtime DB]   [Live Dashboard]
     |
     v
[Power BI Dashboard]

[Arduino Uno + DHT20]
     |
     v (Serial COM3 @ 9600 baud)
[Node-RED: Serial In]
     |
     v
[Combine Temp & Humidity + Alert Logic]
     |                        |
     v                        v
[Firebase /environment]  [WebSocket /env-feed]
```

Note: The PDF in `architecture/` reflects an earlier prototype design. The diagram above represents the actual implemented system.

---

## Hardware Components

| Component | Role |
|-----------|------|
| USB Webcam | Overhead image capture of buffet trays |
| Raspberry Pi | Edge node : runs the Python detection script |
| Arduino Uno | Reads the DHT20 sensor and sends data over Serial |
| DHT20 Sensor (I2C) | Measures ambient temperature and humidity |
| UPS | Keeps the system running without interruption |

---

## Software Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Computer Vision | Python, TensorFlow/Keras, OpenCV | CNN inference with contour-based correction |
| Edge Orchestration | Node-RED | Handles HTTP, Serial, WebSocket and Firebase routing |
| Firebase Bridge | Node.js, Express, firebase-admin | Writes data to Firebase Realtime Database |
| Cloud Storage | Firebase Realtime Database | Stores tray events, history and environment logs |
| Analytics | Microsoft Power BI | Historical trends and operational insights |
| Firmware | Arduino IDE, Arduino SensorKit | Reads DHT20 over I2C, outputs via Serial every 2 seconds |

---

## Repository Structure

```
smart-buffet-monitoring-system/
│
├── architecture/
│   └── system_architecture_buffet_monitoring.pdf
│
├── computer_vision/
│   ├── tray_detect_and_send.py
│   └── buffet_tray_model.h5
│
├── dashboard/
│   └── buffet_monitoring_dashboard.pbix
│
├── data/
│   ├── environment_logs.xlsx
│   └── tray_history_logs.xlsx
│
├── firmware/
│   └── temp_humidity.ino
│
├── node_red/
│   ├── .env.example
│   ├── firebase_server.js
│   └── flows.json
│
├── .gitignore
└── README.md
```

---

## Key Features

- Classifies tray fill level into four states: Full, Medium, Low, and Empty
- Only updates tray status after 5 consecutive identical predictions, which reduces false alerts from momentary image noise
- Discards any prediction where the model confidence is below 70%
- If the model predicts Empty but the camera still sees objects in the tray, the result is corrected to Low automatically
- Applies CLAHE contrast enhancement before detection to handle different lighting conditions
- Separates warning and critical thresholds for temperature and humidity
- Pushes tray and environment data independently to Firebase and live WebSocket feeds

---

## Computer Vision Model

The model is a convolutional neural network trained with TensorFlow and Keras. It takes overhead images from the webcam and classifies them into one of four tray states: Full, Medium, Low, or Empty.

Each frame goes through contrast enhancement, edge detection, and contour analysis to locate the tray before the image is passed to the model. If the confidence score is below 70%, the frame is skipped. A secondary OpenCV check runs when the model returns Empty — if objects are still visible inside the tray region, the result is changed to Low to avoid a false empty alert. The final state is only sent to Node-RED once 5 frames in a row agree on the same result.

The model was trained on around 800 images with an input size of 224x224 pixels.

---

## Firmware

The Arduino sketch reads temperature and humidity from a DHT20 sensor over I2C using the Arduino SensorKit library. It prints a reading to Serial every 2 seconds in this format:

```
Temperature = 24.5 C
Humidity = 58.3 %
```

Node-RED picks this up through a Serial In node configured on COM3 at 9600 baud.

---

## Node-RED Flow

The flow is called `Buffet_Monitoring_Flow` and handles two separate pipelines.

The tray pipeline receives HTTP POST requests from the Python script at `/tray-status`, parses the JSON, pushes the data to the WebSocket feed at `/tray-feed`, and forwards it to Firebase through `firebase_server.js`.

The environment pipeline reads Serial data from the Arduino, pairs temperature and humidity readings, evaluates alert thresholds, writes to Firebase under `/environment`, and pushes to the WebSocket feed at `/env-feed`.

Alert thresholds:
- Critical: temperature above 30°C or below 15°C, humidity above 70% or below 30%
- Warning: temperature between 27–30°C or 15–18°C, humidity between 65–70% or 30–35%

To use: open Node-RED, go to Menu → Import, and paste the contents of `flows.json`. After importing, update the Firebase URL in the HTTP request node to your own database URL.

---

## Firebase Bridge

`firebase_server.js` is a small Express server that receives data from Node-RED and writes it to Firebase Realtime Database using the firebase-admin SDK.

| Endpoint | Method | Writes to |
|----------|--------|-----------|
| `/tray-update` | POST | `trays/`, `tray_history/`, `logs/` |
| `/env-update` | POST | `environment/` |

To run locally:

1. Go into `node_red/`
2. Create a file called `.env` based on `.env.example`
3. Fill in your Firebase service account JSON and database URL
4. Install dependencies:
   ```bash
   npm install express body-parser firebase-admin dotenv
   ```
5. Run with:
   ```bash
   node firebase_server.js
   ```

Never upload your `.env` file or Firebase service account key to GitHub. Both are blocked by `.gitignore`.

---

## Dashboard

The Power BI dashboard (`dashboard/buffet_monitoring_dashboard.pbix`) connects to Firebase data and shows tray fill trends, temperature and humidity history, alert frequency, and general operational patterns. It requires Power BI Desktop to open, which is free to download from Microsoft.

---

## Getting Started

**Python (Raspberry Pi):**
```
tensorflow
opencv-python
numpy
requests
```

**Node.js (Firebase server):**
```bash
npm install express body-parser firebase-admin dotenv
```

**Arduino:** Arduino IDE with the Arduino_SensorKit library installed

Setup steps:
1. Upload `firmware/temp_humidity.ino` to the Arduino
2. Create your `.env` file in `node_red/` based on `.env.example`
3. Run `node firebase_server.js`
4. Import `flows.json` into Node-RED and deploy
5. Run `python tray_detect_and_send.py` on the Raspberry Pi
6. Open the `.pbix` file in Power BI Desktop

---

## Limitations

- The model was trained on a small dataset of around 800 images, so it may struggle in environments with very different lighting or tray types
- Tray detection depends on the tray having a clear rectangular shape in view
- The Serial port is hardcoded to COM3 in Node-RED — this needs to be changed if your setup uses a different port
- The architecture PDF is from an earlier version of the project and does not reflect the final system

---

## Future Improvements

- Train on a larger and more varied dataset
- Support monitoring multiple trays from one camera
- Add predictive refill alerts based on usage patterns
- Build a mobile-friendly live dashboard
- Add SMS or push notification alerts
- Auto-detect the Arduino serial port rather than hardcoding it

---

## Author

Azar Rza
KTH — Digitalisation in Sustainable Production Development
March – June 2025
