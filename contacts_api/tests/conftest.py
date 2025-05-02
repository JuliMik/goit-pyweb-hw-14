import pytest
from fastapi.testclient import TestClient
from app.main import app  # або інший файл, де створюється FastAPI()

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
