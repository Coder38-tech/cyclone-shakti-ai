import { Marker, Popup } from "react-leaflet";
import L from "leaflet";

function CycloneMarker({ point, cycloneId }) {
  const cycloneIcon = L.divIcon({
    className: "cyclone-icon-wrapper",
    html: `
      <div class="cyclone-icon">
        <div class="cyclone-ring"></div>
        <div class="cyclone-eye">◉</div>
      </div>
    `,
    iconSize: [50, 50],
    iconAnchor: [25, 25],
    popupAnchor: [0, -25],
  });

  return (
    <Marker
      position={[point.latitude, point.longitude]}
      icon={cycloneIcon}
    >
      <Popup>
        <strong>{cycloneId}</strong>
        <br />
        Forecast: +{point.hour} hours
        <br />
        Wind Speed: {point.wind_speed} km/h
      </Popup>
    </Marker>
  );
}

export default CycloneMarker;