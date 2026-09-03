import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.utils.geojson import forecast_points_to_geojson
from app.utils.validation import classify_intensity
from app.models.schemas import ForecastPoint


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def test_classify_intensity_ordering():
    categories = [classify_intensity(ws) for ws in [20, 55, 70, 100, 130, 180, 300]]
    # Ensure monotonic classification (lower wind -> lower or equal category rank)
    order = [
        "Depression",
        "Deep Depression",
        "Cyclonic Storm",
        "Severe Cyclonic Storm",
        "Very Severe Cyclonic Storm",
        "Extremely Severe Cyclonic Storm",
        "Super Cyclonic Storm",
    ]
    ranks = [order.index(c) for c in categories]
    assert ranks == sorted(ranks)


def test_forecast_points_to_geojson_order():
    pts = [
        ForecastPoint(hour=0, latitude=15.52, longitude=73.21, wind_speed=120),
        ForecastPoint(hour=12, latitude=16.2, longitude=73.8, wind_speed=128),
    ]
    geojson = forecast_points_to_geojson(pts)
    assert geojson.type == "LineString"
    assert len(geojson.coordinates) == 2
    lon0, lat0 = geojson.coordinates[0]
    assert abs(lon0 - 73.21) < 1e-6
    assert abs(lat0 - 15.52) < 1e-6


@pytest.mark.anyio
async def test_predict_detection_empty_validation(client):
    resp = await client.post("/predict-detection", json={})
    assert resp.status_code in {400, 503}


@pytest.mark.anyio
async def test_analytics_summary(client):
    resp = await client.get("/analytics/summary")
    assert resp.status_code == 200
    body = resp.json()
    for k in ["total_cyclones", "active_cyclones", "average_detection_confidence", "average_prediction_confidence"]:
        assert k in body
    assert 0 <= body["average_detection_confidence"] <= 1
    assert 0 <= body["average_prediction_confidence"] <= 1


@pytest.mark.anyio
async def test_analytics_cyclone_mock(client):
    resp = await client.get("/analytics/cyclone/CY001")
    assert resp.status_code == 200
    body = resp.json()
    assert body["cyclone_id"] == "CY001"
    assert body["data_source"] in {"database", "mock_demo"}
    assert isinstance(body["observations"], list)
    assert isinstance(body["predictions"], list)
