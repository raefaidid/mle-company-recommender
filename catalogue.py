from dataclasses import dataclass

import psycopg
from psycopg import sql

from intake import Company


@dataclass(frozen=True)
class Card:
    registration_number: str
    company_name: str | None
    industry: str | None
    state: str | None


class Catalogue:
    def __init__(self, dsn: str, schema: str = "public") -> None:
        if not schema.isidentifier():
            raise ValueError(schema)
        self._schema = schema
        self._conn = psycopg.connect(dsn, autocommit=True)
        self._ensure()

    def close(self) -> None:
        self._conn.close()

    def upsert(self, company: Company, vector: list[float]) -> None:
        self._conn.execute(
            sql.SQL(
                """
                INSERT INTO {}.companies (
                    registration_number, company_name, industry, state, embedding
                )
                VALUES (%s, %s, %s, %s, %s)
                """
            ).format(sql.Identifier(self._schema)),
            (
                company.registration_number,
                company.company_name,
                company.industry,
                company.state,
                _vector(vector),
            ),
        )

    def similar(self, registration_number: str) -> list[Card]:
        rows = self._conn.execute(
            sql.SQL(
                """
                SELECT registration_number, company_name, industry, state
                FROM {}.companies
                WHERE registration_number <> %s
                ORDER BY embedding <=> (
                    SELECT embedding
                    FROM {}.companies
                    WHERE registration_number = %s
                )
                LIMIT 4
                """
            ).format(sql.Identifier(self._schema), sql.Identifier(self._schema)),
            (registration_number, registration_number),
        ).fetchall()
        return [Card(*row) for row in rows]

    def _ensure(self) -> None:
        self._conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        self._conn.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(self._schema)))
        self._conn.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS {}.companies (
                    registration_number text PRIMARY KEY,
                    company_name text,
                    industry text,
                    state text,
                    embedding vector(2) NOT NULL
                )
                """
            ).format(sql.Identifier(self._schema))
        )


def _vector(vector: list[float]) -> str:
    return "[" + ",".join(str(value) for value in vector) + "]"
