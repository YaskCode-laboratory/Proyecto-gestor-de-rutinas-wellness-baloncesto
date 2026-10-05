# 🏀 Wellness Basket

**El baloncesto como herramienta para el bienestar.**

Una plataforma inteligente diseñada para ayudarte a desarrollar hábitos de entrenamiento saludables, mejorar tu rendimiento deportivo y descubrir rutinas que transformen tu juego.

---

## 🏀 ¿Qué es Wellness Basket?

Wellness Basket es una aplicación desarrollada con Python (FastAPI + Flet) que funciona como un gestor personal de rutinas de baloncesto.

Permite registrar usuarios, configurar metas, generar rutinas automáticas mediante inteligencia artificial, crear rutinas manuales, ejecutar entrenamientos, valorar el esfuerzo y analizar el progreso a lo largo del tiempo.

Todo ello con un mismo propósito:

**Promover el bienestar integral de los jugadores mediante la disciplina del entrenamiento.**

---

## 📋 Problema que aborda

Muchos jugadores de baloncesto entrenan sin un plan estructurado o sin acceso a un entrenador personal que adapte las rutinas a su posición, nivel y tiempo disponible. Las aplicaciones existentes en el mercado están orientadas a mercados internacionales, con precios en dólares y sin funcionamiento offline, lo que las hace poco accesibles para el contexto local.

Wellness Basket resuelve esto al generar rutinas personalizadas con inteligencia artificial a partir del perfil del jugador, funcionar sin conexión mediante SQLite y mantener un registro auditable de todas las actividades.

---

## 🎯 Objetivo

Gestionar rutinas de entrenamiento de baloncesto, registrar el progreso del jugador y ofrecer análisis personalizados que orienten su mejora continua.

---

## 🌎 Área de Wellness

Deporte / Baloncesto / Rendimiento físico / Salud.

---

## 📋 Funcionalidades principales

### Cliente

- Registro y autenticación con JWT.
- Configuración de perfil deportivo (posición, nivel, edad, altura, peso, experiencia).
- Definición de metas con indicador visual (alcanzada / no alcanzada).
- Consulta del catálogo de ejercicios por categorías.
- Generación de rutinas con IA y fallback heurístico.
- Creación manual de rutinas con series y repeticiones editables.
- Ejecución de rutinas con valoración de esfuerzo (escala 1-5).
- Consulta de estadísticas: resumen, esfuerzo por categoría y racha.
- Análisis con IA de fortalezas, debilidades y recomendaciones.
- Compartir progreso como imagen PNG.
- Historial de metas anteriores.

### Agente de IA

- Procesamiento del perfil del usuario para generar rutinas personalizadas.
- Análisis de estadísticas para emitir recomendaciones.
- Fallback heurístico cuando el servicio de IA no está disponible.

### Sistema

- Registro de actividad en `logs.txt` con FECHA, USUARIO y ACTIVIDAD.
- Persistencia en 8 tablas: User, Goal, Category, Exercise, Routine, RoutineExercise, Metric, ExecutionLog.

---

## 🏗️ Arquitectura y diseño

Arquitectura en capas con separación entre presentación, lógica y persistencia.

- **Presentación:** Flet como cliente de escritorio.
- **API:** FastAPI con routers por dominio.
- **Servicios:** AuthService, IAService y Logger.
- **Persistencia:** SQLAlchemy sobre SQLite local.
- **IA externa:** Google Gemini con fallback heurístico ante fallos.

---

## 🌎 Tecnologías

### Backend

- Python
- FastAPI
- SQLAlchemy
- Uvicorn
- PyJWT
- Pwdlib (bcrypt + argon2)

### Frontend

- Python
- Flet

### Base de datos

- SQLite

### Inteligencia Artificial

- Google Gemini (modelo `gemini-3.5-flash`)
- SDK oficial: `google-genai`
- Import en el código: `from google import genai`

### Generación de imágenes

- Pillow

---

## 🚀 Instalación

### Requisitos previos

- Python
- Git

### 1. Clonar el repositorio

```

git clone https://github.com/vyi060417-lgtm/Proyecto-gestor-de-rutinas-wellness-baloncesto.git
cd Proyecto-gestor-de-rutinas-wellness-baloncesto

```

### 2. Crear entorno virtual e instalar dependencias

```

python -m venv venv
venv\Scripts\activate       # Windows CMD
source venv/bin/activate    # Linux/Mac

pip install -r requirements.txt

```

### 3. Configurar variables de entorno

**Backend:**

```

cd IsWellnessBackend-main
copy .env.example .env      # Windows CMD
cp .env.example .env        # Linux/Mac

```

Edita `IsWellnessBackend-main/.env` con tus credenciales:

```

DATABASE_URL=sqlite:///./wellness.db
SECRET_KEY=tu-clave-secreta
ACCESS_TOKEN_EXPIRE_MINUTES=30
GEMINI_API_KEY=tu-api-key-de-gemini

```

**Frontend** (en otra terminal, desde la raíz del proyecto):

```

cd IsWellness-main
copy .env.example .env      # Windows CMD
cp .env.example .env        # Linux/Mac

```

