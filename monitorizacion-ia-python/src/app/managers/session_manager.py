"""
Gestión de sesiones y métricas del sistema de hipotecas.

Este módulo proporciona clases para gestionar sesiones de usuario, incluyendo
el seguimiento de métricas como tokens utilizados, costes, duración y valoraciones.
Implementa un patrón singleton para el gestor de sesiones globales.

Classes:
    - Session: Representa una sesión individual con métricas y metadatos

Features:
    - Seguimiento de tokens de entrada y salida
    - Cálculo automático de costes en dólares
    - Gestión de tiempos de sesión (inicio, fin, duración)
    - Almacenamiento de valoraciones y comentarios de usuario
    - Registro de muestras de interés y centros asociados
"""

from datetime import datetime


class Session:
    """
    Representa una sesión individual de usuario con métricas y metadatos.

    Gestiona información de tokens, costes, duración, valoraciones y otros
    datos relevantes para el seguimiento de la actividad del usuario.

    Attributes:
        session_id (str): Identificador único de la sesión
        input_tokens (int): Tokens de entrada utilizados
        output_tokens (int): Tokens de salida generados
        cost (float): Coste calculado en dólares
        valoracion (int): Valoración del usuario (-1 por defecto)
        comentarios (str): Comentarios del usuario
        muestra_de_interes (int): Indicador de interés mostrado
        session_duration (int): Duración en segundos
        session_start (datetime): Fecha y hora de inicio
        session_end (datetime): Fecha y hora de finalización
        centro (str): Centro asociado a la sesión
        gestor (str): Código del gestor
        conversacion (str): Conversación mantenida durante la sesión
    """

    def __init__(self, session_id: str, centro: str, gestor: str):
        self.session_id = session_id
        self.input_tokens = 0
        self.output_tokens = 0
        self.cost = 0.0  # Coste en euros
        self.valoracion = -1
        self.comentarios = ""
        self.muestra_de_interes = 0
        self.session_duration = 0  # Duración en segundos
        self.session_start = None  # Fecha y hora de inicio de la sesión (TIMESTAMP)
        self.session_end = None  # Fecha y hora de finalización de la sesión (TIMESTAMP)
        self.centro = centro
        self.gestor = gestor
        self.conversacion = ""
        self.ultima_llamada_guardar_muestra_de_interes = ""

    def calcular_costes_dolares(self):
        coste_en_dolares: float = (
            2.5 * self.input_tokens / 1000000 + 10 * self.output_tokens / 1000000
        )
        self.cost = coste_en_dolares
        return coste_en_dolares

    def iniciar_sesion(self):
        self.session_start = datetime.now()

    def actualizar_tiempos_sesion(self):
        self.session_end = datetime.now()
        if self.session_start:
            self.session_duration = (
                self.session_end - self.session_start
            ).total_seconds()

    def actualizar(self):
        self.actualizar_tiempos_sesion()
