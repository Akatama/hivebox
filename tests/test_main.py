from app.main import app
from fastapi.testclient import TestClient
import toml

client = TestClient(app)
pyproject = toml.load("pyproject.toml")


def test_get_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": f"{pyproject['project']['version']}"}
