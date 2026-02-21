# 📦 "FastAPI Microservice" - Configuración y Ejecución

Este proyecto ha sido desarrollado en Python y requiere la configuración de un entorno virtual para garantizar el aislamiento de dependencias y una correcta ejecución. A continuación, se describen los pasos necesarios para su preparación y puesta en marcha.

## ⚙️ Configuración y Ejecución

Sigue los  pasos desde la raíz del proyecto para configurar y ejecutar la aplicación:

### En Windows (cmd o PowerShell):

**Creamos el entorno virtual**
```bash
python -m venv .venv
```
**lo activamos**
```bash
.venv\Scripts\activate 
```
**agregamos la ultima version de pip**
```bash
python -m pip install --upgrade pip 
```
**instalamos los requisitos**
```bash
pip install -r requirements.txt 
```

**y para ejecutar el microservicio utilizamos el siguiente comando desde la carpeta src**

```bash
uvicorn main:app --port=8002
```
🐧 En macOS/Linux
**creamos el entorno virtual**
```bash
python3 -m venv .venv
```
**lo activamos**
```bash
source .venv/bin/activate 
```
**agregamos la ultima version de pip**
```bash
python -m pip install --upgrade pip 
```
**instalamos los requisitos**
```bash
pip install -r requirements.txt 
```
**y para ejecutar el orquestador utilizamos el siguiente comando**
```bash
uvicorn main:app --port=8002
```

Si necesitas asistencia adicional o soporte técnico, por favor contacta con el equipo de desarrollo correspondiente.












# Crear / levantar contenedor

```
docker run -d --name mvp3 -e POSTGRES_USER=mvp3 -e POSTGRES_PASSWORD=mvp3_2233 -e POSTGRES_DB=mvp3 -p 5432:5432 postgres:latest
```

En caso de que ya exista, buscarlo

```
docker ps -a
```

Y levantarlo

```
docker start mvp3
```

# Procesar el archivo de carga de creación de BD

Aquí tenemos dos opciones: bien por comandos (a continuación los indico) o bien conectarnos a la BD (por línea de comandos app gráfica como DBeaver, que es la que uso yo) y ejecutar el DDL de creación, en la raíz del proyecto (ddl.sql). Si es mediante comandos, lo más sencillo:

Copiar el archivo al contenedor

```
docker cp ./ddl.sql mvp3:/ddl.sql
```

Ejecutar el script

```
docker exec -it mvp3 bash -c "psql -U mvp3 mvp3 < ddl.sql"
```

Con esto ya tendríamos la DB lista para almacenar la info de sesiones.


# Instalar el gestor de entornos si no está

```
apt install python3.11-venv
```

## Generar nuevo entorno

```
python3.11 -m venv .venv
```

## Activar el entorno

```
source .venv/bin/activate
```

## Cargar librerías

```
.venv/bin/pip install -r requirements.txt
```

---

# Extras

Se ha preparado un script para arrancar todo, solamente hay que darle permisos de ejecución. Esto se encarga de cargar las variables de entorno, levanta el contenedor y ejecuta uvicorn para servir todo.

```
chmod +x start.sh
```

Así que para ponerlo a funcionar:

```
./start.sh
```

Si se quiere levantar manualmente con **UVICORN**, después de habernos asegurado de tener pSQL levantado, sería sólo ejecutar

```
uvicorn main:app --reload
```

Como os he comentado, el frontend se ha incluido dentro de la ruta `/static`, y ya está ajustado el main.py para enrutar dicho contenido estático.

Una vez levantado todo, se puede acceder el frontend (por defecto en el puerto 8000) http://localhost:8000/static/index.html