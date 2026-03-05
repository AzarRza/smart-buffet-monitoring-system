require('dotenv').config();

const express = require("express");
const bodyParser = require("body-parser");
const admin = require("firebase-admin");

// ---------------------------------------------------------------
// SECURITY: credentials are loaded from environment variables,
// NOT from a file. Never hardcode your service account key here.
// To run locally: create a .env file (see .env.example for format)
// ---------------------------------------------------------------
const serviceAccount = JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT);

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: process.env.FIREBASE_DATABASE_URL
});

const app = express();
const port = 3000;

app.use(bodyParser.json());

// Tray updates route
app.post("/tray-update", (req, res) => {
  const data = req.body;
  console.log("Tray data received:", data);

  if (!data || !data.tray_id || !data.timestamp) {
    console.error("Missing tray_id or malformed data.");
    return res.status(400).send("Invalid tray data");
  }

  const trayRef = admin.database().ref("trays").child(data.tray_id);
  const historyRef = admin.database().ref("tray_history").child(data.tray_id).child(data.timestamp);
  const logRef = admin.database().ref("logs").push();

  trayRef.set(data);
  historyRef.set(data);
  logRef.set(data);

  res.send("Tray data stored.");
});

// Temperature and Humidity route
app.post("/env-update", (req, res) => {
  const data = req.body;
  console.log("Env data received:", data);

  if (!data || !data.temperature || !data.humidity || !data.timestamp) {
    console.error("Missing env fields or malformed.");
    return res.status(400).send("Invalid env data");
  }

  const envRef = admin.database().ref("environment").child(data.timestamp);
  envRef.set(data, (err) => {
    if (err) {
      console.error("Failed to store env data:", err);
      return res.status(500).send("Write failed");
    }
    res.send("Environment data stored.");
  });
});

app.listen(port, () => {
  console.log(`Firebase server listening at http://localhost:${port}`);
});
