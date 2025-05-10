from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import login_router
from routers.controles import router as controles_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # cuidado si lo haces público
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login_router)
app.include_router(controles_router)