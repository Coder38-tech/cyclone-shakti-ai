import { useEffect, useState } from "react";

import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  Polyline,
  Polygon,
} from "react-leaflet";

import CycloneMarker from "./CycloneMarker";


function MapSection({
  cyclone,
  selectedPoint,
  setSelectedPoint,
}) {

  // ==============================
  // PLAY / PAUSE
  // ==============================

  const [isPlaying, setIsPlaying] =
    useState(false);


  // ==============================
  // FORECAST DATA
  // ==============================

  const forecastPoints =
    cyclone?.track?.forecast_points || [];

  const activePoint =
    forecastPoints[selectedPoint] ||
    forecastPoints[0];


  // ==============================
  // CURRENT CYCLONE LOCATION
  // ==============================

  const latitude =
    cyclone?.center?.latitude || 0;

  const longitude =
    cyclone?.center?.longitude || 0;


  // ==============================
  // CONVERT GEOJSON TRACK
  // ==============================

  const trackPositions =
    cyclone?.track?.geojson?.coordinates?.map(
      ([longitude, latitude]) => [
        latitude,
        longitude,
      ]
    ) || [];


  // ==============================
  // UNCERTAINTY CONE
  // ==============================

  const uncertaintyPositions =
    cyclone?.track?.uncertainty_cone?.coordinates?.[0]?.map(
      ([longitude, latitude]) => [
        latitude,
        longitude,
      ]
    ) || [];


  // ==============================
  // PLAY FORECAST
  // ==============================

  useEffect(() => {

    if (!isPlaying) {
      return;
    }

    const timer = setInterval(() => {

      setSelectedPoint((currentPoint) => {

        if (
          currentPoint >=
          forecastPoints.length - 1
        ) {

          setIsPlaying(false);

          return currentPoint;
        }

        return currentPoint + 1;

      });

    }, 2000);


    return () => clearInterval(timer);

  }, [
    isPlaying,
    forecastPoints.length,
    setSelectedPoint,
  ]);


  // ==============================
  // SLIDER
  // ==============================

  const handleSliderChange = (event) => {

    setIsPlaying(false);

    setSelectedPoint(
      Number(event.target.value)
    );

  };


  // ==============================
  // PLAY / PAUSE BUTTON
  // ==============================

  const handlePlayPause = () => {

    if (
      selectedPoint >=
      forecastPoints.length - 1
    ) {

      setSelectedPoint(0);

    }

    setIsPlaying(
      (playing) => !playing
    );

  };


  // ==============================
  // RENDER
  // ==============================

  return (

    <div className="map-container-wrapper">

      {/* ================= MAP ================= */}

      <section className="map-section">

        <MapContainer
          center={[
            latitude,
            longitude,
          ]}
          zoom={5}
          scrollWheelZoom={true}
          style={{
            height: "100%",
            width: "100%",
          }}
        >

          {/* MAP TILES */}

          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />


          {/* ================= UNCERTAINTY CONE ================= */}

          {uncertaintyPositions.length > 0 && (

            <Polygon
              positions={
                uncertaintyPositions
              }
              pathOptions={{
                weight: 2,
                fillOpacity: 0.15,
              }}
            />

          )}


          {/* ================= PREDICTED TRACK ================= */}

          {trackPositions.length > 0 && (

            <Polyline
              positions={trackPositions}
              pathOptions={{
                weight: 4,
              }}
            />

          )}


          {/* ================= ACTIVE CYCLONE ================= */}

          {activePoint && (

            <CycloneMarker
              point={activePoint}
              cycloneId={
                cyclone.cyclone_id
              }
            />

          )}


          {/* ================= FORECAST POINTS ================= */}

          {forecastPoints.map(
            (point) => (

              <CircleMarker
                key={point.hour}
                center={[
                  point.latitude,
                  point.longitude,
                ]}
                radius={6}
              >

                <Popup>

                  <strong>
                    Forecast: +
                    {point.hour} hours
                  </strong>

                  <br />

                  Wind Speed:{" "}
                  {point.wind_speed} km/h

                  <br />

                  Latitude:{" "}
                  {point.latitude}

                  <br />

                  Longitude:{" "}
                  {point.longitude}

                </Popup>

              </CircleMarker>

            )
          )}

        </MapContainer>

      </section>


      {/* ================= TIMELINE ================= */}

      <section
        className="forecast-timeline"
        onPointerDown={(event) =>
          event.stopPropagation()
        }
      >

        <div className="timeline-header">

          <div>

            <span className="timeline-title">
              Forecast Timeline
            </span>

            <span className="timeline-description">
              Predicted cyclone movement
            </span>

          </div>


          {activePoint && (

            <div className="timeline-current">
              +{activePoint.hour} hours
            </div>

          )}

        </div>


        {/* ================= PLAY BUTTON ================= */}

        <button
          className="play-button"
          onClick={handlePlayPause}
        >

          {isPlaying
            ? "⏸ Pause Forecast"
            : "▶ Play Forecast"}

        </button>


        {/* ================= SLIDER ================= */}

        {forecastPoints.length > 0 && (

          <input
            type="range"
            min="0"
            max={forecastPoints.length - 1}
            value={selectedPoint}
            onChange={handleSliderChange}
            onPointerDown={(event) =>
              event.stopPropagation()
            }
            onClick={(event) =>
              event.stopPropagation()
            }
            className="forecast-slider"
          />

        )}


        {/* ================= TIME LABELS ================= */}

        <div className="timeline-labels">

          {forecastPoints.map(
            (point) => (

              <span key={point.hour}>
                {point.hour}h
              </span>

            )
          )}

        </div>

      </section>

    </div>

  );

}

export default MapSection;