🌪️ Cyclone Shakti AI — Frontend
AI-Powered Cyclone Monitoring & Decision Support Dashboard

The Cyclone Shakti AI Frontend is a React-based web dashboard designed for real-time cyclone monitoring, track visualization, intensity analysis, and disaster advisories.

It provides an interactive GIS interface that allows users to visualize cyclone movement, forecast tracks, uncertainty regions, wind-speed predictions, cyclone intelligence, and AI-generated advisories.

🚀 Features
🗺️ Interactive Cyclone Tracking
Interactive map powered by Leaflet and OpenStreetMap
Current cyclone center visualization
Custom animated cyclone-eye marker
Predicted cyclone track
Forecast position markers
Clickable forecast points
Forecast information popups
Cyclone uncertainty cone visualization
Latitude/longitude-based cyclone positioning
📊 Analytics Dashboard
Maximum predicted wind speed
Average forecast wind speed
Forecast duration
AI prediction confidence
Wind-speed forecast visualization
Intensity analysis
Confidence progress indicator
Forecast analysis table
Wind-speed change analysis
🚨 AI Advisory System
Current cyclone alert status
Cyclone severity classification
Cyclone information
Detailed advisory message
Recommended safety actions
Disaster preparedness information
Advisory disclaimer
🎯 Dashboard

The main dashboard provides a consolidated view of:

Current cyclone information
Cyclone location
Detection confidence
Intensity prediction
Track prediction
Forecast timeline
AI advisory
Interactive cyclone map
⏱️ Forecast Timeline
Forecast timeline slider
Select individual forecast hours
Play/Pause forecast animation
Automatically moves through forecast points
Synchronized map and cyclone information
🧭 Navigation

The application contains four main sections:

Dashboard
Cyclone Tracking
Analytics
Advisories

Navigation is implemented using React state-based page switching.

🛠️ Technology Stack
Technology	Purpose
React	Frontend UI
Vite	Development & build tool
JavaScript	Application logic
CSS	Styling & responsive layout
Leaflet	Interactive maps
React Leaflet	React integration for Leaflet
OpenStreetMap	Map tiles
Git & GitHub	Version control
📁 Project Structure
frontend/
│
├── public/
│
├── src/
│   │
│   ├── assets/
│   │   ├── hero.png
│   │   ├── react.svg
│   │   └── vite.svg
│   │
│   ├── components/
│   │   ├── AdvisoryPanel.jsx
│   │   ├── CycloneInfo.jsx
│   │   ├── CycloneMarker.jsx
│   │   ├── MapSection.jsx
│   │   ├── Navbar.jsx
│   │   └── Sidebar.jsx
│   │
│   ├── pages/
│   │   ├── Analytics.jsx
│   │   ├── Advisories.jsx
│   │   └── CycloneTracking.jsx
│   │
│   ├── App.css
│   ├── App.jsx
│   ├── dummyData.js
│   └── main.jsx
│
├── .gitignore
├── eslint.config.js
├── index.html
├── package.json
├── package-lock.json
├── README.md
└── vite.config.js
⚙️ Requirements

Before running the frontend, make sure you have:

Node.js installed
npm installed
Git installed if working with the team repository

Check your versions:

node --version
npm --version
📦 Installation

Clone the repository:

git clone https://github.com/Coder38-tech/cyclone-shakti-ai.git

Navigate to the frontend:

cd cyclone-shakti-ai/frontend

Install dependencies:

npm install
▶️ Running the Frontend

Start the development server:

npm run dev

Vite will provide a local development URL similar to:

http://localhost:5173

Open the URL in your browser.

🗺️ GIS Implementation

The frontend uses Leaflet + React Leaflet for cyclone visualization.

Cyclone coordinates are handled according to the GeoJSON convention:

GeoJSON:
[longitude, latitude]

while Leaflet expects:

[latitude, longitude]

Therefore, GeoJSON coordinates are converted before being rendered on the map.

Example:

const [longitude, latitude] = coordinate;

const position = [latitude, longitude];
🌪️ Cyclone Visualization

The application uses a custom cyclone marker to represent the cyclone eye.

The marker includes:

Cyclone eye
Animated ring
Custom Leaflet divIcon
Forecast information popup

Forecast points are displayed separately on the track and can be selected to update the forecast information.

📈 Forecast Visualization

The frontend supports forecast points containing information such as:

{
  "hour": 24,
  "latitude": 17.1,
  "longitude": 74.5,
  "wind_speed": 138
}

The selected forecast point updates:

Cyclone position
Forecast hour
Wind speed
Cyclone information
Map marker
