import { useState } from "react";

import "./App.css";

import Advisories from "./pages/Advisories";
import Analytics from "./pages/Analytics";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import StatCard from "./components/StatCard";
import MapSection from "./components/MapSection";
import CycloneInfo from "./components/CycloneInfo";
import AdvisoryPanel from "./components/AdvisoryPanel";

import CycloneTracking from "./pages/CycloneTracking";

import cycloneData from "./data/dummyData";


function App() {

  // ==============================
  // PAGE NAVIGATION
  // ==============================

  const [currentPage, setCurrentPage] =
    useState("dashboard");


  // ==============================
  // FORECAST STATE
  // ==============================

  const [selectedPoint, setSelectedPoint] =
    useState(0);

  const forecastPoints =
    cycloneData.track.forecast_points;

  const activePoint =
    forecastPoints[selectedPoint];


  return (

    <div className="app">

      {/* ================= NAVBAR ================= */}

      <Navbar />


      <div className="app-body">

        {/* ================= SIDEBAR ================= */}

        <Sidebar
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
        />


        {/* ================= MAIN CONTENT ================= */}

        <main className="main-content">


          {/* ================================================= */}
          {/* DASHBOARD */}
          {/* ================================================= */}

          {currentPage === "dashboard" && (

            <>

              {/* PAGE HEADER */}

              <div className="page-header">

                <div>

                  <h1>
                    Cyclone Monitoring Dashboard
                  </h1>

                  <p>
                    AI-powered tropical cyclone detection,
                    classification and prediction
                  </p>

                </div>

                <div className="cyclone-id">
                  {cycloneData.cyclone_id}
                </div>

              </div>


              {/* TOP STAT CARDS */}

              <div className="stats-grid">

                <StatCard
                  title="Wind Speed"
                  value={
                    activePoint.wind_speed
                  }
                  unit=" km/h"
                  subtitle={`Forecast at +${activePoint.hour} hours`}
                />


                <StatCard
                  title="Category"
                  value={
                    cycloneData.intensity
                      .intensity_category
                  }
                  subtitle="Current classification"
                />


                <StatCard
                  title="Detection Confidence"
                  value={
                    cycloneData
                      .detection_confidence * 100
                  }
                  unit="%"
                  subtitle="AI detection confidence"
                />


                <StatCard
                  title="Forecast"
                  value={
                    activePoint.hour
                  }
                  unit=" hrs"
                  subtitle="Selected forecast time"
                />

              </div>


              {/* MAP + TIMELINE */}

              <MapSection
                selectedPoint={selectedPoint}
                setSelectedPoint={
                  setSelectedPoint
                }
              />


              {/* CYCLONE INTELLIGENCE */}

              <CycloneInfo
                cyclone={cycloneData}
                activePoint={activePoint}
              />


              {/* AI ADVISORY */}

              <AdvisoryPanel
                advisory={
                  cycloneData.advisory
                }
              />

            </>

          )}


          {/* ================================================= */}
          {/* CYCLONE TRACKING */}
          {/* ================================================= */}

          {currentPage === "tracking" && (

            <CycloneTracking />

          )}


       

          {/* ================================================= */}
          {/* ADVISORIES - COMING NEXT */}
          {/* ================================================= */}
          {currentPage === "analytics" && (

  <Analytics />

)}
{currentPage === "advisories" && (

  <Advisories />

)}
        </main>

      </div>

    </div>

  );
}

export default App;

