"""
Modelos principales del dominio de hipotecas.

Define esquemas Pydantic complejos para datos de preevaluación, operaciones,
intervinientes y estructuras completas de solicitudes hipotecarias, incluyendo
validaciones de negocio y transformaciones entre versiones simples y completas.
"""

from pydantic import BaseModel  # type: ignore
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, conint, constr
import re
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from app.models.models_helper import get_traduccion_from_db
from app.managers.items import EzDataPreeval


Base = declarative_base()

CODIGOS_PAIS_EJEMPLO = {
    "España": "011",
    "Afganistan": "660",
    "Albania": "070",
    "Alemania": "004",
    "Andorra": "043",
}
INDICADOR_CONSUMIDOR = "Indicador de consumidor. Siempre es S. No pedir al usuario"


codEstadoInmu_desc = get_traduccion_from_db("IAG_TRD_ESTADO_INMUEBLE")


class Messages(BaseModel):
    """Clase para definir el modelos de datos de Messages"""

    messages: List[object]
    idSesion: Optional[str]


class ParametrosRecomendadorHipotecas(BaseModel):
    """Clase para definir el modelos de datos del input de la recomendación de una hipoteca"""

    tipo_interes: Optional[List[str]] = Field(
        ["Fijo", "Variable", "Mixto"],
        description="Lista con los tipos de interés sobre los que está interesado el cliente (fijo, mixto, variable)",
    )

    ingresos: Optional[float] = Field(
        None,
        description="""Ingresos mensuales totales de todos los intervinientes en euros. Si hay dos intervinientes, 
        es la suma de ambos.""",
    )
    edad: Optional[int] = Field(
        description="""Edad del cliente. Este campo debe calcularse utilizando la fecha de nacimiento del cliente 
        y la fecha actual obtenida mediante la herramienta `get_current_time`. 
        Si la fecha de nacimiento no está disponible, solicita este dato al usuario.""",
    )
    certificacion_energetica_vivienda: Optional[str] = Field(
        None,
        description="""Código de la certificación energética de la vivienda que quiere adquirir. Si la vivienda no 
        tiene certificación energética, indicar cadena vacía. Ejemplos: A,B""",
    )
    vivienda_propiedad_unicaja: Optional[str] = Field(
        "N",
        description="""Indica si la vivienda para la que se solicita la recomendación es propiedad de Unicaja.
        Debe tener valor 'S' o 'N'""",
    )

    def validar_inputs(self) -> str:
        """
        Valida los parámetros de entrada para la recomendación de hipoteca.
        Devuelve un string con los errores encontrados. Si está vacío, no hay errores.
        """
        errores_inputs: str = ""

        # Validación de tipo de interes
        if self.tipo_interes is None:
            errores_inputs += "Debe indicar al menos un tipo de interés\n"
        # Validación de ingresos
        if self.ingresos is None or self.ingresos <= 0:
            errores_inputs += "Debe indicar los ingresos en euros\n"

        # Validación de edad
        if self.edad is None or self.edad <= 17:
            errores_inputs += "Por favor, indique una edad correcta\n"

        # Validación de certificación energética
        if self.certificacion_energetica_vivienda is None:
            errores_inputs += (
                "Por favor, confirma la certificación energética con el usuario. "
                "Si no la conoce, se debe pasar un string vacío ''.\n"
            )
        elif self.certificacion_energetica_vivienda not in (
            "",
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
        ):
            errores_inputs += (
                "La certificación energética debe ser '', A, B, C, D, E, F o G\n"
            )

        # Validación de vivienda propiedad Unicaja
        if self.vivienda_propiedad_unicaja is None:
            errores_inputs += (
                "Debe indicar si la vivienda es propiedad de Unicaja ('S' o 'N')\n"
            )
        elif self.vivienda_propiedad_unicaja not in ("S", "N"):
            errores_inputs += (
                "El valor de vivienda_propiedad_unicaja debe ser 'S' o 'N'\n"
            )

        return errores_inputs


class DatosSimulacionPrecios(ParametrosRecomendadorHipotecas):
    """Clase para definir el modelos de datos del input de la simulación de precios"""

    usuario: Optional[str] = Field(None, description="Código del gestor.")
    centro: Optional[str] = Field(
        None,
        description="Centro del gestor actual.",
    )
    codigo_provincia: Optional[int] = Field(
        None,
        description="""Código de la provincia en la que se encuentra el inmueble. Si no tienes el dato, pide el nombre
        de la provincia e infiere el código.
        Este dato NO ES EL MISMO que la provincia de residencia del cliente/interesado""",
    )
    imp_concedido: Optional[int] = Field(
        None, description="Importe que solicita el cliente/interesado a la entidad."
    )
    primera_vivienda: Optional[str] = Field(
        None,
        description="'S' si la finalidad de la adquisición es para primera vivienda, 'N' en caso contrario",
    )
    funcionario: Optional[str] = Field(
        None,
        description="'S' si el cliente/interesa es funcionario, 'N'' en caso contrario",
    )
    num_titulares: Optional[int] = Field(
        None, description="Número total de intervinientes."
    )
    plazoTotalU: str = Field(
        default="A", description="Unidad del plazo total delpréstamo."
    )
    plazoTotal: Optional[str] = Field(
        None,
        description="Plazo total del préstamo. Número de años o meses (según el valor de plazoTotalU).",
    )

    @classmethod
    def desde_recomendacion(
        cls, recomendacion: ParametrosRecomendadorHipotecas, **kwargs
    ):
        """
        Constructor que crea una instancia de DatosSimulacionPrecios a partir de DatosRecomendacion.
        Se pueden pasar campos adicionales como kwargs.
        """
        base_dict = recomendacion.dict()
        base_dict.update(kwargs)
        return cls(**base_dict)


class DatosPreEval(BaseModel):
    """Clase para definir el modelos de datos de DatosPreEval"""

    valorTasa: float = Field(
        description="Valor de tasación del inmueble. Es una cantidad de euros.",
    )
    tipoInmu: str = Field(
        description="""Código de tres caracteres que representa el tipo de inmueble. 
        Es obligatorio solicitarlo al usuario, está prohibido inferirlo. Las opciones son
        Piso=PSO, Chalet=CHI, Chalet Adosado=CHA, Casa=CAS.""",
    )
    provincia: str = Field(
        description="Código de provincia de dos caracteres numéricos."
    )
    numInmueblesHip: str = Field(
        default="1", description="Número de inmuebles hipotecados"
    )
    precioVivienda: Optional[float] = Field(
        description="""Precio de compraventa del inmueble. Hay que solicitarlo al usuario. 
        Es una cantidad en euros.""",
    )
    importeInv: float = Field(
        description="""Corresponde exclusivamente al importe total de inversión, que incluye el precio de compraventa 
        y los gastos de escritura de compraventa.  El usuario puede proporcionar este valor directamente.
        Si no se proporciona, el sistema debe calcularlo utilizando la herramienta
        'calcular_gastos_escritura_compraventa' y los datos proporcionados por el usuario.
        Si no se dispone de todos los datos necesarios para el cálculo, este campo no se debe informar.
        """
    )
    hipVvdaHab: str = Field(
        default="S", description="¿Se hipoteca la vivienda habitual?"
    )
    divisaTasa: str = Field(default="EUR", description="Código de divisa. Ejemplo: EUR")
    divisa: str = Field(default="EUR", description="Código de divisa. Ejemplo: EUR")
    codEstadoInmu: str = Field(
        default="N",
        description=f"Código del estado del inmueble. La traducción de códigos es {codEstadoInmu_desc}",
    )


