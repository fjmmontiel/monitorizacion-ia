"""
Tests para `ConsultaConsentimientoService`.


"""

import pytest
from types import SimpleNamespace

import app.services.consulta_consentimiento_service as mod
from app.services.consulta_consentimiento_service import ConsultaConsentimientoService


class FakeResp:
    """Respuesta simulada para requests.post con soporte de JSON y texto."""

    def __init__(self, code: int, payload=None, text: str = ""):
        """
        Inicializa la respuesta falsa.

        Args:
            code: Código de estado HTTP.
            payload: Objeto a devolver en json() o excepción a lanzar.
            text: Contenido de texto de la respuesta.
        """
        self.status_code = code
        self._payload = payload
        self.text = text

    def json(self):
        """Devuelve el payload o lanza la excepción configurada."""
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class FakeReq:
    """Request de dominio simulado con método model_dump()."""

    def __init__(self, body=None):
        """
        Inicializa el request simulado.

        Args:
            body: Diccionario que representa el cuerpo.
        """
        self._body = body or {}

    def model_dump(self):
        """Devuelve el cuerpo del request como dict."""
        return self._body


@pytest.fixture
def svc(monkeypatch):
    """Crea el servicio parcheando la configuración para URL determinística."""
    cfg = SimpleNamespace(api_consulta_consentimiento="https://api.test/consent")
    monkeypatch.setattr(mod, "UnicajaServicesConfig", lambda: cfg)
    return ConsultaConsentimientoService(headers={"Auth": "jwt"})


def test_init(monkeypatch):
    """Verifica que __init__ asigna api_url y headers correctamente."""
    cfg = SimpleNamespace(api_consulta_consentimiento="https://a.b/consent")
    monkeypatch.setattr(mod, "UnicajaServicesConfig", lambda: cfg)
    s = ConsultaConsentimientoService(headers={"H": "V"})
    assert s.api_url == "https://a.b/consent"
    assert s.headers == {"H": "V"}


def test_consulta_2xx_devuelve_json(monkeypatch, svc):
    """Cuando status 2xx y cuerpo JSON válido, devuelve el JSON."""
    resp = FakeResp(code=200, payload={"data": 123}, text="ok-text")
    monkeypatch.setattr(mod.requests, "post", lambda url, headers, json: resp)

    out = svc._consulta_consentimiento({"x": 1})
    assert out == {"data": 123}


def test_consulta_no_2xx_json(monkeypatch, svc):
    """Cuando status !2xx y cuerpo JSON válido, devuelve dict de error con código y cuerpo."""
    resp = FakeResp(code=500, payload={"data": 123}, text="err-text")
    monkeypatch.setattr(mod.requests, "post", lambda url, headers, json: resp)

    out = svc._consulta_consentimiento({"a": "b"})
    assert isinstance(out, dict)
    assert "error" in out
    assert "HTTP error occurred" in out["error"]
    assert "500" in out["error"]
    # El cuerpo JSON se incluye como representación de dict en el mensaje
    assert "123" in out["error"]  # para verificar que aparece el contenido del JSON


def test_consulta_no_2xx_no_json(monkeypatch, svc):
    """Cuando status !2xx y cuerpo no JSON, devuelve dict de error con el texto plano."""
    # FakeResp configurado para que .json() lance ValueError
    resp = FakeResp(code=503, payload=ValueError("no-json"), text="plain-text")
    monkeypatch.setattr(mod.requests, "post", lambda url, headers, json: resp)

    out = svc._consulta_consentimiento({"a": "b"})
    assert isinstance(out, dict)
    assert "error" in out
    assert "HTTP error occurred" in out["error"]
    assert "503" in out["error"]
    assert "plain-text" in out["error"]


@pytest.mark.parametrize(
    "indicador, esperado",
    [
        ("C", "Cliente: consentimiento ya aceptado."),
        ("P", "Precliente: consentimiento ya aceptado."),
        ("A", "Nueva alta: mail enviado para aceptar consentimiento."),
    ],
)
def test_call_mapea_indicador(monkeypatch, svc, indicador, esperado):
    """Mapea correctamente los valores de indicadorSituacion a los mensajes esperados."""
    monkeypatch.setattr(
        svc, "_consulta_consentimiento", lambda body: {"indicadorSituacion": indicador}
    )
    out = svc.call(FakeReq({"dni": "X"}))
    assert out == esperado


def test_call_devuelve_respuesta_cruda(monkeypatch, svc):
    """Si no hay indicadorSituacion reconocido, devuelve el dict crudo de la API."""
    monkeypatch.setattr(svc, "_consulta_consentimiento", lambda body: {"otro": "val"})
    out = svc.call(FakeReq({"dni": "Y"}))
    assert out == {"otro": "val"}


def test_call_manejo_excepcion(monkeypatch, svc):
    """Captura excepciones de _consulta_consentimiento y devuelve dict de error."""

    def raise_err(_):
        raise Exception("fallo-consent")

    monkeypatch.setattr(svc, "_consulta_consentimiento", raise_err)
    out = svc.call(FakeReq({"dni": "Z"}))
