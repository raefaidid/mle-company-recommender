"""Serve the similar-companies panel over HTTP."""

import os

import uvicorn

from catalogue import Catalogue
from panel import create_app

DEFAULT_DSN = "postgresql://postgres:postgres@localhost:5432/companies"


def main() -> None:
    dsn = os.environ.get("POSTGRES_DSN", DEFAULT_DSN)
    host = os.environ.get("PANEL_HOST", "127.0.0.1")
    port = int(os.environ.get("PANEL_PORT", "8000"))
    uvicorn.run(create_app(Catalogue(dsn)), host=host, port=port)


if __name__ == "__main__":
    main()
