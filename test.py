from flask import Flask, jsonify, render_template_string
import serial
import threading
import time
from datetime import datetime

app = Flask(__name__)

# Serial Port Configuration
SERIAL_PORT = 'COM3'  # Change to your correct COM port
BAUD_RATE = 115200

# Latest Telemetry Data
latest_data = {
    "yaw": 0, "roll": 0, "pitch": 0, "heading": 0,
    "temperature": 0, "pressure": 0, "altitude": 0,
    "latitude": 0, "longitude": 0, "gpsAlt": 0,
    "distance": 0, "targetAlt": 0, "velocity": 0,
    "pitch1": 0, "pitch2": 0, "roll1": 0, "roll2": 0
}


def read_serial():
    global latest_data
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"✅ Connected to {SERIAL_PORT}")
        time.sleep(2)  # Allow connection to stabilize
    except Exception as e:
        print(f"❌ Serial connection failed: {e}")
        return

    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line.startswith("Sent:"):
                parts = line[5:].split(",")
                if len(parts) >= 16:  # Updated for all parameters
                    latest_data = {
                        "yaw": float(parts[0]),
                        "roll": float(parts[1]),
                        "pitch": float(parts[2]),
                        "heading": float(parts[3]),
                        "temperature": float(parts[4]),
                        "pressure": float(parts[5]),
                        "altitude": float(parts[6]),
                        "latitude": float(parts[7]),
                        "longitude": float(parts[8]),
                        "gpsAlt": float(parts[9]),
                        "distance": float(parts[10]),
                        "targetAlt": float(parts[11]),
                        "pitch1": float(parts[12]),
                        "pitch2": float(parts[13]),
                        "roll1": float(parts[14]),
                        "roll2": float(parts[15]),
                        "velocity": float(parts[16])if len(parts) > 16 else 0
                    }
                    print("✅ Parsed:", latest_data)
        except Exception as e:
            print(f"⚠️  Error reading serial data: {e}")


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/data')
def data():
    # Ensure all values are float (handle None cases)
    response_data = {k: float(v) if v is not None else 0.0
                    for k, v in latest_data.items()}
    return jsonify(response_data)


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>TELEMENTRY DASHBOARD</title>

  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

  <!-- Leaflet CSS and JS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <!--three.js for 3d-->
  <script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>

  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: Arial, sans-serif;
      background: #0f1622;
      color: #fff;
      display: flex;
      height: 100vh;
      overflow: hidden;
    }

    .sidebar {
      width: 180px;
      background: #0a0f18;
      height: 100%;
      padding-top: 20px;
      border-right: 1px solid #1a283a;
    }

    .logo {
      display: flex;
      align-items: center;
      padding: 0 15px 20px 15px;
      color: white;
      font-weight: bold;
      font-size: 18px;
    }

    .logo img {
      width: 24px;
      height: 24px;
      margin-right: 10px;
      border-radius: 50%;
      background: #4a60ea;
    }

    .nav-item {
      display: flex;
      align-items: center;
      padding: 12px 15px;
      color: #8899aa;
      cursor: pointer;
      transition: all 0.2s;
    }

    .nav-item:hover {
      background: #1a283a;
    }

    .nav-item.active {
      background: #1a283a;
      color: white;
    }

    .nav-item svg {
      margin-right: 12px;
      width: 20px;
      height: 20px;
    }

    .collapse-btn {
      margin-top: auto;
      padding: 12px 15px;
      display: flex;
      align-items: center;
      color: #8899aa;
      cursor: pointer;
    }

    .collapse-btn svg {
      margin-right: 12px;
      width: 20px;
      height: 20px;
    }

    .main-content {
      flex: 1;
      padding: 0px;
      display: flex;
      flex-direction: column;
      overflow-y: auto;
    }

    .status-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #0f1622;
      padding: 10px 20px;
      border-bottom: 1px solid #1a283a;
      color: #8899aa;
    }

    .status-item {
      display: flex;
      flex-direction: column;
    }

    .status-label {
      font-size: 12px;
      margin-bottom: 4px;
    }

    .status-value {
      color: white;
      font-size: 14px;
    }

    .status-disconnected {
      color: #0ebd20;
    }

    .panel-container {
      display: flex;
      flex-direction: column;
      flex: 1;
      padding: 20px;
      gap: 20px;
    }

    .panel-row {
      display: flex;
      gap: 20px;
    }

    .panel-column {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .panel {
      background: #19202e;
      border-radius: 10px;
      padding: 15px;
      flex: 1;
      display: flex;
      flex-direction: column;
    }

    .panel-header {
      font-size: 16px;
      font-weight: bold;
      margin-bottom: 5px;
      color: white;
    }

    .data-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
      margin-bottom: 10px;
    }

    .data-item {
      background: #121a28;
      padding: 10px;
      border-radius: 5px;
    }

    .data-label {
      font-size: 12px;
      color: #8899aa;
      margin-bottom: 5px;
    }

    .data-value {
      font-size: 16px;
      font-weight: bold;
    }

    #map {
      height: 380px;
      width: 100%;
      border-radius: 5px;
      margin-top: 10px;
    }

    .altitude-value {
      color: #9966ff;
    }

    .velocity-value {
      color: #22cc66;
    }

    .temperature-value {
      color: #ff5757;
    }

    .chart-container {
      background-color: #1e2a3a;
      padding:15px;
      border-radius: 12px;
      height: 150px;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .chart-grid{
      display:grid;
      grid-template-columns: repeat(auto-fit,minmax(200px 1fr));
      gap: 10px;
      padding: 20px;
    }

    #rocket-viewer {
      width: 580px;
      height: 200px;
      background-color: black;
      border-radius: 12px;
      overflow: hidden;
    }

    /* For the chart legends and grid lines */
    canvas {
      border-radius: 5px;
      width: 100%;
      height: 100%;
    }

    .fin1-value {
      color: #ff9966;
    }

    .fin2-value {
      color: #66ff99;
    }

    .fin3-value {
      color: #6699ff;
    }

    .fin4-value {
      color: #ff66cc;
    }
  </style>
