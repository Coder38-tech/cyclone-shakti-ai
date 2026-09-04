import { useEffect, useState } from "react";
import { getCurrentCyclone } from "../api";

function Analytics() {
  const [cycloneData, setCycloneData] = useState(null);

  useEffect(() => {
    async function loadCyclone() {
      try {
        const data = await getCurrentCyclone();
        setCycloneData(data);
      } catch (error) {
        console.error("Failed to load cyclone analytics:", error);
      }
    }

    loadCyclone();
  }, []);

  if (!cycloneData) {
    return (
      <div className="analytics-page">
        <div className="analytics-header">
          <div>
            <span className="analytics-label">
              CYCLONE ANALYTICS
            </span>

            <h1>
              Cyclone Intelligence
            </h1>

            <p>
              Loading cyclone analytics...
            </p>
          </div>
        </div>
      </div>
    );
  }

  const forecastPoints =
    cycloneData.track?.forecast_points || [];

  const windSpeeds = forecastPoints.map(
    (point) => point.wind_speed
  );

  const maxWind =
    windSpeeds.length > 0
      ? Math.max(...windSpeeds)
      : 0;

  const minWind =
    windSpeeds.length > 0
      ? Math.min(...windSpeeds)
      : 0;

  const averageWind =
    windSpeeds.length > 0
      ? windSpeeds.reduce(
          (sum, speed) => sum + speed,
          0
        ) / windSpeeds.length
      : 0;

  return (
    <div className="analytics-page">

      {/* ================= HEADER ================= */}

      <div className="analytics-header">

        <div>
          <span className="analytics-label">
            CYCLONE ANALYTICS
          </span>

          <h1>
            Cyclone Intelligence
          </h1>

          <p>
            Analyze cyclone intensity,
            forecast progression and
            predicted wind behaviour.
          </p>
        </div>

        <div className="analytics-cyclone-id">
          {cycloneData.cyclone_id}
        </div>

      </div>


      {/* ================= STATISTICS ================= */}

      <div className="analytics-stats">

        <div className="analytics-stat-card">

          <span>
            MAX WIND SPEED
          </span>

          <strong>
            {maxWind}
            <small> km/h</small>
          </strong>

        </div>


        <div className="analytics-stat-card">

          <span>
            AVERAGE WIND
          </span>

          <strong>
            {averageWind.toFixed(1)}
            <small> km/h</small>
          </strong>

        </div>


        <div className="analytics-stat-card">

          <span>
            FORECAST RANGE
          </span>

          <strong>
            {cycloneData.track?.forecast_hours || 0}
            <small> hrs</small>
          </strong>

        </div>


        <div className="analytics-stat-card">

          <span>
            AI CONFIDENCE
          </span>

          <strong>
            {(
              (cycloneData.intensity?.confidence || 0) *
              100
            ).toFixed(0)}
            <small>%</small>
          </strong>

        </div>

      </div>


      {/* ================= ANALYTICS GRID ================= */}

      <div className="analytics-grid">


        {/* ================= WIND CHART ================= */}

        <section className="analytics-panel">

          <div className="analytics-panel-header">

            <div>
              <h2>
                Wind Speed Forecast
              </h2>

              <p>
                Predicted wind speed over
                the forecast period.
              </p>
            </div>

            <span>
              km/h
            </span>

          </div>


          <div className="wind-chart">

            {forecastPoints.map(
              (point) => {

                const height =
                  ((point.wind_speed -
                    minWind) /
                    (maxWind -
                      minWind || 1)) *
                    180 +
                  40;

                return (

                  <div
                    className="wind-chart-column"
                    key={point.hour}
                  >

                    <div
                      className="wind-bar"
                      style={{
                        height: `${height}px`,
                      }}
                    >

                      <span>
                        {point.wind_speed}
                      </span>

                    </div>

                    <small>
                      +{point.hour}h
                    </small>

                  </div>

                );
              }
            )}

          </div>

        </section>


        {/* ================= INTENSITY ================= */}

        <section className="analytics-panel">

          <div className="analytics-panel-header">

            <div>
              <h2>
                Intensity Analysis
              </h2>

              <p>
                Current predicted cyclone
                classification.
              </p>
            </div>

          </div>


          <div className="intensity-content">

            <span className="analytics-label">
              CURRENT CATEGORY
            </span>

            <h2>
              {
                cycloneData.intensity
                  ?.intensity_category
              }
            </h2>


            <div className="intensity-value">

              <strong>
                {
                  cycloneData.intensity
                    ?.predicted_wind_speed
                }
              </strong>

              <span>
                km/h predicted wind
              </span>

            </div>


            <div className="confidence-progress">

              <div className="confidence-progress-header">

                <span>
                  Prediction Confidence
                </span>

                <strong>
                  {(
                    (cycloneData.intensity
                      ?.confidence || 0) *
                    100
                  ).toFixed(0)}
                  %
                </strong>

              </div>

              <div className="confidence-bar">

                <div
                  style={{
                    width: `${
                      (cycloneData.intensity
                        ?.confidence || 0) *
                      100
                    }%`,
                  }}
                />

              </div>

            </div>

          </div>

        </section>

      </div>


      {/* ================= FORECAST TABLE ================= */}

      <section className="analytics-table-panel">

        <div className="analytics-panel-header">

          <div>

            <h2>
              Forecast Analysis
            </h2>

            <p>
              Detailed forecast progression.
            </p>

          </div>

        </div>


        <div className="analytics-table">

          <div className="analytics-table-row analytics-table-header">

            <span>
              TIME
            </span>

            <span>
              LATITUDE
            </span>

            <span>
              LONGITUDE
            </span>

            <span>
              WIND SPEED
            </span>

            <span>
              CHANGE
            </span>

          </div>


          {forecastPoints.map(
            (point, index) => {

              const previousPoint =
                forecastPoints[index - 1];

              const change =
                previousPoint
                  ? point.wind_speed -
                    previousPoint.wind_speed
                  : 0;

              return (

                <div
                  className="analytics-table-row"
                  key={point.hour}
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
                    <strong>
                      {point.wind_speed}
                    </strong>{" "}
                    km/h
                  </span>

                  <span
                    className={
                      change > 0
                        ? "wind-increase"
                        : change < 0
                        ? "wind-decrease"
                        : ""
                    }
                  >
                    {change > 0
                      ? `+${change}`
                      : change}{" "}
                    km/h
                  </span>

                </div>

              );

            }
          )}

        </div>

      </section>

    </div>
  );
}

export default Analytics;