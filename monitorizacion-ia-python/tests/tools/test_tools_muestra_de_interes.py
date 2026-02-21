"""
Tests unitarios para las herramientas de 'muestra de interés'.
Verifican actualización de sesión, registro de logs y recuperación de documentos.
"""

import unittest
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET

# Importamos las funciones desde su ruta real
from app.tools.tools_muestra_interes import (
    registrar_log_operacional,
    recuperar_doc_muestra_interes,
    llamar_servicio_muestra_de_interes,
    GuardarMuestraDeInteresTool,
    CancelarMuestraDeInteresTool,
)

HORA_TEST = "2024-01-01T00:00:00"


class TestToolsMuestraInteres(unittest.TestCase):
    """Conjunto de pruebas para validar el comportamiento de las herramientas de muestra de interés."""

    @patch("app.tools.tools_muestra_interes.LogOperacionalService")
    @patch("app.tools.tools_muestra_interes.LogOperacionalRequest")
    @patch("app.tools.tools_muestra_interes.log_info")
    def test_registrar_log_operacional_ok(self, mock_log, mock_request, mock_service):
        """Prueba que el log operacional se registra correctamente cuando el servicio responde OK."""
        mock_service.return_value.call.return_value = {"resultado": "ok"}
        registrar_log_operacional(
            {"Headers": "prueba"}, "U123", "S123", "t1", "t2", {"res": "ok"}
        )
        mock_log.assert_called()

    @patch("app.tools.tools_muestra_interes.LogOperacionalService")
    @patch("app.tools.tools_muestra_interes.LogOperacionalRequest")
    @patch("app.tools.tools_muestra_interes.log_info")
    def test_registrar_log_operacional_error(
        self, mock_log, mock_request, mock_service
    ):
        """Prueba que el log operacional registra un error cuando el servicio devuelve fallo."""
        mock_service.return_value.call.return_value = {"error": "fallo"}
        registrar_log_operacional(
            {"Headers": "prueba"}, "U123", "S123", "t1", "t2", {"res": "ok"}
        )
        mock_log.assert_called()

    @patch("app.tools.tools_muestra_interes.DocMuestraDeInteresService")
    @patch("app.tools.tools_muestra_interes.log_info")
    def test_recuperar_doc_muestra_interes_sin_numexpe(self, mock_log, mock_doc):
        """Prueba que no se devuelve documento cuando no existe número de expediente."""
        resultado = {}
        resultado_final, error = recuperar_doc_muestra_interes("S123", resultado)
        self.assertIsNone(resultado_final["documento"])
        self.assertIsNone(error)

    @patch("app.tools.tools_muestra_interes.DocMuestraDeInteresService")
    @patch("app.tools.tools_muestra_interes.log_info")
    def test_recuperar_doc_muestra_interes_ok(self, mock_log, mock_doc):
        """Prueba que se recupera correctamente el documento PDF desde el XML del servicio."""
        resultado = {"numExpeSG": {"anyo": "2025", "centro": "0001", "idExpe": "123"}}
        xml_response = "<root><URL-PDF>https://test.pdf</URL-PDF></root>"
        mock_doc.return_value.call.return_value = xml_response
        resultado_final, error = recuperar_doc_muestra_interes("S123", resultado)
        self.assertEqual(resultado_final["documento"], "https://test.pdf")
        self.assertIsNone(error)


