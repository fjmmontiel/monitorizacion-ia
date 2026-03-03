# AGENTS.md
## Objetivo del respositorio
Este repositorio ejemplifica el uso de un único Frontal que nos sirva de monitorización de diferentes casos de uso de IA generativa en el ambiente conversacional.

Toda la monitorización se hace con un naming convention sobre el orquestador

## Definition of Done (bloqueante)
- Implementar la feature no es suficiente por sí solo.
- Una tarea del sistema solo se considera terminada cuando, además del cambio mínimo necesario, queda verificado que el flujo principal desde el frontend es usable y funcional de extremo a extremo.
- La verificación obligatoria debe cubrir, como mínimo:
  - que la UI renderiza sin errores bloqueantes,
  - que las interacciones clave del flujo funcionan desde el frontend real,
  - que el backend responde correctamente a las llamadas implicadas,
  - que se aportan evidencias concretas (tests, logs, comandos, capturas o equivalentes).
- Si la feature está implementada pero el flujo frontend no se ha validado, la tarea no está terminada.
