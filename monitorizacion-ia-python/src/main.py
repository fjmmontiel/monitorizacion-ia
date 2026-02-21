"""
main.py
Este módulo define la aplicación FastAPI principal y configura las rutas,
eventos y el endpoint de verificación de salud.
Clases:
    Ninguna
Funciones:
    health() -> dict:
        Endpoint para verificar el estado de salud de la aplicación.
    on_startup() -> None:
        Evento que se ejecuta al iniciar la aplicación.
    on_shutdown() -> None:
        Evento que se ejecuta al apagar la aplicación.
Atributos:
    app (FastAPI): Instancia principal de la aplicación FastAPI configurada
    con el nombre del proyecto y el prefijo de ruta raíz.
"""

from fastapi import FastAPI
from app.settings import settings
from app.routes.routes import router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from qgdiag_lib_arquitectura import CustomLogger, LoggingMiddleware, init_error_handlers
from qgdiag_lib_arquitectura.security import authentication

logger = CustomLogger("Main.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    root_path="/iagmvps-ms-backend-av-hipotecas",
)

# Include your API routes
app.include_router(router)

app.mount(
    "/static", StaticFiles(directory="app/static", check_dir=False), name="static"
)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.URL_FRONT],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(LoggingMiddleware)
init_error_handlers(app, context_name=settings.PROJECT_NAME)


# Health check endpoint
@app.get("/health", tags=["Root"])
async def health():
    """Check if the API is running"""
    return {"estado": 200, "detalle": "Fast API Skeleton is up!", "contenido": []}


@app.on_event("startup")
async def on_startup():
    """
    Evento que se ejecuta al iniciar la aplicación.
    Obtiene claves JWKS
    """
    jwks = settings.get_jwks()
    if not jwks:
        jwks = await authentication.fetch_jwks(channel="1")
    app.state.jwks_store = authentication.Authenticator(jwks)


@app.on_event("shutdown")
async def on_shutdown():
    """Evento que se ejecuta al apagar la aplicación."""
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")


if __name__ == "__main__":
    uvicorn.run(app, port=8000, log_level="info")
