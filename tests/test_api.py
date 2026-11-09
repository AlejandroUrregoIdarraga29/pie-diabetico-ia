from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_system_status():
    response = client.get("/api/v1/system/status")
    assert response.status_code == 200
    assert response.json()["system"] == "ONLINE"

def test_create_session():
    file_data = ("test.png", b"fake image bytes", "image/png")
    response = client.post(
        "/api/v1/sessions/",
        data={"patient_code": "PAC-12345"},
        files={"file": file_data}
    )
    assert response.status_code == 200
    assert response.json()["patient_code"] == "PAC-12345"
    assert "session_id" in response.json()