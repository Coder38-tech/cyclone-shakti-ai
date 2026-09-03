import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert "message" in body
    assert "Cyclone Shakti AI Backend is running" in body["message"]


@pytest.mark.anyio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "online"
    assert body["service"] == "cyclone-shakti-ai-backend"
    assert "version" in body


@pytest.mark.anyio
async def test_cyclone_current_frontend_shape(client):
    resp = await client.get("/cyclone/current")
    assert resp.status_code == 200
    body = resp.json()

    for field in ["cyclone_id", "center", "detection_confidence", "intensity", "track", "advisory"]:
        assert field in body, f"Missing top-level frontend field: {field}"

    center = body["center"]
    assert "latitude" in center and "longitude" in center
    assert -90 <= center["latitude"] <= 90
    assert -180 <= center["longitude"] <= 180

    intensity = body["intensity"]
    for field in ["predicted_wind_speed", "intensity_category", "confidence"]:
        assert field in intensity
    assert 0 <= intensity["confidence"] <= 1

    track = body["track"]
    for field in ["forecast_hours", "forecast_points", "geojson"]:
        assert field in track
    assert isinstance(track["forecast_points"], list)
    for fp in track["forecast_points"]:
        for k in ["hour", "latitude", "longitude", "wind_speed"]:
            assert k in fp

    geojson = track["geojson"]
    assert geojson["type"] == "LineString"
    assert isinstance(geojson["coordinates"], list)
    for pair in geojson["coordinates"]:
        assert len(pair) == 2
        lon, lat = pair
        assert -180 <= lon <= 180
        assert -90 <= lat <= 90

    advisory = body["advisory"]
    for field in ["severity", "language", "message"]:
        assert field in advisory
    assert advisory["severity"] in {"LOW", "MODERATE", "HIGH", "EXTREME"}


@pytest.mark.anyio
async def test_invalid_coordinates_intensity(client):
    resp = await client.post(
        "/predict-intensity",
        json={
            "cyclone_id": "CYINVALID",
            "latitude": 95.0,
            "longitude": 73.21,
            "current_wind_speed": 120,
        },
    )
    assert resp.status_code in {400, 422}


@pytest.mark.anyio
async def test_missing_fields_intensity(client):
    resp = await client.post(
        "/predict-intensity",
        json={"cyclone_id": "CY001", "latitude": 15.52},
    )
    assert resp.status_code == 422
    body = resp.json()
    assert body.get("code") == "VALIDATION_ERROR" or "detail" in body or "error" in body
