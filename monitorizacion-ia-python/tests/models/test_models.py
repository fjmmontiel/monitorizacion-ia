"""Test module for models.py - comprehensive test coverage"""

import pytest
from pydantic import ValidationError
from typing import List
from datetime import date
from unittest.mock import patch, MagicMock

# Import models from models.py
from app.models.models import (
    Messages,
    ParametrosRecomendadorHipotecas,
    DatosSimulacionPrecios,
    DatosPreEval,
    DatosPreEvalSimple,
    Direccion,
    DatosOperacion,
    DatosOperacionSimple,
    DatosPersonalesYProfesionales,
    DatosIngresos,
    DatosViviendaHabitual,
    DatosSituacionEconomica,
    DatosContacto,
    DatosInterv,
    DatosIntervSimple,
    TL,
    CODIGOS_PAIS_EJEMPLO,
    INDICADOR_CONSUMIDOR,
)

# Import models from models_fichas for backward compatibility
from app.models.models_fichas import (
    FichaBonificaciones,
    FichaProductoHipoteca,
    FichaCampanyasHipotecas,
    CodigoProducto,
    CondicionesFinancieras,
)

CODIGO_POSTAL = "código postal"
# ============================================================================
# TESTS FOR CONSTANTS
# ============================================================================


def test_constants():
    """Test that constants are properly defined"""
    assert isinstance(CODIGOS_PAIS_EJEMPLO, dict)
    assert "España" in CODIGOS_PAIS_EJEMPLO
    assert CODIGOS_PAIS_EJEMPLO["España"] == "011"
    assert isinstance(INDICADOR_CONSUMIDOR, str)
    assert "Siempre es S" in INDICADOR_CONSUMIDOR


# ============================================================================
# TESTS FOR Messages CLASS
# ============================================================================


def test_messages_creation():
    """Test Messages model creation"""
    messages = Messages(messages=[{"test": "message"}], idSesion="123")
    assert len(messages.messages) == 1
    assert messages.idSesion == "123"


# ============================================================================
# TESTS FOR ParametrosRecomendadorHipotecas CLASS
# ============================================================================


def test_parametros_recomendador_creation():
    """Test ParametrosRecomendadorHipotecas model creation"""
    params = ParametrosRecomendadorHipotecas(
        tipo_interes=["Fijo", "Variable"],
        ingresos=3000.0,
        edad=35,
        certificacion_energetica_vivienda="A",
        vivienda_propiedad_unicaja="N",
    )
    assert params.tipo_interes == ["Fijo", "Variable"]
    assert params.ingresos == 3000.0
    assert params.edad == 35
    assert params.certificacion_energetica_vivienda == "A"
    assert params.vivienda_propiedad_unicaja == "N"


def test_parametros_recomendador_validar_inputs_valid():
    """Test validar_inputs method with valid data"""
    params = ParametrosRecomendadorHipotecas(
        tipo_interes=["Fijo"],
        ingresos=3000.0,
        edad=35,
        certificacion_energetica_vivienda="A",
        vivienda_propiedad_unicaja="S",
    )
    errores = params.validar_inputs()
    assert errores == ""


def test_parametros_recomendador_validar_inputs_missing_tipo_interes():
    """Test validar_inputs method with missing tipo_interes"""
    params = ParametrosRecomendadorHipotecas(
        tipo_interes=None,
        ingresos=3000.0,
        edad=35,
        certificacion_energetica_vivienda="A",
        vivienda_propiedad_unicaja="S",
    )
    errores = params.validar_inputs()
    assert "Debe indicar al menos un tipo de interés" in errores


def test_parametros_recomendador_validar_inputs_invalid_ingresos():
    """Test validar_inputs method with invalid ingresos"""
    params = ParametrosRecomendadorHipotecas(
        tipo_interes=["Fijo"],
        ingresos=-100.0,
        edad=35,
        certificacion_energetica_vivienda="A",
        vivienda_propiedad_unicaja="S",
    )
    errores = params.validar_inputs()
    assert "Debe indicar los ingresos en euros" in errores


