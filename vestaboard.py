"""Vestaboard API client. Sends character arrays and composes VBML."""

import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

API_URL = "https://rw.vestaboard.com/"
VBML_URL = "https://vbml.vestaboard.com/compose"
API_KEY = os.getenv("VESTABOARD_API_KEY")
TIMEOUT_SECONDS = 10


class VestaboardError(Exception):
    """Raised when the Vestaboard API returns a non-success response."""

    def __init__(self, message, status_code=None, body=None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


def send_characters(characters):
    """Send a 6x22 character array to the Vestaboard."""
    if not API_KEY:
        raise VestaboardError("VESTABOARD_API_KEY is not set")
    headers = {
        "X-Vestaboard-Read-Write-Key": API_KEY,
        "Content-Type": "application/json",
    }
    response = requests.post(
        API_URL,
        json={"characters": characters},
        headers=headers,
        timeout=TIMEOUT_SECONDS,
    )
    if not response.ok:
        raise VestaboardError(
            "send_characters failed",
            status_code=response.status_code,
            body=response.text,
        )
    return response.json() if response.content else None


def compose_vbml(template):
    """Render a VBML template into a 6x22 character array. No auth required."""
    payload = {
        "components": [
            {
                "style": {"justify": "center", "align": "center"},
                "template": template,
            }
        ]
    }
    response = requests.post(VBML_URL, json=payload, timeout=TIMEOUT_SECONDS)
    if not response.ok:
        raise VestaboardError(
            "compose_vbml failed",
            status_code=response.status_code,
            body=response.text,
        )
    data = response.json()
    # VBML responses have been observed in two shapes; accept either.
    if isinstance(data, dict) and "characters" in data:
        return data["characters"]
    return data
