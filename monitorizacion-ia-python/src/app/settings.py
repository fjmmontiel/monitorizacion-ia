"""
Fichero de configuración del proyecto. Empleado para cargar las
variables de entorno y definir la configuración del proyecto.
"""

import os
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """
    Clase de configuración para la aplicación.
    """

    JWKS_LOCAL: Optional[Dict[str, Any]] = None

    # General
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "FastAPI Microservice")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION", "1.0.0")
    URL_FRONT: str = os.getenv("URL_FRONT", "")
    IAG_APP_ID: str = os.getenv("X_IAG_APP_ID", "iagmvps-ms-backend-av-hipotecas")
    VERBOSE: str = os.getenv("VERBOSE", "False")
    # Orchestrator
    ORCHESTRATOR_URL: str = os.getenv("ORCHESTRATOR_URL", "https://orchestrator:8000")
    PROMPT_ID: str = os.getenv("PROMPT_ID", "prompt‑generate‑summary")

    # Database
    DATABASE_USER: str = os.getenv("DATABASE_USER", "root")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "")
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "JK-MISERSQL.unicajasc.corp")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "IAG_HIPOTECAS_DB")
    DATABASE_DRIVER: str = os.getenv("DATABASE_DRIVER", "ODBC Driver 17 for SQL Server")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", 1434))
    DATABASE_ENCRYPT: str = os.getenv("DATABASE_ENCRYPT", "yes")
    DATABASE_TRUST_SERVER_CERTIFICATE: str = os.getenv(
        "DATABASE_TRUST_SERVER_CERTIFICATE", "yes"
    )
    DATABASE_SERVER_TYPE: str = os.getenv("DATABASE_SERVER_TYPE", "mssql")
    DATABASE_DRIVER_TYPE: str = os.getenv("DATABASE_DRIVER_TYPE", "pyodbc")

    # Servicios Unicaja
    # Gastos hipotecarios
    API_GASTOS_HIPOTECARIOS: str = os.getenv(
        "API_GASTOS_HIPOTECARIOS",
        "https://apis-nopr.unicajasc.corp/interno/inte-unicaja/prestamos/simulador-hipotecario/atg",
    )
    # Gastos tasacion
    API_GASTOS_TASACION: str = os.getenv(
        "API_GASTOS_TASACION",
        "https://apis-nopr.unicajasc.corp/interno/inte-unicaja/prestamos/simulador-hipotecario/simulacion",
    )
    # Hipoteca Digital
    API_CONSULTA_CLIENTE: str = os.getenv(
        "API_CONSULTA_CLIENTE",
        "https://apis-nopr.unicajasc.corp/interno/inte-unicaja/prestamos/"
        "hipoteca-digital/salesforce/consulta-datos-cliente",
    )
    API_MUESTRA_INTERES: str = os.getenv(
        "API_MUESTRA_INTERES",
        "https://apis-nopr.unicajasc.corp/interno/inte-unicaja/prestamos/"
        "hipoteca-digital/salesforce/alta-muestra-interes",
    )

    API_CANCELAR_MUESTRA_INTERES: str = os.getenv(
        "API_CANCELAR_MUESTRA_INTERES",
        "https://apis-nopr.unicajasc.corp/interno/inte-unicaja/prestamos/"
        "hipoteca-digital/salesforce/cancelacion-solicitud",
    )
    API_DOC_MUESTRA_INTERES: str = os.getenv(
        "API_DOC_MUESTRA_INTERES",
        "https://apis-nopr.unicajasc.corp/interno/inte-unicaja/prestamos/hipoteca-digital/muestra-interes/alta",
    )

    CLIENT_ID_HIPOTECA_DIGITAL: str = os.getenv(
        "CLIENT_ID_HIPOTECA_DIGITAL", "a70a2980fff8e952a0f3e32812af4a66"
    )
    CLIENT_SECRET_HIPOTECA_DIGITAL: str = os.getenv(
        "CLIENT_SECRET_HIPOTECA_DIGITAL", "78753fd4d755187c46e60a0ada12e69e"
    )

    API_CONSULTA_CONSENTIMIENTO: str = os.getenv(
        "API_CONSULTA_CONSENTIMIENTO",
        "https://ltd.backend-desa.unicajasc.corp:443/ltd-personas-ms-alta-precliente/alta-precliente",
    )
    API_BONIFICACIONES: str = os.getenv(
        "API_BONIFICACIONES",
        "https://pudgc.backend-desa.unicajasc.corp/tcd-pudgc-ms-bonificaciones/modulo/consulta-bonificaciones",
    )

    API_SIMULAR_PRECIOS: str = os.getenv(
        "API_SIMULAR_PRECIOS",
        "https://sgd.backend-desa.unicajasc.corp:443/"
        "ssd-expediente-ms-simulador-precios/iag/simular-precios",
    )

    # Log Operacional
    URL_TOKEN_LOG_OPERACIONAL: str = os.getenv(
        "URL_TOKEN_LOG_OPERACIONAL",
        "https://apis-nopr.unicajasc.corp/interno/inte-unicaja/soporte/"
        "arquitectura/token-microservicios?idSession=1234567&appName=interno&usuario=UX8326C",
    )
    API_LOG_OPERACIONAL: str = os.getenv(
        "API_LOG_OPERACIONAL",
        "https://pudgc.backend-desa.unicajasc.corp:443/"
        "pudgc-portal-gestor-ms-log-operacional/log-operacional",
    )
    CLIENT_ID_LOG_OPERACIONAL: str = os.getenv(
        "CLIENT_ID_LOG_OPERACIONAL", "b501eeb2cd6658bb92a70c620ad3c1d2"
    )
    CLIENT_SECRET_LOG_OPERACIONAL: str = os.getenv("CLIENT_SECRET_LOG_OPERACIONAL", "")

    # Variables para conectar AI Core
    AICORE_URL: str = os.getenv("AICORE_URL", "")
    ENGINE_ID: str = os.getenv("ENGINE_ID", "")
    URL_GESTIONES: str = os.getenv("URL_GESTIONES", "")
    PUERTO_GESTIONES: str = os.getenv("PUERTO_GESTIONES", "")

    URL_TOKEN_JWT: str = os.getenv("URL_TOKEN_JWT", "")
    URL_TOKEN_OAUTH: str = os.getenv("URL_TOKEN_OAUTH", "")

    LDAP_URL: str = os.getenv("LDAP_URL", "")
    LDAP_APP: str = os.getenv("LDAP_APP", "")

    @classmethod
    def load_from_yaml(cls, path: str = "config.yaml"):
        """
        Carga la configuración desde un archivo YAML.

        En este caso, dado que settings.py está en src/app y config.yaml en src,
        se calcula la ruta subiendo un nivel desde el directorio actual.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "..", path)
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found at {config_path}")
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def is_local(self) -> bool:
        return self.ENVIRONMENT.lower() == "local"

    def get_jwks(self) -> Optional[Dict[str, Any]]:
        if self.is_local():
            if not self.JWKS_LOCAL:
                raise RuntimeError("JWKS_LOCAL debe estar definido en entorno local")
            return self.JWKS_LOCAL
        return None


settings = Settings()