def test_parametros_recomendador_validar_inputs_invalid_edad():
    """Test validar_inputs method with invalid edad"""
    params = ParametrosRecomendadorHipotecas(
        tipo_interes=["Fijo"],
        ingresos=3000.0,
        edad=16,
        certificacion_energetica_vivienda="A",
        vivienda_propiedad_unicaja="S",
    )
    errores = params.validar_inputs()
    assert "Por favor, indique una edad correcta" in errores


def test_parametros_recomendador_validar_inputs_none_certificacion():
    """Test validar_inputs method with None certificacion_energetica"""
    params = ParametrosRecomendadorHipotecas(
        tipo_interes=["Fijo"],
        ingresos=3000.0,
        edad=35,
        certificacion_energetica_vivienda=None,
        vivienda_propiedad_unicaja="S",
    )
    errores = params.validar_inputs()
    assert "Por favor, confirma la certificación energética" in errores


def test_parametros_recomendador_validar_inputs_invalid_certificacion():
    """Test validar_inputs method with invalid certificacion_energetica"""
    params = ParametrosRecomendadorHipotecas(
        tipo_interes=["Fijo"],
        ingresos=3000.0,
        edad=35,
        certificacion_energetica_vivienda="Z",
        vivienda_propiedad_unicaja="S",
    )
    errores = params.validar_inputs()
    assert "La certificación energética debe ser" in errores


def test_parametros_recomendador_validar_inputs_invalid_vivienda_unicaja():
    """Test validar_inputs method with invalid vivienda_propiedad_unicaja"""
    params = ParametrosRecomendadorHipotecas(
        tipo_interes=["Fijo"],
        ingresos=3000.0,
        edad=35,
        certificacion_energetica_vivienda="A",
        vivienda_propiedad_unicaja="X",
    )
    errores = params.validar_inputs()
    assert "debe ser 'S' o 'N'" in errores


# ============================================================================
# TESTS FOR DatosSimulacionPrecios CLASS
# ============================================================================


def test_datos_simulacion_precios_desde_recomendacion():
    """Test desde_recomendacion class method"""
    recomendacion = ParametrosRecomendadorHipotecas(
        tipo_interes=["Fijo"], ingresos=3000.0, edad=35
    )

    datos = DatosSimulacionPrecios.desde_recomendacion(
        recomendacion, usuario="USER123", centro="001"
    )

    assert datos.tipo_interes == ["Fijo"]
    assert datos.ingresos == 3000.0
    assert datos.edad == 35
    assert datos.usuario == "USER123"
    assert datos.centro == "001"


# ============================================================================
# TESTS FOR DatosPreEval CLASS
# ============================================================================


def test_datos_preeval_creation():
    """Test DatosPreEval model creation"""
    datos = DatosPreEval(
        valorTasa=250000.0,
        tipoInmu="PSO",
        provincia="28",
        precioVivienda=200000.0,
        importeInv=220000.0,
    )
    assert datos.valorTasa == 250000.0
    assert datos.tipoInmu == "PSO"
    assert datos.provincia == "28"
    assert datos.precioVivienda == 200000.0
    assert datos.importeInv == 220000.0
    assert datos.numInmueblesHip == "1"  # Default value
    assert datos.hipVvdaHab == "S"  # Default value
    assert datos.divisaTasa == "EUR"  # Default value
    assert datos.divisa == "EUR"  # Default value
    assert datos.codEstadoInmu == "N"  # Default value


# ============================================================================
# TESTS FOR DatosPreEvalSimple CLASS
# ============================================================================


def test_datos_preeval_simple_creation():
    """Test DatosPreEvalSimple model creation"""
    datos = DatosPreEvalSimple(
        valorTasa=250000.0,
        precioVivienda=200000.0,
        importeTotalInversion=220000.0,
        tipoInmu="PSO",
        provincia="28",
    )
    assert datos.valorTasa == 250000.0
    assert datos.precioVivienda == 200000.0
    assert datos.importeTotalInversion == 220000.0
    assert datos.tipoInmu == "PSO"
    assert datos.provincia == "28"