class DatosPreEvalSimple(BaseModel):
    """
    Este modelo agrupa los datos que el usuario proporciona para crear o actualizar una preevaluación.
    Todos los valores deben provenir del usuario o de herramientas específicas en otros pasos del flujo.
    Los valores definidos en este modelo NO deben inferirse ni inventarse. Si el usuario no proporciona
    un dato, debe mantenerse como None.
    """

    valorTasa: Optional[float] = Field(
        None,
        description="""Valor de tasación del inmueble. Es una cantidad de euros. Si el usuario no lo indica, se
        puede poner el precio de vivienda.""",
    )
    precioVivienda: Optional[float] = Field(
        None,
        description="""Precio de compraventa del inmueble. Hay que solicitarlo al usuario. 
        Es una cantidad en euros.""",
    )
    importeTotalInversion: Optional[float] = Field(
        None,
        description="""Corresponde exclusivamente al importe total de inversión, que incluye el precio de compraventa 
        y los gastos de escritura de compraventa.  El usuario puede proporcionar este valor directamente.
        Si no se proporciona, el sistema debe calcularlo utilizando la herramienta
        'calcular_gastos_escritura_compraventa' y los datos proporcionados por el usuario.
        Si no se dispone de todos los datos necesarios para el cálculo, este campo no se debe informar.
        """,
    )
    tipoInmu: Optional[str] = Field(
        None,
        description="""Código de tres caracteres que representa el tipo de inmueble. 
        Es obligatorio solicitarlo al usuario, está prohibido inferirlo. Las opciones son
        Piso=PSO, Chalet=CHI, Chalet Adosado=CHA, Casa=CAS.""",
    )
    provincia: Optional[str] = Field(
        None,
        description="""Recibirás el nombre de la provincia, pero tu debes poner el código correspondiente 
                                              de dos caracteres numéricos.""",
    )
    hipVvdaHab: Optional[str] = Field(
        default=None,
        description="""Indica si se hipoteca la vivienda habitual. Puede ser 'S' (si) o 'N' (no). 
        Este dato debe ser proporcionado explícitamente por el usuario. 
        Si no se conoce, este dato no se debe informar.""",
    )
    codEstadoInmu: Optional[str] = Field(
        default=None,
        description=f"""Código del estado del inmueble. La traducción de códigos es {codEstadoInmu_desc}.
        Este dato debe ser proporcionado explícitamente por el usuario. 
        Si no se conoce, este dato no se debe informar.""",
    )

    def get_full_object(self) -> DatosPreEval:
        return DatosPreEval(
            valorTasa=self.valorTasa,
            tipoInmu=self.tipoInmu,
            provincia=self.provincia,
            numInmueblesHip="1",  # Valor por defecto
            precioVivienda=self.precioVivienda,
            importeInv=self.importeTotalInversion,
            hipVvdaHab=self.hipVvdaHab,
            divisaTasa="EUR",  # Valor por defecto
            divisa="EUR",  # Valor por defecto
            codEstadoInmu=self.codEstadoInmu,
        )

    def validar(self) -> List[str]:
        """
        Valida el contenido de un objeto EzDataPreeval.
        Verifica si todos los campos obligatorios están presentes y contienen valores válidos.

        Returns:

        """

        errores = []

        if self.importeTotalInversion is None:
            errores.append(
                """
                FALTA_IMPORTE_INV: Falta el importe de inversión (importeTotalInversion). 
                Debe calcularse como precioVivienda + los gastos de escritura de compraventa. 
                Los gastos de escritura de compraventa deben calcularse 
                usando la herramienta 'calcular_gastos_escritura_compraventa'.
                Informa al usuario sobre esta acción y actualiza la preevaluación usando `update_preeval` con 
                el `importeTotalInversion` calculado. 
                """
            )

        if self.tipoInmu not in {"PSO", "CHI", "CHA", "CAS"}:
            errores.append(
                "Debe introducir un tipo de inmueble válido: Piso, Chalet, Chalet Adosado o Casa."
            )
        if (
            not isinstance(self.precioVivienda, (int, float))
            or self.precioVivienda <= 0
        ):
            errores.append("El precio de copmpraventa debe ser un número mayor que 0.")

        if not isinstance(self.valorTasa, (int, float)) or self.valorTasa <= 0:
            errores.append(
                "El valor de tasación debe ser un número mayor que 0. Si no se conoce, se debe confirmar "
                "con el usuario que se va a poner la misma cifra que el precio de la vivienda: 'precioVivienda'."
            )

        if (
            not isinstance(self.importeTotalInversion, (int, float))
            or self.importeTotalInversion <= 0
        ):
            errores.append("El importe de inversión debe ser un número mayor que 0.")

        if not isinstance(self.provincia, str) or not self.provincia.strip():
            errores.append("Debe introducir una provincia válida.")

        if self.hipVvdaHab not in {"S", "N"}:
            errores.append(
                "Debe indicar si se hipoteca la vivienda habitual con 'S' (Sí) o 'N' (No)."
            )

        if self.codEstadoInmu not in {"P", "R", "N", "C", "O", "T"}:
            errores.append(
                "Debe introducir un código de estado de inmueble válido: "
                "P (En proyecto), R (En rehabilitación), N (Obra terminada nueva), C (En construcción), "
                "O (Obra parada), T (Obra terminada usada)"
            )

        return errores


class Direccion(BaseModel):
    """Clase para definir el modelos de datos de Direccion"""

    tipoVia: Optional[str] = Field(
        default="CL",
        description="""Identificador del tipo de vía. Debe tener dos caracteres: Alameda=AL, Aldea=AD, 
            Apartamentos=AP, Arroyo=AY, Avenida=AV, Bajada=BJ, Barranco=BR, Barrio=BO, Bloque=BL, Calle=CL, Calleja=CJ,
            Camino=CM, Carretera=CR, Caserío=CS, Chalet=CH, Colegio=CG, Colonia=CO, Conjunto=CN, Cuesta=CT, 
            Edificio=ED, Entrada=EN, Escalinata=ES, Explanada=EX, Extramuros=EM, Extrarradio=ER, Ferrocarril=FC, 
            Glorieta=GL, Gran Vía=GV, Grupo=GR, Huerta=HT, JR=Jardines, LD=Lado, Lugar=LG, Manzana=MZ, Masía=MS, 
            Mercado=MC, Monte=MT, Muelle=ML, Municipio=MN, Parcela=PA, Parque=PQ, Parroquia=PI, Partida=PD, Pasaje=PJ, 
            Paseo=PS, Plaza=PZ, Poblado=PB, Poligono=PG, Prolongación=PR, Puente=PT, Puerta=PU, Quinta=QT, Ramal=RM,
            Rampa=RP, Riera=RR, Rincón=RC, Ronda=RD, Rúa=RU, Salida=SA, Sector=SC, Senda=SD, Solar=SL, Subida=SB, 
            Terrenos=TN, Torrente=TO, Travesía=TR, Urbanización=UR, Vía=VI, Vía pública=VP, Área=AR, Arrabal=AR""",
    )
    puerta: Optional[str] = Field(
        default="",
        description="""Generalmente es una letra, aunque también puede ser un número. Máximo 3 caracteres. 
                    # Valores posibles: IZQ, DER, 1, 2, 3, 4, A, B, C, ...""",
    )
    portal: Optional[str] = Field(
        default="",
        description="Generalmente es una letra, aunque también puede ser un número. Máximo 3 caracteres",
    )
    poblacion: Optional[str] = Field(
        default="",
        description="Nombre de la población. Es un campo obligatorio. Ejemplos: Madrid, Estepona, Ponferrada",
    )
    planta: Optional[str] = Field(
        default="",
        description="Generalmente es un número, aunque también pueden ser letras. Máximo 3 caracteres",
    )
    numero: Optional[str] = Field(
        default="",
        description="Número de la dirección. Máximo 5 caracteres. Intenta inferirlo de la información del cliente.",
    )
    domicilio: Optional[str] = Field(
        default="",
        description="Nombre de la vía. Ejemplos: Sagasta, Bravo Murillo. Máximo 50 caracteres",
    )
    restoDireccion: Optional[str] = Field(
        default="",
        description="Resto del campo dirección. Utilizar sólo si el campo domicilio supera el máximo de 50 caracteres",
    )
    codProvincia: Optional[str] = Field(
        default="",
        description="Código de provincia de dos caracteres numéricos: Álava=01, Albacete=02, Alicante=03...",
    )
    codPostal: Optional[str] = Field(
        default="",
        description="Código postal: código numérico de cinco caracteres. Ejemplos: 28080, 08005",
    )
    codPais: Optional[str] = Field(
        default="011",
        description=f"Código  de país. Ejemplos: {CODIGOS_PAIS_EJEMPLO}",
    )
    bloque: Optional[str] = Field(
        default="", description="Números o letras. Máximo 3 caracteres"
    )
    escalera: Optional[str] = Field(
        default="", description="Escalera (número o letras). Máximo 3 caracteres"
    )
    km: Optional[str] = Field(default="", description="Kilómetro (número o letras)")
    parcela: Optional[str] = Field(default="", description="Parcela (número o letras)")

    def validar(self) -> List[str]:
        errores = []

        # Check mandatory fields not being None or empty
        if not self.domicilio:
            errores.append("Direccion: Falta el domicilio en la dirección")
        elif len(self.domicilio) > 50:
            errores.append("Direccion: El domicilio excede el máximo de 50 caracteres")

        if not self.poblacion:
            errores.append("Direccion: Falta la población en la dirección")
        if not self.numero:
            errores.append("Direccion: Falta el número en la dirección")
        elif len(self.numero) > 5:
            errores.append("Direccion: El número excede el máximo de 5 caracteres")

        if not self.codPostal:
            errores.append("Direccion: Falta el código postal en la dirección")
        elif not re.match(r"^\d{5}$", self.codPostal):
            errores.append(
                "Direccion: El código postal debe ser numérico de 5 caracteres"
            )

        if not self.codProvincia:
            errores.append("Direccion: Falta el código de provincia en la dirección")
        elif not re.match(r"^\d{2}$", self.codProvincia):
            errores.append(
                "Direccion: El código de provincia debe ser numérico de 2 caracteres"
            )

        # Validate maximum lengths for optional fields
        if len(self.puerta) > 3:
            errores.append("Direccion: La puerta excede el máximo de 3 caracteres")

        if len(self.portal) > 3:
            errores.append("Direccion: El portal excede el máximo de 3 caracteres")

        if len(self.planta) > 3:
            errores.append("Direccion: La planta excede el máximo de 3 caracteres")

        if len(self.bloque) > 3:
            errores.append("Direccion: El bloque excede el máximo de 3 caracteres")

        if len(self.escalera) > 3:
            errores.append("Direccion: La escalera excede el máximo de 3 caracteres")

        return errores


