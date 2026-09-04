import { useEffect, useState } from "react";

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


function App() {

  // ==============================
  // PAGE NAVIGATION
  // ==============================

  const [currentPage, setCurrentPage] =
    useState("dashboard");


  // ==============================
  // CYCLONE DATA FROM BACKEND
  // ==============================

  const [cycloneData, setCycloneData] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState(null);


  // ==============================
  // FORECAST STATE
  // ==============================

  const [selectedPoint, setSelectedPoint] =
    useState(0);


  // ==============================
  // FETCH BACKEND DATA
  // ==============================

  useEffect(() => {

    const fetchCycloneData = async () => {

      try {

        setLoading(true);
        setError(null);

        const response = await fetch(
          "http://127.0.0.1:8000/cyclone/current"
        );

        if (!response.ok) {
          throw new Error(
            `Backend returned ${response.status}`
          );
        }

        const data = await response.json();

        setCycloneData(data);

      } catch (err) {

        console.error(
          "Failed to fetch cyclone data:",
          err
        );

        setError(
          "Unable to connect to Cyclone AI backend."
        );

      } finally {

        setLoading(false);

      }

    };


    fetchCycloneData();

  }, []);


  // ==============================
  // LOADING SCREEN
  // ==============================

  if (loading) {

    return (
      <div className="app">

        <Navbar />

        <main className="main-content">

          <div className="page-header">

            <div>

              <h1>
                Cyclone Monitoring Dashboard
              </h1>

              <p>
                Connecting to Cyclone AI backend...
              </p>

            </div>

          </div>

        </main>

      </div>
    );

  }


  // ==============================
  // ERROR SCREEN
  // ==============================

  if (error || !cycloneData) {

    return (
      <div className="app">

        <Navbar />

        <main className="main-content">

          <div className="page-header">

            <div>

              <h1>
                Cyclone Monitoring Dashboard
              </h1>

              <p>
                {error}
              </p>

              <p>
                Make sure the FastAPI backend is running on
                port 8000.
              </p>

            </div>

          </div>

        </main>

      </div>
    );

  }


  // ==============================
  // FORECAST DATA
  // ==============================

  const forecastPoints =
    cycloneData.track?.forecast_points || [];

  const activePoint =
    forecastPoints[selectedPoint] ||
    forecastPoints[0];


  // ==============================
  // MAIN UI
  // ==============================

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
                    activePoint?.wind_speed ?? 0
                  }
                  unit=" km/h"
                  subtitle={`Forecast at +${activePoint?.hour ?? 0} hours`}
                />


                <StatCard
                  title="Category"
                  value={
                    cycloneData.intensity
                      ?.intensity_category
                  }
                  subtitle="Current classification"
                />


                <StatCard
                  title="Detection Confidence"
                  value={
                    (
                      cycloneData
                        .detection_confidence * 100
                    ).toFixed(0)
                  }
                  unit="%"
                  subtitle="AI detection confidence"
                />


                <StatCard
                  title="Forecast"
                  value={
                    activePoint?.hour ?? 0
                  }
                  unit=" hrs"
                  subtitle="Selected forecast time"
                />

              </div>


              {/* MAP + TIMELINE */}

              <MapSection
                cyclone={cycloneData}
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
          {/* ANALYTICS */}
          {/* ================================================= */}

          {currentPage === "analytics" && (

            <Analytics />

          )}


          {/* ================================================= */}
          {/* ADVISORIES */}
          {/* ================================================= */}

          {currentPage === "advisories" && (

            <Advisories />

          )}

        </main>

      </div>

    </div>

  );

}

export default App;