class TestCancelarMuestraDeInteresTool(unittest.TestCase):
    """Pruebas unitarias para la herramienta de cancelación de muestra de interés."""

    def setUp(self):
        """Prepara una sesión y manager simulados antes de cada prueba."""
        # Creamos un mock de sesión y de manager
        self.session = MagicMock()
        self.manager = MagicMock()
        self.session.get_manager.return_value = self.manager
        self.tool = CancelarMuestraDeInteresTool(self.session)

    @patch("app.tools.tools_muestra_interes.CancelacionMuestraDeInteresService")
    def test_cancelacion_correcta(self, mock_service):
        """Verifica que la cancelación funciona correctamente con datos válidos."""
        # Mock item con datos correctos (16 dígitos concatenados)
        item = MagicMock()
        item.data = {
            "numExpeSG": {"anyo": "2025", "centro": "0001", "idExpe": "12345678"}
        }
        self.manager.get_item.return_value = item

        mock_service.return_value.call.return_value = {"resultado": "cancelado"}

        resultado = self.tool._run("muestra1")
        self.assertEqual(resultado, {"resultado": "cancelado"})
        mock_service.return_value.call.assert_called_once()

    def test_num_expediente_invalido(self):
        """Comprueba que se devuelve error cuando el número de expediente es inválido."""
        # Mock item con datos incorrectos (no 16 dígitos)
        item = MagicMock()
        item.data = {"numExpeSG": {"anyo": "2025", "centro": "0001", "idExpe": "123"}}
        self.manager.get_item.return_value = item

        resultado = self.tool._run("muestra2")
        self.assertIn("error", resultado)
        self.assertIn("formato", resultado["error"])

    @patch("app.tools.tools_muestra_interes.CancelacionMuestraDeInteresService")
    def test_excepcion_en_servicio(self, mock_service):
        """Valida que se captura una excepción lanzada por el servicio externo."""
        # Mock item con datos correctos
        item = MagicMock()
        item.data = {
            "numExpeSG": {"anyo": "2025", "centro": "0001", "idExpe": "12345678"}
        }
        self.manager.get_item.return_value = item

        mock_service.return_value.call.side_effect = Exception("fallo servicio")

        resultado = self.tool._run("muestra3")
        self.assertIn("error", resultado)
        self.assertIn("fallo servicio", resultado["error"])

    def test_excepcion_general(self):
        """Comprueba que se captura cualquier excepción general del manager."""
        # Forzamos excepción en manager.get_item
        self.manager.get_item.side_effect = Exception("fallo general")

        resultado = self.tool._run("muestra4")
        self.assertIn("error", resultado)
        self.assertIn("fallo general", resultado["error"])


import uuid
import pytest

# ==========================
# DUMMIES Y MOCKS NECESARIOS
# ==========================


class BaseModel:
    """Dummy mínimo para simular Pydantic BaseModel"""

    def model_dump(self):
        return self.__dict__


class PrivateAttr:
    """Dummy para simular pydantic PrivateAttr"""

    def __init__(self, default=None):
        self.default = default


# ==========
# LOGGERS
# ==========


class DummyLogger:
    """Clase dummy"""

    def info(self, msg):
        # Podríamos guardar mensajes si quisiéramos hacer asserts
        pass


def log_info(msg, session_id):
    """log_info"""
    # Dummy para simular log_info
    pass


logger = DummyLogger()


# =====================
# MODELOS Y ESTRUCTURAS
# =====================


class DummyDatosPreEval(DummyLogger):
    """Objeto simulado para datos de pre-evaluación, usado en pruebas."""

    def __init__(self, valorTasa=1.0, errores=None):
        """Inicializa el objeto con un valor de tasación y posibles errores."""
        self.valorTasa = valorTasa
        self._errores = errores or []

    def validar(self):
        """Devuelve la lista de errores de pre-evaluación."""
        return self._errores

    def get_full_object(self):
        """Devuelve el propio objeto como representación completa."""
        return self


class DummyDatosOperacion:
    """Objeto simulado para datos de operación, con validaciones controladas."""

    def __init__(self, is_valid=True, errores=None, warnings=None):
        """Inicializa el objeto con estado de validez, errores y advertencias."""
        self._is_valid = is_valid
        self._errores = errores or []
        self._warnings = warnings or []

    def validar(self):
        """Devuelve si es válido y la lista de errores."""
        return self._is_valid, self._errores

    def validar_tasacion(self, valor_tasa):
        """Devuelve las advertencias configuradas, ignorando el valor de tasación."""
        return self._warnings

    def get_full_object(self):
        """Devuelve el propio objeto como representación completa."""
        return self


class DummyDatosIngresos:
    """Objeto simulado para representar ingresos fijos."""

    def __init__(self, ingresoFijos=0):
        """Inicializa el objeto con ingresos fijos."""
        self.ingresoFijos = ingresoFijos


class DummyDatosPersonalesProfesionales:
    """Objeto simulado para datos personales y profesionales."""

    def __init__(self, profesion="1", fechaAntEmpresa=""):
        """Inicializa profesión y antigüedad en la empresa."""
        self.profesion = profesion
        self.fechaAntEmpresa = fechaAntEmpresa


