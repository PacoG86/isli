from pydantic import BaseModel, Field, condecimal, EmailStr
from typing import List, Literal, Optional, Annotated
from datetime import datetime
from decimal import Decimal


class DefectoMedido(BaseModel):
    area: Annotated[Decimal, condecimal(gt=0, max_digits=6, decimal_places=2)]
    clasificacion: Literal['ok', 'nok']


class ImagenDefecto(BaseModel):
    nombre_archivo: str
    fecha_captura: datetime
    max_dim_defecto_medido: Annotated[Decimal, condecimal(gt=0, max_digits=6, decimal_places=2)]
    clasificacion: Literal['ok', 'nok']
    defectos: Optional[List[DefectoMedido]] = []


class RolloControladoInput(BaseModel):
    ruta_local_rollo: str
    nombre_rollo: str
    num_defectos_rollo: int
    total_defectos_intolerables_rollo: int
    resultado_rollo: Literal['ok', 'nok']
    orden_analisis: int


class ControlCalidadInput(BaseModel):
    id_usuario: int
    umbral_tamano_defecto: Annotated[Decimal, condecimal(gt=0, max_digits=5, decimal_places=2)]
    num_defectos_tolerables_por_tamano: int
    fecha_control: datetime
    rollo: RolloControladoInput
    imagenes: List[ImagenDefecto]

class InformeControlInput(BaseModel):
    id_control: int
    ruta_pdf: str
    generado_por: int
    fecha_generacion: datetime
    notas: Optional[str] = None


class ActualizarNotasInput(BaseModel):
    id_control: int
    notas: str

class SolicitudCambioPassword(BaseModel):
    email_usuario: EmailStr
    motivo: str = ""
    timestamp: datetime