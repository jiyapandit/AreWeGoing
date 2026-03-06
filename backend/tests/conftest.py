import importlib
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def client():
    test_db_path = Path("test_api.db")
    if test_db_path.exists():
        test_db_path.unlink()
    os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"

    db_session = importlib.import_module("db.session")
    db_session = importlib.reload(db_session)

    main = importlib.import_module("app.main")
    main = importlib.reload(main)

    deps = importlib.import_module("app.deps")
    deps = importlib.reload(deps)
    from db.base import Base
    from app.main import app

    Base.metadata.create_all(bind=db_session.engine)

    def override_get_db():
        db = Session(db_session.engine)
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[deps.get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    db_session.engine.dispose()
    if test_db_path.exists():
        test_db_path.unlink()
