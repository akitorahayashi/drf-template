"""
Database connection tests.

Tests to verify PostgreSQL database connectivity and basic operations.
"""


def test_database_connection_exists(db_connection):
    """Test that we can connect to the PostgreSQL database."""
    assert db_connection is not None

    # Test basic query
    cursor = db_connection.cursor()
    cursor.execute("SELECT version()")
    version = cursor.fetchone()
    cursor.close()

    assert version is not None
    assert "PostgreSQL" in version[0]


def test_database_basic_operations(db_connection):
    """Test basic database operations (CREATE, INSERT, SELECT, DROP)."""
    cursor = db_connection.cursor()

    try:
        # Create a test table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Insert test data
        cursor.execute(
            "INSERT INTO test_table (name) VALUES (%s) RETURNING id", ("test_entry",)
        )
        inserted_id = cursor.fetchone()[0]

        # Query the data
        cursor.execute("SELECT name FROM test_table WHERE id = %s", (inserted_id,))
        result = cursor.fetchone()

        assert result is not None
        assert result[0] == "test_entry"

        # Clean up
        cursor.execute("DROP TABLE test_table")
        db_connection.commit()

    except Exception as e:
        db_connection.rollback()
        raise e
    finally:
        cursor.close()


def test_database_transaction_rollback(db_connection):
    """Test that database transactions can be rolled back properly."""
    cursor = db_connection.cursor()

    try:
        # Create test table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS test_rollback (
                id SERIAL PRIMARY KEY,
                value VARCHAR(50)
            )
        """
        )
        db_connection.commit()

        # Start a transaction that we'll rollback
        cursor.execute(
            "INSERT INTO test_rollback (value) VALUES (%s)", ("should_be_rolled_back",)
        )

        # Rollback the transaction
        db_connection.rollback()

        # Verify the data was not committed
        cursor.execute(
            "SELECT COUNT(*) FROM test_rollback WHERE value = %s",
            ("should_be_rolled_back",),
        )
        count = cursor.fetchone()[0]

        assert count == 0, "Transaction was not properly rolled back"

        # Clean up
        cursor.execute("DROP TABLE test_rollback")
        db_connection.commit()

    except Exception as e:
        db_connection.rollback()
        raise e
    finally:
        cursor.close()
