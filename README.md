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
- Python
- Git

### 1. Clonar el repositorio
git clone https://github.com/vyi060417-lgtm/Proyecto-gestor-de-rutinas-wellness-baloncesto.git
cd Proyecto-gestor-de-rutinas-wellness-baloncesto

### 2. Crear entorno virtual e instalar dependencias
python -m venv venv
venv\Scripts\activate       # Windows CMD
source venv/bin/activate    # Linux/Mac

pip install -r requirements.txt

### 3. Configurar variables de entorno

Backend:
cd IsWellnessBackend-main
copy .env.example .env      # Windows CMD
cp .env.example .env        # Linux/Mac

Edita IsWellnessBackend-main/.env con tus credenciales:
DATABASE_URL=sqlite:///./wellness.db
SECRET_KEY=tu-clave-secreta
ACCESS_TOKEN_EXPIRE_MINUTES=30
GEMINI_API_KEY=tu-api-key-de-gemini

Frontend (en otra terminal, desde la raíz del proyecto):
cd IsWellness-main
copy .env.example .env      # Windows CMD
cp .env.example .env        # Linux/Mac

El archivo IsWellness-main/.env debe contener:
BASE_URL=http://localhost:8000

### 4. Poblar la base de datos

Desde IsWellnessBackend-main:
python scripts/seed_data.py

### 5. Ejecutar

Opción rápida (Windows):
En la raíz del proyecto, doble clic en:
iniciar_app.bat

Opción manual:
- Terminal 1 (backend):
  cd IsWellnessBackend-main
  uvicorn main:app --reload

- Terminal 2 (frontend):
  cd IsWellness-main
  flet run 

---

👥 Equipo

Integrante
Víctor Alejandro Yi Rosario

---

🚧 Estado del proyecto

Wellness Basket continúa en desarrollo activo.

Entre las próximas incorporaciones se encuentran:

· 📈 Gráficos avanzados de progreso.
· 🏆 Sistema de logros y medallas.
· 🔔 Recordatorios de entrenamiento.
· 📱 Optimización para dispositivos móviles.
· 🎨 Nuevas mejoras de interfaz y accesibilidad.

---
