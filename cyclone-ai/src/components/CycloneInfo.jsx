function CycloneInfo({
  cyclone,
  activePoint,
}) {

  const {
    cyclone_id,
    center,
    detection_confidence,
    intensity,
  } = cyclone;


  return (
    <section className="cyclone-info">

      {/* HEADER */}

      <div className="cyclone-info-header">

        <div>

          <span className="info-label">
            ACTIVE CYCLONE
          </span>

          <h2>
            {cyclone_id}
          </h2>

        </div>


        <div className="detected-status">
          ● DETECTED
        </div>

      </div>


      {/* CURRENT FORECAST STATE */}

      <div className="location-info">

        <span className="info-label">
          SELECTED FORECAST
        </span>

        <strong>
          +{activePoint.hour} hours
        </strong>

      </div>


      {/* INFORMATION GRID */}

      <div className="info-grid">

        {/* WIND */}

        <div className="info-item">

          <span className="info-label">
            WIND SPEED
          </span>

          <strong>
            {activePoint.wind_speed}
            <small> km/h</small>
          </strong>

        </div>


        {/* LOCATION */}

        <div className="info-item">

          <span className="info-label">
            LOCATION
          </span>

          <strong>
            {activePoint.latitude}° N
          </strong>

          <small>
            {activePoint.longitude}° E
          </small>

        </div>


        {/* DETECTION */}

        <div className="info-item">

          <span className="info-label">
            DETECTION CONFIDENCE
          </span>

          <strong>
            {(detection_confidence * 100).toFixed(0)}%
          </strong>

        </div>


        {/* PREDICTION */}

        <div className="info-item">

          <span className="info-label">
            PREDICTION CONFIDENCE
          </span>

          <strong>
            {(intensity.confidence * 100).toFixed(0)}%
          </strong>

        </div>

      </div>

    </section>
  );
}

export default CycloneInfo;