</head>
<body>

  <!-- Sidebar -->
  <div class="sidebar">
    <div class="logo"><img src="C:/Users/lenovo/Downloads/1690036204691.jpg" alt="SZI Rocket Logo" width="200">
      SPACE ZONE INDIA
    </div>

    <div class="nav-item active">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>
      Dashboard
    </div>
    <div class="nav-item">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
       stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M4.5 16.5L9 15l3-3 1.5-4.5L15 3l6 6-4.5 1.5-3 3-1.5 4.5-1.5 1.5-1.5-1.5-1.5 1.5-1.5-1.5z" />
    <path d="M9 15l-3 3" />
  </svg>
      Target Mapping
    </div>
    <div class="nav-item">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
      Record
    </div>
    <div class="nav-item">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
      Data Dump
    </div>
    <div class="nav-item">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="4"></circle><line x1="4.93" y1="4.93" x2="9.17" y2="9.17"></line><line x1="14.83" y1="14.83" x2="19.07" y2="19.07"></line><line x1="14.83" y1="9.17" x2="19.07" y2="4.93"></line><line x1="14.83" y1="9.17" x2="18.36" y2="5.64"></line><line x1="4.93" y1="19.07" x2="9.17" y2="14.83"></line></svg>
      Peripherals
    </div>
    <div class="nav-item">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"></polyline><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path></svg>
      Gyroscopes
    </div>
    <div class="nav-item">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>
      Accelerometers
    </div>
    <div class="nav-item">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
      Debug
    </div>
    <div class="nav-item">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg>
      Location
    </div>

    <div class="collapse-btn">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>

    </div>
  </div>

  <!-- Main Content -->
  <div class="main-content">
    <div class="status-bar">
      <div class="status-item">
        <div class="status-label">Local Time</div>
        <div class="status-value" id="localTime">12:59 PM</div>
      </div>
      <div class="status-item">
        <div class="status-label">Satellite</div>
        <div class="status-value">0</div>
      </div>
      <div class="status-item">
        <div class="status-label">STATUS</div>
        <div class="status-value status-disconnected">CONNECTED</div>
      </div>
      <div class="status-item">
        <div class="status-label">Signal</div>
        <div class="status-value">5.7.0 dBm</div>
      </div>
      <div class="status-item">
        <div class="status-label">Battery</div>
        <div class="status-value">70%</div>
      </div>
    </div>

    <div class="panel-container">
      <!-- Left Column -->
      <div class="panel-row" style="flex: 0 0 auto;">
        <div class="panel">
          <div class="panel-header">GPS Location</div>
          <div class="data-grid">
            <div class="data-item">
              <div class="data-label">Latitude</div>
              <div class="data-value" id="latitudeVal">0.00000°</div>
            </div>
            <div class="data-item">
              <div class="data-label">Longitude</div>
              <div class="data-value" id="longitudeVal">0.00000°</div>
            </div>
            <div class="data-item">
              <div class="data-label">Heading</div>
              <div class="data-value" id="headingVal">270°</div>
            </div>
          </div>
          <div id="map"></div>
        </div>
        <div class="panel" style="flex: 1;">
          <div class="panel-header">Flight Data</div>
          <div class="data-grid">
            <div class="data-item">
              <div class="data-label">Pitch</div>
              <div class="data-value" id="pitchVal">-29.75°</div>
            </div>
            <div class="data-item">
              <div class="data-label">Roll</div>
              <div class="data-value" id="rollVal">0.27°</div>
            </div>
            <div class="data-item">
              <div class="data-label">Yaw</div>
              <div class="data-value" id="yawVal">-3.22°</div>
            </div>
            <div class="data-item">
              <div class="data-label">Current Altitude</div>
              <div class="data-value" id="currentAltitudeVal">0.0 m</div>
            </div>
          </div>
          <div class="data-item" style="margin-top: 10px;">
            <div class="data-label">Distance</div>
            <div class="data-value altitude-value" id="distanceVal">8946.51 km</div>
          </div>
          <div style="display: flex; justify-content: space-between; margin-top: 10px;">
            <div class="data-label">SGNM Alt: 0.0 m</div>
            <div class="data-label">Target ALT: 1.5 m</div>
          </div>
          <div class="panel">
            <div class="panel-header">3D Rocket Orientation</div>
            <div id="rocket-viewer" style="width: 590px; height: 250px; border: 1px solid #333;"></div>
          </div>
        </div>
       </div> 

      <div class="panel-row" style="flex: 0 0 auto;">
        <div class="panel" style="flex: 1;">
          <div class="panel-header">Altitude</div>
          <div class="altitude-value" id="altitudeVal" style="font-size: 24px; margin-bottom: 10px;">0.28 m</div>
          <div class="chart-container">
            <canvas id="altitudeChart"></canvas>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 12px; color: #8899aa; margin-top: 5px;">
            <div>Min: 0.00 m</div>
            <div>Max: 0.00 km</div>
          </div>
        </div>

        <div class="panel" style="flex: 1;">
          <div class="panel-header">Pressure</div>
          <div class="data-value" id="pressureVal" style="font-size: 24px; margin-bottom: 10px; color: orchid;">1000.72 kPa</div>
          <div class="chart-container">
            <canvas id="pressureChart"></canvas>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 12px; color: #8899aa; margin-top: 5px;">
            <div>Min: 999 kPa</div>
            <div>Max: 1001 kPa</div>
          </div>
        </div>

       <div class="panel" style="flex: 1;">
          <div class="panel-header">Temperature</div>
          <div class="temperature-value" id="temperatureVal" style="font-size: 24px; margin-bottom: 10px;">30.6 °C</div>
          <div class="chart-container">
            <canvas id="temperatureChart"></canvas>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 12px; color: #8899aa; margin-top: 5px;">
            <div>Min: 30.00 °C</div>
            <div>Max: 150.00 °C</div>
          </div>
        </div>
       </div> 

      <!-- Right Column -->
      <div class="panel-row" style="flex: 0 0 auto;">
        <div class="panel" style="flex: 1;">
          <div class="panel-header">Velocity</div>
          <div class="velocity-value" id="velocityVal" style="font-size: 24px; margin-bottom: 10px;">0.00 m/s</div>
          <div class="chart-container">
            <canvas id="velocityChart"></canvas>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 12px; color: #8899aa; margin-top: 5px;">
            <div>Min: 0.00 m/s</div>
            <div>Max: 0.00 m/s</div>
          </div>
        </div>

        <div class="panel" style="flex: 1;">
          <div class="panel-header">Gyroscopes</div>
          <div style="font-family: monospace; margin-bottom: 10px; font-size: 14px;">
            <div style="color: #7559f3;" id="x-val">X: 0.00</div>
            <div style="color: #f04a68;" id="y-val">Y: 0.00</div>
            <div style="color: #6be362;" id="z-val">Z: 0.00</div>
          </div>
          <div class="chart-container">
            <canvas id="gyroscopeChart"></canvas>
          </div>
        </div>

        <div class="panel" style="flex: 1;">
          <div class="panel-header">Accelerometers</div>
          <div style="font-family: monospace; margin-bottom: 10px; font-size: 14px;">
            <div style="color: #5f57ff;" id="x-value">X: 0.00</div>
            <div style="color: #dc1e24;" id="y-value">Y: 0.00</div>
            <div style="color: #66ff69;" id="z-value">Z: 0.00</div>
          </div>
          <div class="chart-container">
            <canvas id="accelerometerChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Fin Angles Row -->
      <div class="panel-row" style="flex: 0 0 auto;">
        <div class="panel" style="flex: 1;">
          <div class="panel-header">Fin-1 Angle</div>
          <div class="fin1-value" id="pitch1Val" style="font-size: 24px; margin-bottom: 10px;">0.00°</div>
          <div class="chart-container">
            <canvas id="pitch1Chart"></canvas>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 12px; color: #8899aa; margin-top: 5px;">
            <div>Min: 0.00°</div>
            <div>Max: 180.00°</div>
          </div>
        </div>

        <div class="panel" style="flex: 1;">
          <div class="panel-header">Fin-2 Angle</div>
          <div class="fin2-value" id="roll1Val" style="font-size: 24px; margin-bottom: 10px;">0.00°</div>
          <div class="chart-container">
            <canvas id="roll1Chart"></canvas>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 12px; color: #8899aa; margin-top: 5px;">
            <div>Min: 0.00°</div>
            <div>Max: 180.00°</div>
          </div>
        </div>

         <div class="panel" style="flex: 1;">
          <div class="panel-header">Fin-3 Angle</div>
          <div class="fin3-value" id="pitch2Val" style="font-size: 24px; margin-bottom: 10px;">0.00°</div>
          <div class="chart-container">
            <canvas id="pitch2Chart"></canvas>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 12px; color: #8899aa; margin-top: 5px;">
            <div>Min: 0.00°</div>
            <div>Max: 180.00°</div>
          </div>
        </div>

        <div class="panel" style="flex: 1;">
          <div class="panel-header">Fin-4 Angle</div>
          <div class="fin4-value" id="roll2Val" style="font-size: 24px; margin-bottom: 10px;">0.00°</div>
          <div class="chart-container">
            <canvas id="roll2Chart"></canvas>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 12px; color: #8899aa; margin-top: 5px;">
            <div>Min: 0.00°</div>
            <div>Max: 180.00°</div>
          </div>
        </div>
      </div>
     </div>
    </div>


