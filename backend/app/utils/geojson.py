from typing import Iterable, List, Tuple

from app.core.exceptions import ValidationError
from app.models.schemas import ForecastPoint, GeoJSONLineString


LAT_MIN, LAT_MAX = -90.0, 90.0
LON_MIN, LON_MAX = -180.0, 180.0


def validate_coordinates(latitude: float, longitude: float) -> None:
    """Validate latitude/longitude against WGS-84 range.

    Raises ValidationError with a specific code if values are out of range.
    """
    errors: List[str] = []
    if not (LAT_MIN <= latitude <= LAT_MAX):
        errors.append(f"latitude={latitude} is out of range [{LAT_MIN}, {LAT_MAX}]")
    if not (LON_MIN <= longitude <= LON_MAX):
        errors.append(f"longitude={longitude} is out of range [{LON_MIN}, {LON_MAX}]")
    if errors:
        raise ValidationError(
            message="Invalid coordinates",
            code="INVALID_COORDINATES",
            details={"issues": errors},
        )


def validate_coordinate_pair(pair: Iterable[float]) -> None:
    """Validate a [lon, lat] GeoJSON-style pair or (lat, lon) iterable of length 2."""
    coords = list(pair)
    if len(coords) != 2:
        raise ValidationError(
            message="Coordinate pair must have exactly 2 values",
            code="INVALID_COORDINATES",
        )
    if isinstance(coords[0], (int, float)) and isinstance(coords[1], (int, float)):
        validate_coordinates(float(coords[1]), float(coords[0]))


def forecast_points_to_geojson(points: List[ForecastPoint]) -> GeoJSONLineString:
    """Convert forecast points to a GeoJSON LineString.

    IMPORTANT: GeoJSON LineString coordinates use [longitude, latitude] order.
    """
    coords: List[List[float]] = []
    for pt in points:
        validate_coordinates(pt.latitude, pt.longitude)
        coords.append([float(pt.longitude), float(pt.latitude)])
    return GeoJSONLineString(type="LineString", coordinates=coords)


def points_from_geojson_linestring(linestring: GeoJSONLineString) -> List[Tuple[float, float]]:
    """Return list of (latitude, longitude) tuples from a GeoJSON LineString."""
    result: List[Tuple[float, float]] = []
    for pair in linestring.coordinates:
        if len(pair) != 2:
            continue
        lon, lat = pair[0], pair[1]
        validate_coordinates(lat, lon)
        result.append((lat, lon))
    return result
