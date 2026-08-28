import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class Database:
    """Small SQLite infrastructure boundary for durable application state."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        """Open a configured SQLite connection."""

        connection = sqlite3.connect(
            self.path,
            detect_types=sqlite3.PARSE_DECLTYPES
            | sqlite3.PARSE_COLNAMES,
        )

        connection.row_factory = sqlite3.Row

        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA busy_timeout = 5000")

        return connection

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Open a transaction and commit or rollback atomically."""

        connection = self.connect()

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def execute(
        self,
        sql: str,
        parameters: tuple[object, ...] = (),
    ) -> None:
        """Execute one statement inside an atomic transaction."""

        with self.transaction() as connection:
            connection.execute(sql, parameters)
