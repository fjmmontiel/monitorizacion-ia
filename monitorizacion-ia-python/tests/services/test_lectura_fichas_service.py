"""Tests  para el servicio de lectura de fichas."""

import pytest
from unittest.mock import MagicMock, patch
from app.services.lectura_fichas_service import (
    leer_pdf,
    conversion_doc_pdf,
)


from pathlib import Path


def test_leer_pdf():
    """Modulo para test"""

    mock_loader = MagicMock()
    mock_page1 = MagicMock()
    mock_page1.page_content = "Página 1"
    mock_page2 = MagicMock()
    mock_page2.page_content = "Página 2"
    mock_loader.load.return_value = [mock_page1, mock_page2]

    with patch(
        "app.services.lectura_fichas_service.PyPDFLoader", return_value=mock_loader
    ):
        resultado = leer_pdf("dummy_path.pdf")
        assert resultado == "Página 1\nPágina 2"


def test_conversion_doc_pdf_success():
    """Modulo para test"""

    docx_path = Path("archivo.docx")
    output_pdf_path = docx_path.with_suffix(".pdf")
    with patch(
        "app.services.lectura_fichas_service.convert", return_value=None
    ) as mock_convert, patch(
        "app.services.lectura_fichas_service.logger"
    ) as mock_logger:
        result = conversion_doc_pdf(docx_path)
        mock_convert.assert_called_once_with(docx_path, output_pdf_path)
        mock_logger.info.assert_called_once()
        assert result == output_pdf_path


def test_conversion_doc_pdf_exception():
    """Modulo para test"""

    docx_path = Path("archivo.docx")
    with patch(
        "app.services.lectura_fichas_service.convert", side_effect=Exception("fail")
    ), patch("app.services.lectura_fichas_service.logger"):
        result = conversion_doc_pdf(docx_path)
        assert result is False