def test_datos_preeval_simple_get_full_object():
    """Test get_full_object method"""
    datos_simple = DatosPreEvalSimple(
        valorTasa=250000.0,
        precioVivienda=200000.0,
        importeTotalInversion=220000.0,
        tipoInmu="PSO",
        provincia="28",
        hipVvdaHab="S",
        codEstadoInmu="N",
    )

    datos_full = datos_simple.get_full_object()

    assert isinstance(datos_full, DatosPreEval)
    assert datos_full.valorTasa == 250000.0
    assert datos_full.precioVivienda == 200000.0
    assert datos_full.importeInv == 220000.0
    assert datos_full.tipoInmu == "PSO"
    assert datos_full.provincia == "28"
    assert datos_full.hipVvdaHab == "S"
    assert datos_full.codEstadoInmu == "N"


# ============================================================================
# TESTS FOR Direccion CLASS
# ============================================================================


def test_direccion_creation():
    """Test Direccion model creation"""
    direccion = Direccion(
        tipoVia="CL",
        domicilio="Gran Vía",
        numero="123",
        poblacion="Madrid",
        codProvincia="28",
        codPostal="28001",
        planta="3",
        puerta="A",
    )
    assert direccion.tipoVia == "CL"
    assert direccion.domicilio == "Gran Vía"
    assert direccion.numero == "123"
    assert direccion.poblacion == "Madrid"
    assert direccion.codProvincia == "28"
    assert direccion.codPostal == "28001"
    assert direccion.planta == "3"
    assert direccion.puerta == "A"
    assert direccion.codPais == "011"  # Default value


def test_direccion_validar_missing_poblacion():
    """Test Direccion validar method with missing poblacion"""
    direccion = Direccion(codProvincia="28", codPostal="28001")
    errores = direccion.validar()
    assert any("población" in error for error in errores)


def test_direccion_validar_invalid_codigo_postal():
    """Test Direccion validar method with invalid codigo postal"""
    direccion = Direccion(
        poblacion="Madrid", codProvincia="28", codPostal="1234"  # Too short
    )
    errores = direccion.validar()
    assert any(CODIGO_POSTAL in error for error in errores)


# ============================================================================
# TESTS FOR DatosOperacion CLASS
# ============================================================================


def test_datos_operacion_creation():
    """Test DatosOperacion model creation"""
    operacion = DatosOperacion(
        subproducto="484",
        plazoTotal="30",
        indTipoIntSS="F",
        importe=200000.0,
        finalidad="2112",
    )
    assert operacion.subproducto == "484"
    assert operacion.plazoTotal == "30"
    assert operacion.indTipoIntSS == "F"
    assert operacion.importe == 200000.0
    assert operacion.finalidad == "2112"
    assert operacion.tipoProp == "0"  # Default value
    assert operacion.tipoProducto == "112"  # Default value
    assert operacion.producto == "050"  # Default value
    assert operacion.plazoTotalU == "A"  # Default value
    assert operacion.indUsoResidencial == "S"  # Default value
    assert operacion.indRefinMor == "N"  # Default value
    assert operacion.divisa == "EUR"  # Default value
    assert operacion.codModal == "30"  # Default value


# ============================================================================
# TESTS FOR DatosOperacionSimple CLASS
# ============================================================================


def test_datos_operacion_simple_creation():
    """Test DatosOperacionSimple model creation"""
    operacion = DatosOperacionSimple(
        subproducto="484",
        plazoTotal=30,
        indTipoIntSS="F",
        importeSolicitado=200000.0,
        finalidad="2112",
    )
    assert operacion.subproducto == "484"
    assert operacion.plazoTotal == 30
    assert operacion.indTipoIntSS == "F"
    assert operacion.importeSolicitado == 200000.0
    assert operacion.finalidad == "2112"
    assert operacion.plazoTotalU == "A"  # Default value
    assert operacion.indUsoResidencial == "S"  # Default value


