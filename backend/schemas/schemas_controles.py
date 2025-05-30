from pydantic import BaseModel, Field, condecimal, EmailStr
from typing import List, Literal, Optional, Annotated
from datetime import datetime
from decimal import Decimal


class DefectoMedido(BaseModel):
    """
    Información individual de un defecto medido en una imagen (tipo y área).
    """
    area: Annotated[Decimal, condecimal(gt=0, max_digits=6, decimal_places=2)]
    tipo_valor: Literal["min", "max"]
    tipo_defecto: str


class ImagenDefecto(BaseModel):
    """
    Imagen de inspección con clasificación OK/NOK y sus defectos detectados.
    """
    nombre_archivo: str
    fecha_captura: datetime
    max_dim_defecto_medido: Annotated[Decimal, condecimal(ge=0, max_digits=6, decimal_places=2)]
    min_dim_defecto_medido: Annotated[Decimal, condecimal(ge=0, max_digits=6, decimal_places=2)]
    clasificacion: Literal['ok', 'nok']
    defectos: List[DefectoMedido] = []


class RolloControladoInput(BaseModel):
    """
    Datos de un rollo analizado en una sesión de control de calidad.
    """
    ruta_local_rollo: str
    nombre_rollo: str
    num_defectos_rollo: int
    total_defectos_intolerables_rollo: int
    resultado_rollo: Literal['ok', 'nok']
    orden_analisis: int


class ControlCalidadInput(BaseModel):
    """
    Modelo completo de entrada para registrar un nuevo control de calidad.
    """
    id_usuario: int
    umbral_tamano_defecto: Annotated[Decimal, condecimal(gt=0, max_digits=5, decimal_places=2)]
    num_defectos_tolerables_por_tamano: int
    fecha_control: datetime
    rollo: RolloControladoInput
    imagenes: List[ImagenDefecto]

class InformeControlInput(BaseModel):
    """
    Datos requeridos para registrar un informe PDF asociado a un control.
    """
    id_control: int
    ruta_pdf: str
    generado_por: int
    fecha_generacion: datetime
    notas: Optional[str] = None


class ActualizarNotasInput(BaseModel):
    """
    Modelo para actualizar las notas de un informe existente.
    """
    id_control: int
    notas: str


class SolicitudCambioPassword(BaseModel):
    """
    Solicitud de cambio de contraseña con nuevo password y motivo.
    """
    email_usuario: EmailStr
    motivo: str = ""
    password_nueva: str
    timestamp: datetime
