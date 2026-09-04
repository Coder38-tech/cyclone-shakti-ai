function StatCard({ title, value, unit, subtitle }) {
  return (
    <div className="stat-card">
      <div className="stat-title">{title}</div>

      <div className="stat-value">
        {value}
        {unit && <span>{unit}</span>}
      </div>

      <div className="stat-subtitle">
        {subtitle}
      </div>
    </div>
  );
}

export default StatCard;