"""
Servicio de verificación de documentos de identidad.

Proporciona funcionalidad para validar DNI y NIE españoles, calcular
dígitos de control y consultar información de clientes asociados.
"""

import json
from app.services.consulta_cliente_service import ConsultaClienteService


class DocumentoIdentidad:
    """
    Servicio para verificación y validación de DNI/NIE.

    Valida el formato, calcula dígitos de control y consulta
    información del cliente asociado al documento verificado.
    """

    def __init__(self, documento):
        self.documento = documento.upper()

    @staticmethod
    def calcular_letra_dni_nie(numeros):
        letras = "TRWAGMYFPDXBNJZSQVHLCKE"
        return letras[numeros % 23]

    def verificar(self, segundo_interviniente: bool) -> dict:
        """
        Verifica un DNI/NIE y, si es válido y no es segundo interviniente, consulta su información.
        En caso de precliente (indCliente == "P"), añade un aviso explícito para el agente.

        Args:
            segundo_interviniente (bool): Si True, no se consulta info de cliente.

        Returns:
            dict: {
              "valido": bool,
              "mensaje": str,
              "info_cliente": dict | None,
              "tipo_cliente": "cliente" | "precliente" | None,
              "aviso_agente": str | None
            }
        """

        resultado = {
            "valido": False,
            "mensaje": "",
            "info_cliente": None,
            "tipo_cliente": None,
            "aviso_agente": None,
        }

        # Validar longitud
        if len(self.documento) != 9:
            resultado["mensaje"] = (
                "El formato del documento no es correcto (longitud ≠ 9)."
            )
            return resultado

        # Convertir NIE si aplica
        if self.documento[0] in "XYZ":
            switch = {"X": "0", "Y": "1", "Z": "2"}
            numero_convertido = switch[self.documento[0]] + self.documento[1:-1]
        else:
            numero_convertido = self.documento[:-1]

        # Validar que los números sean dígitos
        if not numero_convertido.isdigit():
            resultado["mensaje"] = "El número del documento no es válido."
            return resultado

        # Calcular letra
        numeros = int(numero_convertido)
        letra_correcta = self.calcular_letra_dni_nie(numeros)
        letra = self.documento[-1]

        if letra != letra_correcta:
            resultado["mensaje"] = "La letra del DNI/NIE es incorrecta."
            return resultado

        # Documento válido
        resultado["valido"] = True
        resultado["mensaje"] = "El DNI/NIE es válido."

        # Si es segundo interviniente, no consultamos info de cliente
        if segundo_interviniente:
            # Mantener claro para el agente que no se consultó info
            resultado["aviso_agente"] = (
                "Documento válido. No se consulta información del cliente por ser segundo interviniente."
            )
            return resultado

        # Consultar info de cliente
        info_cliente = ConsultaClienteService().call(self.documento)
        resultado["info_cliente"] = info_cliente

        # Determinar tipo de cliente y avisar al agente si es precliente
        ind_cliente = (info_cliente or {}).get("indCliente", "").strip().upper()

        if ind_cliente == "N":
            resultado["tipo_cliente"] = "no_cliente"
            resultado["aviso_agente"] = (
                "El documento es válido y pertenece a un NO CLIENTE (indCliente='N'). "
            )
            resultado["mensaje"] = (
                "El DNI/NIE es válido. El usuario no figura como cliente ni como precliente."
            )

        elif ind_cliente == "P":
            resultado["tipo_cliente"] = "precliente"
            # Aviso preciso para el agente
            resultado["aviso_agente"] = (
                "El documento es válido y pertenece a un PRECLIENTE (indCliente='P'). "
            )
            resultado["mensaje"] = (
                "El DNI/NIE es válido. El usuario figura como precliente."
            )
        elif ind_cliente == "C":
            resultado["tipo_cliente"] = "cliente"
            resultado["aviso_agente"] = (
                "El documento es válido y pertenece a un cliente registrado."
            )
        else:
            # Sin indCliente informado: avisar al agente para manejar incertidumbre
            resultado["aviso_agente"] = (
                "El documento es válido. No se ha recibido 'indCliente' en los datos consultados; "
                "gestiona el flujo como desconocido y solicita confirmación o reintento de consulta."
            )

        return resultado
