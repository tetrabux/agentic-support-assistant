from fastapi import Header, HTTPException

API_KEYS = {
    "dev-key-alice": {"customer_id": 1, "name": "Alice Nguyen"},
    "dev-key-bob": {"customer_id": 2, "name": "Bob Smith"},
}


def get_identity(authorization: str = Header(...)) -> dict:
    if authorization not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return API_KEYS[authorization]

