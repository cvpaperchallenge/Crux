import http
import pytest
import fastapi
from fastapi.testclient import TestClient

from src import routers

@pytest.fixture
def dummy_client():
    app = fastapi.FastAPI()
    app.include_router(routers.router)
    return TestClient(app)

def test_health_check(dummy_client):
    response = dummy_client.get("/health")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {"health": "ok"}