from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
import string
import random

app = FastAPI()

CHARACTERS = string.ascii_letters + string.digits  # a-z + A-Z + 0-9 (62 chars)

url_store: dict[str, str] = {}  # short_code -> original_url


def generate_short_code(length: int = 6) -> str:
    return "".join(random.choices(CHARACTERS, k=length))


class URLRequest(BaseModel):
    url: HttpUrl


@app.get("/")
def root():
    return {"message": "SnipURL is running"}


@app.post("/shorten")
def shorten_url(request: URLRequest):
    short_code = generate_short_code()

    while short_code in url_store:
        short_code = generate_short_code()

    url_store[short_code] = str(request.url)

    return {
        "short_code": short_code,
        "short_url": f"http://127.0.0.1:8000/{short_code}",
        "original_url": str(request.url),
    }


@app.get("/{short_code}")
def redirect_to_url(short_code: str):
    if short_code not in url_store:
        raise HTTPException(status_code=404, detail="Short URL not found")

    original_url = url_store[short_code]
    return RedirectResponse(url=original_url, status_code=307)
