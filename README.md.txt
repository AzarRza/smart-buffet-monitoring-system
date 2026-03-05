# Smart Buffet Monitoring & Hygiene Alert System

## Overview

This project presents an IoT-based system for monitoring buffet tray levels and environmental conditions in real time.

The system combines computer vision, environmental sensors, edge computing, and real-time dashboards to help kitchen staff monitor buffet stations and respond quickly when trays become empty or when environmental conditions exceed safe limits.

---

## Prototype Demo

Watch the system prototype here:

https://youtu.be/i4Smz0XSJ2A

---

## System Architecture

The system integrates multiple hardware and software components:

Camera → Raspberry Pi → CNN Model → Node-RED → Firebase → Dashboard
Arduino → Sensor Data → Node-RED → Firebase → Dashboard

---

## Hardware Components

* USB Webcam (tray monitoring)
* Raspberry Pi (edge computing node)
* Arduino Uno
* DHT20 Temperature & Humidity Sensor
* UPS for power stability

---

## Software Stack

* Python
* TensorFlow / Keras
* Node-RED
* Firebase Realtime Database
* Arduino IDE
* Power BI

---

## Repository Structure

```
smart-buffet-monitoring-system
│
├── architecture
│   └── system_architecture_buffet_monitoring.pdf
│
├── firmware
│   └── temp_humidity.ino
│
├── computer_vision
│   ├── tray_detect_and_send.py
│   └── buffet_tray_model.h5
│
├── node_red
│   └── flows.json
│
├── data
│   ├── environment_logs.xlsx
│   └── tray_history_logs.xlsx
│
├── dashboard
│   └── buffet_monitoring_dashboard.pbix
```

---

## Key Features

* Tray fill level detection (Full / Medium / Low / Empty)
* Real-time temperature monitoring
* Real-time humidity monitoring
* Alert when trays become empty
* Web dashboard updates via WebSocket
* Historical data storage in Firebase

---

## Computer Vision Model

A convolutional neural network trained using TensorFlow/Keras classifies tray fill levels using overhead camera images.

Classes:

* Full
* Medium
* Low
* Empty

To reduce prediction noise, the system uses a **2-out-of-3 consensus rule** across recent predictions before updating the tray state.

---

## Dashboard

The system includes a monitoring dashboard showing:

* tray status
* temperature
* humidity
* alerts

Historical analytics can be explored using the Power BI dashboard included in this repository.

---

## Limitations

* Model trained on limited dataset (~800 images)
* Lighting variation can affect classification
* Requires stable overhead camera installation

---

## Future Improvements

* larger training dataset
* multi-tray monitoring
* predictive refill alerts
* mobile-friendly dashboard
