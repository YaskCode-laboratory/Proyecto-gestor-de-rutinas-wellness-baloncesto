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
- Borrado lógico mediante `is_deleted`.

---

## 🏗️ Arquitectura y diseño

Arquitectura en capas con separación entre presentación, lógica de negocio y persistencia.

- **Presentación:** Flet como cliente de escritorio.
- **API:** FastAPI con routers por dominio (auth, routines, exercises, estadisticas).
- **Servicios:** AuthService, IAService y Logger.
- **Persistencia:** SQLAlchemy sobre SQLite local y MySQL Aiven en la nube.
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

- SQLite (desarrollo local)
- MySQL Aiven (entorno en la nube)

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

## 🧪 Pruebas

Las pruebas funcionales cubren:

- Registro, login y logout.
- Generación de rutina con IA y con fallback.
- Creación manual de rutina con series y repeticiones.
- Ejecución con valoración de esfuerzo.
- Consulta de estadísticas y análisis con IA.
- Generación de imagen PNG de progreso.
- Registro de eventos en `logs.txt`.

Las pruebas se ejecutan manualmente desde la aplicación en Flet.

---

## 🔄 Mantenimiento

El sistema contempla las cuatro categorías de mantenimiento:

- **Correctivo:** corrección del cálculo de racha y del layout de botones.
- **Adaptativo:** integración con Google Gemini y detección dinámica de modelos.
- **Perfectivo:** optimización de `database.py`, deduplicación en `estadisticas.py` y creación del endpoint `/estadisticas/dashboard`.
- **Preventivo:** creación del índice `ix_execution_logs_user_date` y limpieza de código.

---

## 📁 Documentación

| Documento | Descripción |
|---|---|
| Diagrama de Casos de Uso UML | Actores, casos y relaciones `<<Include>>` |
| Diagrama de Actividades con Responsables | Pools: Cliente, Sistema, Agente de IA |
| Diagrama de Clases UML | Entidades, servicios y enumeraciones |
| Diagrama de Objetos UML | Instancias reales del sistema |
| Diagrama UML de Base de Datos | Modelo entidad-relación de las 8 tablas |
| Registro de Aspectos Desarrollados | Plantilla de auditoría con 24 aspectos |
| Registro de Evidencias | Capturas de pantalla y base de datos |
| Plan de Actividades ejecutadas | Cronología del desarrollo (julio - septiembre 2026) |

---

## 👥 Equipo

| Integrante |
|---|
| Víctor Alejandro Yi Rosario |

---

## 🚧 Estado del proyecto

Wellness Basket continúa en desarrollo activo.

Entre las próximas incorporaciones se encuentran:

- 📈 Gráficos avanzados de progreso.
- 🏆 Sistema de logros y medallas.
- 🔔 Recordatorios de entrenamiento.
- 📱 Optimización para dispositivos móviles.
- 🎨 Nuevas mejoras de interfaz y accesibilidad.

---

## 📄 Licencia

Proyecto desarrollado con fines académicos para la Universidad del Zulia, Facultad Experimental de Ciencias, Licenciatura en Computación.
