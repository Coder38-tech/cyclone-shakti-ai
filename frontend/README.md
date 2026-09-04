# 🌪️ Cyclone Shakti AI — Frontend

### AI-Powered Cyclone Monitoring, GIS Visualization & Decision Support Dashboard

> A modern React + Leaflet frontend for visualizing cyclone movement, forecast tracks, uncertainty regions, intensity predictions, analytics, and disaster advisories.

---

## 🚀 Overview

**Cyclone Shakti AI** is an AI-powered cyclone monitoring and decision-support platform developed for disaster management and early-warning use cases.

The frontend provides an interactive **GIS-based command dashboard** that transforms cyclone prediction data into clear and actionable visual information.

It allows users to:

- 🗺️ Monitor the current cyclone position
- 🌪️ Visualize predicted cyclone movement
- 📍 Explore individual forecast positions
- 🌀 View the cyclone uncertainty region
- 📊 Analyze predicted wind speed and intensity
- 🚨 View cyclone severity and safety advisories
- ⏱️ Animate the predicted cyclone path over time
- 🎯 Monitor AI detection and prediction confidence

---

# ✨ Key Features

## 🗺️ Interactive Cyclone Tracking

The tracking interface provides a real-time-style GIS visualization of cyclone movement.

**Features include:**

- Interactive Leaflet map
- OpenStreetMap base layer
- Current cyclone center
- Custom animated cyclone-eye marker
- Predicted cyclone track
- Forecast position markers
- Clickable forecast points
- Forecast information popups
- Cyclone uncertainty cone
- Latitude / longitude visualization
- Interactive forecast timeline

---

## 📊 Analytics Dashboard

The Analytics section converts forecast data into an easy-to-understand analytical view.

### Displays:

- 🌬️ Maximum predicted wind speed
- 📈 Average forecast wind speed
- ⏱️ Forecast duration
- 🎯 AI prediction confidence
- 📊 Wind-speed forecast visualization
- 🌪️ Intensity classification
- 📉 Wind-speed change analysis
- 📋 Forecast analysis table

---

## 🚨 AI Advisory System

The advisory interface presents cyclone-related warnings and recommended actions.

### Includes:

- Current cyclone alert status
- Severity classification
- Cyclone information
- Detailed advisory message
- Recommended safety actions
- Disaster preparedness guidance
- Advisory disclaimer

The interface is designed to make technical prediction output easier to understand for decision-makers and users.

---

## 🎯 Command Dashboard

The main dashboard provides a consolidated operational view.

### Dashboard includes:

| Information | Visualization |
|---|---|
| Cyclone Location | Interactive GIS Map |
| Cyclone Track | Forecast Polyline |
| Current Position | Custom Cyclone Marker |
| Forecast Positions | Map Markers |
| Uncertainty | Uncertainty Cone |
| Wind Speed | Forecast Data |
| Detection Confidence | Intelligence Panel |
| Prediction Confidence | Intelligence Panel |
| Advisory | AI Advisory Panel |
| Forecast Time | Interactive Timeline |

---

# ⏱️ Forecast Timeline

The frontend includes an interactive forecast timeline.

Users can:

- Select individual forecast hours
- Move through predicted cyclone positions
- Play the forecast automatically
- Pause the forecast animation
- Observe synchronized map updates
- View corresponding wind-speed predictions

### Forecast flow

```text
Forecast Hour
      ↓
Selected Forecast Point
      ↓
Cyclone Position
      ↓
Wind Speed + Information
      ↓
Map + Intelligence Panel Update
