import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app
from database.deps import get_db
# This requires tests/db/conftest.py to be active, so we import the fixture or let pytest discover it.
# Assuming pytest discovers fixtures from tests/db/conftest.py because of pytest.ini or similar,
# or we can explicitly import it if it fails, but pytest usually finds them if they are in a conftest.

@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_create_and_get_camera(client: AsyncClient):
    payload = {
        "name": "API Cam",
        "location": "Main St",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "status": "active",
        "num_lanes": 4
    }
    response = await client.post("/api/v1/cameras/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "API Cam"
    assert "id" in data
    
    camera_id = data["id"]
    get_resp = await client.get(f"/api/v1/cameras/{camera_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "API Cam"

@pytest.mark.asyncio
async def test_traffic_api(client: AsyncClient):
    cam_resp = await client.post("/api/v1/cameras/", json={
        "name": "Traffic Cam", "location": "Test", "latitude": 0, "longitude": 0
    })
    cam_id = cam_resp.json()["id"]

    traffic_payload = [
        {
            "camera_id": cam_id,
            "direction": "north",
            "lane_number": 1,
            "speed_kmh": 45.5
        }
    ]
    bulk_resp = await client.post("/api/v1/traffic/bulk", json=traffic_payload)
    assert bulk_resp.status_code == 201
    assert bulk_resp.json()["inserted"] == 1

    recent_resp = await client.get(f"/api/v1/traffic/{cam_id}/recent")
    assert recent_resp.status_code == 200
    assert len(recent_resp.json()) == 1

@pytest.mark.asyncio
async def test_signals_api(client: AsyncClient):
    cam_resp = await client.post("/api/v1/cameras/", json={
        "name": "Signal Cam", "location": "Test", "latitude": 0, "longitude": 0
    })
    cam_id = cam_resp.json()["id"]

    sig_payload = {
        "camera_id": cam_id,
        "phase": "red",
        "duration_seconds": 30.0,
        "triggered_by": "fixed"
    }
    create_resp = await client.post("/api/v1/signals/", json=sig_payload)
    assert create_resp.status_code == 201

    last_resp = await client.get(f"/api/v1/signals/{cam_id}/last")
    assert last_resp.status_code == 200
    assert last_resp.json()["phase"] == "red"

@pytest.mark.asyncio
async def test_emergencies_api(client: AsyncClient):
    cam_resp = await client.post("/api/v1/cameras/", json={
        "name": "Emergency Cam", "location": "Test", "latitude": 0, "longitude": 0
    })
    cam_id = cam_resp.json()["id"]

    em_payload = {
        "camera_id": cam_id,
        "emergency_type": "ambulance",
        "priority": 1,
        "timestamp": "2026-07-14T10:00:00Z"
    }
    create_resp = await client.post("/api/v1/emergencies/", json=em_payload)
    assert create_resp.status_code == 201
    em_id = create_resp.json()["id"]

    active_resp = await client.get("/api/v1/emergencies/active")
    assert active_resp.status_code == 200
    assert len(active_resp.json()) >= 1

    resolve_resp = await client.post(f"/api/v1/emergencies/{em_id}/resolve")
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "resolved"

@pytest.mark.asyncio
async def test_plates_api(client: AsyncClient):
    plate_payload = {
        "plate_text": "MH-12-3456",
        "plate_text_normalized": "MH123456",
        "confidence": 0.95
    }
    create_resp = await client.post("/api/v1/plates/", json=plate_payload)
    assert create_resp.status_code == 201

    search_resp = await client.get("/api/v1/plates/search/MH-12-3456")
    assert search_resp.status_code == 200
    assert len(search_resp.json()) >= 1

@pytest.mark.asyncio
async def test_camera_crud_extra(client: AsyncClient):
    cam_resp = await client.post("/api/v1/cameras/", json={
        "name": "CRUD Cam", "location": "Test", "latitude": 0, "longitude": 0, "status": "active"
    })
    cam_id = cam_resp.json()["id"]

    # List cameras
    list_resp = await client.get("/api/v1/cameras/")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # Active cameras
    active_resp = await client.get("/api/v1/cameras/active")
    assert active_resp.status_code == 200

    # Update camera
    patch_resp = await client.patch(f"/api/v1/cameras/{cam_id}", json={"name": "Updated Cam"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["name"] == "Updated Cam"

    # Delete camera
    del_resp = await client.delete(f"/api/v1/cameras/{cam_id}")
    assert del_resp.status_code == 204

    # Get non-existent
    get_fail = await client.get(f"/api/v1/cameras/{cam_id}")
    assert get_fail.status_code == 404

@pytest.mark.asyncio
async def test_traffic_density(client: AsyncClient):
    cam_resp = await client.post("/api/v1/cameras/", json={
        "name": "Density Cam", "location": "Test", "latitude": 0, "longitude": 0
    })
    cam_id = cam_resp.json()["id"]
    density_resp = await client.get(f"/api/v1/traffic/{cam_id}/density?start=2026-07-14T00:00:00Z&end=2026-07-14T23:59:59Z")
    assert density_resp.status_code == 200
    assert "count" in density_resp.json()

@pytest.mark.asyncio
async def test_signals_history(client: AsyncClient):
    cam_resp = await client.post("/api/v1/cameras/", json={
        "name": "History Cam", "location": "Test", "latitude": 0, "longitude": 0
    })
    cam_id = cam_resp.json()["id"]
    hist_resp = await client.get(f"/api/v1/signals/{cam_id}/history")
    assert hist_resp.status_code == 200
    em_resp = await client.get(f"/api/v1/signals/{cam_id}/emergencies")
    assert em_resp.status_code == 200

@pytest.mark.asyncio
async def test_emergencies_extra(client: AsyncClient):
    cam_resp = await client.post("/api/v1/cameras/", json={
        "name": "Em Extra Cam", "location": "Test", "latitude": 0, "longitude": 0
    })
    cam_id = cam_resp.json()["id"]
    em_resp = await client.post("/api/v1/emergencies/", json={
        "camera_id": cam_id, "emergency_type": "fire_truck", "priority": 5, "timestamp": "2026-07-14T10:00:00Z"
    })
    em_id = em_resp.json()["id"]
    patch_resp = await client.patch(f"/api/v1/emergencies/{em_id}", json={"notes": "Fire resolved"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["notes"] == "Fire resolved"

@pytest.mark.asyncio
async def test_plates_extra(client: AsyncClient):
    cam_resp = await client.post("/api/v1/cameras/", json={
        "name": "Plate Cam", "location": "Test", "latitude": 0, "longitude": 0
    })
    cam_id = cam_resp.json()["id"]
    recent_resp = await client.get(f"/api/v1/plates/{cam_id}/recent")
    assert recent_resp.status_code == 200
    hc_resp = await client.get("/api/v1/plates/high-confidence?min_confidence=0.9")
    assert hc_resp.status_code == 200

@pytest.mark.asyncio
async def test_analytics_api(client: AsyncClient):
    cam_resp = await client.post("/api/v1/cameras/", json={
        "name": "Analytics Cam", "location": "Test", "latitude": 0, "longitude": 0
    })
    cam_id = cam_resp.json()["id"]
    trend_resp = await client.get(f"/api/v1/analytics/{cam_id}/trend?hours=24")
    assert trend_resp.status_code == 200
    latest_resp = await client.get(f"/api/v1/analytics/{cam_id}/latest")
    assert latest_resp.status_code == 404
