from dataclasses import dataclass
from datetime import datetime

import psycopg
from psycopg import sql

from intake import Company


@dataclass(frozen=True)
class Card:
    registration_number: str
    company_name: str | None
    industry: str | None
    state: str | None


@dataclass(frozen=True)
class StoredCompany:
    registration_number: str
    company_name: str | None
    industry: str | None
    state: str | None
    status: str
    source_updated_at: datetime
    created_at: datetime
    updated_at: datetime
    embedding: list[float] | None


class Catalogue:
    def __init__(self, dsn: str, schema: str = "public") -> None:
        if not schema.isidentifier():
            raise ValueError(schema)
        self._schema = schema
        self._conn = psycopg.connect(dsn, autocommit=True)
        self._ensure()

    def close(self) -> None:
        self._conn.close()

    def upsert(self, company: Company, vector: list[float] | None) -> None:
        self._conn.execute(
            sql.SQL(
                """
                INSERT INTO {}.companies (
                    registration_number, company_name, industry, state, status,
                    source_updated_at, embedding
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (registration_number) DO UPDATE SET
                    company_name = EXCLUDED.company_name,
                    industry = EXCLUDED.industry,
                    state = EXCLUDED.state,
                    status = EXCLUDED.status,
                    source_updated_at = EXCLUDED.source_updated_at,
                    updated_at = now(),
                    embedding = EXCLUDED.embedding
                WHERE EXCLUDED.source_updated_at > {}.companies.source_updated_at
                """
            ).format(sql.Identifier(self._schema), sql.Identifier(self._schema)),
            (
                company.registration_number,
                company.company_name,
                company.industry,
                company.state,
                company.status,
                company.source_updated_at,
                None if vector is None else _vector(vector),
            ),
        )

    def get(self, registration_number: str) -> StoredCompany | None:
        row = self._conn.execute(
            sql.SQL(
                """
                SELECT registration_number, company_name, industry, state, status,
                       source_updated_at, created_at, updated_at, embedding::text
                FROM {}.companies
                WHERE registration_number = %s
                """
            ).format(sql.Identifier(self._schema)),
            (registration_number,),
        ).fetchone()
        if row is None:
            return None
        return StoredCompany(
            registration_number=row[0],
            company_name=row[1],
            industry=row[2],
            state=row[3],
            status=row[4],
            source_updated_at=row[5],
            created_at=row[6],
            updated_at=row[7],
            embedding=_parse_vector(row[8]),
        )

    def similar(self, registration_number: str) -> list[Card]:
        rows = self._conn.execute(
            sql.SQL(
                """
                SELECT registration_number, company_name, industry, state
                FROM {}.companies
                WHERE registration_number <> %s
                  AND status = 'active'
                  AND embedding IS NOT NULL
                  AND (
                    SELECT embedding
                    FROM {}.companies
                    WHERE registration_number = %s
                  ) IS NOT NULL
                ORDER BY embedding <=> (
                    SELECT embedding
                    FROM {}.companies
                    WHERE registration_number = %s
                )
                LIMIT 4
                """
            ).format(
                sql.Identifier(self._schema),
                sql.Identifier(self._schema),
                sql.Identifier(self._schema),
            ),
            (registration_number, registration_number, registration_number),
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
                    status text NOT NULL,
                    source_updated_at timestamptz NOT NULL,
                    created_at timestamptz NOT NULL DEFAULT now(),
                    updated_at timestamptz NOT NULL DEFAULT now(),
                    embedding vector(384)
                )
                """
            ).format(sql.Identifier(self._schema))
        )


def _vector(vector: list[float]) -> str:
    return "[" + ",".join(str(value) for value in vector) + "]"


def _parse_vector(value: str | None) -> list[float] | None:
    if value is None:
        return None
    body = value.strip("[]")
    if not body:
        return []
    return [float(item) for item in body.split(",")]
