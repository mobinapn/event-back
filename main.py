import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routers import auth
from backend.routers import home
from backend.routers import profile
from backend.routers import event

app = FastAPI(debug=True)

origins = [
    "http://localhost:9000",
    "https://event-front-tq88-pteq931x4-mobinapns-projects.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(home.router, prefix="/home")
app.include_router(profile.router, prefix="/profile")
app.include_router(event.router, prefix="/events")

# app.mount("/media", StaticFiles(directory="backend/media"), name="media")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
