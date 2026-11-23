"""Serve the similar-companies panel over HTTP."""

import uvicorn

from company_recommender.config import PANEL_HOST, PANEL_PORT, POSTGRES_DSN
from company_recommender.panel.app import create_app
from company_recommender.storage.catalogue import Catalogue


def main() -> None:
    uvicorn.run(create_app(Catalogue(POSTGRES_DSN)), host=PANEL_HOST, port=PANEL_PORT)


if __name__ == "__main__":
    main()