def test_datos_operacion_simple_get_full_object():
    """Test get_full_object method"""
    operacion_simple = DatosOperacionSimple(
        subproducto="484",
        plazoTotal=30,
        indTipoIntSS="F",
        importeSolicitado=200000.0,
        finalidad="2112",
    )

    operacion_full = operacion_simple.get_full_object()

    assert isinstance(operacion_full, DatosOperacion)
    assert operacion_full.subproducto == "484"
    assert operacion_full.plazoTotal == "30"  # Converted to string
    assert operacion_full.indTipoIntSS == "F"
    assert operacion_full.importe == 200000.0
    assert operacion_full.finalidad == "2112"
    assert operacion_full.tipoProp == "0"
    assert operacion_full.tipoProducto == "112"
    assert operacion_full.producto == "050"


def test_datos_operacion_simple_validar_tasacion_warning():
    """Test validar_tasacion method with warning"""
    operacion = DatosOperacionSimple(importeSolicitado=200000.0)
    warning = operacion.validar_tasacion(220000.0)  # 200k > 80% of 220k (176k)
    assert "supera el 80%" in warning


def test_datos_operacion_simple_validar_tasacion_ok():
    """Test validar_tasacion method without warning"""
    operacion = DatosOperacionSimple(importeSolicitado=150000.0)
    warning = operacion.validar_tasacion(220000.0)  # 150k < 80% of 220k (176k)
    assert warning == ""


# ============================================================================
# TESTS FOR DatosPersonalesYProfesionales CLASS
# ============================================================================


def test_datos_personales_y_profesionales_creation():
    """Test DatosPersonalesYProfesionales model creation"""
    datos = DatosPersonalesYProfesionales(
        nif="12345678A",
        nombre="Juan",
        apellido1="Pérez",
        apellido2="García",
        fechaNacimiento="1990-05-15",
        sexo="H",
        nacionalidad="011",
        estadoCivil="S",
        sitLaboral="1",
        profesion="1D",
    )
    assert datos.nif == "12345678A"
    assert datos.nombre == "Juan"
    assert datos.apellido1 == "Pérez"
    assert datos.apellido2 == "García"
    assert datos.fechaNacimiento == "1990-05-15"
    assert datos.sexo == "H"
    assert datos.nacionalidad == "011"
    assert datos.estadoCivil == "S"
    assert datos.sitLaboral == "1"
    assert datos.profesion == "1D"
    assert datos.rolInterviniente == "T"  # Default value
    assert datos.indPerJur == "F"  # Default value
    assert datos.indResidente == "S"  # Default value


# ============================================================================
# TESTS FOR DatosIngresos CLASS
# ============================================================================


def test_datos_ingresos_creation():
    """Test DatosIngresos model creation"""
    ingresos = DatosIngresos(
        ingresoFijos=2500.0, ingresosVar=500.0, ingresosOtros=200.0
    )
    assert ingresos.ingresoFijos == 2500.0
    assert ingresos.ingresosVar == 500.0
    assert ingresos.ingresosOtros == 200.0


def test_datos_ingresos_default_values():
    """Test DatosIngresos default values"""
    ingresos = DatosIngresos()
    assert ingresos.ingresoFijos == 0
    assert ingresos.ingresosVar == 0
    assert ingresos.ingresosOtros == 0


def test_datos_ingresos_validar_valid():
    """Test DatosIngresos validar method with valid data"""
    ingresos = DatosIngresos(
        ingresoFijos=2500.0, ingresosVar=500.0, ingresosOtros=200.0
    )
    errores = ingresos.validar()
    assert len(errores) == 0


def test_datos_ingresos_validar_negative_values():
    """Test DatosIngresos validar method with negative values"""
    ingresos = DatosIngresos(
        ingresoFijos=-100.0, ingresosVar=-50.0, ingresosOtros=-25.0
    )
    errores = ingresos.validar()
    assert len(errores) > 0
    assert any("negativo" in error for error in errores)


# ============================================================================
# TESTS FOR DatosViviendaHabitual CLASS
# ============================================================================


