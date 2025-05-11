from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers.auth import login_router
from routers.controles import router as controles_router
from admin_panel.routes_admin import admin_router
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # cuidado si lo haces público
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejador global de excepciones
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Error interno del servidor", "error": str(exc)}
    )

# Incluir routers
app.include_router(login_router)
app.include_router(controles_router)
app.include_router(admin_router)

@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}