class DatosOperacion(BaseModel):
    """Clase para definir el modelos de datos de DatosOperacion"""

    tipoProp: Optional[str] = Field(
        default="0",
        description="Tipo de propiedad. Siempre será 0. No es necesario pedírselo al usuario",
    )
    tipoProducto: Optional[str] = Field(
        default="112",
        description="Tipo de producto. Siempre será 112. No es necesario pedírselo al usuario",
    )
    producto: str = Field(
        default="050",
        description="Tres primeros caracteres del código de producto administrativo. Siempre 050",
    )
    subproducto: str = Field(
        description="Tres últimos caracteres del código de producto administrativo. Ejemplos: 050484=484, 050436=436"
    )
    plazoTotalU: str = Field(default="A", description="Unidad del plazo total.")
    plazoTotal: str = Field(
        description="Plazo total del préstamo. Número de años o meses (según el valor de plazoTotalU)"
    )
    indUsoResidencial: str = Field(
        default="S",
        description="¿El bien que garantiza la operación es de uso residencial?",
    )
    indTipoIntSS: str = Field(
        description="Indicador del tipo de interés: 'F' fijo, 'V' variable o 'M' mixto."
    )
    indRefinMor: str = Field(
        default="N", description="Siempre debe ser N. No solicitar al usuario"
    )
    importe: float = Field(description="Importe solicitado, expresado en euros")
    finalidad: Optional[str] = Field(
        description="""Código de la finalidad de la adquisición. Valores posibles: 
        Adquisición de vivienda 1ª residencia = 2112
        Adquisición de vivienda 2ª residencia = 2113"""
    )
    divisa: str = Field(
        default="EUR",
        description="Código de la divisa de los importes del registro",
    )
    codModal: str = Field(
        default="30",
        description="Código de modalidad. Siempre debe valer 30. No solicitar al usuario",
    )


class DatosOperacionSimple(BaseModel):
    """
    Este modelo agrupa los datos que el usuario proporciona para crear o actualizar una operación.
    Todos los valores deben provenir del usuario o de herramientas específicas en otros pasos del flujo.
    Los valores definidos en este modelo NO deben inferirse ni inventarse.
    """

    subproducto: Optional[str] = Field(
        None,
        description="""Tres últimos caracteres del código de producto administrativo. Solicítalo al usuario de
        inmediato. Si el usuario no lo conoce, utiliza la herramienta `create_recomendacion_hipoteca` para recomendar
        tres productos adecuados. Confirma el producto con el usuario antes de continuar.
        Cómo extraerlo: 050NNN=NNN """,
    )
    plazoTotalU: Optional[str] = Field(
        default="A", description="Unidad del plazo total."
    )
    plazoTotal: Optional[int] = Field(
        None,
        description="Plazo total del préstamo. Número de años o meses (según el valor de plazoTotalU)",
    )
    indUsoResidencial: Optional[str] = Field(
        default="S",
        description="¿El bien que garantiza la operación es de uso residencial?",
    )
    indTipoIntSS: Optional[str] = Field(
        default=None,
        description="Indicador del tipo de interés: 'F' fijo, 'V' variable o 'M' mixto.",
    )
    importeSolicitado: Optional[float] = Field(
        None,
        description="""Este campo representa únicamente el importe solicitado por el cliente para la hipoteca.
        Es la cantidad de dinero que el cliente desea financiar mediante el préstamo hipotecario, expresada en euros.
        Este dato debe ser proporcionado explícitamente por el usuario. 
        Si no se conoce, este dato no se debe informar.""",
    )

    finalidad: Optional[str] = Field(
        None,
        description="""Código de la finalidad de la adquisición. Valores posibles: 
        Adquisición de vivienda 1ª residencia = 2112
        Adquisición de vivienda 2ª residencia = 2113""",
    )

    def get_full_object(self) -> DatosOperacion:
        return DatosOperacion(
            tipoProp="0",  # Valor por defecto
            tipoProducto="112",  # Valor por defecto
            producto="050",  # Valor por defecto
            subproducto=self.subproducto,
            plazoTotalU=self.plazoTotalU,
            plazoTotal=f"{self.plazoTotal}",  # Formateado como cadena
            indUsoResidencial=self.indUsoResidencial,
            indTipoIntSS=self.indTipoIntSS,
            indRefinMor="N",  # Valor por defecto
            importe=self.importeSolicitado,
            finalidad=self.finalidad,
            divisa="EUR",  # Valor por defecto
            codModal="30",  # Valor por defecto
        )

    def validar(self) -> tuple[bool, str, list[str]]:
        """
        Valida el contenido de un objeto EzDataOperacion.
        """

        errores = []
        errores += self._validate_rules()
        errores += self._validate_tipo_interes()
        errores += self._validate_plazo_maximo()

        return len(errores) == 0, " ".join(errores)

    def validar_tasacion(self, valor_tasacion: float) -> str:
        """Valida que el capital solicitado no supere el 80% de la tasación."""
        warnings = []
        try:
            capital_solicitado = self.importeSolicitado
            if valor_tasacion and capital_solicitado > 0.8 * valor_tasacion:
                warnings.append(
                    f"ATENCIÓN: El capital solicitado ({capital_solicitado}) supera el 80% "
                    f"de la tasación ({valor_tasacion}). Se debe confirmar si esto es correcto"
                )

        except Exception as e:
            warnings.append(f"No se pudo verificar la tasación: {e}")
        return "\n".join(warnings)

    def _validate_rules(self) -> list[str]:
        """Valida reglas básicas de la operación."""
        errores = []
        reglas = [
            (
                "subproducto",
                lambda v: isinstance(v, str) and len(v) == 3,
                "El campo 'subproducto' debe ser una cadena de 3 caracteres. Si el usuario no lo conoce, "
                " ofrece recomendar productos usando la tool `create_recomendacion_hipoteca`. Debes solicitar:"
                " indicador del tipo de interés (fijo, variable o mixto), ingresos mensuales, edad y"
                " certificación energética. El usuario debe seleccionar un producto para completar la operación.",
            ),
            (
                "plazoTotal",
                lambda v: isinstance(v, int) and v > 0,
                "El campo 'plazoTotal' debe ser un número entero mayor que 0.",
            ),
            (
                "plazoTotalU",
                lambda v: v in {"A", "M"},
                "El campo 'plazoTotalU' debe ser 'A' (años) o 'M' (meses).",
            ),
            (
                "indUsoResidencial",
                lambda v: v in {"S", "N"},
                "El campo 'indUsoResidencial' debe ser 'S' o 'N'.",
            ),
            (
                "indTipoIntSS",
                lambda v: v in {"Fijo", "Variable", "Mixta", "F", "V", "M"},
                "El campo 'indTipoIntSS' debe ser 'Fijo', 'Variable', 'Mixta' o F/V/M.",
            ),
            (
                "importeSolicitado",
                lambda v: isinstance(v, (int, float)) and v > 0,
                "El campo 'importeSolicitado' debe ser un número mayor que 0.",
            ),
            (
                "finalidad",
                lambda v: isinstance(v, str) and v.strip(),
                "El campo 'finalidad' es obligatorio y no puede estar vacío.",
            ),
        ]

        errores.extend(
            [
                mensaje
                for campo, regla, mensaje in reglas
                if not regla(getattr(self, campo))
            ]
        )

        return errores

    def _validate_plazo_maximo(self) -> list[str]:
        """Valida que el plazo total no supere los 30 años."""
        errores = []
        plazo = getattr(self, "plazoTotal", None)
        unidad = getattr(self, "plazoTotalU", None)

        if plazo is not None and unidad in {"A", "M"}:
            if unidad == "A" and plazo > 30:
                errores.append("El plazo total no puede ser superior a 30 años.")
            elif unidad == "M" and plazo > 30 * 12:
                errores.append(
                    "El plazo total no puede ser superior a 360 meses (30 años)."
                )

        return errores

    def _validate_tipo_interes(self) -> list[str]:
        """Verifica que el tipo de interés indicado coincide con el tipo real del subproducto."""
        errores = []
        subproducto = self.subproducto
        tipo_indicado = self.indTipoIntSS

        if not (subproducto and tipo_indicado):
            return errores

        normalizacion = {
            "f": "fijo",
            "fijo": "fijo",
            "variable": "variable",
            "v": "variable",
            "mixto": "mixto",
            "m": "mixto",
        }

        tipo_indicado_norm = normalizacion.get(tipo_indicado.strip().lower())
        if not tipo_indicado_norm:
            errores.append(
                f"El valor '{tipo_indicado}' de 'indTipoIntSS' no se pudo normalizar correctamente."
            )
            return errores

        try:
            from app.services.data.logica_recomendador_hipotecas import hipotecas

            codigo_completo = f"50{subproducto}"

            hipoteca = next(
                (
                    h
                    for h in hipotecas
                    if h.get("codigo_administrativo") == codigo_completo
                ),
                None,
            )

            if not hipoteca:
                errores.append(
                    f"No se encontró ninguna hipoteca asociada al subproducto '{subproducto}' "
                    f"(código comercial {codigo_completo})."
                )
                return errores

            tipo_real = hipoteca.get("tipo_interes", "").lower()
            if tipo_real != tipo_indicado_norm:
                errores.append(
                    f"Incoherencia detectada: el tipo de interés indicado ('{tipo_indicado}') "
                    f"no coincide con el tipo real del subproducto '{subproducto}' ({tipo_real})."
                )
        except Exception as e:
            errores.append(f"Error al validar el tipo de interés del subproducto: {e}")

        return errores