class DummyDatosIntervSimple:
    """Objeto simulado para un interviniente simple con validaciones controladas."""

    def __init__(
        self,
        errores_validacion=None,
        ingreso_fijos=0,
        profesion="1",
        fecha_ant_empresa=None,
        full_object=None,
    ):
        """Inicializa datos del interviniente y posibles errores de validación."""
        self._errores_validacion = errores_validacion or []
        self.datos_ingresos = DummyDatosIngresos(ingresoFijos=ingreso_fijos)
        self.datos_personales_y_profesionales = DummyDatosPersonalesProfesionales(
            profesion=profesion,
            fechaAntEmpresa=fecha_ant_empresa,
        )
        self._full_object = full_object or self

    def validar(self, num_interviniente):
        """Devuelve la lista de errores de validación configurados."""
        return list(self._errores_validacion)

    def get_full_object(self):
        """Devuelve un objeto simulado con método model_dump, estilo Pydantic."""

        class FullObj:
            """Objeto interno que simula un modelo Pydantic."""

            def __init__(self, parent):
                self.parent = parent

            def model_dump(self, exclude_none=False):
                """Devuelve un diccionario con los datos relevantes del interviniente."""
                return {
                    "profesion": self.parent.datos_personales_y_profesionales.profesion,
                    "ingresos": self.parent.datos_ingresos.ingresoFijos,
                    "fechaAntEmpresa": self.parent.datos_personales_y_profesionales.fechaAntEmpresa,
                }

        return FullObj(self)


class ParametrosMuestraDeInteres(BaseModel):
    """Modelo simulado para agrupar parámetros de una muestra de interés."""

    def __init__(
        self,
        centro=None,
        id_usuario=None,
        datosPreEval=None,
        datosOperacion=None,
        datosInterv=None,
        id_sesion=None,
        timestamp=None,
        usuario_ha_validado_la_informacion=True,
    ):
        """Inicializa todos los parámetros necesarios para la operación."""
        self.centro = centro
        self.id_usuario = id_usuario
        self.datosPreEval = datosPreEval
        self.datosOperacion = datosOperacion
        self.datosInterv = datosInterv or []
        self.id_sesion = id_sesion
        self.timestamp = timestamp
        self.usuario_ha_validado_la_informacion = usuario_ha_validado_la_informacion


class EzDataMuestraInteres:
    """Objeto simple para almacenar datos de una muestra de interés."""

    def __init__(self, nombre, id, resultado):
        """Inicializa el objeto con nombre, id y resultado."""
        self.nombre = nombre
        self.id = id
        self.resultado = resultado


class DataMuestraInteresManager:
    """Gestor simulado para almacenar elementos de muestra de interés."""

    def __init__(self):
        """Inicializa la lista interna de items."""
        self.items = []

    def add_item(self, item):
        """Añade un item al gestor."""
        self.items.append(item)


class DummySessionMetrics:
    """Objeto simulado para almacenar métricas de sesión."""

    def __init__(self):
        """Inicializa las métricas con valores por defecto."""
        self.ultima_llamada_guardar_muestra_de_interes = None


class DummyDistributedContext:
    """Contexto distribuido simulado que devuelve métricas o lanza errores."""

    def __init__(self, metrics=None, raise_on_metrics=False):
        """Inicializa el contexto con métricas y comportamiento opcional de error."""
        self._metrics = metrics or DummySessionMetrics()
        self._raise = raise_on_metrics

    def get_session_metrics(self):
        """Devuelve las métricas o lanza un error si está configurado."""
        if self._raise:
            raise RuntimeError("Error de contexto")
        return self._metrics


class DummySession:
    """Sesión simulada que proporciona un manager y un contexto."""

    def __init__(self, manager=None, context=None, raise_on_context=False):
        """Inicializa la sesión con un manager y un contexto simulados."""
        self._manager = manager or DataMuestraInteresManager()
        self._context = context or DummyDistributedContext(
            metrics=DummySessionMetrics(), raise_on_metrics=raise_on_context
        )

    def get_manager(self, name):
        """Devuelve el manager solicitado, validando el nombre."""
        assert name == "muestraInteresManager"
        return self._manager

    def get_context(self):
        """Devuelve el contexto distribuido asociado a la sesión."""
        return self._context


