import pytest
from psycopg import connect

from company_recommender.storage.catalogue import Catalogue

DSN = "postgresql://postgres:postgres@localhost:5432/companies"


@pytest.fixture
def catalogue():
    schema = "test_catalogue"
    stored = Catalogue(DSN, schema=schema)
    yield stored
    stored.close()
    with connect(DSN, autocommit=True) as conn:
        conn.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
