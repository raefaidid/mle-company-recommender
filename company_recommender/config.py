"""Environment-backed settings shared by the worker and the panel."""

import os

POSTGRES_DSN = os.environ.get(
    "POSTGRES_DSN", "postgresql://postgres:postgres@localhost:5432/companies"
)
RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE = "company-events"
RETRY_DELAY_SECONDS = float(os.environ.get("RETRY_DELAY_SECONDS", "1"))
PANEL_HOST = os.environ.get("PANEL_HOST", "127.0.0.1")
PANEL_PORT = int(os.environ.get("PANEL_PORT", "8000"))
