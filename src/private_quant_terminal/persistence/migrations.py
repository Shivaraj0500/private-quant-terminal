from private_quant_terminal.persistence.database import Database

SCHEMA_VERSION = 1


def initialize_database(database: Database) -> None:
    """Initialize the persistence schema and migration metadata."""

    with database.transaction() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            INSERT INTO schema_metadata (key, value)
            VALUES ('schema_version', ?)
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value
            """,
            (str(SCHEMA_VERSION),),
        )