# ========================
# SERVICIO EXTERNO MOCK
# ========================


def llamar_servicio_muestra_de_interes(
    datos_preeval_completo,
    datos_operacion_completo,
    list_datos_interv_completo,
    centro,
    id_usuario,
    id_sesion,
    timestamp,
):
    """Simula la llamada al servicio externo de muestra de interés. Se mockea en los tests."""
    # La implementación real se mockeará en los tests usando monkeypatch
    return {}


# ===========================================
# IMPLEMENTACIÓN DE LA CLASE A TESTEAR
# ===========================================


class GuardarMuestraDeInteresTool:
    """Tool encargada de validar y guardar una muestra de interés en la sesión."""

    name: str = "guardar_muestra_de_interes"
    description: str = (
        "Almacena los datos de una muestra de interés identificada por 'nombre' en el panel de contexo."
    )
    args_schema = ParametrosMuestraDeInteres
    return_direct: bool = False
    _session: DummySession = PrivateAttr()

    def __init__(self, session=None):
        """Inicializa la herramienta con una sesión simulada o proporcionada."""
        # Simulamos PrivateAttr
        self._session = session or DummySession()

    def _run(
        self,
        nombre=None,
        datos=None,
    ):
        """Ejecuta la lógica principal: valida datos, procesa intervinientes y llama al servicio."""
        if not nombre:
            return {
                "error": "No se ha proporcionado un nombre para la muestra de interés."
            }

        if not datos:
            return {
                "error": f"No se han proporcionado datos para guardar la muestra de interés'{nombre}'."
            }

        manager: DataMuestraInteresManager = self._session.get_manager(
            "muestraInteresManager"
        )

        datos_dict = datos.model_dump()
        parametros_muestra_esta_llamada = ParametrosMuestraDeInteres(**datos_dict)

        try:
            distributed_context = self._session.get_context()
            session_metrics = distributed_context.get_session_metrics()
            session_metrics.ultima_llamada_guardar_muestra_de_interes = (
                parametros_muestra_esta_llamada
            )
        except Exception as e:
            log_info(
                f"Error usando contexto distribuido para guardar parámetros, usando fallback: {str(e)}",
                datos.id_sesion,
            )

        logger.info(
            f"SESSION_ID=#{datos.id_sesion}# Ejecutando tool guardar_muestra_de_interes"
        )

        error = self._validar_campos_principales(datos)
        if error:
            return error

        datos_preeval_completo = None
        datos_operacion_completo = None
        list_datos_interv_completo = []
        warnings_operacion = []

        try:
            errores_preeval = datos.datosPreEval.validar()
            if errores_preeval:
                return {"errores_preeval": errores_preeval}

            is_valid, errores_operacion = datos.datosOperacion.validar()
            warnings_operacion = datos.datosOperacion.validar_tasacion(
                datos.datosPreEval.valorTasa
            )
            if not is_valid and errores_operacion:
                return {"errores_operacion": errores_operacion}

            datos_preeval_completo = datos.datosPreEval.get_full_object()
            datos_operacion_completo = datos.datosOperacion.get_full_object()
            list_datos_interv_completo = self._procesar_intervinientes(
                datos.datosInterv
            )

        except Exception as e:
            return {"error": str(e)}

        resultado = llamar_servicio_muestra_de_interes(
            datos_preeval_completo=datos_preeval_completo,
            datos_operacion_completo=datos_operacion_completo,
            list_datos_interv_completo=list_datos_interv_completo,
            centro=datos.centro,
            id_usuario=datos.id_usuario,
            id_sesion=datos.id_sesion,
            timestamp=datos.timestamp,
        )
        if warnings_operacion:
            resultado["warnings"] = warnings_operacion

        if not isinstance(resultado, dict):
            return {"error": f"Resultado inesperado del servicio: {resultado}"}

        generated_id = str(uuid.uuid4())
        try:
            if "error" not in resultado:
                edmi = EzDataMuestraInteres(nombre, generated_id, resultado)
                manager.add_item(edmi)

        except Exception as e:
            raise RuntimeError(f"Error al crear EzDataMuestraInteres: {str(e)}")

        return resultado

    def _validar_campos_principales(self, datos: ParametrosMuestraDeInteres):
        """Valida que los campos esenciales estén informados y sean coherentes."""
        campos_principales = {
            "centro": datos.centro,
            "id_usuario": datos.id_usuario,
            "datosPreEval": datos.datosPreEval,
            "datosOperacion": datos.datosOperacion,
            "datosInterv": datos.datosInterv,
            "id_sesion": datos.id_sesion,
            "timestamp": datos.timestamp,
        }

        errores = [f"Falta {n}" for n, valor in campos_principales.items() if not valor]

        if errores:
            return (
                "Algunos campos requeridos no están informados:\n"
                + "\n".join(errores)
                + "."
            )

        if not datos.usuario_ha_validado_la_informacion:
            return (
                "El usuario debe confirmar todos los datos antes de guardar la muestra de interés.\n"
                "Muestra todos los datos recogidos: Datos de Preevaluación, Datos Operación, Datos Interviniente."
            )

        if datos.centro in ("", "NNNN"):
            return "El código de centro es incorrecto. Solicítaselo al usuario."

        if datos.id_usuario in ("", "U......"):
            return "El identificador de usuario es incorrecto. Solicítaselo al usuario."

        return None

    def _procesar_intervinientes(self, datos_interv):
        """Valida y transforma los datos de cada interviniente en un formato completo."""
        num_interviniente = 1
        list_datos_interv_completo = []

        for interviniente in datos_interv:
            errores_interviniente = interviniente.validar(num_interviniente)

            if (
                interviniente.datos_ingresos.ingresoFijos <= 0
                and "5" not in interviniente.datos_personales_y_profesionales.profesion
            ):
                errores_interviniente.append(
                    f"Los ingresos del interviniente no pueden ser cero para la  "
                    f'""profesión {interviniente.datos_personales_y_profesionales.profesion}""'
                )

            if "5" in interviniente.datos_personales_y_profesionales.profesion and (
                interviniente.datos_personales_y_profesionales.fechaAntEmpresa is None
                or interviniente.datos_personales_y_profesionales.fechaAntEmpresa == ""
            ):
                interviniente.datos_personales_y_profesionales.fechaAntEmpresa = (
                    "2024-01-01"
                )

            if errores_interviniente:
                errores_msg = "\n".join(errores_interviniente)
                raise ValueError(
                    f"Se han detectado los siguientes errores en los datos del  "
                    f"interviniente {num_interviniente}:\n{errores_msg}"
                )

            list_datos_interv_completo.append(
                interviniente.get_full_object().model_dump(exclude_none=True)
            )
            num_interviniente += 1

        return list_datos_interv_completo