class DatosPersonalesYProfesionales(BaseModel):
    """Clase para definir el modelos de datos de DatosPersonalesYProfesionales"""

    codCliente: Optional[str] = Field(
        default="",
        description="Indicar este código si el usuario ya es cliente del banco",
    )
    rolInterviniente: Optional[str] = Field(
        default="T",
        description="""Rol del interviniente durante la operación. Para el interviniente titular debe ser siempre "T".
            "Valores posibles: Titular=T, Avalista=A, Otros=[blank]""",
    )
    nif: Optional[str] = Field(default=None, description="DNI/NIF del interviniente")
    nombre: Optional[str] = Field(
        default="",
        description="Nombre del interviniente. No debe incluir los apellidos.",
    )
    apellido1: Optional[str] = Field(
        default="", description="Primer apellido del interviniente"
    )
    apellido2: Optional[str] = Field(
        default="", description="Segundo apellido del interviniente"
    )
    indPerJur: Optional[str] = Field(
        default="F",
        description="""Tipo de persona (física o jurídica). Sólo se envía F. No pedir dato al cliente.
                Valores posibles: Persona Física=F, Persona Jurídica=J""",
    )
    fechaNacimiento: Optional[str] = Field(
        default=None,
        description="Fecha de nacimiento en formato AAAA-MM-DD. Ejemplo: 1981-09-01",
    )
    fechaAntEmpresa: Optional[str] = Field(
        default=None,
        description="""Fecha de antigüedad en empresa actual. El usuario lo expresará en lenguaje natural pero tu
        debes almacenarlo en formato AAAA-MM-DD. Utiliza la fecha de hoy para calcular la antigüedad.""",
    )
    sexo: Optional[str] = Field(
        default=None,
        description="""Código de género. Se debe inferir a partir de la información del cliente.
                        Valores posibles: Hombre=H, Mujer=M""",
    )
    comUniFamiliar: Optional[int] = Field(
        default=None,
        description="Componentes de la unidad familiar. Si no se conoce, este dato no se debe informar.",
    )
    indResidente: Optional[str] = Field(
        default="S",
        description="Indicador de residente. Siempre es S. No pedir al usuario",
    )
    nacionalidad: Optional[str] = Field(
        default=None,
        description=f"""Nacionalidad del interviniente. Se debe solicitar al usuario.
                    Código de país. Ejemplos: {CODIGOS_PAIS_EJEMPLO}""",
    )
    estadoCivil: Optional[str] = Field(
        default=None,
        description="""Estado civil. Este dato debe ser proporcionado explícitamente por el usuario.  
        Si no se conoce, este dato no se debe informar. Valores posibles: Casado=C, Divorciado=D,
        Pareja de Hecho=P, Soltero=S, Viudo=V, Separado de Hecho=H, Separado Judicial=J""",
    )
    relacPrimerTitular: Optional[str] = Field(
        default="",
        description="""Relación con el primer titular. Solicitar solo para el segundo interviniente. Obligatorio
        informar para el segundo interviniente. Valores posibles: Padre/Madre='01', Hermano/a='02', Hijo/a='03', 
        Conyuge/Pareja='04', Otros='05'""",
    )
    sitLaboral: Optional[str] = Field(
        default=None,
        description="""Identificador de la situación laboral. Valores posibles: Fijo=1, Temporal=2, Temporero=3, 
        Autonomo=4, Otros=5, Funcionario=6.""",
    )
    profesion: Optional[str] = Field(
        default="SIN ESPECIFICAR=00",
        description="""Código de la profesión del interviniente. Debes convertir la profesión que diga el usuario en
        uno de los códigos válidos de la lista y confirmar siempre con el usuario antes de guardarlo:
        - Debes elegir siempre un código del grupo correspondiente al valor de 'sitLaboral'. Nunca uses códigos 
        de otro grupo.
        - Si no estás seguro del código correcto, muestra al usuario las opciones más probables y pide al usuario
        que elija una.

            Códigos válidos:
            Grupo GENERAL (para sitLaboral ≠ 4 y ≠ 5):
                1A = Gerente / Alto Cargo / Ejecutivo
                1B = Técnico Superior (para ingenieros y titulados superiores)
                1C = Mando Intermedio
                1D = Administrativo
                1E = Representante Comisionista
                1F = Vendedor de Comercio
                1G = Encargado
                1H = Obrero Especializado
                1I = Obrero No Especializado
                1J = Profesor
                1K = Militar / Policía (No Municipal)
                1L = Policía Municipal

            Si "sitLaboral" = 4 (Autónomo):
                4A = Médico
                4B = Abogado
                4C = Notario / Procurador
                4D = Arquitecto / Ingeniero
                4E = Periodista / Escritor / Traductor
                4F = Veterinario
                4G = Farmacéutico
                4H = Artista / Deportista
                4I = Otras Profesiones Liberales
                4J = No Profesionales Liberales

            Si "sitLaboral" = 5 (Otros),:
                5A = Religioso
                5B = Ama de casa
                5C = Rentista
                5D = Estudiante
                5E = Jubilado / Pensionista
                5F = Parado
        """,
    )
    actEconomica: Optional[str] = Field(
        default=None,
        description="""Código de la actividad económica. Inferir a partir de la profesión, si es posible. Valores 
        posibles: AGRICULTURA Y CAZA=1A, PESCA=1B, 
            ENERGIA Y AGUA=1C, MINERIA=1D, METALURGIA-SIDERURGIA=1E, MAQUINARIA-INGENIERIA-MECANICA=1F, 
            FAB. ELECTRICA Y ELECTRONICA=1G, CONSTRUCCION=1H, ALIMENTACION Y TABACO=1I, TEXTIL-MADERA-MUEBLE=1J, 
            PAPEL Y ARTES GRAFICAS=1K, CUERO-PIEL-CALZADO-VESTIDO=1L, ADMINISTRACION PUBLICA=2A, MILITAR-POLICIA=2B, 
            DIPLOMATICOS-ORG.INTERNACIONAL=2C, SANIDAD-SERVICIOS VETERINARIOS=2D, ENSE.ANZA=2E, 
            BANCA-FINANCIERAS-SEGUROS=2F, INFORMATICA-SERVICIOS=2G, SERV. FINANCIEROS Y DE EMPRESA=2H, 
            SERV. DOMESTICOS O PERSONALES=2I, COMERCIO-HOSTELERIA=2J, REPARACION VEHICULOS=2K, ALQUILER 
            MUEBLES-INMUEBLES=2L, PRENSA-RADIO-T.V.=2M, ESPECTACULOS-DEPORTES=2N, TRANSPORTE TERRESTRE=2O, 
            TRANSPORTE AEREO=2P, TR.MARITIMO-FLUVIAL-FERROVIAR=2Q, AGENCIAS DE VIAJE=2R, 
            COMUNICACIONES(CORREOS-CTNE)=2S, ACTIVIDAD NO PRODUCTIVA=3A
            """,
    )
    cnae: Optional[str] = Field(
        default="",
        description="CNAE. Es un código con 4 dígitos. Solicitar sólo si sitLaboral=4 (autónomo)",
    )

    def validar_intervinientes(self, num_interviniente, errores):
        if num_interviniente == 1 and self.rolInterviniente == "T":
            if self.relacPrimerTitular not in [None, ""]:
                errores.append(
                    """DatosPersonalesYProfesionales: el titular principal debe contener cadena vacía en el 
                    campo 'relacPrimerTitular'"""
                )
        elif self.relacPrimerTitular not in ["01", "02", "03", "04", "05", ""]:
            errores.append(
                "Los datos de relación con el primer titular son incorrectos. Se debe insertar el código."
                "Debería ser alguno de: Padre/Madre='01', Hermano/a='02', Hijo/a='03', Conyuge/Pareja='04', Otros='05'"
            )
        return errores

    def validar(self, num_interviniente: int | None = None) -> List[str]:
        errores = []

        # --- Campos obligatorios ---
        campos_obligatorios = {
            "nif": self.nif,
            "nombre": self.nombre,
            "apellido1": self.apellido1,
            "fechaNacimiento": self.fechaNacimiento,
            "fechaAntEmpresa": self.fechaAntEmpresa,
            "comUniFamiliar": self.comUniFamiliar,
            "sitLaboral": self.sitLaboral,
            "profesion": self.profesion,
            "actEconomica": self.actEconomica,
            "estadoCivil": self.estadoCivil,
        }

        for campo, valor in campos_obligatorios.items():
            if valor in [None, ""]:
                errores.append(
                    f"DatosPersonalesYProfesionales: El campo {campo} es obligatorio y está vacío"
                )

        # --- Restricciones de valores permitidos ---
        valores_permitidos = {
            "sitLaboral": ["1", "2", "3", "4", "5", "6"],
            "rolInterviniente": ["T", "A", ""],
            "indPerJur": ["F"],
            "profesion": [
                # Grupo 1 – Cuenta ajena
                "1A",
                "1B",
                "1C",
                "1D",
                "1E",
                "1F",
                "1G",
                "1H",
                "1I",
                "1J",
                "1K",
                "1L",
                # Grupo 4 – Autónomos / liberales
                "4A",
                "4B",
                "4C",
                "4D",
                "4E",
                "4F",
                "4G",
                "4H",
                "4I",
                "4J",
                # Grupo 5 – Otros
                "5A",
                "5B",
                "5C",
                "5D",
                "5E",
                "5F",
            ],
        }

        for campo, permitidos in valores_permitidos.items():
            valor = getattr(self, campo)
            if valor and valor not in permitidos:
                errores.append(
                    f"DatosPersonalesYProfesionales: El campo {campo} tiene un valor no permitido"
                )

        # --- Restricciones de longitud ---
        if self.sitLaboral and len(self.sitLaboral) > 1:
            errores.append(
                "DatosPersonalesYProfesionales: El campo sitLaboral tiene longitud mayor de la esperada (1)"
            )

        # --- Validación CNAE para autónomos ---
        if self.sitLaboral == "4" and (
            not self.cnae or len(self.cnae) != 4 or not self.cnae.isdigit()
        ):
            errores.append(
                """DatosPersonalesYProfesionales: El campo cnae es obligatorio y debe contener 4 cifras
                si sitLaboral es 4 (autónomo)"""
            )

        # --- Validación relacPrimerTitular ---
        if num_interviniente in (1, 2):
            errores = self.validar_intervinientes(num_interviniente, errores)

        return errores


