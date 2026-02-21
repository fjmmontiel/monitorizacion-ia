"""
Modelos Pydantic para peticiones API del sistema de hipotecas.

Define los esquemas de validación y serialización para las diferentes
operaciones del API: recomendaciones, muestras de interés, consentimientos
y logging operacional.
"""

from pydantic import BaseModel  # type: ignore
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from app.models.models import (
    DatosIntervSimple,
    DatosOperacionSimple,
    DatosPreEvalSimple,
    TL,
)

Base = declarative_base()


class ParametrosMuestraDeInteres(BaseModel):
    """
    Clase para el modelo de datos de ParametrosMuestraDeInteres
    """

    usuario_ha_validado_la_informacion: Optional[bool] = Field(
        None,
        description="""Indicar en este campo si el usuario ha confirmado todos los datos que se van a guardar""",
    )
    centro: Optional[str] = Field(
        None,
        description=""" Es el código de centro desde el que trabaja el empleado. 
                        Es el primer dato que se debe solicitar al usuario.""",
    )
    id_usuario: Optional[str] = Field(
        None,
        description=""" Es el identificador de usuario del empleado. 
                        Se debe solicitar al usuario junto con el código de centro""",
    )
    datosPreEval: Optional[DatosPreEvalSimple] = Field(
        None,
        description="""
        Datos de preevaluación. Solicítalo al usuario con una frase como la siguiente: 'Por favor, 
        dime el tipo de inmueble (Piso, Chalet, Chalet Adosado o Casa), su valor de tasación, valor de compraventa,
        provincia, si se hipoteca la vivienda habitual (Sí o No), y el estado del inmueble (En proyecto, 
        En rehabilitación, Terminado nuevo, En construcción, Obra parada, Terminado usado).'
        """,
    )
    datosOperacion: Optional[DatosOperacionSimple] = Field(
        None,
        description="""Datos de la operación. Solicítalo al usuario con una frase como la siguiente: 'Por favor, 
        proporcióname el plazo del préstamo (en años o meses), si el bien es de uso residencial, el importe solicitado,
        la finalidad de la adquisición (primera / segunda vivienda) y el código administrativo del producto. 
        Si no lo conoces, puedo aydarte a encontrarlo generando una recomendación.'.
        """,
    )
    datosInterv: Optional[List[DatosIntervSimple]] = Field(
        None,
        description="""Datos de los intervinientes. ="Datos de los intervinientes. Deben indicarse los datos de los
        intervinientes (máximo 2). Pregunta previamente al usuario cuántos intervinientes se darán de alta y 
        solicita el NIF de los mismos para consultarlos en la base de datos.
        """,
    )
    id_sesion: Optional[str] = Field(
        None,
        description="id_sesion del usuario que se estableció en el primer mensaje del chat",
    )
    timestamp: Optional[str] = Field(
        datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
        description="timestamp de la sesión que se estableció en el primer mensaje del chat",
    )


class MuestraInteresRequests(BaseModel):
    """
    Clase para definir el modelos de datos de APIRequest
    """

    tl: TL
    indLlamada: str = Field(
        description="""Indicador de llamada batch u online. Valores posibles: Batch=B, Online=O"""
    )
    indAccion: str = Field(
        description="""Indicador de acción. Valores posibles: Alta=ALTA, Modificación=MODI"""
    )
    idSolicDigital: str = Field(default="IAG-MVP3")
    empresa: str = Field(default="2103", description="Indicador de empresa")
    centro: str = Field(
        description="""Centro desde el que se está dando de alta la muestra de interés"""
    )
    usuario: str = Field(description="Identificador de usuario del empleado")


class ConsentimientoRequest(BaseModel):
    """
    Clase para definir el modelo de datos de la consulta de consentimiento
    """

    codigoDocumentacion: str = Field(description="DNI del cliente.")
    email: str = Field(description="Email del cliente.")
    movil: str = Field(description="Número móvil del cliente.")
    nombreRazonSocial: str = Field()
    tipoDocumentacion: str = Field(
        default="0001", description="Tipo de documentación del cliente."
    )
    apellidoUno: str = Field(description="Primer apellido del cliente.")
    apellidoDos: str = Field(description="Segundo apellido del cliente.")
    paisExpedidorDocumento: str = Field(
        default="011",
        description="Código del país expedidor del documento del cliente.",
    )


