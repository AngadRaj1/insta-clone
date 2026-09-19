import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.domains.users.router import router as users_router # user_router
from app.domains.posts.router import router as posts_router # post_router
from app.domains.interactions.router import router as interactions_router
from fastapi.staticfiles import StaticFiles

# This context manager handles startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Instagram backend is starting up...")
    # We will eventually put database connection logic here
    yield
    print("Instagram backend is shutting down...")

# Initialize the FastAPI app
app = FastAPI(
    title="Instagram Clone API",
    description="A high-performance asynchronous backend for a social media app.",
    version="1.0.0",
    lifespan=lifespan
)


app = FastAPI(title="Instagram Clone", lifespan=lifespan)

os.makedirs("uploads", exist_ok=True)

app.mount("/static", StaticFiles(directory="uploads"), name="static")


app.include_router(users_router) # user the router here!
app.include_router(posts_router) # post the router here!
app.include_router(interactions_router) # like and comments router here!

# A simple health-check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "message": "The Instagram clone API is running!"}