class DatosIngresos(BaseModel):
    """Clase para definir el modelos de datos de DatosIngresos.
    Estos valores NUNCA deben copiarse ni inferirse."""

    ingresoFijos: Optional[float] = Field(
        default=0,
        description="Ingresos fijos mensuales netos percibidos por el interviniente",
    )
    ingresosVar: Optional[float] = Field(
        default=0,
        description="Ingresos variables mensuales percibidos por el interviniente",
    )
    ingresosOtros: Optional[float] = Field(
        default=0,
        description="Otros ingresos mensuales percibidos por el interviniente",
    )

    def validar(self) -> List[str]:
        errores = []
        # Check if ingresoFijos are negative
        if self.ingresoFijos < 0:
            errores.append("DatosIngresos: El campo ingresoFijos debe ser positivo.")

        if self.ingresosVar < 0:
            errores.append("DatosIngresos: El campo ingresosVar no puede ser negativo.")

        if self.ingresosOtros < 0:
            errores.append(
                "DatosIngresos: El campo ingresosOtros no puede ser negativo."
            )
        return errores


class DatosViviendaHabitual(BaseModel):
    """Clase para definir el modelos de datos de DatosViviendaHabitual"""

    sitViviendaHab: Optional[str] = Field(
        default=None,
        description="""Situación de la vivienda habitual. Valores posibles: Libre de cargas=2,
        Propiedad hipotecada y mantiene la hipoteca=4, Vivienda actual en alquiler=3, domicilio de los padres
        o familia=6, Propiedad hipotecada pero se cancelará la hipoteca=5, Sin vivenda actual=1""",
    )
    valorVivienda: Optional[float] = Field(
        default=0,
        description="""Valor de la vivienda actual del interviniente. 
        Solicitar al usuario sólo si sitViviendaHab es 2, 4 o 5. En otro caso usa el valor 0.""",
    )
    gastosAlquiler: Optional[float] = Field(
        default=0,
        description="""Cantidad dedicada a gastos de alquiler del interviniente.
        Solicitar al usuario sólo si sitViviendaHab es 3. En otro caso usa el valor 0.""",
    )
    cargasVivienda: Optional[float] = Field(
        default=0,
        description="""Importe de las cargas de la vivienda actual del interviniente.
        Solicitar sólo si sitViviendaHab es 4 o 5.""",
    )

    def validar(self) -> List[str]:
        errores = []

        # Check situation of housing
        if self.sitViviendaHab not in ["1", "2", "3", "4", "5", "6", None]:
            errores.append(
                "DatosViviendaHabitual: El campo sitViviendaHab tiene un valor no permitido"
            )

        # Check valorVivienda for specific situations
        if self.sitViviendaHab in ["2", "4", "5"] and (
            self.valorVivienda is None or self.valorVivienda <= 0
        ):
            errores.append(
                """DatosViviendaHabitual: El campo valorVivienda es obligatorio y debe ser mayor que
                           0 para las situaciones 2, 4, o 5 """
            )

        # Check gastosAlquiler only if sitViviendaHab is 3
        if self.sitViviendaHab == "3" and (
            self.gastosAlquiler is None or self.gastosAlquiler <= 0
        ):
            errores.append(
                """DatosViviendaHabitual: El campo gastosAlquiler es obligatorio y debe ser mayo
                que 0 si sitViviendaHab es 3"""
            )

        # Check cargasVivienda for specific situations
        if self.sitViviendaHab in ["4", "5"] and (
            self.cargasVivienda is None or self.cargasVivienda <= 0
        ):
            errores.append(
                """DatosViviendaHabitual: El campo cargasVivienda es obligatorio y debe ser mayor que 0
            para las situaciones 4 o 5"""
            )

        # Example: Ensure that cargasVivienda is not provided for others
        if self.sitViviendaHab not in ["4", "5"] and self.cargasVivienda > 0:
            errores.append(
                "DatosViviendaHabitual: El campo cargasVivienda no debe estar informado si sitViviendaHab no es 4 o 5"
            )

        return errores


