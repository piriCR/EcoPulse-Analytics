# EcoPulse Analytics

EcoPulse Analytics es una aplicación en Streamlit para explorar indicadores de calidad del aire urbano. La app permite navegar por vistas de monitoreo, comparación entre ciudades, evolución temporal, alertas OMS y perfiles de ciudad.

## Requisitos

- Python 3.12 o superior
- `pip`

## Instalación

1. Crea el entorno virtual.

```bash
python -m venv .venv
```

2. Actívalo según tu sistema operativo.

En Linux:

```bash
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

En Windows CMD:

```bat
.venv\Scripts\activate.bat
```

3. Instala las dependencias del proyecto.

```bash
pip install -r requirements.txt
```

## Archivo `.env`

La aplicación puede usar una clave opcional de OpenWeather para habilitar la fuente de datos adicional.

Contenido sugerido del archivo `.env`:

```env
OPENWEATHER_API_KEY=API_KEY
```

## Correr el proyecto

Desde la raíz del repositorio ejecuta:

```bash
streamlit run streamlit_app.py
```

La aplicación abrirá en el navegador, normalmente en `http://localhost:8501`.

## Estructura general

- `streamlit_app.py`: punto de entrada de la aplicación
- `pages/`: pantallas principales de la experiencia
- `providers/`: conectores y normalización de datos
- `config/`: constantes, ciudades y umbrales
- `components/`: componentes reutilizables de interfaz
- `utils/`: utilidades de filtrado y contexto

## Fuente de datos

La app consume datos de Open-Meteo y, de forma secundaria con `OPENWEATHER_API_KEY`, también puede consultar OpenWeather.
