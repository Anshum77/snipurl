import os
import importlib
from pathlib import Path
import tempfile

import pytest


@pytest.fixture(scope="session")
def test_db_path() -> Path:
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test.db"


@pytest.fixture(scope="session", autouse=True)
def _configure_test_env(test_db_path: Path):
    os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{test_db_path.as_posix()}"
    os.environ["APP_BASE_URL"] = "http://testserver"
    os.environ["REDIS_URL"] = "redis://invalid"  # force Redis init failure (best-effort)
    os.environ["GEOIP_DB_PATH"] = ""  # no GeoIP DB in unit tests

    import app.config as config_module
    importlib.reload(config_module)

    import app.database as database_module
    importlib.reload(database_module)

    import app.models  # noqa: F401 - register models with SQLAlchemy metadata
    database_module.Base.metadata.create_all(bind=database_module.engine)

    yield

    try:
        database_module.engine.dispose()
    except Exception:
        pass


@pytest.fixture(scope="session")
def app(_configure_test_env):
    from app.database import Base, engine as test_engine, SessionLocal
    from app.dependencies import get_db
    from app.main import create_app

    application = create_app(engine=test_engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    application.dependency_overrides[get_db] = override_get_db

    yield application


@pytest.fixture()
def client(app):
    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def db_session():
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _clean_db(db_session):
    from app.models import ClickEvent, URL

    db_session.query(ClickEvent).delete()
    db_session.query(URL).delete()
    db_session.commit()
