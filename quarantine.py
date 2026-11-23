from dataclasses import dataclass

import psycopg
from psycopg import sql


@dataclass(frozen=True)
class Quarantined:
    raw: bytes
    reason: str


class Quarantine:
    def __init__(self, dsn: str, schema: str = "public") -> None:
        if not schema.isidentifier():
            raise ValueError(schema)
        self._schema = schema
        self._conn = psycopg.connect(dsn, autocommit=True)
        self._ensure()

    def close(self) -> None:
        self._conn.close()

    def add(self, raw: bytes, reason: str) -> None:
        self._conn.execute(
            sql.SQL(
                """
                INSERT INTO {}.quarantined_messages (raw, reason)
                VALUES (%s, %s)
                """
            ).format(sql.Identifier(self._schema)),
            (raw, reason),
        )

    def matching(self, raw: bytes) -> list[Quarantined]:
        rows = self._conn.execute(
            sql.SQL(
                """
                SELECT raw, reason
                FROM {}.quarantined_messages
                WHERE raw = %s
                ORDER BY id
                """
            ).format(sql.Identifier(self._schema)),
            (raw,),
        ).fetchall()
        return [Quarantined(*row) for row in rows]

    def _ensure(self) -> None:
        self._conn.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS {}.quarantined_messages (
                    id bigserial PRIMARY KEY,
                    raw bytea NOT NULL,
                    reason text NOT NULL,
                    quarantined_at timestamptz NOT NULL DEFAULT now()
                )
                """
            ).format(sql.Identifier(self._schema))
        )
