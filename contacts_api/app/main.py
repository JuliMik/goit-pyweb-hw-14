from . import models
from .database import engine
from .routes import contacts
from fastapi import FastAPI
from app.routes import auth
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import cloudinary

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

"""
    Creates all database tables based on SQLAlchemy models.

"""
models.Base.metadata.create_all(bind=engine)

"""
    Initializes the FastAPI application.

"""
app = FastAPI()

origins = [
    "http://localhost:3000"
]

"""
    Adds CORS middleware to allow specified origins.

"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """
    Returns a welcome message for the root endpoint.

    :return: dict: A welcome message.
    """
    return {"message": "Welcome to the contacts API, my homework!"}


"""

Includes routers for contacts and authentication.

"""
app.include_router(contacts.router)
app.include_router(auth.router)


@app.on_event("startup")
async def startup():
    """
    Initializes the Redis connection and FastAPILimiter on application startup.

    """
    redis_client = redis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    await FastAPILimiter.init(redis_client)


@app.on_event("shutdown")
async def shutdown():
    """
    Closes the Redis connection on application shutdown.

    """
    await FastAPILimiter.close()