class LogOperacionalRequest(BaseModel):
    """
    Clase para definir el modelo de datos del log operacional
    """

    codGestor: str = Field(description="Código del gestor.")
    timestampInicio: str = Field(description="Hora de inicio de la operación.")
    timestampFin: str = Field(description="Hora de fin de la operación.")
    claper: str = Field(description="Claper del gestor.")
    httpMethod: str = Field(description="Tipo de método.")
    modulo: str = Field(description="Módulo.")
    seccion: str = Field(description="Sección a la que pertenece la operación.")
    operacion: str = Field(description="Operación.")
    path: str = Field(description="Ruta de la petición.")
    request: Optional[str] = Field(default=None, description="Request de la petición.")
    response: str = Field(description="Respuesta de la operación.")
    status: str = Field(description="Estado de la petición.")


class Ingresos(BaseModel):
    """Modelo de ingresos para SimuladorPreciosRequest"""

    ingresosMensuales: int = Field(
        description="""Ingresos mensuales totales de todos los intervinientes en euros. Si hay dos intervinientes, 
        es la suma de ambos."""
    )
    numTitulares: int = Field(
        description="Número de intervinientes que aportan ingresos al préstamo."
    )


class SimuladorPreciosRequest(BaseModel):
    """
    Modelo de datos para la solicitud de simulación de precios hipotecarios.

    Incluye información del solicitante, la vivienda y la operación para
    calcular condiciones y precios mediante el motor de simulación.
    """

    centro: str = Field(
        default="7383",
        description="Código del centro u oficina donde se gestiona la solicitud.",
    )
    empresa: str = Field(
        default="2103",
        description="Código de la empresa o entidad financiera responsable de la operación.",
    )
    usuario: str = Field(
        description="Claper del usuario que realiza la consulta o simulación."
    )
    idioma: str = Field(
        default="E",
        description="""Idioma en el que se quiere recibir la información de la simulación 
        (por ejemplo, 'E' para español).""",
    )
    codigoProvincia: str = Field(
        description="Código de la provincia donde se encuentra la vivienda objeto del préstamo."
    )
    edad: str = Field(
        description="Edad del solicitante principal, se debe inferir de la información del cliente."
    )
    indFuncionario: str = Field(
        description="Indicador de si el solicitante es funcionario ('S' o 'N')."
    )
    indicadorPrimeraVivienda: str = Field(
        description="Indica si la vivienda es la primera del solicitante ('S' o 'N')."
    )
    indicadorViviendaNueva: str = Field(
        description="Indica si la vivienda es de nueva construcción ('S' o 'N')."
    )
    plazoTotal: str = Field(
        description="""Plazo total del préstamo (número de unidades de tiempo, por ejemplo meses o años). 
        Debe pedirse al usuario y no es posible inventarlo."""
    )
    plazoTotalU: str = Field(
        description="""Unidad de medida del plazo total ('A' para años, 'M' para meses). 
        Debe pedirse al usuario y no es posible inventarlo."""
    )
    impConcedido: int = Field(
        description="""Importe total concedido del préstamo en euros. 
        Debe pedirse al usuario y no es posible inventarlo."""
    )
    tasacion: int = Field(description="Valor de tasación de la vivienda en euros.")
    ingresos: Ingresos = Field(
        description="Detalle de los ingresos de los intervinientes y el número de intervinientes."
    )
    indiceAccion: Optional[str] = Field(
        default="CIAG",
        description="Código del índice de acción comercial, usado para segmentación interna.",
    )
    indiceLlamada: Optional[str] = Field(
        default="B", description="Código de índice de llamada o canal de contacto."
    )
    programaLlamante: Optional[str] = Field(
        default="",
        description="Nombre del programa o aplicación que realiza la solicitud, si aplica.",
    )
    terminal: Optional[str] = Field(
        default="",
        description="Identificador del terminal o punto de acceso usado para la consulta.",
    )
    transaccion: Optional[str] = Field(
        default="",
        description="Código de la transacción o acción específica que se solicita.",
    )


