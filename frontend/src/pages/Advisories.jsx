import cycloneData from "../data/dummyData";

function Advisories() {
  const advisory = cycloneData.advisory;
  const intensity = cycloneData.intensity;

  return (
    <div className="advisories-page">

      {/* ================= HEADER ================= */}

      <div className="advisories-header">

        <div>
          <span className="advisories-label">
            DISASTER MANAGEMENT
          </span>

          <h1>
            AI Disaster Advisories
          </h1>

          <p>
            AI-generated safety guidance based on
            cyclone intensity and forecast conditions.
          </p>
        </div>

        <div className="advisory-cyclone-id">
          {cycloneData.cyclone_id}
        </div>

      </div>


      {/* ================= STATUS ================= */}

      <div className="advisory-status-card">

        <div className="advisory-status-left">

          <div className="advisory-warning-icon">
            ⚠
          </div>

          <div>
            <span className="advisories-label">
              CURRENT ALERT STATUS
            </span>

            <h2>
              {advisory.severity} RISK
            </h2>

            <p>
              Cyclone activity requires attention.
              Follow official disaster management
              instructions.
            </p>
          </div>

        </div>

        <div
          className={`large-severity-badge severity-${advisory.severity.toLowerCase()}`}
        >
          {advisory.severity}
        </div>

      </div>


      {/* ================= INFORMATION CARDS ================= */}

      <div className="advisory-info-grid">

        <div className="advisory-info-card">

          <span>
            CYCLONE
          </span>

          <strong>
            {cycloneData.cyclone_id}
          </strong>

        </div>


        <div className="advisory-info-card">

          <span>
            INTENSITY
          </span>

          <strong>
            {intensity.intensity_category}
          </strong>

        </div>


        <div className="advisory-info-card">

          <span>
            PREDICTED WIND
          </span>

          <strong>
            {intensity.predicted_wind_speed}
            <small> km/h</small>
          </strong>

        </div>


        <div className="advisory-info-card">

          <span>
            LANGUAGE
          </span>

          <strong>
            {advisory.language}
          </strong>

        </div>

      </div>


      {/* ================= MAIN ADVISORY ================= */}

      <section className="main-advisory-card">

        <div className="main-advisory-header">

          <div>
            <span className="advisories-label">
              ⚠ AI GENERATED ADVISORY
            </span>

            <h2>
              Safety Advisory
            </h2>
          </div>

          <span className="ai-status">
            ● AI GENERATED
          </span>

        </div>


        <div className="main-advisory-message">

          {advisory.advisory}

        </div>


        {/* ================= ACTIONS ================= */}

        <div className="advisory-actions">

          <h3>
            Recommended Actions
          </h3>

          <div className="action-grid">

            <div className="action-card">

              <div className="action-number">
                01
              </div>

              <div>
                <strong>
                  Follow Official Advisories
                </strong>

                <p>
                  Monitor instructions from official
                  disaster management authorities.
                </p>
              </div>

            </div>


            <div className="action-card">

              <div className="action-number">
                02
              </div>

              <div>
                <strong>
                  Prepare Emergency Supplies
                </strong>

                <p>
                  Keep essential medicines, food,
                  drinking water and emergency
                  supplies ready.
                </p>
              </div>

            </div>


            <div className="action-card">

              <div className="action-number">
                03
              </div>

              <div>
                <strong>
                  Avoid Coastal Risk Areas
                </strong>

                <p>
                  Stay away from coastal and
                  flood-prone areas when instructed.
                </p>
              </div>

            </div>


            <div className="action-card">

              <div className="action-number">
                04
              </div>

              <div>
                <strong>
                  Evacuate When Ordered
                </strong>

                <p>
                  Follow evacuation instructions from
                  local authorities immediately.
                </p>
              </div>

            </div>

          </div>

        </div>

      </section>


      {/* ================= PREPAREDNESS ================= */}

      <section className="preparedness-card">

        <div className="preparedness-header">

          <div>
            <span className="advisories-label">
              EMERGENCY PREPAREDNESS
            </span>

            <h2>
              Before the Cyclone
            </h2>
          </div>

          <span className="preparedness-icon">
            ✓
          </span>

        </div>


        <div className="preparedness-list">

          <div>
            <span>✓</span>
            Secure loose objects around your home.
          </div>

          <div>
            <span>✓</span>
            Charge phones, power banks and emergency
            equipment.
          </div>

          <div>
            <span>✓</span>
            Keep important documents protected.
          </div>

          <div>
            <span>✓</span>
            Know your nearest safe shelter or
            evacuation location.
          </div>

        </div>

      </section>


      {/* ================= FOOTER ================= */}

      <div className="advisory-disclaimer">

        <strong>
          Important:
        </strong>

        AI-generated information is intended to
        support situational awareness. Always follow
        official instructions from IMD, NDRF and
        local disaster management authorities.

      </div>

    </div>
  );
}

export default Advisories;