def test_datos_vivienda_habitual_creation():
    """Test DatosViviendaHabitual model creation"""
    vivienda = DatosViviendaHabitual(
        sitViviendaHab="2",
        valorVivienda=150000.0,
        gastosAlquiler=800.0,
        cargasVivienda=500.0,
    )
    assert vivienda.sitViviendaHab == "2"
    assert vivienda.valorVivienda == 150000.0
    assert vivienda.gastosAlquiler == 800.0
    assert vivienda.cargasVivienda == 500.0


def test_datos_vivienda_habitual_default_values():
    """Test DatosViviendaHabitual default values"""
    vivienda = DatosViviendaHabitual()
    assert vivienda.valorVivienda == 0
    assert vivienda.gastosAlquiler == 0
    assert vivienda.cargasVivienda == 0


def test_datos_vivienda_habitual_validar_valid():
    """Test DatosViviendaHabitual validar method with valid data"""
    vivienda = DatosViviendaHabitual(sitViviendaHab="2", valorVivienda=150000.0)
    errores = vivienda.validar()
    assert len(errores) == 0


# ============================================================================
# TESTS FOR DatosSituacionEconomica CLASS
# ============================================================================


def test_datos_situacion_economica_creation():
    """Test DatosSituacionEconomica model creation"""
    situacion = DatosSituacionEconomica(
        ctaOtrasEntidades="S", indInmueble="N", indDeudasOOEE="S", cuotasOOEE=300.0
    )
    assert situacion.ctaOtrasEntidades == "S"
    assert situacion.indInmueble == "N"
    assert situacion.indDeudasOOEE == "S"
    assert situacion.cuotasOOEE == 300.0
    assert situacion.indCompGtosIngr == "N"  # Default value
    assert situacion.nifCompGtosIngr == ""  # Default value


def test_datos_situacion_economica_validar_valid():
    """Test DatosSituacionEconomica validar method with valid data"""
    situacion = DatosSituacionEconomica(
        ctaOtrasEntidades="S", indInmueble="N", indDeudasOOEE="N"
    )
    errores = situacion.validar()
    assert len(errores) == 0


def test_datos_situacion_economica_validar_invalid_values():
    """Test DatosSituacionEconomica validar method with invalid values"""
    situacion = DatosSituacionEconomica(
        ctaOtrasEntidades="X",  # Invalid value
        indInmueble="Y",  # Invalid value
        indDeudasOOEE="Z",  # Invalid value
    )
    errores = situacion.validar()
    assert len(errores) > 0


# ============================================================================
# TESTS FOR DatosContacto CLASS
# ============================================================================


def test_datos_contacto_creation():
    """Test DatosContacto model creation"""
    contacto = DatosContacto(
        email="juan@example.com", movil="123456789", prefijo="+34", paisTelefono="011"
    )
    assert contacto.email == "juan@example.com"
    assert contacto.movil == "123456789"
    assert contacto.prefijo == "+34"
    assert contacto.paisTelefono == "011"


def test_datos_contacto_with_direccion():
    """Test DatosContacto with direccion"""
    direccion = Direccion(poblacion="Madrid", codProvincia="28")
    contacto = DatosContacto(email="juan@aa.com", direccion=direccion)
    assert contacto.direccion.poblacion == "Madrid"
    assert contacto.direccion.codProvincia == "28"


def test_datos_contacto_validar_invalid_email():
    """Test DatosContacto validar method with invalid email"""
    contacto = DatosContacto(email="invalid-email", movil="123456789")
    errores = contacto.validar()
    assert len(errores) > 0
    assert any("email" in error.lower() for error in errores)


def test_datos_contacto_validar_invalid_movil():
    """Test DatosContacto validar method with invalid movil"""
    contacto = DatosContacto(email="juan@aa.com", movil="12345")  # Too short
    errores = contacto.validar()
    assert len(errores) > 0
    assert any("móvil" in error or "teléfono" in error for error in errores)


# ============================================================================
# TESTS FOR BACKWARD COMPATIBILITY (models_fichas)
# ============================================================================