class DatosBaseGastos(BaseModel):
    precio_vivienda: Optional[int]
    provincia: Optional[str]
    tipo_vivienda: Optional[int]

    indicador_vivienda_habitual: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    ingresos: Optional[float] = None

    def _validate_precio_vivienda(self) -> List[str]:
        if self.precio_vivienda is None:
            return ["El campo 'precio_vivienda' es obligatorio."]
        if self.precio_vivienda <= 0:
            return ["El 'precio_vivienda' debe ser mayor que 0."]
        return []

    def _validate_provincia(self) -> List[str]:
        if not self.provincia:
            return ["El campo 'provincia' es obligatorio."]
        if len(self.provincia) != 2 or not self.provincia.isdigit():
            return ["El campo 'provincia' debe tener dos cifras numéricas."]
        return []

    def _validate_tipo_vivienda(self) -> List[str]:
        if self.tipo_vivienda is None:
            return ["El campo 'tipo_vivienda' es obligatorio."]
        if self.tipo_vivienda not in [1, 2]:
            return ["El campo 'tipo_vivienda' debe ser 1 o 2."]
        return []

    def _validate_indicador_vivienda_habitual(self) -> List[str]:
        if not self.indicador_vivienda_habitual:
            return ["El campo 'indicador_vivienda_habitual' es obligatorio."]
        if self.indicador_vivienda_habitual not in ["S", "N"]:
            return ["El campo 'indicador_vivienda_habitual' debe ser 'S' o 'N'."]
        return []

    def _validate_fecha_nacimiento(self) -> List[str]:
        if not self.fecha_nacimiento:
            return ["El campo 'fecha_nacimiento' es obligatorio."]
        from datetime import datetime

        try:
            datetime.strptime(self.fecha_nacimiento, "%Y-%m-%d")
            return []
        except ValueError:
            return ["El campo 'fecha_nacimiento' debe tener formato 'AAAA-MM-DD'."]

    def _validate_ingresos(self) -> List[str]:
        if self.ingresos is None:
            return ["El campo 'ingresos' es obligatorio."]
        if self.ingresos <= 0:
            return ["El campo 'ingresos' debe ser mayor que 0."]
        return []


class DatosGastosEscrituraCompraventa(DatosBaseGastos):

    def validate_data(self) -> List[str]:
        errores = []
        errores.extend(self._validate_precio_vivienda())
        errores.extend(self._validate_provincia())
        errores.extend(self._validate_tipo_vivienda())
        return errores


class DatosGastosTasacion(DatosBaseGastos):

    def validate_data(self) -> List[str]:
        errores = []
        errores.extend(self._validate_precio_vivienda())
        errores.extend(self._validate_provincia())
        errores.extend(self._validate_tipo_vivienda())
        errores.extend(self._validate_indicador_vivienda_habitual())
        errores.extend(self._validate_fecha_nacimiento())
        errores.extend(self._validate_ingresos())
        return errores


