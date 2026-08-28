from pathlib import Path

from private_quant_terminal.persistence import (
    Database,
    initialize_database,
)


def test_database_creates_parent_directory(tmp_path: Path) -> None:
    database_path = tmp_path / "nested" / "terminal.db"

    database = Database(database_path)

    with database.transaction() as connection:
        connection.execute(
            """
            CREATE TABLE example (
                id INTEGER PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        connection.execute(
            "INSERT INTO example (value) VALUES (?)",
            ("hello",),
        )

    assert database_path.exists()


def test_database_transaction_commits(tmp_path: Path) -> None:
    database = Database(tmp_path / "terminal.db")

    with database.transaction() as connection:
        connection.execute(
            """
            CREATE TABLE example (
                id INTEGER PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        connection.execute(
            "INSERT INTO example (value) VALUES (?)",
            ("committed",),
        )

    with database.connect() as connection:
        row = connection.execute(
            "SELECT value FROM example"
        ).fetchone()

    assert row["value"] == "committed"


def test_database_transaction_rolls_back(tmp_path: Path) -> None:
    database = Database(tmp_path / "terminal.db")

    with database.transaction() as connection:
        connection.execute(
            """
            CREATE TABLE example (
                id INTEGER PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

    try:
        with database.transaction() as connection:
            connection.execute(
                "INSERT INTO example (value) VALUES (?)",
                ("should-rollback",),
            )
            raise RuntimeError("force rollback")
    except RuntimeError:
        pass

    with database.connect() as connection:
        row = connection.execute(
            "SELECT COUNT(*) AS count FROM example"
        ).fetchone()

    assert row["count"] == 0


def test_initialize_database_records_schema_version(tmp_path: Path) -> None:
    database = Database(tmp_path / "terminal.db")

    initialize_database(database)

    with database.connect() as connection:
        row = connection.execute(
            """
            SELECT value
            FROM schema_metadata
            WHERE key = 'schema_version'
            """
        ).fetchone()

    assert row["value"] == "1"
