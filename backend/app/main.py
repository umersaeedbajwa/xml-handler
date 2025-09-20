from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.routers.auth_routes import router as api_router
from app.routers.freeswitch_routes import router as freeswitch_router
from app.database import baseDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await baseDB.connect()
    
    
    # Shutdown
    await baseDB.disconnect()
    
app = FastAPI(lifespan=lifespan,title="XML Handler API",dependencies=[], description="API for managing XML data", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the API routers
app.include_router(api_router)
app.include_router(freeswitch_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the XML Handler API!"}
