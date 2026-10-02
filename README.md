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

### Inteligencia Artificial

- Google Gemini (modelo `gemini-3.5-flash`)

### Generación de imágenes

- Pillow

---

## 🚀 Instalación

### Requisitos previos

- Python 3.14 o superior.
- Git.

### Clonar el repositorio

```bash
git clone https://github.com/vyi060417-lgtm/Wellness-Basket.git
cd Wellness-Basket
```

Configurar el backend

```bash
cd IsWellnessBackend-main

pip install -r requirements.txt

cp .env.example .env
# Edita el archivo .env con tus credenciales
```

Variables de entorno requeridas:

```
DATABASE_URL=sqlite:///./wellness.db
SECRET_KEY=tu-clave-secreta
ACCESS_TOKEN_EXPIRE_MINUTES=30
GEMINI_API_KEY=tu-api-key-de-gemini
```

Poblar la base de datos con categorías y ejercicios:

```bash
python scripts/seed_data.py
```

Iniciar el backend:

```bash
uvicorn main:app --reload
```

El backend estará disponible en http://localhost:8000.

Configurar el frontend

En otra terminal:

```bash
cd IsWellness-main

cp .env.example .env
# BASE_URL=http://localhost:8000

flet run
```

Ejecución rápida (Windows)

En la raíz del proyecto, haz doble clic sobre el archivo:

```
Iniciar_Wellness.bat
```

El script levanta el backend y el frontend automáticamente.

---
