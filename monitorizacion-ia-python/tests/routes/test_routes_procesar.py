"""Tests para endpoints adicionales de procesamiento y contexto distribuido.

Este módulo prueba:
- `procesar_ficha_campana`: procesa PDFs de campañas.
- `procesar_traducciones`: procesa Excels de traducciones.
- `procesar_ficha_producto`: procesa PDFs y guarda fichas de producto.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import pandas as pd
from pathlib import Path
from qgdiag_lib_arquitectura.exceptions.types import ExceptionTErrorInterno

# Importar funciones a testear
from app.routes.routes import (
    procesar_ficha_producto,
    procesar_ficha_campana,
    procesar_traducciones,
)

# ==== TEST procesar_ficha_campana ====


class TestProcesarFichaCampana:
    """Pruebas para `procesar_ficha_campana`."""

    @pytest.mark.asyncio
    async def test_procesar_ficha_campana_error(self):
        """Lanza ExceptionTErrorInterno si ocurre error inesperado."""
        db_session = MagicMock()
        headers = {"Token": "abc"}
        with patch(
            "app.routes.routes.LecturaFichaCampanyaService",
            side_effect=Exception("fallo"),
        ):
            with pytest.raises(ExceptionTErrorInterno) as exc:
                await procesar_ficha_campana(db_session=db_session, headers=headers)
            assert exc.value.status_code == 500


# ==== TEST procesar_ficha_producto ====
class TestProcesarFichaProducto:
    """Pruebas para `procesar_ficha_producto`."""

    @pytest.mark.asyncio
    async def test_procesar_ficha_producto_ok(self):
        """Procesa PDFs y devuelve respuesta exitosa."""
        db_session = MagicMock()
        headers = {"Token": "abc"}

        lectura_service = MagicMock()
        lectura_service.procesar.return_value = {"producto": "mock"}
        lectura_service.guardar_ficha_producto.return_value = True

        # conexion_modelo es una corrutina (se usa 'await'), por ello AsyncMock
        with patch(
            "app.routes.routes.LecturaFichaProductoService",
            return_value=lectura_service,
        ), patch(
            "app.routes.routes.conexion_modelo",
            new=AsyncMock(return_value="cliente"),
        ), patch(
            "app.routes.routes.Path.glob",
            return_value=[Path("file1.pdf"), Path("file2.pdf")],
        ), patch(
            "app.routes.routes.GlobalConstants.MESSAGE_EXECUTE_ENDPOINT_PROCESS_200_SUCCESS",
            "OK",
        ):
            result = await procesar_ficha_producto(
                db_session=db_session, headers=headers
            )
            assert result["estado"] == 200
            assert "OK" in result["detalle"]
            assert isinstance(result["contenido"], list)
            lectura_service.procesar.assert_called()

    @pytest.mark.asyncio
    async def test_procesar_ficha_producto_error(self):
        """Lanza ExceptionTErrorInterno si ocurre error inesperado."""
        db_session = MagicMock()
        headers = {"Token": "abc"}
        with patch(
            "app.routes.routes.LecturaFichaProductoService",
            side_effect=Exception("fallo"),
        ):
            with pytest.raises(ExceptionTErrorInterno) as exc:
                await procesar_ficha_producto(db_session=db_session, headers=headers)