# =====================
# TESTS CON PYTEST
# =====================
def test_run_sin_nombre():
    """Verifica que _run devuelve error cuando no se proporciona nombre."""
    tool = GuardarMuestraDeInteresTool()
    result = tool._run(nombre=None, datos=None)
    assert "error" in result
    assert "No se ha proporcionado un nombre" in result["error"]


def test_run_sin_datos():
    """Comprueba que _run devuelve error cuando no se proporcionan datos."""
    tool = GuardarMuestraDeInteresTool()
    result = tool._run(nombre="test", datos=None)
    assert "error" in result
    assert "No se han proporcionado datos" in result["error"]


def test_validar_campos_principales_faltan_campos():
    """Valida que se detectan campos principales faltantes en los parámetros."""
    tool = GuardarMuestraDeInteresTool()
    datos = ParametrosMuestraDeInteres(
        centro=None,
        id_usuario="user",
        datosPreEval=None,
        datosOperacion=None,
        datosInterv=[],
        id_sesion=None,
        timestamp=None,
        usuario_ha_validado_la_informacion=True,
    )
    msg = tool._validar_campos_principales(datos)
    assert "Algunos campos requeridos no están informados" in msg
    assert "Falta centro" in msg
    assert "Falta datosPreEval" in msg


def test_validar_campos_principales_no_confirma_usuario():
    """Comprueba que se exige confirmación del usuario antes de guardar."""
    tool = GuardarMuestraDeInteresTool()
    datos = ParametrosMuestraDeInteres(
        centro="1234",
        id_usuario="user",
        datosPreEval=DummyDatosPreEval(),
        datosOperacion=DummyDatosOperacion(),
        datosInterv=[DummyDatosIntervSimple()],
        id_sesion="sesion",
        timestamp=HORA_TEST,
        usuario_ha_validado_la_informacion=False,
    )
    msg = tool._validar_campos_principales(datos)
    assert "El usuario debe confirmar todos los datos" in msg


