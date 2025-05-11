from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de plantillas
ruta_templates = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=ruta_templates)

# Seguridad JWT
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "superclave")
ALGORITHM = "HS256"

admin_router = APIRouter()

def obtener_rol_desde_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    print("🪪 Token recibido:", credentials.credentials)
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        print("✅ Payload decodificado:", payload)
        rol = payload.get("rol")
        if rol != "administrador":
            raise HTTPException(status_code=403, detail="Acceso restringido a administradores")
        return rol
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


#@admin_router.get("/admin", response_class=HTMLResponse)
#def mostrar_panel_admin(request: Request, rol: str = Depends(obtener_rol_desde_token)):
#    return templates.TemplateResponse("dashboard.html", {"request": request})

@admin_router.get("/admin", response_class=HTMLResponse)
def mostrar_panel_admin(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