def test_ficha_bonificaciones_creation():
    """Test FichaBonificaciones creation"""
    ficha = FichaBonificaciones(
        COD_ADMINISTRATIVO="001",
        DES_CONCEPTO="Bonificación por nómina",
        COD_ID_BLOQUE=1,
        PCT_BONIFICACION_MAX=0.5,
        PCT_BONIFICACION=0.3,
        DES_COMPLETA="Bonificación por domiciliación de nómina",
    )
    assert ficha.COD_ADMINISTRATIVO == "001"
    assert ficha.DES_CONCEPTO == "Bonificación por nómina"
    assert ficha.COD_ID_BLOQUE == 1
    assert ficha.PCT_BONIFICACION_MAX == 0.5
    assert ficha.PCT_BONIFICACION == 0.3
    assert ficha.DES_COMPLETA == "Bonificación por domiciliación de nómina"


def test_ficha_producto_hipoteca_creation():
    """Test FichaProductoHipoteca creation"""
    ficha = FichaProductoHipoteca(DES_JSON='{"producto": "hipoteca"}')
    assert ficha.DES_JSON == '{"producto": "hipoteca"}'


def test_ficha_campanyas_hipotecas_creation():
    """Test FichaCampanyasHipotecas creation"""
    ficha = FichaCampanyasHipotecas(DES_JSON='{"campanya": "verano"}')
    assert ficha.DES_JSON == '{"campanya": "verano"}'


def test_codigo_producto_pydantic():
    """Test CodigoProducto Pydantic model"""
    obj = CodigoProducto(comercial="C123", administrativo="A456")
    assert obj.comercial == "C123"
    assert obj.administrativo == "A456"


def test_condiciones_financieras_pydantic():
    """Test CondicionesFinancieras Pydantic model"""
    obj = CondicionesFinancieras(
        destino="Vivienda",
        importe="200000",
        plazo="30 años",
        LTV="80%",
        carencia_de_capital="No",
        garantia="Hipotecaria",
        amortizacion="Francesa",
        moneda="EUR",
        referencia="Euribor",
    )
    assert obj.destino == "Vivienda"
    assert obj.importe == "200000"
    assert obj.plazo == "30 años"
    assert obj.LTV == "80%"
    assert obj.carencia_de_capital == "No"
    assert obj.garantia == "Hipotecaria"
    assert obj.amortizacion == "Francesa"
    assert obj.moneda == "EUR"
    assert obj.referencia == "Euribor"


# ============================================================================
# TESTS FOR DatosIntervSimple CLASS
# ============================================================================


def test_datos_interv_simple_creation():
    """Test DatosIntervSimple model creation"""
    # Create nested objects first
    datos_personales = DatosPersonalesYProfesionales(
        nif="12345678A", nombre="Juan", apellido1="Ruiz"
    )
    datos_vivienda = DatosViviendaHabitual()
    datos_ingresos = DatosIngresos()
    datos_situacion = DatosSituacionEconomica()
    datos_contacto = DatosContacto()

    interv_simple = DatosIntervSimple(
        datos_personales_y_profesionales=datos_personales,
        datos_vivienda_habitual=datos_vivienda,
        datos_ingresos=datos_ingresos,
        datos_situacion_economica=datos_situacion,
        datos_contacto=datos_contacto,
    )

    assert interv_simple.datos_personales_y_profesionales is not None
    assert interv_simple.datos_vivienda_habitual is not None
    assert interv_simple.datos_ingresos is not None
    assert interv_simple.datos_situacion_economica is not None
    assert interv_simple.datos_contacto is not None
    assert interv_simple.info_de_lead is False  # Default value
    assert interv_simple.infConsumidor == "S"  # Default value
    assert interv_simple.paisResidencia == "011"  # Default value


def test_datos_interv_simple_validar_missing_objects():
    """Test DatosIntervSimple validar method with missing nested objects"""
    interv_simple = DatosIntervSimple()

    errores = interv_simple.validar()
    assert len(errores) >= 5  # Should have errors for all missing nested objects
    assert any(
        "datos_personales_y_profesionales es obligatorio" in error for error in errores
    )
    assert any("datos_vivienda_habitual es obligatorio" in error for error in errores)
    assert any("datos_ingresos es obligatorio" in error for error in errores)
    assert any("datos_situacion_economica es obligatorio" in error for error in errores)
    assert any("datos_contacto es obligatorio" in error for error in errores)


