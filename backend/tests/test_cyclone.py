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
async def test_predict_detection_with_location(client):
    payload = {"latitude": 15.52, "longitude": 73.21, "timestamp": "2026-09-03T12:00:00"}
    resp = await client.post("/predict-detection", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "cyclone_detected" in body
    assert "confidence" in body
    assert 0 <= body["confidence"] <= 1


@pytest.mark.anyio
async def test_predict_detection_with_bad_coords(client):
    payload = {"latitude": 200.0, "longitude": 73.21}
    resp = await client.post("/predict-detection", json=payload)
    status = resp.status_code
    assert status in {400, 422, 503}


@pytest.mark.anyio
async def test_predict_intensity_success(client):
    payload = {
        "cyclone_id": "CYTEST",
        "latitude": 15.52,
        "longitude": 73.21,
        "current_wind_speed": 120,
        "pressure": 980,
        "temperature": 28.5,
        "humidity": 80,
    }
    resp = await client.post("/predict-intensity", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["cyclone_id"] == "CYTEST"
    assert "predicted_wind_speed" in body
    assert "intensity_category" in body
    assert 0 <= body["confidence"] <= 1


@pytest.mark.anyio
async def test_predict_track_success(client):
    payload = {
        "cyclone_id": "CYTEST",
        "current_position": {"latitude": 15.52, "longitude": 73.21},
        "current_wind_speed": 120,
        "forecast_hours": 48,
    }
    resp = await client.post("/predict-track", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["cyclone_id"] == "CYTEST"
    assert body["forecast_hours"] == 48
    assert isinstance(body["forecast_points"], list)
    assert len(body["forecast_points"]) >= 1
    geojson = body["geojson"]
    assert geojson["type"] == "LineString"
    assert len(geojson["coordinates"]) == len(body["forecast_points"])
    for pair in geojson["coordinates"]:
        assert len(pair) == 2


@pytest.mark.anyio
async def test_predict_track_missing_position(client):
    payload = {
        "cyclone_id": "CYTEST",
        "current_wind_speed": 120,
        "forecast_hours": 48,
    }
    resp = await client.post("/predict-track", json=payload)
    assert resp.status_code == 422