<script>
  // Initialize Leaflet map with satellite imagery
  const map = L.map('map', {attributionControl: false}).setView([0, 0], 2);
  const googleSat = L.tileLayer('https://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}', {
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
    maxZoom: 20,
    attribution: 'Map data ©2024 Google'
  });
  googleSat.addTo(map);

  // Add marker for rocket position
  const marker = L.marker([0, 0]).addTo(map);

  // Update local time
  function updateLocalTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    document.getElementById('localTime').textContent = timeString;
  }
  updateLocalTime();
  setInterval(updateLocalTime, 60000);

  const maxPoints = 20;

  // Create chart with styling to match the screenshots
  const createLineChart = (ctx, color) => new Chart(ctx, {
    type: 'line',
    data: {
      labels: Array(20).fill(''),
      datasets: [{ 
        data: Array(20).fill(null),
        borderColor: color,
        backgroundColor: 'transparent',
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: { 
        x: { 
          grid: { 
            display: true,
            drawBorder: true
          },
          ticks: { display: true }
        },
        y: { 
          grid: { 
            color: '#2a3345',
            drawBorder: true
          },
          ticks: { 
            display: true
          }
        }
      },
      animation: false
    }
  });

  // Create charts
  const altitudeChart = createLineChart(document.getElementById('altitudeChart').getContext('2d'), '#9966ff');
  const velocityChart = createLineChart(document.getElementById('velocityChart').getContext('2d'), '#22cc66');
  const temperatureChart = createLineChart(document.getElementById('temperatureChart').getContext('2d'), '#ff5757');
  const pressureChart = createLineChart(document.getElementById('pressureChart').getContext('2d'), '#9966ff');
  const pitch1Chart = createLineChart(document.getElementById('pitch1Chart').getContext('2d'), '#ff9966');
  const pitch2Chart = createLineChart(document.getElementById('pitch2Chart').getContext('2d'), '#66ff99');
  const roll1Chart = createLineChart(document.getElementById('roll1Chart').getContext('2d'), '#6699ff');
  const roll2Chart = createLineChart(document.getElementById('roll2Chart').getContext('2d'), '#ff66cc');

  const gyroscopeChart = new Chart(document.getElementById('gyroscopeChart').getContext('2d'), {
    type: 'line',
    data: {
      labels: Array(20).fill(''),
      datasets: [
        { 
          data: Array(20).fill(null), 
          borderColor: '#ff5757', 
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.4
        },
        { 
          data: Array(20).fill(null), 
          borderColor: '#22cc66', 
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.4
        },
        { 
          data: Array(20).fill(null), 
          borderColor: '#9966ff', 
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: { 
        x: { 
          grid: { 
            display: true,
            drawBorder: true
          },
          ticks: { display: true }
        },
        y: { 
          grid: { 
            color: '#2a3345',
            drawBorder: true
          },
          ticks: { 
            display: true
          }
        }
      },
      animation: false
    }
  });

  const accelerometerChart = new Chart(document.getElementById('accelerometerChart').getContext('2d'), {
    type: 'line',
    data: {
      labels: Array(20).fill(''),
      datasets: [
        { 
          data: Array(20).fill(null), 
          borderColor: '#ff5757', 
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.4
        },
        { 
          data: Array(20).fill(null), 
          borderColor: '#22cc66', 
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.4
        },
        { 
          data: Array(20).fill(null), 
          borderColor: '#9966ff', 
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: { 
        x: { 
          grid: { 
            display: true,
            drawBorder: true
          },
          ticks: { display: true }
        },
        y: { 
          grid: { 
            color: '#2a3345',
            drawBorder: true
          },
          ticks: { 
            display: true
          }
        }
      },
      animation: false
    }
  });

  // Update chart data function
  function updateChartData(chart, newValue) {
    chart.data.datasets[0].data.push(newValue);
    if (chart.data.datasets[0].data.length > maxPoints) {
      chart.data.datasets[0].data.shift();
    }
    chart.update();
  }

  // Initialize charts with flat line data
  function initializeChartData() {
    // Seed initial flat line data
    const flatLineAltitude = Array(maxPoints).fill(0);
    const flatLineVelocity = Array(maxPoints).fill(0);
    const flatLineTemperature = Array(maxPoints).fill(30.6);
    const flatLinePressure = Array(maxPoints).fill(1000.72);
    const flatLinePitch1 = Array(maxPoints).fill(32);
    const flatLinePitch2 = Array(maxPoints).fill(32);
    const flatLineRoll1 = Array(maxPoints).fill(96);
    const flatLineRoll2 = Array(maxPoints).fill(96);

    altitudeChart.data.datasets[0].data = flatLineAltitude;
    velocityChart.data.datasets[0].data = flatLineVelocity;
    temperatureChart.data.datasets[0].data = flatLineTemperature;
    pressureChart.data.datasets[0].data = flatLinePressure;
    pitch1Chart.data.datasets[0].data = flatLinePitch1;
    pitch2Chart.data.datasets[0].data = flatLinePitch2;
    roll1Chart.data.datasets[0].data = flatLineRoll1;
    roll2Chart.data.datasets[0].data = flatLineRoll2;

    // Initialize gyroscope and accelerometer charts
    const zeroLine = Array(maxPoints).fill(0);

    gyroscopeChart.data.datasets[0].data = [...zeroLine];
    gyroscopeChart.data.datasets[1].data = [...zeroLine];
    gyroscopeChart.data.datasets[2].data = [...zeroLine];

    accelerometerChart.data.datasets[0].data = [...zeroLine];
    accelerometerChart.data.datasets[1].data = [...zeroLine];
    accelerometerChart.data.datasets[2].data = [...zeroLine];

    altitudeChart.update();
    velocityChart.update();
    temperatureChart.update();
    pressureChart.update();
    pitch1Chart.update();
    pitch2Chart.update();
    roll1Chart.update();
    roll2Chart.update();
    gyroscopeChart.update();
    accelerometerChart.update();
  }

  // Initialize charts
  initializeChartData();

  // 3D Rocket Viewer
  const container = document.getElementById('rocket-viewer');
  let scene, camera, renderer, rocketGroup, flameParticles;

  function initScene() {
    scene = new THREE.Scene();

    camera = new THREE.PerspectiveCamera(
      75,
      container.clientWidth / container.clientHeight,
      0.1,
      1000
    );
    camera.position.set(0, 2, 6);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setClearColor(0x000011);
    container.appendChild(renderer.domElement);

    // === 🚀 Improved Missile ===
    rocketGroup = new THREE.Group();

    // Body (slimmer and taller)
    const bodyGeometry = new THREE.CylinderGeometry(0.2, 0.25, 4, 32);
    const bodyMaterial = new THREE.MeshStandardMaterial({ color: 0x1a2a4f, metalness: 0.4, roughness: 0.3 });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    rocketGroup.add(body);

    // Nose cone (sharp and metallic)
    const coneGeometry = new THREE.ConeGeometry(0.25, 1.2, 32);
    const coneMaterial = new THREE.MeshStandardMaterial({ color: 0xff3b3b, metalness: 0.7, roughness: 0.2 });
    const cone = new THREE.Mesh(coneGeometry, coneMaterial);
    cone.position.y = 2.6;
    rocketGroup.add(cone);

    // Fins (angled and sleek)
    const finGeometry = new THREE.BoxGeometry(0.05, 0.6, 0.3);
    const finMaterial = new THREE.MeshStandardMaterial({ color: 0x999999 });
    for (let i = 0; i < 4; i++) {
      const fin = new THREE.Mesh(finGeometry, finMaterial);
      fin.position.set(Math.cos(i * Math.PI / 2) * 0.3, -1.8, Math.sin(i * Math.PI / 2) * 0.3);
      fin.rotation.y = i * Math.PI / 2;
      fin.rotation.z = Math.PI / 8;
      rocketGroup.add(fin);
    }

    // Nozzle (rear cylinder)
    const nozzleGeometry = new THREE.CylinderGeometry(0.1, 0.15, 0.3, 16);
    const nozzleMaterial = new THREE.MeshStandardMaterial({ color: 0x333333 });
    const nozzle = new THREE.Mesh(nozzleGeometry, nozzleMaterial);
    nozzle.position.y = -2.15;
    rocketGroup.add(nozzle);

    // Flame effect (particles)
    const flameGeometry = new THREE.BufferGeometry();
    const flameCount = 100;
    const flamePositions = new Float32Array(flameCount * 3);
    for (let i = 0; i < flameCount; i++) {
      flamePositions[i * 3 + 0] = (Math.random() - 0.5) * 0.3;
      flamePositions[i * 3 + 1] = -2.4 - Math.random() * 0.4;
      flamePositions[i * 3 + 2] = (Math.random() - 0.5) * 0.3;
    }
    flameGeometry.setAttribute('position', new THREE.BufferAttribute(flamePositions, 3));
    const flameMaterial = new THREE.PointsMaterial({
      color: 0xff6600,
      size: 0.1,
      transparent: true,
      opacity: 0.85
    });
    flameParticles = new THREE.Points(flameGeometry, flameMaterial);
    rocketGroup.add(flameParticles);

    scene.add(rocketGroup);

    // === ✨ Stars ===
    const starGeometry = new THREE.BufferGeometry();
    const starCount = 1000;
    const starVertices = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount; i++) {
      starVertices[i * 3 + 0] = (Math.random() - 0.5) * 200;
      starVertices[i * 3 + 1] = (Math.random() - 0.5) * 200;
      starVertices[i * 3 + 2] = -Math.random() * 200;
    }
    starGeometry.setAttribute('position', new THREE.BufferAttribute(starVertices, 3));
    const starMaterial = new THREE.PointsMaterial({ color: 0xffffff, size: 0.5 });
    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);

    // === 🔲 Grid ===
    const gridHelper = new THREE.GridHelper(20, 40, 0x00ffff, 0x003355);
    gridHelper.position.y = -2.2;
    scene.add(gridHelper);

    // === 💡 Lights ===
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(5, 10, 5);
    scene.add(light);

    const ambient = new THREE.AmbientLight(0x404040);
    scene.add(ambient);

    animate();
  }

  function animate() {
    requestAnimationFrame(animate);

    // Flicker flame particles slightly
    const positions = flameParticles.geometry.attributes.position.array;
    for (let i = 0; i < positions.length; i += 3) {
      positions[i + 1] += (Math.random() - 0.5) * 0.05;
      if (positions[i + 1] > -1.8) positions[i + 1] = -2.2 - Math.random() * 0.3;
    }
    flameParticles.geometry.attributes.position.needsUpdate = true;

    renderer.render(scene, camera);
  }

  function setRocketOrientation(pitch, roll, yaw) {
    if (!rocketGroup) return;
    rocketGroup.rotation.x = THREE.MathUtils.degToRad(pitch);
    rocketGroup.rotation.z = THREE.MathUtils.degToRad(roll);
    rocketGroup.rotation.y = THREE.MathUtils.degToRad(yaw);
  }

  // Data fetching and update
  async function fetchData() {
    try {
      const response = await fetch('/data');
      const data = await response.json();

      // Update displayed values
      document.getElementById("temperatureVal").textContent = `${data.temperature?.toFixed(1) ?? '30.6'} °C`;
      document.getElementById("pressureVal").textContent = `${data.pressure?.toFixed(2) ?? '1000.72'} kPa`;
      document.getElementById("altitudeVal").textContent = `${(data.gpsAlt ?? 0).toFixed(2)} m`;
      document.getElementById("currentAltitudeVal").textContent = `${(data.gpsAlt ?? 0).toFixed(2)} m`;
      document.getElementById("velocityVal").textContent = `${data.velocity?.toFixed(3) ?? '0.00'} m/s`;
      document.getElementById("latitudeVal").textContent = `${data.latitude?.toFixed(4) ?? '0.00000'}°`;
      document.getElementById("longitudeVal").textContent = `${data.longitude?.toFixed(4) ?? '0.00000'}°`;
      document.getElementById("headingVal").textContent = `${data.heading ?? '270'}°`;
      document.getElementById("distanceVal").textContent = `${data.distance?.toFixed(2) ?? '8946.51'} km`;
      document.getElementById("rollVal").textContent = `${data.roll?.toFixed(2) ?? '0.27'}°`;
      document.getElementById("pitchVal").textContent = `${data.pitch?.toFixed(2) ?? '-29.75'}°`;
      document.getElementById("yawVal").textContent = `${data.yaw?.toFixed(2) ?? '-3.22'}°`;

      // Update fin angle values
      document.getElementById("pitch1Val").textContent = `${data.pitch1?.toFixed(2) ?? '32.00'}°`;
      document.getElementById("pitch2Val").textContent = `${data.pitch2?.toFixed(2) ?? '32.00'}°`;
      document.getElementById("roll1Val").textContent = `${data.roll1?.toFixed(2) ?? '96.00'}°`;
      document.getElementById("roll2Val").textContent = `${data.roll2?.toFixed(2) ?? '96.00'}°`;

      // Update gyroscope and accelerometer values
      document.getElementById("x-val").textContent = `X: ${data.roll?.toFixed(2) ?? '0.00'}`;
      document.getElementById("y-val").textContent = `Y: ${data.pitch?.toFixed(2) ?? '0.00'}`;
      document.getElementById("z-val").textContent = `Z: ${data.yaw?.toFixed(2) ?? '0.00'}`;

      document.getElementById("x-value").textContent = `X: ${data.roll?.toFixed(2) ?? '0.00'}`;
      document.getElementById("y-value").textContent = `Y: ${data.pitch?.toFixed(2) ?? '0.00'}`;
      document.getElementById("z-value").textContent = `Z: ${data.yaw?.toFixed(2) ?? '0.00'}`;

      // Update charts
      updateChartData(altitudeChart, data.gpsAlt ?? 0);
      updateChartData(velocityChart, data.velocity ?? 0);
      updateChartData(temperatureChart, data.temperature ?? 30.6);
      updateChartData(pressureChart, data.pressure ?? 1000.72);
      updateChartData(pitch1Chart, data.pitch1 ?? 32);
      updateChartData(pitch2Chart, data.pitch2 ?? 32);
      updateChartData(roll1Chart, data.roll1 ?? 96);
      updateChartData(roll2Chart, data.roll2 ?? 96);

      // Update gyroscope chart
      gyroscopeChart.data.datasets[0].data.push(data.yaw ?? 0);
      gyroscopeChart.data.datasets[1].data.push(data.roll ?? 0);
      gyroscopeChart.data.datasets[2].data.push(data.pitch ?? 0);

      if (gyroscopeChart.data.datasets[0].data.length > maxPoints) {
        gyroscopeChart.data.datasets.forEach(dataset => dataset.data.shift());
      }
      gyroscopeChart.update();

      // Update accelerometer chart
      accelerometerChart.data.datasets[0].data.push(data.roll ?? 0);
      accelerometerChart.data.datasets[1].data.push(data.pitch ?? 0);
      accelerometerChart.data.datasets[2].data.push(data.yaw ?? 0);

      if (accelerometerChart.data.datasets[0].data.length > maxPoints) {
        accelerometerChart.data.datasets.forEach(dataset => dataset.data.shift());
      }
      accelerometerChart.update();

      // Update map position
      if (data.latitude && data.longitude) {
        const pos = [parseFloat(data.latitude), parseFloat(data.longitude)];
        marker.setLatLng(pos);
        map.panTo(pos);
      }

      // Update 3D rocket orientation
      setRocketOrientation(data.pitch ?? 0, data.roll ?? 0, data.yaw ?? 0);
    } catch (err) {
      console.error('Error fetching data:', err);
    }
  }

  // Initialize 3D scene
  window.addEventListener('load', () => {
    initScene();
    setInterval(fetchData, 300);
    fetchData();
  });

  window.addEventListener('resize', () => {
    if (!camera || !renderer) return;
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
  });
</script>
</body>
</html>
"""

if __name__ == '__main__':
    threading.Thread(target=read_serial, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False)