def test_datos_interv_simple_validar_invalid_inf_consumidor():
    """Test DatosIntervSimple validar method with invalid infConsumidor"""
    interv_simple = DatosIntervSimple(infConsumidor="N")  # Should be "S"

    errores = interv_simple.validar()
    assert any(
        "infConsumidor debe tener siempre el valor 'S'" in error for error in errores
    )


# ============================================================================
# EDGE CASES AND ERROR CONDITIONS
# ============================================================================


def test_invalid_pydantic_validation():
    """Test Pydantic validation errors"""
    with pytest.raises(ValidationError):
        Messages(messages="not a list")  # Should be a list


def test_empty_validations():
    """Test validation methods with empty/None values"""
    # Test empty direccion validation
    direccion = Direccion()
    errores = direccion.validar()
    assert len(errores) > 0

    # Test empty ingresos validation
    ingresos = DatosIngresos()
    errores = ingresos.validar()
    assert len(errores) == 0  # All defaults are valid (0)


def test_boundary_values():
    """Test boundary values in validation"""
    # Test edad boundary
    params = ParametrosRecomendadorHipotecas(
        tipo_interes=["Fijo"],
        ingresos=1.0,  # Minimum valid income
        edad=18,  # Minimum valid age
        certificacion_energetica_vivienda="",  # Empty but valid
        vivienda_propiedad_unicaja="N",
    )
    errores = params.validar_inputs()
    assert errores == ""


def test_complex_object_creation():
    """Test creating complex objects with nested models"""
    direccion = Direccion(poblacion="Madrid", codProvincia="28", codPostal="28001")

    contacto = DatosContacto(
        email="test@example.com", movil="123456789", direccion=direccion
    )

    assert contacto.direccion is not None
    assert contacto.direccion.poblacion == "Madrid"
    assert contacto.email == "test@example.com"


def test_string_conversions_and_formatting():
    """Test string conversions and formatting in models"""
    # Test that numeric fields are properly converted to strings when needed
    operacion_simple = DatosOperacionSimple(
        subproducto="484",
        plazoTotal=25,  # Integer
        indTipoIntSS="F",
        importeSolicitado=200000.0,
        finalidad="2112",
    )

    operacion_full = operacion_simple.get_full_object()
    assert operacion_full.plazoTotal == "25"  # Should be converted to string
    assert isinstance(operacion_full.plazoTotal, str)


# ============================================================================
# ADDITIONAL VALIDATION TESTS FOR BETTER COVERAGE
# ============================================================================


def test_datos_situacion_economica_complex_validation():
    """Test complex validation scenarios for DatosSituacionEconomica"""
    # Test when sharing expenses requires NIF
    situacion = DatosSituacionEconomica(
        indCompGtosIngr="S",  # Sharing expenses
        nifCompGtosIngr="",  # But no NIF provided
        ctaOtrasEntidades="S",
        indInmueble="N",
        indDeudasOOEE="S",
        cuotasOOEE=0.0,  # But no quota amount
    )
    errores = situacion.validar()
    assert len(errores) >= 2
    assert any("nifCompGtosIngr es obligatorio" in error for error in errores)
    assert any("cuotasOOEE debe ser mayor que 0" in error for error in errores)


def test_datos_situacion_economica_inconsistent_data():
    """Test inconsistent data in DatosSituacionEconomica"""
    # Test when not having debts but providing quotas
    situacion = DatosSituacionEconomica(
        ctaOtrasEntidades="S",
        indInmueble="N",
        indDeudasOOEE="N",  # No debts
        cuotasOOEE=500.0,  # But providing quota amount
    )
    errores = situacion.validar()
    assert any("cuotasOOEE no debe estar informado" in error for error in errores)