class DatosSituacionEconomica(BaseModel):
    """Clase para definir el modelos de datos de DatosSituacionEconomica"""

    indCompGtosIngr: Optional[str] = Field(
        default="N",
        description="""Indicar siempre valor N. Si tiene gastos compartidos, se debe indicar el NIF de la persona
                    con la que comparte gastos""",
    )
    nifCompGtosIngr: Optional[str] = Field(
        default="",
        description="""Nif del cliente que comparte gastos e ingresos. Preguntar si el cliente comparte 
                gastos, y en ese caso pedir el NIF de la persona con la que comparte gastos""",
    )
    ctaOtrasEntidades: Optional[str] = Field(
        default=None,
        description="""¿Tiene cuentas en otras entidades? (S/N). Debe ser ser proporcionado explícitamente por el
        usuario. Si no se conoce, este dato no se debe informar.""",
    )
    indInmueble: Optional[str] = Field(
        default=None,
        description="""Indica si el interviniente ya posee algún inmueble a su nombre antes de la operación actual.
        Debe ser proporcionado explícitamente por el usuario. Si no se conoce, este dato no se debe informar.
        Si no se conoce, este dato no se debe informar""",
    )
    indDeudasOOEE: Optional[str] = Field(
        default=None,
        description="""¿Tiene  deudas en  otras entidades? (S/N). Debe ser proporcionado explícitamente por el usuario.
        Si no se conoce, este dato no se debe informar.Si no se conoce, este dato no se debe informar""",
    )
    cuotasOOEE: Optional[float] = Field(
        default=0,
        description="""Importe de la cuota mensual por las deudas en otras entidades. 
        Solicitar sólo si indDeudasOOEE es S.""",
    )

    def validar(self) -> List[str]:
        errores = []

        # Check for correct value of indCompGtosIngr
        if self.indCompGtosIngr not in ["S", "N"]:
            errores.append(
                "DatosSituacionEconomica: El campo indCompGtosIngr debe tener valor 'S' o 'N'"
            )

        # Check for required nifCompGtosIngr if they share expenses/incomes
        if self.indCompGtosIngr == "S" and not self.nifCompGtosIngr:
            errores.append(
                "DatosSituacionEconomica: El campo nifCompGtosIngr es obligatorio porque se comparten gastos/ingresos"
            )

        # Check for values of optional S/N fields
        if self.ctaOtrasEntidades not in ["S", "N"]:
            errores.append(
                "DatosSituacionEconomica: El campo ctaOtrasEntidades debe ser 'S' o 'N'"
            )

        if self.indInmueble not in ["S", "N"]:
            errores.append(
                "DatosSituacionEconomica: El campo indInmueble debe ser 'S' o 'N'"
            )

        if self.indDeudasOOEE not in ["S", "N"]:
            errores.append(
                "DatosSituacionEconomica: El campo indDeudasOOEE debe ser 'S' o 'N'"
            )

        # Check cuotasOOEE for indDeudasOOEE
        if self.indDeudasOOEE == "S" and self.cuotasOOEE <= 0:
            errores.append(
                "DatosSituacionEconomica: El campo cuotasOOEE debe ser mayor que 0 si indDeudasOOEE es 'S'"
            )

        if self.indDeudasOOEE != "S" and self.cuotasOOEE > 0:
            errores.append(
                "DatosSituacionEconomica: El campo cuotasOOEE no debe estar informado si indDeudasOOEE no es 'S'"
            )

        return errores


class DatosContacto(BaseModel):
    """Clase para definir el modelos de datos de DatosContacto"""

    email: Optional[str] = Field(default=None, description="E-mail del interviniente")
    prefijo: Optional[str] = Field(
        default="+34", description="Prefijo telefónico. Ejemplo: +34"
    )
    movil: Optional[str] = Field(
        default=None,
        description="Número de teléfono móvil en formato string. Debe contener 9 dígitos.",
    )
    paisTelefono: Optional[str] = Field(
        default="011",
        description=f"Código de país. Ejemplos: {CODIGOS_PAIS_EJEMPLO}",
    )
    direccion: Optional[Direccion] = Field(
        default=None,
        description="""Dirección completa del interviniente (Tipo vía, nombre vía, número de portal, piso, puerta,
        bloque, codigo postal, provincia, país)""",
    )

    def validar(self) -> List[str]:
        errores = []

        # Validar el email con una expresión regular
        if self.email:
            email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if not re.match(email_pattern, self.email) or self.email.endswith(
                "@example.com"
            ):
                errores.append("DatosContacto: El email no es válido")

        if self.movil and not re.match(r"^\d{9}$", self.movil):
            errores.append("DatosContacto: El móvil no es válido")

        if self.direccion is None:
            errores.append("DatosContacto: Falta la dirección")
        else:
            errores.extend(self.direccion.validar())

        return errores