El archivo `IsWellness-main/.env` debe contener:

```

BASE_URL=http://localhost:8000

```

### 4. Poblar la base de datos

Desde `IsWellnessBackend-main`:

```

python scripts/seed_data.py

```

### 5. Ejecutar

**Opción rápida (Windows):**

En la raíz del proyecto, doble clic en:

```

iniciar_app.bat

```

**Opción manual:**

- Terminal 1 (backend):
```

cd IsWellnessBackend-main
uvicorn main:app --reload

```

- Terminal 2 (frontend):
```

cd IsWellness-main
flet run

```

---

## 📚 Documentación

Toda la documentación del proyecto se encuentra en la carpeta [`docs/`](docs/).

| Documento | Descripción |
|---|---|
| [Plan de actividades](docs/Plan%20de%20actividades.docx) | Cronología del desarrollo con las tareas ejecutadas día por día, desde julio hasta septiembre de 2026. |
| [Ingeniería de Software 2026](docs/Ingenieria%20Software%202026.docx) | Documento principal: estado del arte, requisitos, riesgos, Gantt, casos de uso, diagramas UML, codificación POO y metodología. |
| [Presentación del Proyecto](docs/Presentacion%20del%20proyecto%20para%20defensa%202026.pptx) | Diapositivas de defensa: descripción, estado del arte, planificación, riesgos, tecnologías, UML, arquitectura, pruebas, mantenimiento y conclusiones. |
| [Matriz de casos](docs/Matriz%20de%20casos.xlsx) | Plantilla de auditoría con los 20 aspectos analizados, pasos para reproducir, resultado esperado, resultado obtenido y estado de conformidad. |
| [Evidencias de las pruebas](docs/Evidencias%20de%20las%20pruebas%20de%20la%20matriz%20de%20casos.pdf) | Registro fotográfico de las 20 pruebas ejecutadas sobre el sistema, con capturas de pantalla de cada caso. |
| [Diagramas UML](docs/UML/) | Carpeta con los diagramas finales: casos de uso, actividades con responsables, clases, objetos y base de datos. |

---

## 🧪 Pruebas

Las pruebas funcionales cubren:

- Registro, login y logout.
- Generación de rutina con IA y con fallback.
- Creación manual de rutina con series y repeticiones.
- Ejecución con valoración de esfuerzo.
- Consulta de estadísticas y análisis con IA.
- Generación de imagen PNG de progreso.
- Registro de eventos en `logs.txt`.

Las pruebas se ejecutan manualmente desde la aplicación en Flet y se registraron de manera detallada (pasos para reproducir, resultado esperado, resultado obtenido y estado de conformidad) en [`docs/Matriz de casos.xlsx`](docs/Matriz%20de%20casos.xlsx). Las capturas de pantalla que evidencian cada prueba están compiladas en [`docs/Evidencias de las pruebas de la matriz de casos.pdf`](docs/Evidencias%20de%20las%20pruebas%20de%20la%20matriz%20de%20casos.pdf)..

---

## 🔄 Mantenimiento

El sistema contempla las cuatro categorías de mantenimiento:

- **Correctivo:** corrección del cálculo de racha y del layout de botones.
- **Adaptativo:** integración con Google Gemini y detección dinámica de modelos.
- **Perfectivo:** optimización de `database.py`, deduplicación en `estadisticas.py` y creación del endpoint `/estadisticas/dashboard`.
- **Preventivo:** creación del índice `ix_execution_logs_user_date` y limpieza de código.

---

## 👥 Equipo

| Integrante |
|---|
| Víctor Alejandro Yi Rosario |

---

## 🚧 Estado del Proyecto

### Versión académica final (v1.0)

El sistema se encuentra en su versión académica final, con todas las funcionalidades implementadas, probadas y documentadas: autenticación con JWT, perfil deportivo, metas con indicador visual, catálogo de ejercicios, generación de rutinas con IA y fallback heurístico, creación manual de rutinas, ejecución con valoración de esfuerzo, estadísticas de progreso, análisis con IA, imagen PNG de progreso y registro en `logs.txt` con FECHA, USUARIO y ACTIVIDAD. El sistema opera con un único rol: **Cliente**. El rol Administrador/instructor fue eliminado porque el catálogo se carga por script y el Agente de IA añade ejercicios nuevos automáticamente; el Instructor/administrador se redujo del alcance porque el sistema está diseñado como plataforma de autogestión donde el usuario configura su perfil, define sus metas y genera rutinas sin intermediación humana.

---

## 🔮 Futuras Incorporaciones

Las siguientes funcionalidades quedan documentadas como líneas de trabajo posteriores a la versión académica:

- Notificaciones y recordatorios de entrenamiento.
- Sistema de logros y medallas.
- Gráficos avanzados de progreso.
- Módulos de visión por cámara para análisis automático de tiro.
- Optimización para dispositivos móviles.

---

## 📄 Licencia

Proyecto desarrollado con fines académicos para la Universidad del Zulia, Facultad Experimental de Ciencias, Licenciatura en Computación.