class DatosCuotaHipoteca(BaseModel):
    """Modelo de datos para calcular la cuota hipotecaria (amortización francesa)."""

    tipo_hipoteca: Optional[str] = Field(
        None, description="Tipo de hipoteca: 'fija', 'mixta' o 'variable'."
    )
    tipo_interes_inicial: Optional[float] = Field(
        None, description="TIN anual inicial en % (>= 0)."
    )
    tipo_interes_posterior: Optional[float] = Field(
        None,
        description="TIN anual posterior en % (>= 0). Requerido en 'mixta' y 'variable'.",
    )
    capital_prestado: Optional[float] = Field(
        None, description="Importe del préstamo en euros (> 0)."
    )
    plazo_anos: Optional[int] = Field(
        None, description="Plazo del préstamo en años (>= 1)."
    )
    comision_apertura: Optional[float] = Field(
        None, description="Comisión de apertura en % (>= 0)."
    )
    periodo_interes_inicial: Optional[int] = Field(
        6,
        description="Meses con tipo inicial. Requerido en 'mixta'. Debe estar entre 1 y plazo_anos*12.",
    )
    euribor_inicial: Optional[float] = Field(
        3.166, description="Euríbor de referencia en % (>= 0). Opcional."
    )
    bonificacion: Optional[bool] = Field(
        None, description="Indica si aplica bonificación (True/False)."
    )

    # -------- Validación agregada al estilo del modelo anterior --------
    def validate_data(self) -> List[str]:
        """Valida presencia, formato y coherencia mínima entre campos."""
        errores: List[str] = []

        errores.extend(self._validate_tipo_hipoteca())
        errores.extend(self._validate_tipos_interes())
        errores.extend(self._validate_capital_prestado())
        errores.extend(self._validate_plazo_anos())
        errores.extend(self._validate_comision_apertura())
        errores.extend(self._validate_periodo_interes_inicial())
        errores.extend(self._validate_euribor_inicial())

        return errores

    # -------------------- Validadores de campo --------------------
    def _validate_tipo_hipoteca(self) -> List[str]:
        """Valida el tipo de hipoteca."""
        if not self.tipo_hipoteca:
            return [
                "El campo 'tipo_hipoteca' es obligatorio ('fija', 'mixta' o 'variable')."
            ]
        if self.tipo_hipoteca not in {"fija", "mixta", "variable"}:
            return ["El campo 'tipo_hipoteca' debe ser 'fija', 'mixta' o 'variable'."]
        return []

    def _validate_tipos_interes(self) -> List[str]:
        """Valida los tipos de interés."""
        errs = []
        if self.tipo_interes_inicial is None:
            errs.append("El campo 'tipo_interes_inicial' es obligatorio.")
        elif self.tipo_interes_inicial < 0:
            errs.append("El 'tipo_interes_inicial' debe ser ≥ 0.")

        # Posterior
        if self.tipo_interes_posterior is not None and self.tipo_interes_posterior < 0:
            errs.append("El 'tipo_interes_posterior' debe ser ≥ 0.")
        return errs

    def _validate_capital_prestado(self) -> List[str]:
        """Valida el capital prestado."""
        if self.capital_prestado is None:
            return ["El campo 'capital_prestado' es obligatorio."]
        if self.capital_prestado <= 0:
            return ["El 'capital_prestado' debe ser un valor positivo mayor que 0."]
        return []

    def _validate_plazo_anos(self) -> List[str]:
        """Valida el plazo en años."""
        if self.plazo_anos is None:
            return ["El campo 'plazo_anos' es obligatorio."]
        if self.plazo_anos < 1:
            return ["El 'plazo_anos' debe ser un entero mayor o igual que 1."]
        return []

    def _validate_comision_apertura(self) -> List[str]:
        """Valida la comisión de apertura."""
        if self.comision_apertura is None:
            return ["El campo 'comision_apertura' es obligatorio."]
        if self.comision_apertura < 0:
            return ["La 'comision_apertura' debe ser ≥ 0."]
        return []

    def _validate_periodo_interes_inicial(self) -> List[str]:
        """Valida que el periodo, si se informa, no sea negativo."""
        if (
            self.periodo_interes_inicial is not None
            and self.periodo_interes_inicial < 0
        ):
            return ["El 'periodo_interes_inicial' (si se informa) debe ser ≥ 0."]
        return []

    def _validate_euribor_inicial(self) -> List[str]:
        """Valida el tipo de euribor inicial."""
        # Opcional; si se informa, validar rango
        if self.euribor_inicial is not None and self.euribor_inicial < 0:
            return ["El 'euribor_inicial' (si se informa) debe ser ≥ 0."]
        return []
