import pytest


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("SIGNA_HOME", str(tmp_path))
    return tmp_path
