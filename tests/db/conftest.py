"""
Configuration for database tests.

Database tests use testcontainers to provide isolated PostgreSQL instances.
"""

import os

import psycopg2
import pytest
from dotenv import load_dotenv
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container():
    """
    Provides a PostgreSQL container for database tests.
    """
    load_dotenv(".env", override=True)

    db_user = os.getenv("DB_USER", "django_user")
    db_password = os.getenv("DB_PASSWORD", "django_password")
    db_name = os.getenv("DB_NAME", "django_db_test")

    with PostgresContainer(
        "postgres:15-alpine", username=db_user, password=db_password, dbname=db_name
    ) as postgres:
        yield postgres


@pytest.fixture
def db_connection(postgres_container):
    """
    Provides a database connection for individual tests.
    """
    conn = psycopg2.connect(
        host=postgres_container.get_container_host_ip(),
        port=postgres_container.get_exposed_port(5432),
        user=postgres_container.username,
        password=postgres_container.password,
        database=postgres_container.dbname,
    )

    yield conn

    conn.close()