class DatosInterv(BaseModel):
    """Clase para definir el modelos de datos de DatosInterv"""

    # Datos personales y profesionales
    codCliente: str = Field(
        default="",
        description="Indicar este código si el usuario ya es cliente del banco",
    )
    indRelac: str = Field(
        default="T",
        description="""Relación del interviniente con la operación. Valores posibles: Titular=T, Avalista=A, 
        Otros=[blank]""",
    )
    nif: str = Field(description="DNI/NIF del interviniente")
    nombre: str = Field(
        description="Nombre del interviniente. No debe incluir los apellidos."
    )
    apellido1: str = Field(description="Primer apellido del interviniente")
    apellido2: Optional[str] = Field(description="Segundo apellido del interviniente")
    indPerJur: str = Field(
        default="F",
        description="""Tipo de persona (física o jurídica). Sólo se envía F. No pedir dato al cliente. 
        Valores posibles: Persona Física=F, Persona Jurídica=J""",
    )
    fechaNacimiento: str = Field(
        description="Fecha de nacimiento en formato AAAA-MM-DD. Ejemplo: 1981-09-01"
    )
    fechaAntEmpresa: str = Field(
        description="""Fecha de antigüedad en empresa actual. El usuario lo expresará en lenguaje natural pero tu
        debes almacenarlo en formato AAAA-MM-DD. Utiliza la fecha de hoy para calcular la antigüedad.""",
    )
    sexo: str = Field(
        description="""Código de género. No pedir al usuario si se puede inferir a partir del nombre.
        Valores posibles: Hombre=H, Mujer=M"""
    )
    comUniFamiliar: str = Field(
        description="Componentes de la unidad familiar (número entero). Se debe solicitar al usuario"
    )
    indResidente: str = Field(
        default="S",
        description="Indicador de residente. Siempre es S. No pedir al usuario",
    )
    nacionalidad: str = Field(
        description=f"""Nacionalidad del interviniente. Se debe solicitar al usuario.
                    Código de país. Ejemplos: {CODIGOS_PAIS_EJEMPLO}""",
    )
    estadoCivil: Optional[str] = Field(
        None,
        description="""Estado civil. Se debe solicitar al usuario. Valores posibles: Casado=C, Divorciado=D,
        Pareja de Hecho=P, Soltero=S, Viudo=V, Separado de Hecho=H, Separado Judicial=J""",
    )
    relacPrimerTitular: Optional[str] = Field(
        default="",
        description="""Relación  con el primer titular. Solicitar solo para el segundo interviniente. 
        Valores posibles: Padre/Madre='01', Hermano/a='02', Hijo/a='03', Conyuge/Pareja='04', Otros='05'""",
    )
    sitLaboral: Optional[str] = Field(
        default=None,
        description="""Identificador de la situación laboral. Valores posibles: Fijo=1, Temporal=2, Temporero=3, 
        Autonomo=4, Otros=5, Funcionario=6.""",
    )
    profesion: str = Field(
        description="""Código de la profesión del interviniente. Debes convertir la profesión que diga el usuario en
        uno de los códigos válidos de la lista y confirmar siempre con el usuario antes de guardarlo:
        - Si el usuario dice una profesión similar o equivalente debes proponer el código más adecuado y pedir 
        confirmación.
        - Si no estás seguro del código correcto, muestra al usuario las opciones más probables y pide al usuario
        que elija una.

        Códigos válidos:
        Grupo GENERAL (para sitLaboral ≠ 4 y ≠ 5):
            1A = Gerente / Alto Cargo / Ejecutivo
            1B = Técnico Superior (para ingenieros y titulados superiores)
            1C = Mando Intermedio
            1D = Administrativo
            1E = Representante Comisionista
            1F = Vendedor de Comercio
            1G = Encargado
            1H = Obrero Especializado
            1I = Obrero No Especializado
            1J = Profesor
            1K = Militar / Policía (No Municipal)
            1L = Policía Municipal

        Si "sitLaboral" = 4 (Autónomo):
            4A = Médico
            4B = Abogado
            4C = Notario / Procurador
            4D = Arquitecto / Ingeniero
            4E = Periodista / Escritor / Traductor
            4F = Veterinario
            4G = Farmacéutico
            4H = Artista / Deportista
            4I = Otras Profesiones Liberales
            4J = No Profesionales Liberales

        Si "sitLaboral" = 5 (Otros):
            5A = Religioso
            5B = Ama de casa
            5C = Rentista
            5D = Estudiante
            5E = Jubilado / Pensionista
            5F = Parado
        """,
    )
    actEconomica: str = Field(
        description="""
            Código de la actividad económica. La traducción de códigos es AGRICULTURA Y CAZA=1A, PESCA=1B, 
            ENERGIA Y AGUA=1C, MINERIA=1D, METALURGIA-SIDERURGIA=1E, MAQUINARIA-INGENIERIA-MECANICA=1F, 
            FAB. ELECTRICA Y ELECTRONICA=1G, CONSTRUCCION=1H, ALIMENTACION Y TABACO=1I, TEXTIL-MADERA-MUEBLE=1J, 
            PAPEL Y ARTES GRAFICAS=1K, CUERO-PIEL-CALZADO-VESTIDO=1L, ADMINISTRACION PUBLICA=2A, MILITAR-POLICIA=2B, 
            DIPLOMATICOS-ORG.INTERNACIONAL=2C, SANIDAD-SERVICIOS VETERINARIOS=2D, ENSE.ANZA=2E, 
            BANCA-FINANCIERAS-SEGUROS=2F, INFORMATICA-SERVICIOS=2G, SERV. FINANCIEROS Y DE EMPRESA=2H, 
            SERV. DOMESTICOS O PERSONALES=2I, COMERCIO-HOSTELERIA=2J, REPARACION VEHICULOS=2K, ALQUILER 
            MUEBLES-INMUEBLES=2L, PRENSA-RADIO-T.V.=2M, ESPECTACULOS-DEPORTES=2N, TRANSPORTE TERRESTRE=2O, 
            TRANSPORTE AEREO=2P, TR.MARITIMO-FLUVIAL-FERROVIAR=2Q, AGENCIAS DE VIAJE=2R, 
            COMUNICACIONES(CORREOS-CTNE)=2S, ACTIVIDAD NO PRODUCTIVA=3A
            """,
    )
    cnae: str = Field(
        default="",
        description="CNAE. Solicitar sólo si sitLaboral=4 (autónomo)",
    )

    # Vivienda habitual
    sitViviendaHab: str = Field(
        description="""Situacion de la vivienda habitual. Valores posibles: Libre de cargas=2, 
        Propiedad hipotecada y mantiene la hipoteca=4,   Vivienda actual en alquiler=3, domicilio de los padres o
        familia=6, Propiedad hipotecada pero se cancelará la hipoteca=5, Sin vivenda actual=1""",
    )
    valorVivienda: float = Field(
        default=0,
        description="""Valor de la vivienda actual del interviniente. Solicitar al usuario sólo si sitViviendaHab
          es 1, 2 o 6""",
    )
    gastosAlquiler: float = Field(
        default=0,
        description="Cantidad dedicada a gastos de alquiler. Solicitar al usuario sólo si sitViviendaHab es 3",
    )
    cargasVivienda: float = Field(
        default=0,
        description="Importe de las cargas en la vivienda actual. Solicitar sólo si sitViviendaHab es 2 o 6",
    )

    # Ingresos
    ingresoFijos: float = Field(
        default=0,
        description="Ingresos fijos mensuales percibidos por el interviniente",
    )
    ingresosVar: float = Field(
        default=0,
        description="Ingresos variables mensuales percibidos por el interviniente",
    )
    ingresosOtros: float = Field(
        default=0,
        description="Otros ingresos mensuales percibidos por el interviniente",
    )

    # Situación económica
    indCompGtosIngr: str = Field(description="¿Comparte gastos/ingresos? S/N")
    nifCompGtosIngr: str = Field(
        default="",
        description="Nif del cliente que comparte gastos e ingresos. Solicitar sólo si indCompGtosIngr=S",
    )
    ctaOtrasEntidades: str = Field(
        default="N", description="¿Tiene cuentas en otras entidades? (S/N)"
    )
    indInmueble: str = Field(
        description="El interviniente posee algún inmueble a su nombre antes de la operación? (S/N)"
    )
    indDeudasOOEE: str = Field(description="¿Tiene deudas en otras entidades? (S/N)")
    cuotasOOEE: float = Field(
        description="""Importe de la cuota mensual por las deudas en otras entidades. 
        Solicitar sólo si indDeudasOOEE es S"""
    )

    # Datos de contacto
    email: Optional[EmailStr] = Field(
        default=None,
        description="E-mail del interviniente. No obligatorio si la información viene de un lead",
    )
    prefijo: str = Field(default="+34", description="Prefijo telefónico. Ejemplo: +34")
    movil: Optional[str] = Field(
        default=None,
        description="Número de teléfono móvil. No obligatorio si la información viene de un lead",
    )
    paisTelefono: str = Field(
        default="011",
        description=f"Código de país. Ejemplos: {CODIGOS_PAIS_EJEMPLO}",
    )
    direccion: Direccion = Field(
        description="""Dirección completa del interviniente (Tipo vía, nombre vía, número de portal, piso, puerta, 
        bloque, codigo postal, provincia, país)"""
    )
    infConsumidor: str = Field(default="S", description=INDICADOR_CONSUMIDOR)
    indConsumidor: str = Field(default="S", description=INDICADOR_CONSUMIDOR)
    paisResidencia: str = Field(
        default="011", description=f"Código de país. Ejemplos: {CODIGOS_PAIS_EJEMPLO}"
    )


