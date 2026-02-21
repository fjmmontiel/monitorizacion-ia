"""Tests para tools_recomendacion_hipoteca."""

import pytest
from unittest.mock import MagicMock, patch
from app.managers.items import EzRecomendacionHipoteca
from app.tools.tools_recomendacion_hipoteca import (
    CreateRecomendacionHipotecaTool,
    DeleteRecomendacionHipotecaTool,
    ConsultarProductoTool,
    NegociarBonificacionesTool,
    EzRecomendacionHipotecaBaseTool,
)


from app.models.models import DatosSimulacionPrecios
from sqlalchemy.exc import SQLAlchemyError

DB_ERROR = "DB error"


@pytest.fixture
def mock_session():
    """Mock session"""
    session = MagicMock()
    manager = MagicMock()
    session.get_manager.return_value = manager
    return session


def test_get_hipoteca_by_nombre(mock_session):
    """Test para _get_hipoteca_by_nombre"""
    tool = EzRecomendacionHipotecaBaseTool(session=mock_session)
    mock_hipoteca = EzRecomendacionHipoteca(name="test", id="1", data={})
    mock_session.get_manager.return_value.get_item.return_value = mock_hipoteca

    result = tool._get_hipoteca_by_nombre("test")
    assert result == mock_hipoteca
    mock_session.get_manager.assert_called_with("recomendacionHipotecaManager")
    mock_session.get_manager.return_value.get_item.assert_called_with("test")


def test_register_request(mock_session):
    """Test para _register_request"""
    tool = EzRecomendacionHipotecaBaseTool(session=mock_session)
    mock_request = EzRecomendacionHipoteca(name="test", id="1", data={})

    tool._register_request(mock_request)
    mock_session.get_manager.assert_called_with("recomendacionHipotecaManager")
    mock_session.get_manager.return_value.add_item.assert_called_with(mock_request)


def test_run_not_implemented(mock_session):
    """Test para _run que lanza NotImplementedError"""
    tool = EzRecomendacionHipotecaBaseTool(session=mock_session)
    with pytest.raises(NotImplementedError):
        tool._run()


@pytest.fixture
def mock_session():
    """Tests para tools_recomendacion_hipoteca."""
    session = MagicMock()
    manager = MagicMock()
    session.get_manager.return_value = manager
    return session


def test_delete_recomendacion_hipoteca_tool_success(mock_session):
    """Tests para tools_recomendacion_hipoteca."""
    tool = DeleteRecomendacionHipotecaTool(session=mock_session)
    # Simulamos que _get_hipoteca_by_nombre devuelve un objeto
    mock_session.get_manager.return_value.get_item.return_value = (
        EzRecomendacionHipoteca(name="test", id="1", data={})
    )

    result = tool._run(nombre="test")
    assert "eliminada correctamente" in result
    mock_session.get_manager.return_value.remove_item.assert_called_once()


def test_delete_recomendacion_hipoteca_tool_error(mock_session):
    """Tests para tools_recomendacion_hipoteca."""
    tool = DeleteRecomendacionHipotecaTool(session=mock_session)
    # Forzamos excepción en _get_hipoteca_by_nombre
    tool._get_hipoteca_by_nombre = MagicMock(side_effect=Exception("fail"))
    result = tool._run(nombre="test")
    assert "error" in result["error"].lower()


@pytest.fixture
def mock_datos():
    """Mock datos"""
    datos = MagicMock(spec=DatosSimulacionPrecios)
    datos.tipo_interes = ["fija"]
    datos.ingresos = 3000
    datos.edad = 35
    datos.certificacion_energetica_vivienda = "C"
    datos.model_dump.return_value = {
        "tipo_interes": ["fija"],
        "ingresos": 3000,
        "edad": 35,
        "certificacion_energetica_vivienda": "C",
    }
    return datos


@pytest.fixture
def mock_datos():
    """Mock datos"""
    datos = MagicMock()
    datos.tipo_interes = ["fija"]
    datos.ingresos = 3000
    datos.edad = 35
    datos.certificacion_energetica_vivienda = "C"
    return datos


@patch("app.tools.tools_recomendacion_hipoteca.get_manual_db_session")
@patch("app.tools.tools_recomendacion_hipoteca.FichaProductoHipoteca")
@patch("app.tools.tools_recomendacion_hipoteca.logica_recomendador_hipotecas")
def test_recomendar_hipotecas_producto_none(
    mock_logica, mock_model, mock_db_session, mock_datos
):
    """Test cuando el producto no existe en la base de datos"""
    mock_logica.hipotecas = [
        {
            "tipo_interes": "fijo",
            "valor": 100,
            "prioridad_interes": 1,
            "vivienda_propiedad_unicaja": "N",
            "ingresos_minimos": 2000,
            "edad_maxima_primera_residencia": 40,
            "certificacion_energetica": "",
            "codigo_administrativo": "ABC123",
        }
    ]

    mock_query = MagicMock()
    mock_query.filter_by.return_value.first.return_value = None

    mock_db = MagicMock()
    mock_db.query.return_value = mock_query
    mock_db_session.return_value = mock_db

    tool = CreateRecomendacionHipotecaTool(session=MagicMock())
    result = tool.recomendar_hipotecas(mock_datos)

    assert "resultado" in result
    mock_db.close.assert_called_once()


@patch("app.tools.tools_recomendacion_hipoteca.DataSession")
def test_run_codigo_invalido(mock_data_session, mock_session):
    """Test para código inválido (no numérico o longitud incorrecta)"""
    tool = ConsultarProductoTool(session=mock_session)
    result = tool._run("abc")
    assert "error" in result
    assert result["codigo_administrativo"] == "000abc"


@patch("app.tools.tools_recomendacion_hipoteca.DataSession")
def test_run_producto_no_encontrado(mock_data_session, mock_session):
    """Test cuando no se encuentra el producto en la BD"""
    mock_db = MagicMock()
    mock_db.listar_productos.return_value = []
    mock_data_session.return_value = mock_db

    tool = ConsultarProductoTool(session=mock_session)
    result = tool._run("123456")
    assert "error" in result
    assert "No se encontró producto" in result["error"]


@patch("app.tools.tools_recomendacion_hipoteca.DataSession")
def test_run_producto_encontrado(mock_data_session, mock_session):
    """Test exitoso: producto encontrado y convertido a dict"""
    mock_producto = MagicMock()
    mock_producto.DES_JSON = '{"nombre": "Hipoteca Variable"}'

    mock_db = MagicMock()
    mock_db.listar_productos.return_value = [mock_producto]
    mock_data_session.return_value = mock_db

    tool = ConsultarProductoTool(session=mock_session)
    result = tool._run("123456")
    assert result["codigo_administrativo"] == "123456"
    assert result["informacion_producto"]["nombre"] == "Hipoteca Variable"


@patch("app.tools.tools_recomendacion_hipoteca.DataSession")
def test_run_codigo_invalido(mock_data_session, mock_session):
    """Test para código inválido (no numérico o longitud incorrecta)"""
    tool = NegociarBonificacionesTool(session=mock_session)
    result = tool._run("abc")
    assert "error" in result
    assert result["codigo_administrativo"] == "000abc"
    assert "6 dígitos" in result["error"]
