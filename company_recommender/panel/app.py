from fastapi import FastAPI

from company_recommender.storage.catalogue import Catalogue


def create_app(catalogue: Catalogue) -> FastAPI:
    app = FastAPI()

    @app.get("/companies/{registration_number}/similar")
    def similar(registration_number: str) -> dict:
        return {
            "companies": [
                {
                    "registrationNumber": card.registration_number,
                    "companyName": card.company_name,
                    "industry": card.industry,
                    "state": card.state,
                }
                for card in catalogue.similar(registration_number)
            ]
        }

    return app
