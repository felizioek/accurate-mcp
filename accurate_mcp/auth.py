import hashlib
import hmac
import time
import os
import requests
from typing import Optional


def get_timestamp() -> str:
    return str(int(time.time() * 1000))


def generate_signature(api_secret: str, timestamp: str) -> str:
    message = timestamp.encode("utf-8")
    secret = api_secret.encode("utf-8")
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def get_auth_headers(api_secret: str, bearer_token: str) -> dict:
    timestamp = get_timestamp()
    signature = generate_signature(api_secret, timestamp)
    return {
        "Authorization": f"Bearer {bearer_token}",
        "X-Api-Timestamp": timestamp,
        "X-Api-Signature": signature,
        "Content-Type": "application/json",
    }


class AccurateClient:

    def __init__(self, api_secret: str, bearer_token: str, server_code: str):
        self.api_secret = api_secret
        self.bearer_token = bearer_token
        self.server_code = server_code
        self.base_url = f"https://{server_code}.accurate.id/accurate"

    @classmethod
    def from_env(cls) -> "AccurateClient":
        required = ["ACCURATE_API_SECRET", "ACCURATE_BEARER_TOKEN", "ACCURATE_SERVER_CODE"]
        missing = [k for k in required if not os.getenv(k)]
        if missing:
            raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")
        return cls(
            api_secret=os.environ["ACCURATE_API_SECRET"],
            bearer_token=os.environ["ACCURATE_BEARER_TOKEN"],
            server_code=os.environ["ACCURATE_SERVER_CODE"],
        )

    def _headers(self) -> dict:
        return get_auth_headers(self.api_secret, self.bearer_token)

    def get(self, path: str, params: Optional[dict] = None) -> dict:
        url = f"{self.base_url}{path}"
        resp = requests.get(url, headers=self._headers(), params=params or {}, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, payload: dict) -> dict:
        url = f"{self.base_url}{path}"
        resp = requests.post(url, headers=self._headers(), json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def delete(self, path: str, params: dict) -> dict:
        url = f"{self.base_url}{path}"
        resp = requests.delete(url, headers=self._headers(), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()