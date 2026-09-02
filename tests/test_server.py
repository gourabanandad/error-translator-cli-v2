from fastapi.testclient import TestClient

from error_translator.api.server import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_translate_endpoint():
    response = client.post(
        "/translate",
        json={"traceback_setting": "NameError: name 'x' is not defined"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "translate_error" in data
    assert "x" in data["translate_error"]["explanation"]


def test_translate_batch_endpoint():
    response = client.post(
        "/translate/batch",
        json={"tracebacks": ["NameError: name 'x' is not defined"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "translations" in data
    assert len(data["translations"]) == 1


def test_translate_empty_input():
    response = client.post("/translate", json={"traceback_setting": ""})
    assert response.status_code == 200


def test_translate_batch_empty_list():
    """Edge case: batch endpoint with zero tracebacks should still succeed."""
    response = client.post("/translate/batch", json={"tracebacks": []})
    assert response.status_code == 200
    assert response.json()["translations"] == []


def test_translate_batch_multiple_tracebacks():
    """Edge case: batch endpoint should preserve order across multiple inputs."""
    response = client.post(
        "/translate/batch",
        json={
            "tracebacks": [
                "NameError: name 'x' is not defined",
                "TypeError: unsupported operand type(s)",
            ]
        },
    )
    assert response.status_code == 200
    assert len(response.json()["translations"]) == 2


def test_translate_missing_field_returns_422():
    """Edge case: FastAPI should reject requests missing the required field."""
    response = client.post("/translate", json={})
    assert response.status_code == 422