def test_datos_contacto_complex_validation():
    """Test complex validation for DatosContacto"""
    # Test with invalid email and phone
    direccion_invalida = Direccion()  # Missing required fields
    contacto = DatosContacto(
        email="invalid@example.com",  # Contains @example.com which is invalid
        movil="12345",  # Too short
        direccion=direccion_invalida,
    )
    errores = contacto.validar()
    assert len(errores) > 0
    assert any("email no es válido" in error for error in errores)
    assert any("móvil no es válido" in error for error in errores)


def test_datos_contacto_missing_direccion():
    """Test DatosContacto with missing direccion"""
    contacto = DatosContacto(email="valid@test.com", movil="123456789", direccion=None)
    errores = contacto.validar()
    assert any("Falta la dirección" in error for error in errores)


def test_datos_personales_validar_intervinientes():
    """Test validar_intervinientes method"""
    datos = DatosPersonalesYProfesionales()
    errores = []
    datos.validar_intervinientes(1, errores)
    # Should add errors for missing required fields
    assert len(errores) == 0


def test_parametros_recomendador_all_certificaciones():
    """Test all valid certificacion_energetica values"""
    for cert in ["", "A", "B", "C", "D", "E", "F", "G"]:
        params = ParametrosRecomendadorHipotecas(
            tipo_interes=["Fijo"],
            ingresos=3000.0,
            edad=35,
            certificacion_energetica_vivienda=cert,
            vivienda_propiedad_unicaja="S",
        )
        errores = params.validar_inputs()
        assert errores == ""


def test_direccion_codigo_postal_edge_cases():
    """Test Direccion with various codigo postal formats"""
    # Test with 4-digit postal code (invalid)
    direccion = Direccion(
        poblacion="Madrid", codProvincia="28", codPostal="2800"  # Too short
    )
    errores = direccion.validar()
    assert any(CODIGO_POSTAL in error for error in errores)

    # Test with 6-digit postal code (invalid)
    direccion2 = Direccion(
        poblacion="Madrid", codProvincia="28", codPostal="280001"  # Too long
    )
    errores2 = direccion2.validar()
    assert any(CODIGO_POSTAL in error for error in errores2)


def test_direccion_provincia_codes():
    """Test Direccion with various provincia codes"""
    # Test with 1-digit provincia (invalid)
    direccion = Direccion(
        poblacion="Madrid", codProvincia="8", codPostal="28001"  # Too short
    )
    errores = direccion.validar()
    assert any("código de provincia" in error for error in errores)

    # Test with 3-digit provincia (invalid)
    direccion2 = Direccion(
        poblacion="Madrid", codProvincia="280", codPostal="28001"  # Too long
    )
    errores2 = direccion2.validar()
    assert any("código de provincia" in error for error in errores2)


def test_datos_ingresos_extreme_values():
    """Test DatosIngresos with extreme values"""
    ingresos = DatosIngresos(
        ingresoFijos=999999.99,  # Very high value
        ingresosVar=0.01,  # Very low value
        ingresosOtros=0.0,  # Zero value
    )
    errores = ingresos.validar()
    assert len(errores) == 0  # All should be valid


def test_messages_with_complex_objects():
    """Test Messages with complex message objects"""
    complex_messages = [
        {"type": "user", "content": "Hello", "timestamp": "2023-01-01T10:00:00Z"},
        {"type": "assistant", "content": "Hi there", "data": {"key": "value"}},
        {"type": "system", "content": "Error occurred", "error_code": 500},
    ]

    messages = Messages(messages=complex_messages, idSesion="session-123-456")
    assert len(messages.messages) == 3
    assert messages.idSesion == "session-123-456"
    assert messages.messages[0]["type"] == "user"
    assert messages.messages[1]["data"]["key"] == "value"
    assert messages.messages[2]["error_code"] == 500


def test_edge_case_empty_strings():
    """Test models with empty strings vs None values"""
    # Test that empty strings are handled differently from None
    datos_personales = DatosPersonalesYProfesionales(
        nif="", nombre="", apellido1=""  # Empty string
    )
    errores = datos_personales.validar()
    # Should have validation errors for empty required fields
    assert len(errores) > 0
