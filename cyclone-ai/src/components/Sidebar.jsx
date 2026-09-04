function Sidebar({ currentPage, setCurrentPage }) {
  return (
    <aside className="sidebar">

      <div className="sidebar-title">
        MONITORING
      </div>

      <nav className="sidebar-nav">

        <button
          className={`sidebar-item ${
            currentPage === "dashboard"
              ? "active"
              : ""
          }`}
          onClick={() =>
            setCurrentPage("dashboard")
          }
        >
          Dashboard
        </button>


        <button
          className={`sidebar-item ${
            currentPage === "tracking"
              ? "active"
              : ""
          }`}
          onClick={() =>
            setCurrentPage("tracking")
          }
        >
          Cyclone Tracking
        </button>


        <button
          className={`sidebar-item ${
            currentPage === "analytics"
              ? "active"
              : ""
          }`}
          onClick={() =>
            setCurrentPage("analytics")
          }
        >
          Analytics
        </button>


        <button
          className={`sidebar-item ${
            currentPage === "advisories"
              ? "active"
              : ""
          }`}
          onClick={() =>
            setCurrentPage("advisories")
          }
        >
          Advisories
        </button>

      </nav>

    </aside>
  );
}

export default Sidebar;