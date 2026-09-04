import { useEffect, useState } from "react";

import {
  MapContainer,
  TileLayer,
  Polyline,
  CircleMarker,
  Popup,
  Polygon,
} from "react-leaflet";

import CycloneMarker from "../components/CycloneMarker";

import { getCurrentCyclone } from "../api";

function CycloneTracking() {
  const [cycloneData, setCycloneData] = useState(null);
  const [selectedPoint, setSelectedPoint] = useState(0);

  useEffect(() => {
    async function loadCyclone() {
      try {
        const data = await getCurrentCyclone();
        setCycloneData(data);
      } catch (error) {
        console.error("Failed to load cyclone:", error);
      }
    }

    loadCyclone();
  }, []);

  if (!cycloneData) {
    return (
      <div className="tracking-page">
        <div className="tracking-header">
          <div>
            <span className="tracking-label">
              CYCLONE TRACKING
            </span>

            <h1>
              Live Cyclone Forecast
            </h1>

            <p>
              Loading cyclone data...
            </p>
          </div>
        </div>
      </div>
    );
  }

  const forecastPoints =
    cycloneData.track?.forecast_points || [];

  const activePoint =
    forecastPoints[selectedPoint] ||
    forecastPoints[0];

  const trackPositions =
    cycloneData.track?.geojson?.coordinates?.map(
      ([longitude, latitude]) => [
        latitude,
        longitude,
      ]
    ) || [];

  const uncertaintyPositions =
    cycloneData.track?.uncertainty_cone?.coordinates?.[0]?.map(
      ([longitude, latitude]) => [
        latitude,
        longitude,
      ]
    ) || [];

  return (
    <div className="tracking-page">

      {/* PAGE HEADER */}

      <div className="tracking-header">

        <div>
          <span className="tracking-label">
            CYCLONE TRACKING
          </span>

          <h1>
            Live Cyclone Forecast
          </h1>

          <p>
            Monitor cyclone trajectory,
            forecast position and wind intensity.
          </p>
        </div>

        <div className="tracking-cyclone-badge">
          {cycloneData.cyclone_id}
        </div>

      </div>

      {/* SUMMARY CARDS */}

      <div className="tracking-summary">

        <div className="tracking-card">

          <span className="tracking-card-label">
            CATEGORY
          </span>

          <strong>
            {
              cycloneData.intensity
                ?.intensity_category
            }
          </strong>

        </div>

        <div className="tracking-card">

          <span className="tracking-card-label">
            WIND SPEED
          </span>

          <strong>
            {activePoint?.wind_speed}
            <small> km/h</small>
          </strong>

        </div>

        <div className="tracking-card">

          <span className="tracking-card-label">
            FORECAST
          </span>

          <strong>
            +{activePoint?.hour}
            <small> hrs</small>
          </strong>

        </div>

        <div className="tracking-card">

          <span className="tracking-card-label">
            CONFIDENCE
          </span>

          <strong>
            {(
              (cycloneData.intensity
                ?.confidence || 0) * 100
            ).toFixed(0)}
            %
          </strong>

        </div>

      </div>

      {/* MAP */}

      <section className="tracking-map-section">

        <MapContainer
          center={[
            cycloneData.center.latitude,
            cycloneData.center.longitude,
          ]}
          zoom={5}
          scrollWheelZoom={true}
          style={{
            height: "100%",
            width: "100%",
          }}
        >

          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Uncertainty Cone - shown when backend provides it */}

          {uncertaintyPositions.length > 0 && (
            <Polygon
              positions={uncertaintyPositions}
              pathOptions={{
                weight: 2,
                fillOpacity: 0.15,
              }}
            />
          )}

          {/* Forecast Track */}

          <Polyline
            positions={trackPositions}
            pathOptions={{
              weight: 4,
            }}
          />

          {/* Cyclone Marker */}

          <CycloneMarker
            point={activePoint}
            cycloneId={
              cycloneData.cyclone_id
            }
          />

          {/* Forecast Points */}

          {forecastPoints.map(
            (point, index) => (

              <CircleMarker
                key={point.hour}
                center={[
                  point.latitude,
                  point.longitude,
                ]}
                radius={
                  index === selectedPoint
                    ? 9
                    : 6
                }
                eventHandlers={{
                  click: () =>
                    setSelectedPoint(index),
                }}
              >

                <Popup>

                  <strong>
                    +{point.hour} hours
                  </strong>

                  <br />

                  Wind:{" "}
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

      {/* FORECAST TIMELINE */}

      <section className="tracking-timeline">

        <div className="tracking-timeline-header">

          <div>
            <h2>
              Forecast Progress
            </h2>

            <p>
              Move through predicted
              cyclone positions.
            </p>
          </div>

          <span>
            +{activePoint?.hour} hours
          </span>

        </div>

        <input
          type="range"
          min="0"
          max={
            Math.max(
              forecastPoints.length - 1,
              0
            )
          }
          value={selectedPoint}
          onChange={(event) =>
            setSelectedPoint(
              Number(event.target.value)
            )
          }
          className="forecast-slider"
        />

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

      {/* SELECTED FORECAST */}

      <section className="selected-forecast">

        <div>

          <span className="tracking-card-label">
            SELECTED FORECAST
          </span>

          <h2>
            +{activePoint?.hour} hours
          </h2>

        </div>

        <div className="forecast-details">

          <div>
            <span>
              Latitude
            </span>

            <strong>
              {activePoint?.latitude}° N
            </strong>
          </div>

          <div>
            <span>
              Longitude
            </span>

            <strong>
              {activePoint?.longitude}° E
            </strong>
          </div>

          <div>
            <span>
              Wind Speed
            </span>

            <strong>
              {activePoint?.wind_speed} km/h
            </strong>
          </div>

        </div>

      </section>

      {/* FORECAST TABLE */}

      <section className="forecast-table-section">

        <h2>
          Forecast Points
        </h2>

        <div className="forecast-table">

          <div className="forecast-table-row forecast-table-header">

            <span>
              Hour
            </span>

            <span>
              Latitude
            </span>

            <span>
              Longitude
            </span>

            <span>
              Wind Speed
            </span>

          </div>

          {forecastPoints.map(
            (point, index) => (

              <div
                key={point.hour}
                className={`forecast-table-row ${
                  index === selectedPoint
                    ? "forecast-row-active"
                    : ""
                }`}
                onClick={() =>
                  setSelectedPoint(index)
                }
              >

                <span>
                  +{point.hour}h
                </span>

                <span>
                  {point.latitude}°
                </span>

                <span>
                  {point.longitude}°
                </span>

                <span>
                  {point.wind_speed} km/h
                </span>

              </div>

            )
          )}

        </div>

      </section>

    </div>
  );
}

export default CycloneTracking;