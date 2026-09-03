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
async def test_generate_advisory_english(client):
    payload = {
        "cyclone_id": "CY001",
        "intensity_category": "Severe Cyclonic Storm",
        "wind_speed": 145.2,
        "location": {"latitude": 15.52, "longitude": 73.21},
        "language": "English",
    }
    resp = await client.post("/generate-alert", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["cyclone_id"] == "CY001"
    assert body["language"] == "English"
    assert body["severity"] in {"LOW", "MODERATE", "HIGH", "EXTREME"}
    assert isinstance(body["recommended_actions"], list)
    assert len(body["recommended_actions"]) >= 2


@pytest.mark.anyio
async def test_generate_advisory_hindi(client):
    payload = {
        "cyclone_id": "CY001",
        "intensity_category": "Severe Cyclonic Storm",
        "wind_speed": 145.2,
        "location": {"latitude": 15.52, "longitude": 73.21},
        "language": "Hindi",
    }
    resp = await client.post("/generate-alert", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["language"] == "Hindi"
    assert isinstance(body["message"], str)
    assert len(body["message"]) > 0


@pytest.mark.anyio
async def test_generate_advisory_unsupported_language(client):
    payload = {
        "cyclone_id": "CY001",
        "intensity_category": "Cyclonic Storm",
        "wind_speed": 80,
        "location": {"latitude": 15.52, "longitude": 73.21},
        "language": "Tamil",
    }
    resp = await client.post("/generate-alert", json=payload)
    assert resp.status_code == 400
    body = resp.json()
    assert body.get("code") == "UNSUPPORTED_LANGUAGE"


@pytest.mark.anyio
async def test_generate_advisory_missing_location(client):
    payload = {
        "cyclone_id": "CY001",
        "intensity_category": "Cyclonic Storm",
        "wind_speed": 80,
        "language": "English",
    }
    resp = await client.post("/generate-alert", json=payload)
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_alerts_evaluate_high(client):
    payload = {
        "cyclone_id": "CY001",
        "intensity_category": "Severe Cyclonic Storm",
        "wind_speed": 145.2,
        "confidence": 0.9,
    }
    resp = await client.post("/alerts/evaluate", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["alert_triggered"] is True
    assert body["severity"] in {"HIGH", "EXTREME"}
    assert "reason" in body
    assert "message" in body


@pytest.mark.anyio
async def test_alerts_evaluate_low(client):
    payload = {
        "cyclone_id": "CY002",
        "intensity_category": "Depression",
        "wind_speed": 35,
        "confidence": 0.6,
    }
    resp = await client.post("/alerts/evaluate", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["alert_triggered"] is True
    assert body["severity"] == "LOW"
