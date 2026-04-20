"""Backend startup smoke tests."""

import time


def test_backend_startup_smoke():
    start = time.time()

    import app  # noqa: F401
    from app.database import init_db
    from app.main import app as fastapi_app

    init_db()

    elapsed = time.time() - start

    assert fastapi_app is not None
    assert fastapi_app.title == "Physician AI Assistant"
    assert elapsed < 30
