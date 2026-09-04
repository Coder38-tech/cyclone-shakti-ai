import { useEffect, useState } from "react";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  CircleMarker,
  Polygon,
} from "react-leaflet";

import cycloneData from "../data/dummyData";

import CycloneMarker from "./CycloneMarker";

function MapSection({ selectedPoint, setSelectedPoint }) {

  // Controls Play / Pause
  const [isPlaying, setIsPlaying] = useState(false);

  const { latitude, longitude } = cycloneData.center;

  const forecastPoints = cycloneData.track.forecast_points;

  // Currently selected forecast point
  const activePoint = forecastPoints[selectedPoint];


  // Convert GeoJSON:
  // [longitude, latitude]
  // to Leaflet:
  // [latitude, longitude]
  const trackPositions =
    cycloneData.track.geojson.coordinates.map(
      ([longitude, latitude]) => [
        latitude,
        longitude,
      ]
    );


  // Convert uncertainty cone coordinates
  const uncertaintyPositions =
    cycloneData.track.uncertainty_cone.coordinates[0].map(
      ([longitude, latitude]) => [
        latitude,
        longitude,
      ]
    );


  // PLAY FORECAST ANIMATION
  useEffect(() => {

    if (!isPlaying) {
      return;
    }

    const timer = setInterval(() => {

      setSelectedPoint((currentPoint) => {

        // Stop at final forecast point
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


    // Clean up timer
    return () => clearInterval(timer);

  }, [
    isPlaying,
    forecastPoints.length,
    setSelectedPoint,
  ]);


  // SLIDER
  const handleSliderChange = (event) => {

    // If user manually moves slider,
    // stop automatic playback
    setIsPlaying(false);

    setSelectedPoint(
      Number(event.target.value)
    );
  };


  // PLAY / PAUSE
  const handlePlayPause = () => {

    // If we are already at 48h,
    // restart from 0h
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


          {/* UNCERTAINTY CONE */}
          <Polygon
            positions={uncertaintyPositions}
            pathOptions={{
              weight: 2,
              fillOpacity: 0.15,
            }}
          />


          {/* PREDICTED TRACK */}
          <Polyline
            positions={trackPositions}
            pathOptions={{
              weight: 4,
            }}
          />


          {/* ACTIVE CYCLONE */}
          <CycloneMarker
            point={activePoint}
            cycloneId={
              cycloneData.cyclone_id
            }
          />


          {/* FORECAST POINTS */}
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

        {/* TIMELINE HEADER */}

        <div className="timeline-header">

          <div>

            <span className="timeline-title">
              Forecast Timeline
            </span>

            <span className="timeline-description">
              Predicted cyclone movement
            </span>

          </div>


          <div className="timeline-current">
            +{activePoint.hour} hours
          </div>

        </div>


        {/* PLAY BUTTON */}

        <button
          className="play-button"
          onClick={handlePlayPause}
        >

          {isPlaying
            ? "⏸ Pause Forecast"
            : "▶ Play Forecast"}

        </button>


        {/* SLIDER */}

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


        {/* TIME LABELS */}

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