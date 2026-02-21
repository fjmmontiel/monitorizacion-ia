"""Tests para endpoints adicionales de procesamiento y contexto distribuido.

Este módulo prueba:
- `get_sesion_list`: obtiene listado de sesiones.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from types import SimpleNamespace

from app.routes.routes import (
    get_sesion_list,
)


# ==== TEST get_sesion_list ====
class TestGetSesionList:
    """Pruebas para `get_sesion_list`."""

    @pytest.mark.asyncio
    async def test_get_sesion_list_ok_con_sesiones(self):
        """Devuelve listado de sesiones sin campo 'conversacion'."""
        options = SimpleNamespace()  # o MagicMock si no se usa internamente
        # Objeto de sesión con atributos simples
        session_obj = SimpleNamespace(
            session_id="sess1",
            input_tokens=0,
            output_tokens=0,
            cost=0.0,
            valoracion=-1,
            comentarios="",
            muestra_de_interes=0,
            session_duration=0,
            session_start=None,
            session_end=None,
            centro="OVIEDO",
            gestor="G001",
            conversacion="texto",
            ultima_llamada_guardar_muestra_de_interes="",
        )

        with patch("app.routes.routes.SessionDAO") as mock_dao:
            mock_dao.return_value.get_sessions.return_value = [session_obj]
            result = await get_sesion_list(options)

        assert isinstance(result, JSONResponse)
        assert result.status_code == 200
        contenido = result.body.decode()
        assert "sess1" in contenido
        assert "conversacion" not in contenido

    @pytest.mark.asyncio
    async def test_get_sesion_list_ok_vacio(self):
        """Devuelve lista vacía si no hay sesiones."""
        options = MagicMock()
        with patch("app.routes.routes.SessionDAO") as mock_dao:
            mock_dao.return_value.get_sessions.return_value = []
            result = await get_sesion_list(options)
            assert isinstance(result, JSONResponse)
            assert result.status_code == 200
            assert result.body.decode() == "[]"