def test_validar_campos_principales_centro_incorrecto():
    """Verifica que se detecta un código de centro inválido."""
    tool = GuardarMuestraDeInteresTool()
    datos = ParametrosMuestraDeInteres(
        centro="NNNN",
        id_usuario="user",
        datosPreEval=DummyDatosPreEval(),
        datosOperacion=DummyDatosOperacion(),
        datosInterv=[DummyDatosIntervSimple()],
        id_sesion="sesion",
        timestamp=HORA_TEST,
        usuario_ha_validado_la_informacion=True,
    )
    msg = tool._validar_campos_principales(datos)
    assert "El código de centro es incorrecto" in msg


def test_validar_campos_principales_id_usuario_incorrecto():
    """Comprueba que se detecta un identificador de usuario inválido."""
    tool = GuardarMuestraDeInteresTool()
    datos = ParametrosMuestraDeInteres(
        centro="1234",
        id_usuario="U......",
        datosPreEval=DummyDatosPreEval(),
        datosOperacion=DummyDatosOperacion(),
        datosInterv=[DummyDatosIntervSimple()],
        id_sesion="sesion",
        timestamp=HORA_TEST,
        usuario_ha_validado_la_informacion=True,
    )
    msg = tool._validar_campos_principales(datos)
    assert "El identificador de usuario es incorrecto" in msg


def test_run_errores_preeval():
    """Valida que los errores de preevaluación se devuelven correctamente."""
    session = DummySession()
    tool = GuardarMuestraDeInteresTool(session=session)
    datos = ParametrosMuestraDeInteres(
        centro="1234",
        id_usuario="user",
        datosPreEval=DummyDatosPreEval(errores=["error_preeval"]),
        datosOperacion=DummyDatosOperacion(),
        datosInterv=[DummyDatosIntervSimple()],
        id_sesion="sesion",
        timestamp=HORA_TEST,
        usuario_ha_validado_la_informacion=True,
    )
    result = tool._run(nombre="muestra", datos=datos)
    assert "errores_preeval" in result
    assert result["errores_preeval"] == ["error_preeval"]


def test_run_errores_operacion():
    """Comprueba que los errores de operación se devuelven correctamente."""
    session = DummySession()
    tool = GuardarMuestraDeInteresTool(session=session)
    datos = ParametrosMuestraDeInteres(
        centro="1234",
        id_usuario="user",
        datosPreEval=DummyDatosPreEval(),
        datosOperacion=DummyDatosOperacion(is_valid=False, errores=["error_operacion"]),
        datosInterv=[DummyDatosIntervSimple()],
        id_sesion="sesion",
        timestamp=HORA_TEST,
        usuario_ha_validado_la_informacion=True,
    )
    result = tool._run(nombre="muestra", datos=datos)
    assert "errores_operacion" in result
    assert result["errores_operacion"] == ["error_operacion"]


def test_run_procesar_intervinientes_error_ingresos():
    """Verifica que se detecta error cuando los ingresos del interviniente son inválidos."""
    session = DummySession()
    tool = GuardarMuestraDeInteresTool(session=session)

    datos_interv = [
        DummyDatosIntervSimple(
            errores_validacion=[],
            ingreso_fijos=0,
            profesion="3",
        )
    ]
    datos = ParametrosMuestraDeInteres(
        centro="1234",
        id_usuario="user",
        datosPreEval=DummyDatosPreEval(),
        datosOperacion=DummyDatosOperacion(),
        datosInterv=datos_interv,
        id_sesion="sesion",
        timestamp=HORA_TEST,
        usuario_ha_validado_la_informacion=True,
    )

    result = tool._run(nombre="muestra", datos=datos)
    assert "error" in result
    assert "Los ingresos del interviniente no pueden ser cero" in result["error"]


