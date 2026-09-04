import os
import requests
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("COPERNICUS_USERNAME")
PASSWORD = os.getenv("COPERNICUS_PASSWORD")

TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"


def get_access_token():
    if not USERNAME or not PASSWORD:
        raise ValueError("Copernicus credentials are missing from .env")

    data = {
        "client_id": "cdse-public",
        "username": USERNAME,
        "password": PASSWORD,
        "grant_type": "password",
    }

    response = requests.post(TOKEN_URL, data=data)

    response.raise_for_status()

    return response.json()["access_token"]


if __name__ == "__main__":
    token = get_access_token()
    print("✅ Copernicus authentication successful!")
    print("Token received.")