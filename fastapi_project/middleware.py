from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging

app = FastAPI(title='My First FastAPI Project')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"]
)

logging.basicConfig(level=logging.INFO)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """ Middleware to log request details """
    logger = logging.getLogger("uvicorn")
    logger.info(f"Request: {request.method} {request.url}")

    response = await call_next(request)

    logger.info(f"Response: {response.status_code}")
    return response