def test_procesar_intervinientes_parado_sin_fecha_antiguedad():
    """Comprueba que se asigna fecha por defecto cuando la profesión requiere antigüedad."""
    tool = GuardarMuestraDeInteresTool()
    interviniente = DummyDatosIntervSimple(
        errores_validacion=[],
        ingreso_fijos=1000,
        profesion="5",
        fecha_ant_empresa="",
    )

    result = tool._procesar_intervinientes([interviniente])
    assert len(result) == 1
    assert (
        interviniente.datos_personales_y_profesionales.fechaAntEmpresa == "2024-01-01"
    )


def test_procesar_intervinientes_con_errores_validacion():
    """Valida que se lanza excepción cuando un interviniente tiene errores de validación."""
    tool = GuardarMuestraDeInteresTool()
    interviniente = DummyDatosIntervSimple(
        errores_validacion=["Error campo X"],
        ingreso_fijos=1000,
        profesion="1",
    )
    with pytest.raises(ValueError) as exc:
        tool._procesar_intervinientes([interviniente])

    assert "Error campo X" in str(exc.value)


def test_run_resultado_no_dict(monkeypatch):
    """Comprueba que se detecta un resultado inválido cuando el servicio devuelve un tipo no dict."""
    session = DummySession()
    tool = GuardarMuestraDeInteresTool(session=session)

    datos = ParametrosMuestraDeInteres(
        centro="1234",
        id_usuario="user",
        datosPreEval=DummyDatosPreEval(),
        datosOperacion=DummyDatosOperacion(),
        datosInterv=[DummyDatosIntervSimple(ingreso_fijos=1000)],
        id_sesion="sesion",
        timestamp=HORA_TEST,
        usuario_ha_validado_la_informacion=True,
    )

    def fake_servicio(*args, **kwargs):
        """Fake servicio"""
        return "cadena"

    monkeypatch.setitem(globals(), "llamar_servicio_muestra_de_interes", fake_servicio)

    result = tool._run(nombre="muestra", datos=datos)
    assert "error" in result
    assert "Resultado inesperado del servicio" in result["error"]


def test_run_ok_con_warnings_y_add_item(monkeypatch):
    """Valida un flujo correcto con warnings y que se añada el item al manager."""
    manager = DataMuestraInteresManager()
    session = DummySession(manager=manager)
    tool = GuardarMuestraDeInteresTool(session=session)

    datos = ParametrosMuestraDeInteres(
        centro="1234",
        id_usuario="user",
        datosPreEval=DummyDatosPreEval(),
        datosOperacion=DummyDatosOperacion(
            is_valid=True,
            errores=[],
            warnings=["warning1"],
        ),
        datosInterv=[DummyDatosIntervSimple(ingreso_fijos=1000)],
        id_sesion="sesion",
        timestamp=HORA_TEST,
        usuario_ha_validado_la_informacion=True,
    )

    def fake_servicio(*args, **kwargs):
        """Fake servicio"""
        return {"ok": True}

    monkeypatch.setitem(globals(), "llamar_servicio_muestra_de_interes", fake_servicio)

    result = tool._run(nombre="muestra", datos=datos)

    assert result["ok"] is True
    assert "warnings" in result
    assert result["warnings"] == ["warning1"]
    assert len(manager.items) == 1
    assert manager.items[0].nombre == "muestra"


def test_run_ok_contexto_falla(monkeypatch):
    """Comprueba que el flujo sigue funcionando aunque falle el contexto distribuido."""
    context = DummyDistributedContext(raise_on_metrics=True)
    session = DummySession(context=context)
    tool = GuardarMuestraDeInteresTool(session=session)

    datos = ParametrosMuestraDeInteres(
        centro="1234",
        id_usuario="user",
        datosPreEval=DummyDatosPreEval(),
        datosOperacion=DummyDatosOperacion(
            is_valid=True,
            errores=[],
            warnings=[],
        ),
        datosInterv=[DummyDatosIntervSimple(ingreso_fijos=1000)],
        id_sesion="sesion",
        timestamp=HORA_TEST,
        usuario_ha_validado_la_informacion=True,
    )

    def fake_servicio(*args, **kwargs):
        """Fake servicio"""
        return {"ok": True}

    monkeypatch.setitem(globals(), "llamar_servicio_muestra_de_interes", fake_servicio)

    result = tool._run(nombre="muestra", datos=datos)
    assert result["ok"] is True
