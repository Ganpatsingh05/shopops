import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models import Product  # noqa: F401

# Build a separate database URL for automated tests.
TEST_DATABASE_URL = make_url(settings.database_url).set(
    database="shopops_test"
)

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture
def client():
    # Create test tables if they do not exist.
    Base.metadata.create_all(bind=test_engine)

    # Start every test with an empty products table.
    with test_engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE products RESTART IDENTITY CASCADE")
        )

    def override_get_db():
        with TestingSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()

        # Clean up test data after each test.
        with test_engine.begin() as connection:
            connection.execute(
                text("TRUNCATE TABLE products RESTART IDENTITY CASCADE")
            )


@pytest.fixture(scope="session", autouse=True)
def close_test_engine():
    yield
    test_engine.dispose()