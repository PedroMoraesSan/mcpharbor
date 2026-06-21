import os

from shared.config import ensure_runtime_environment


def test_ensure_runtime_environment_preserves_existing_path(monkeypatch):
    monkeypatch.setenv("PATH", "/usr/bin:/bin")
    ensure_runtime_environment()
    assert "/usr/bin" in os.environ["PATH"].split(os.pathsep)


def test_ensure_runtime_environment_noop_on_non_darwin(monkeypatch):
    monkeypatch.setattr("shared.config.sys.platform", "linux")
    monkeypatch.setenv("PATH", "/custom/bin")
    ensure_runtime_environment()
    assert os.environ["PATH"] == "/custom/bin"
