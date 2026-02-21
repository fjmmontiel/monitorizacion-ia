"""
Modelos adicionales para datos de clientes y gestores.

Define esquemas Pydantic para información básica de clientes y gestores,
incluyendo constantes y códigos de referencia utilizados en el sistema.
"""

from pydantic import BaseModel, Field
from sqlalchemy.ext.declarative import declarative_base
from typing import List

Base = declarative_base()

CODIGOS_PAIS_EJEMPLO = {
    "España": "011",
    "Afganistan": "660",
    "Albania": "070",
    "Alemania": "004",
    "Andorra": "043",
}
INDICADOR_CONSUMIDOR = "Indicador de consumidor. Siempre es S. No pedir al usuario"


class DatosCliente(BaseModel):
    """Clase para definir el modelos de datos de DatosCliente"""

    nif: str = Field(description="DNI del cliente")
    claper: str = Field(description="Código de cliente en los sistemas de Unicaja")
    fechaNacimiento: str = Field(descripcion="Fecha de nacimiento del cliente")
    nombreCompleto: str = Field(description="Nombre y apellidos del cliente")
    email: str = Field(description="Dirección de e-mail del cliente")
    telefono: str = Field(description="Número de teléfono del cliente")
    direccion: str = Field(description="Dirección postal completa del cliente")


class DatosGestor(BaseModel):
    """Clase para definir el modelos de datos de DatosGestor"""

    codigo: str = Field(description="Código de gestor en los sistemas de Unicaja")
    centro: str = Field(descripcion="Código del centro al que pertenece el gestor")


class SubirFichero(BaseModel):
    """Modelo de datos para definir la estructura del endpoint /subirFichero."""

    fichero: str = Field(None, description="Fichero")
    tipo_fichero: str = Field(None, description="Indicador del tipo de fichero")
    paginas: List[int] = Field(
        None,
        description="Páginas del fichero que se van a leer.",
    )
