"""Punto de entrada del backend ISLI.

Configura la aplicación FastAPI, gestiona middleware, excepciones globales y enrutado de endpoints.
"""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers.auth import login_router
from routers.controles import router as controles_router
from admin_panel.routes_admin import admin_router
import logging
from fastapi.staticfiles import StaticFiles

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejador global de excepciones
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Manejador global de excepciones no capturadas.

    Registra el error en el log y devuelve una respuesta genérica con código 500.
    """
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
    """
    Endpoint de prueba para comprobar que la API está en funcionamiento.
    """
    return {"message": "API funcionando correctamente"}


# Ruta absoluta a la carpeta "docs"
docs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
# Servir documentación HTML generada con pdoc
app.mount("/pdoc", StaticFiles(directory=docs_path, html=True), name="pdoc")

# Ruta absoluta a la carpeta "assets"
assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
# Servir manual PDF u otros recursos
app.mount("/assets", StaticFiles(directory=assets_path, html=True), name="assets")
