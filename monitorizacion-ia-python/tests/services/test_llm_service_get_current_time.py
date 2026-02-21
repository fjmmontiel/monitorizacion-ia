""" Modulo para test """

import pytest
import datetime
from unittest.mock import MagicMock, patch
from app.services.llm_service import get_current_time 

@pytest.mark.asyncio
async def test_get_current_time_format():
    """ Modulo para test """


    result = await get_current_time.arun({})
    # Se verifica que sea string y tenga el formato correcto
    assert isinstance(result, str)
    datetime.datetime.strptime(result, "%Y-%m-%d %H:%M:%S")


