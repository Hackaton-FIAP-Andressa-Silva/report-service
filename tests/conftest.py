import pytest


@pytest.fixture(autouse=True)
def reset_env(monkeypatch):
    """Ensure tests run with predictable environment."""
    monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("MONGODB_DATABASE", "test_reports")
    monkeypatch.setenv("INTERNAL_SERVICE_TOKEN", "test-token")
