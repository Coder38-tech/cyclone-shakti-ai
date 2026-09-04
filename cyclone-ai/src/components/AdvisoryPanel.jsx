function AdvisoryPanel({ advisory }) {
  return (
    <section className="advisory-panel">

      <div className="advisory-header">

        <div>
          <span className="advisory-label">
            ⚠ AI DISASTER ADVISORY
          </span>

          <h2>
            {advisory.cyclone_id}
          </h2>
        </div>

        <span
          className={`severity-badge severity-${advisory.severity.toLowerCase()}`}
        >
          {advisory.severity}
        </span>

      </div>


      <div className="advisory-message">
        {advisory.advisory}
      </div>


      <div className="advisory-footer">

        <span>
          Language: <strong>{advisory.language}</strong>
        </span>

        <span>
          ● AI Generated
        </span>

      </div>

    </section>
  );
}

export default AdvisoryPanel;