class DatosIntervSimple(BaseModel):
    """
    Este modelo agrupa los datos que el usuario proporciona para crear o actualizar un interviniente.
    Todos los valores deben provenir del usuario o de herramientas específicas en otros pasos del flujo.
    Los valores definidos en este modelo NO deben inferirse ni inventarse. Si algún dato no se conoce,
    no se debe informar.
    """

    datos_personales_y_profesionales: Optional[DatosPersonalesYProfesionales] = Field(
        None,
        description="""Datos personales y profesionales del interviniente.  Solicítalos al usuario con 
        una frase como la siguiente: 'Por favor, proporciona el Nif, Nombre completo (Nombre, Primer Apellido,
        Segundo Apellido), Fecha de nacimiento, Sexo (Hombre, Mujer), Nacionalidad, Estado civil (Casado, Divorciado, 
        Pareja de Hecho, Soltero, Viudo, Separado de Hecho, Separado Judicial), Número de componentes 
        de la unidad familiar, Situación laboral (Fijo, Temporal, Temporero, Autónomo, Otros, Funcionario), 
        Profesión, Actividad económica (si no se proporciona puedo averiguarla) y fecha de antigüedad en la 
        empresa actual'.""",
    )
    datos_vivienda_habitual: Optional[DatosViviendaHabitual] = Field(
        None,
        description="Datos relativos a la vivienda habitual.",
    )
    datos_ingresos: Optional[DatosIngresos] = Field(
        None,
        description="Datos relativos a los ingresos del interviniente.",
    )
    datos_situacion_economica: Optional[DatosSituacionEconomica] = Field(
        None,
        description="Situación económica del interviniente.",
    )
    info_de_lead: bool = Field(
        default=False, description="Indica si la información viene de un lead"
    )
    datos_contacto: Optional[DatosContacto] = Field(
        None,
        description="""Datos de contacto del interviniente. Si el usuario es un lead, no se solicitarán ni el email 
        ni el movil""",
    )
    infConsumidor: Optional[str] = Field(default="S", description=INDICADOR_CONSUMIDOR)
    paisResidencia: Optional[str] = Field(
        default="011", description=f"Código de país. Ejemplos: {CODIGOS_PAIS_EJEMPLO}"
    )

    def validar(self, num_interviniente: int | None = None) -> List[str]:
        errores = []

        # Check for mandatory fields not being None
        if self.datos_personales_y_profesionales is None:
            errores.append(
                "DatosIntervSimple: El campo datos_personales_y_profesionales es obligatorio y no puede ser None"
            )

        if self.datos_vivienda_habitual is None:
            errores.append(
                "DatosIntervSimple: El campo datos_vivienda_habitual es obligatorio y no puede ser None"
            )
        if self.datos_ingresos is None:
            errores.append(
                "DatosIntervSimple: El campo datos_ingresos es obligatorio y no puede ser None"
            )
        if self.datos_situacion_economica is None:
            errores.append(
                "DatosIntervSimple: El campo datos_situacion_economica es obligatorio y no puede ser None"
            )
        if self.datos_contacto is None:
            errores.append(
                "DatosIntervSimple: El campo datos_contacto es obligatorio y no puede ser None"
            )
        # Validate infConsumidor
        if self.infConsumidor != "S":
            errores.append(
                "DatosIntervSimple: El campo infConsumidor debe tener siempre el valor 'S'"
            )
        # Validate paisResidencia for valid codes
        if not self.paisResidencia:
            errores.append("DatosIntervSimple: El campo paisResidencia es obligatorio")
        # Validate nested objects if present
        if self.datos_personales_y_profesionales:
            errores.extend(
                self.datos_personales_y_profesionales.validar(num_interviniente)
            )
        if self.datos_vivienda_habitual:
            errores.extend(self.datos_vivienda_habitual.validar())
        if self.datos_ingresos:
            errores.extend(self.datos_ingresos.validar())
        if self.datos_situacion_economica:
            errores.extend(self.datos_situacion_economica.validar())
        if self.datos_contacto:
            errores.extend(self.datos_contacto.validar())

        return errores

    def get_full_object(self) -> DatosInterv:
        data = {
            # Datos personales y profesionales
            "codCliente": self.datos_personales_y_profesionales.codCliente,
            "indRelac": self.datos_personales_y_profesionales.rolInterviniente,
            "nif": self.datos_personales_y_profesionales.nif,
            "nombre": self.datos_personales_y_profesionales.nombre,
            "apellido1": self.datos_personales_y_profesionales.apellido1,
            "apellido2": self.datos_personales_y_profesionales.apellido2,
            "indPerJur": "F",
            "fechaNacimiento": self.datos_personales_y_profesionales.fechaNacimiento,
            "fechaAntEmpresa": self.datos_personales_y_profesionales.fechaAntEmpresa,
            "sexo": self.datos_personales_y_profesionales.sexo,
            "comUniFamiliar": f"{self.datos_personales_y_profesionales.comUniFamiliar}",
            "indResidente": self.datos_personales_y_profesionales.indResidente,
            "nacionalidad": self.datos_personales_y_profesionales.nacionalidad,
            "estadoCivil": self.datos_personales_y_profesionales.estadoCivil,
            "relacPrimerTitular": self.datos_personales_y_profesionales.relacPrimerTitular,
            "sitLaboral": self.datos_personales_y_profesionales.sitLaboral,
            "profesion": self.datos_personales_y_profesionales.profesion,
            "actEconomica": self.datos_personales_y_profesionales.actEconomica,
            "cnae": self.datos_personales_y_profesionales.cnae,
            # Datos de vivienda habitual
            "sitViviendaHab": self.datos_vivienda_habitual.sitViviendaHab,
            "valorVivienda": self.datos_vivienda_habitual.valorVivienda,
            "gastosAlquiler": self.datos_vivienda_habitual.gastosAlquiler,
            "cargasVivienda": self.datos_vivienda_habitual.cargasVivienda,
            # Datos de ingresos
            "ingresoFijos": self.datos_ingresos.ingresoFijos,
            "ingresosVar": self.datos_ingresos.ingresosVar,
            "ingresosOtros": self.datos_ingresos.ingresosOtros,
            # Datos de situación económica
            "indCompGtosIngr": "N",
            "nifCompGtosIngr": "",
            "ctaOtrasEntidades": self.datos_situacion_economica.ctaOtrasEntidades,
            "indInmueble": self.datos_situacion_economica.indInmueble,
            "indDeudasOOEE": self.datos_situacion_economica.indDeudasOOEE,
            "cuotasOOEE": self.datos_situacion_economica.cuotasOOEE,
            # Datos de contacto (opcional según lead)
            "prefijo": self.datos_contacto.prefijo,
            "paisTelefono": self.datos_contacto.paisTelefono,
            "direccion": self.datos_contacto.direccion,
            # Resto
            "infConsumidor": self.infConsumidor,
            "indConsumidor": self.infConsumidor,
            "paisResidencia": self.paisResidencia,
        }

        # Añadir email y móvil solo si existen y no viene de lead
        if self.info_de_lead is False:
            if self.datos_contacto.email:
                data["email"] = self.datos_contacto.email
            if self.datos_contacto.movil:
                data["movil"] = self.datos_contacto.movil

        return DatosInterv(**data)


class TL(BaseModel):
    """Clase para definir el modelos de datos de TL"""

    datosPreEval: DatosPreEval
    datosOperacion: DatosOperacion
    datosInterv: List[DatosInterv]
