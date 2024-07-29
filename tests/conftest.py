import pytest
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from main import app
from app.db.base import Base
from app.db.session import engine

# Setup the test database session
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope='function')
def test_db():
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client
