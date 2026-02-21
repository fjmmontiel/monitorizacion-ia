/* istanbul ignore file */
export const items_mock = `[{
  "id": "e3fc4f49-9ae9-4fc3-9057-4ab14d835d9d",
  "name": "Gestor 1",
  "item_type": "DataGestor",
  "tab": "",
  "data": {
    "codigo": "UX9235A",
    "centro": "7383"
  },
  "llm_header": "Información del gestor"
},
{
  "id": "c5ec0f00-3b80-4067-89d2-099b85a6fb44",
  "name": "Recomendación 1",
  "item_type": "RecomendacionHipoteca",
  "tab": "",
  "data": {
    "tipo_interes": [
      "Variable"
    ],
    "ingresos": 2000.0,
    "edad": 27,
    "certificacion_energetica_vivienda": "",
    "resultado_recomendacion": [
      {
        "nombre_producto": "Hipoteca tipo variable Oportunidad",
        "codigo_producto": {
          "comercial": "112031",
          "administrativo": "050110"
        },
        "descripcion_producto": "Préstamo con garantía hipotecaria a tipo variable, en la cual los ingresos de los titulares de la hipoteca (nómina, pensión, prestación o ingresos recurrentes) deben ser de al menos 2.000 € mensuales y cuyo tipo de interés puede reducirse en función de la contratación y mantenimiento de productos.",
        "publico_objetivo": "Personas físicas cuya suma de ingresos netos mensuales sea de al menos 2.000 €, que necesiten financiación para la adquisición o autoconstrucción de vivienda, vinculados con la Entidad por la domiciliación de ingresos o mantenimiento de productos y que cuenten con recorrido para la contratación de nuevas líneas comerciales que les posibiliten una reducción del tipo de interés.",
        "condiciones_financieras": {
          "destino": "Adquisición/autoconstrucción/rehabilitación de vivienda, siempre y cuando no sea la actividad empresarial principal del prestatario.",
          "importe": "Desde 50.000 euros.",
          "plazo": "Desde 8 años. Hasta 30 años para residencia de uso propio, siempre que la edad de los titulares más el plazo de la operación no sea superior a 75 años para primera residencia uso propio y 70 años para segunda. Para destino alquiler siempre que no sea la actividad empresarial principal de prestatario, plazo máximo 20 años, siempre que la edad de cada uno de los titulares más plazo de la operación no sea superior a 70 años.",
          "LTV": "Hasta el 80% del menor de los dos valores, tasación o precio de compra en escritura pública. Para segunda residencia uso propio, el menor de los valores entre el 70% del valor de tasación y el 80% del precio de compra en escritura.",
          "carencia_de_capital": "Hasta 24 meses (únicamente en autoconstrucción de vivienda habitual) durante los cuales se liquidarán intereses trimestralmente sobre el capital dispuesto en cada momento.",
          "garantia": "Hipotecaria sobre la vivienda (primera o segunda residencia). Se deberá contar necesariamente con tasación vigente de la vivienda a financiar, realizada por sociedad de tasación homologada por banco de España.",
          "amortizacion": "Mensual constante de capital e interés.",
          "moneda": "Euros",
          "referencia": "Euribor 1 año (e09). Revisión anual."
        },
        "tarifas": {
          "tipo_de_interes_fijo_con_bonificacion_por_vinculacion": "Tipo de interés fijo doce primeros meses y resto referenciado a Euribor con posibilidad de bonificación por contratación o consumo de productos. Revisiones anuales de la referencia.",
          "tipos_interes": {
            "grupo_adquisicion_vivienda_1": "PRIMEROS 12M: 1,90% RESTO: Eur + 0,80% / 1,80%",
            "grupo_adquisicion_vivienda_2": "PRIMEROS 12M: 1,90% RESTO: Eur + 0,55% / 1,55%",
            "grupo_no_adquisicion_vivienda": "PRIMEROS 12M: 2,95% RESTO: Eur + 2,90% / 3,90%"
          },
          "comisiones": {
            "comision_de_apertura": "0,15%. Bonificable a nivel oficina.",
            "compensacion_por_reembolso_anticipado": "0,25% durante los tres primeros años desde la apertura del préstamo y el resto exento, con el límite del importe de la pérdida financiera asumida por la entidad.",
            "tipo_demora": "Se añadirá un diferencial del 3% sobre el tipo normal de la operación con carácter general."
          }
        },
        "bonificacion_maxima": "1,00pb.",
        "periodicidad_de_revision": "anual",
        "atribuciones_en_condiciones_financieras": "Las condiciones financieras de las operaciones de importe inferior 50.000 euros o plazo inferior a 10 años deberán ser aprobadas por Dir. Control Comercial y de Precios. Asimismo, las condiciones financieras de las operaciones fuera de esta tarifa deberán ser aprobadas a nivel de Dir. Control Comercial y de Precios. En el caso renegociaciones de precio de préstamos ya formalizados, los precios se deberán de aprobar siempre por Control Comercial y de Precios. Se excluyen las operaciones de refinanciación o reestructuración del balance cuyo precio deberá ser aprobado por admisión de riesgo de crédito en el marco de la propuesta de reestructuración de la operación. Cuando el LTV del préstamo sea >=80% se requiere la aprobación del precio por Control de Precios Red Comercial.",
        "atribuciones_en_concesion_de_operaciones": "Se recuerda que las condiciones de los productos no implican que las oficinas tengan atribuciones. Se tendrá en cuenta, en todo caso lo establecido en el manual de atribuciones para la concesión de operaciones de crédito y en el manual de documentación de operaciones crediticias.",
        "consideraciones_generales": "El importe financiable puede incorporar, adicionalmente, los gastos de notaria, gastos por registro, obligaciones fiscales (IVA o ITP/AJD) y gastos de tramitación relacionados con la operación de compraventa, siempre que dicho importe adicional no supere el 10% del valor de adquisición del bien que se vaya a declarar en escritura pública y se justifique documentalmente.",
        "argumentario_comercial": "Tipo inicial competitivo y para un plazo de un año. Comisiones de reembolso inferiores a las correspondientes a la hipoteca a tipo fijo. Gastos de constitución de hipoteca asumidos por la entidad (excepto tasación). Cuadro de bonificación extenso: ofrecemos una gran variedad de productos que permiten la reducción de tipo y que son flexibles en su aplicación en cada revisión anual. Esta variedad de productos permite adaptarse a las circunstancias personales de cada cliente, las cuales pueden variar durante el plazo de la hipoteca. La modalidad variable implica fijar el precio mediante la suma de un diferencial y una referencia de tipo de interés (Euribor 12 meses con revisión anual). Este sistema de fijación del precio supone adaptar el importe de las cuotas a la evolución de los tipos de interés en cada momento (bajadas/subidas del Euribor). En líneas generales dado que el tipo de interés de partida de una hipoteca a tipo variable es más bajo que de una fija, se trata de una modalidad de tipo de interés recomendable si está previsto realizar elevadas entregas anticipadas de capital desde los momentos iniciales, ya que esto permitirá reducir la cantidad total de intereses abonados en la operación. En autoconstrucción se admite carencia de capital de hasta 24 meses. Solo se pagan intereses por el capital dispuesto y con liquidaciones trimestrales."
      },
      {
        "nombre_producto": "Hipoteca Joven tipo variable",
        "codigo_producto": {
          "comercial": "112004",
          "administrativo": "050476"
        },
        "descripcion_producto": "La hipoteca joven tipo variable es un préstamo con garantía hipotecaria a tipo variable, cuyos titulares tienen que tener edad inferior o igual a 35 años y cuyo tipo de interés puede reducirse en función de la contratación y mantenimiento de productos.",
        "publico_objetivo": "Personas físicas con edad inferior o igual a 35 años que necesiten financiación para la adquisición o autoconstrucción de vivienda, vinculados con la entidad por la domiciliación de ingresos o mantenimiento de productos y que cuenten con recorrido para la contratación de nuevas líneas comerciales que les posibiliten una reducción del tipo de interés.",
        "condiciones_financieras": {
          "destino": "Adquisición/autoconstrucción/rehabilitación de vivienda, siempre y cuando no sea la actividad empresarial principal del prestatario.",
          "importe": "Desde 50.000 euros.",
          "plazo": "Desde 8 años. Hasta 30 años para residencia de uso propio, siempre que la edad de los titulares más el plazo de la operación no sea superior a 75 años para primera residencia uso propio y 70 años para segunda. Para destino alquiler siempre que no sea la actividad empresarial principal de prestatario, plazo máximo 20 años, siempre que la edad de cada uno de los titulares más plazo de la operación no sea superior a 70 años.",
          "LTV": "Hasta el 80% del menor de los dos valores, tasación o precio de compra en escritura pública. Para segunda residencia uso propio, el menor de los valores entre el 70% del valor de tasación y el 80% del precio de compra en escritura.",
          "carencia_de_capital": "Hasta 24 meses (únicamente en autoconstrucción de vivienda habitual). Liquidación trimestral de intereses sobre el capital dispuesto en cada momento.",
          "garantia": "Hipotecaria sobre la vivienda (primera o segunda residencia). Se deberá contar necesariamente con tasación vigente de la vivienda a financiar, realizada por sociedad de tasación homologada por Banco de España.",
          "amortizacion": "Mensual constante de capital e interés.",
          "moneda": "Euro",
          "referencia": "Euribor 1 año (E09). Revisión anual."
        },
        "tarifas": {
          "tipo_de_interes_fijo_con_bonificacion_por_vinculacion": "Tipo de interés fijo doce primeros meses y resto referenciado a Euribor con posibilidad de bonificación por contratación o consumo de productos. Revisiones anuales de la referencia.",
          "tipos_interes": {
            "grupo_adquisicion_vivienda_1": "PRIMEROS 12M: 2,15% RESTO: Eur + 0,85% / 1,85%",
            "grupo_adquisicion_vivienda_2": "PRIMEROS 12M: 2,15% RESTO: Eur + 0,60% / 1,60%",
            "grupo_no_adquisicion_vivienda": "PRIMEROS 12M: 3,00% RESTO: Eur + 2,95% / 3,95%"
          },
          "comisiones": {
            "comision_apertura": "0,15%. Bonificable a nivel oficina",
            "compensacion_reembolso_anticipado": "0,25% durante los tres primeros años desde la apertura del préstamo y el resto exento, con el límite del importe de la pérdida financiera asumida por la entidad. Se establece una aportación mínima de 300 euros y se puede elegir entre reducir plazo o cuota.",
            "tipo_demora": "Se añadirá un diferencial del 3% sobre el tipo normal de la operación con carácter general."
          }
        },
        "bloques_de_bonificacion_por_mantenimiento_y_contratacion_de_productos": [],
        "bonificacion_maxima": "1,00pb",
        "periodicidad_de_revision": "anual",
        "atribuciones_en_condiciones_financieras": "Las condiciones financieras de las operaciones de importe inferior 50.000 euros o plazo inferior a 10 años deberán ser aprobadas por Dir. Control Comercial y de Precios. Las condiciones financieras de las operaciones fuera de esta tarifa deberán ser aprobadas a nivel de Dir. Control Comercial y de Precios. En el caso de renegociaciones de precio de préstamos ya formalizados, los precios se deberán de aprobar siempre por Control Comercial y de Precios, excluyendo las operaciones de refinanciación o reestructuración del balance cuyo precio deberá ser aprobado por admisión de riesgo de crédito en el marco de la propuesta de reestructuración de la operación. Cuando el LTV del préstamo sea >=80% se requiere la aprobación del precio por Control de Precios Red Comercial.",
        "atribuciones_en_concesion_de_operaciones": "Se recuerda que las condiciones de los productos no implican que las oficinas tengan atribuciones. Se tendrá en cuenta, en todo caso lo establecido en el manual de atribuciones para la concesión de operaciones de crédito y en el manual de documentación de operaciones crediticias (ruta de acceso: intranet corporativa: soporte interno / normativa / operatoria / manual de atribuciones).",
        "consideraciones_generales": "El importe financiable puede incorporar, adicionalmente, los gastos de notaría, gastos por registro, obligaciones fiscales (IVA o ITP/AJD) y gastos de tramitación relacionados con la operación de compraventa, siempre que dicho importe adicional no supere el 10% del valor de adquisición del bien que se vaya a declarar en escritura pública y se justifique documentalmente.",
        "argumentario_comercial": "Tipo inicial competitivo y para un plazo de un año. Comisiones de reembolso inferiores a las correspondientes a la hipoteca a tipo fijo. Gastos de constitución de hipoteca asumidos por la entidad (excepto tasación). Cuadro de bonificación extenso: ofrecemos una gran variedad de productos que permiten la reducción de tipo y que son flexibles en su aplicación en cada revisión anual. Esta variedad de productos permite adaptarse a las circunstancias personales de cada cliente. La modalidad variable implica fijar el precio mediante la suma de un diferencial y una referencia de tipo de interés (Euribor 12 meses con revisión anual). Este sistema de fijación del precio supone adaptar el importe de las cuotas a la evolución de los tipos de interés en cada momento. En líneas generales dado que el tipo de interés de partida de una hipoteca a tipo variable es más bajo que de una fija, se trata de una modalidad de tipo de interés recomendable si está previsto realizar elevadas entregas anticipadas de capital desde los momentos iniciales, ya que esto permitirá reducir la cantidad total de intereses abonados en la operación. En autoconstrucción se admite carencia de capital de hasta 24 meses."
      },
      {
        "nombre_producto": "Hipoteca Fidelidad tipo variable",
        "codigo_producto": {
          "comercial": "112003",
          "administrativo": "050460"
        },
        "descripcion_producto": "Préstamo con garantía hipotecaria a tipo variable, cuyo tipo de interés puede reducirse en función de la contratación y mantenimiento de productos.",
        "publico_objetivo": "Personas físicas que necesiten financiación para la adquisición o autoconstrucción de una vivienda. En función de sus líneas comerciales actuales o futuras puedan reducir su tipo de interés vía bonificación.",
        "condiciones_financieras": {
          "destino": "Adquisición/autoconstrucción/rehabilitación de vivienda, siempre y cuando no sea la actividad empresarial principal del prestatario.",
          "importe": "Desde 50.000 euros.",
          "plazo": "Desde 8 años. Hasta 30 años para residencia de uso propio, siempre que la edad de los titulares más el plazo de la operación no sea superior a 75 años para primera residencia uso propio y 70 años para segunda. Para destino alquiler siempre que no sea la actividad empresarial principal de prestatario, plazo máximo de 20 años, siempre que la edad de cada uno de los titulares más plazo de la operación no sea superior a 70 años.",
          "LTV": "Hasta el 80% del menor de los dos valores, tasación o precio de compra en escritura pública. Para segunda residencia uso propio, el menor de los valores entre el 70% del valor de tasación y el 80% del precio de compra en escritura.",
          "carencia_de_capital": "Hasta 24 meses (únicamente en autoconstrucción de vivienda habitual) durante los cuales se liquidarán intereses trimestralmente sobre el capital dispuesto en cada momento.",
          "garantia": "Hipotecaria sobre la vivienda (primera o segunda residencia). Se deberá contar necesariamente con tasación vigente de la vivienda a financiar, realizada por sociedad de tasación homologada por banco de España.",
          "amortizacion": "Mensual constante de capital e interés.",
          "moneda": "Euro",
          "referencia": "Euribor 1 año (E09). Revisión anual."
        },
        "tarifas": {
          "tipo_de_interes_fijo_con_bonificacion_por_vinculacion": "Tipo de interés fijo doce primeros meses y resto referenciado a Euribor con posibilidad de bonificación por contratación o consumo de productos. Revisiones anuales de la referencia.",
          "tipos_interes": {
            "grupo_adquisicion_vivienda_1": "PRIMEROS 12M: 2,20% RESTO: Eur + 0,90% / 1,90%",
            "grupo_adquisicion_vivienda_2": "PRIMEROS 12M: 2,20% RESTO: Eur + 0,65% / 1,65%",
            "grupo_no_adquisicion_vivienda": "PRIMEROS 12M: 3,05% RESTO: Eur + 3,00% / 4,00%"
          },
          "comisiones": {
            "comision_apertura": "0,15%. Bonificable a nivel oficina",
            "compensacion_por_reembolso": "0,25% durante los tres primeros años desde la apertura del préstamo y el resto exento, con el límite del importe de la pérdida financiera asumida por la entidad. Se establece una aportación mínima de 300 euros y se puede elegir entre reducir plazo o cuota.",
            "tipo_demora": "Se añadirá un diferencial del 3% sobre el tipo normal de la operación con carácter general"
          }
        },
        "bonificacion_maxima": "1,00pb",
        "periodicidad_de_revision": "anual",
        "atribuciones_en_condiciones_financieras": "Las condiciones financieras de las operaciones de importe inferior 50.000 euros o plazo inferior a 10 años deberán ser aprobadas por Dir. Control Comercial y de Precios. Asimismo, las condiciones financieras de las operaciones fuera de esta tarifa deberán ser aprobadas a nivel de Dir. Control Comercial y de Precios. En el caso renegociaciones de precio de préstamos ya formalizados, los precios se deberán de aprobar siempre por control comercial y de precios. Se excluyen las operaciones de refinanciación o reestructuración del balance cuyo precio deberá ser aprobado por admisión de riesgo de crédito en el marco de la propuesta de reestructuración de la operación. Cuando el LTV del préstamo sea >=80% se requiere la aprobación del precio por Control de Precios Red Comercial.",
        "atribuciones_en_concesion_de_operaciones": "Se recuerda que las condiciones de los productos no implican que las oficinas tengan atribuciones. Se tendrá en cuenta, en todo caso lo establecido en el manual de atribuciones para la concesión de operaciones de crédito y en el manual de documentación de operaciones crediticias (ruta de acceso: intranet corporativa: soporte interno / normativa / operatoria / manual de atribuciones).",
        "consideraciones_generales": "El importe financiable puede incorporar, adicionalmente, los gastos de notaria, gastos por registro, obligaciones fiscales (IVA o ITP/AJD) y gastos de tramitación relacionados con la operación de compraventa, siempre que dicho importe adicional no supere el 10% del valor de adquisición del bien que se vaya a declarar en escritura pública y se justifique documentalmente.",
        "argumentario_comercial": "Tipo inicial competitivo y para un plazo de un año. Comisiones de reembolso inferiores a las correspondientes a la hipoteca a tipo fijo. Gastos de constitución de hipoteca asumidos por la entidad (excepto tasación). Cuadro de bonificación extenso: ofrecemos una gran variedad de productos que permiten la reducción de tipo y que son flexibles en su aplicación en cada revisión anual. Esta variedad de productos permite adaptarse a las circunstancias personales de cada cliente. La modalidad variable implica fijar el precio mediante la suma de un diferencial y una referencia de tipo de interés (Euribor 12 meses con revisión anual). Este sistema de fijación del precio supone adaptar el importe de las cuotas a la evolución de los tipos de interés en cada momento. En líneas generales dado que el tipo de interés de partida de una hipoteca a tipo variable es más bajo que de una fija, se trata de una modalidad de tipo de interés recomendable si está previsto realizar elevadas entregas anticipadas de capital desde los momentos iniciales, ya que esto permitirá reducir la cantidad total de intereses abonados en la operación. En autoconstrucción se admite carencia de capital de hasta 24 meses."
      }
    ]
  },
  "llm_header": "Recomendación de hipoteca"
}]`;
