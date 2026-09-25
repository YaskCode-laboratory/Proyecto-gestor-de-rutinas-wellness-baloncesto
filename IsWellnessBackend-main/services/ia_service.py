import os
import json
import time
from typing import List, Dict, Optional, Tuple

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
    print("Cliente Gemini inicializado.")
else:
    client = None
    print("GEMINI_API_KEY no configurada. Usando fallback local.")


def obtener_modelos_preferidos() -> List[str]:
    return [
        "models/gemini-3.5-flash",
        "models/gemini-3.1-flash-lite",
        "models/gemini-flash-latest",
        "models/gemini-2.5-flash",
    ]


def obtener_modelo_activo() -> str:
    preferidos = obtener_modelos_preferidos()
    try:
        modelos_disponibles = list(client.models.list())
        disponibles = []
        for m in modelos_disponibles:
            if hasattr(m, "supported_actions") and "generateContent" in m.supported_actions:
                disponibles.append(m.name)
            elif hasattr(m, "supported_generation_methods") and "generateContent" in m.supported_generation_methods:
                disponibles.append(m.name)

        for pref in preferidos:
            if pref in disponibles:
                return pref
        if disponibles:
            return disponibles[0]
    except Exception:
        pass
    return "models/gemini-3.5-flash"


def generar_prompt(
    position: str,
    level: str,
    age: int,
    height: float,
    weight: float,
    objective: str,
    minutes: int,
) -> str:
    return f"""
Eres un entrenador personal de baloncesto con amplia experiencia. Debes generar una rutina de entrenamiento personalizada en ESPAÑOL.

**Datos del jugador:**
- Posicion: {position}
- Nivel: {level}
- Edad: {age} años
- Altura: {height} cm
- Peso: {weight} kg
- Objetivo principal: {objective}
- Tiempo disponible: {minutes} minutos

**Instrucciones:**
1. Genera una rutina de {minutes} minutos que incluya ejercicios especificos de baloncesto.
2. TODOS los nombres de ejercicios y descripciones deben estar en ESPAÑOL.
3. Los ejercicios deben ser apropiados para el nivel y posicion del jugador.
4. Cada ejercicio debe tener series, repeticiones y una categoría.
5. Las categorías deben ser una de las siguientes: "Finalizacion", "Manejo del balon", "Regate", "Tiro", "Habilidades defensivas", "Pase".
6. Devuelve SOLAMENTE una lista JSON de objetos con la siguiente estructura:
[
  {{
    "name": "Nombre del ejercicio en español",
    "sets": 3,
    "reps": 12,
    "description": "Descripción detallada en español de cómo ejecutar el ejercicio y qué habilidad entrena",
    "category": "Tiro"
  }}
]
"""


def generate_routine_from_ia(
    position: str,
    level: str,
    minutes: int,
    objective: str,
    age: Optional[int] = None,
    height: Optional[float] = None,
    weight: Optional[float] = None,
) -> Tuple[List[Dict], str]:
    if not client:
        return generate_fallback_routine(position, level, minutes), "fallback"

    prompt = generar_prompt(
        position=position,
        level=level,
        age=age or 25,
        height=height or 175.0,
        weight=weight or 70.0,
        objective=objective or "Mejorar rendimiento general",
        minutes=minutes,
    )

    modelos_a_probar = obtener_modelos_preferidos()

    for modelo in modelos_a_probar:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )

            respuesta_texto = response.text
            if "```json" in respuesta_texto:
                respuesta_texto = respuesta_texto.split("```json")[1].split("```")[0]
            elif "```" in respuesta_texto:
                respuesta_texto = respuesta_texto.split("```")[1].split("```")[0]

            ejercicios = json.loads(respuesta_texto.strip())

            if not isinstance(ejercicios, list):
                raise ValueError("La respuesta no es una lista")

            for ex in ejercicios:
                ex.setdefault("name", "Ejercicio sin nombre")
                ex.setdefault("sets", 3)
                ex.setdefault("reps", 10)
                ex.setdefault("description", "")
                ex.setdefault("category", "General")

            return ejercicios, "ia"

        except Exception as error:
            mensaje = str(error)

            if "503" in mensaje or "UNAVAILABLE" in mensaje or "429" in mensaje:
                time.sleep(2)
                continue
            if "404" in mensaje or "NOT_FOUND" in mensaje:
                continue
            continue

    return generate_fallback_routine(position, level, minutes), "fallback"


def generate_fallback_routine(position: str, level: str, minutes: int) -> List[Dict]:
    factor = 1
    if level.lower() == "intermedio":
        factor = 2
    elif level.lower() == "avanzado":
        factor = 3

    ejercicios_base = {
        "Base": [
            {"name": "Bote en el lugar", "sets": 3 * factor, "reps": 20, "description": "Bote con ambas manos, mantén la cabeza arriba", "category": "Manejo del balon"},
            {"name": "Pase de pecho", "sets": 3 * factor, "reps": 15, "description": "Pase con compañero o contra la pared", "category": "Manejo del balon"},
            {"name": "Tiro en suspension", "sets": 3 * factor, "reps": 10, "description": "Tiro desde media distancia, enfócate en la mecánica", "category": "Tiro"},
            {"name": "Cambio de direccion", "sets": 3 * factor, "reps": 12, "description": "Bote con cambio de dirección, protege el balón", "category": "Regate"},
        ],
        "Alero": [
            {"name": "Tiro de 3 puntos", "sets": 4 * factor, "reps": 10, "description": "Tiro desde la línea de 3, mantén la pierna firme", "category": "Tiro"},
            {"name": "Entrada a canasta", "sets": 3 * factor, "reps": 10, "description": "Entrada con bote y bandeja o palomita", "category": "Finalizacion"},
            {"name": "Rebote ofensivo", "sets": 3 * factor, "reps": 15, "description": "Simular rebote y tiro rápido", "category": "Finalizacion"},
            {"name": "Tiro en movimiento", "sets": 3 * factor, "reps": 8, "description": "Recibir y tirar en movimiento, sin pausa", "category": "Tiro"},
        ],
        "Pivot": [
            {"name": "Juego de espaldas", "sets": 4 * factor, "reps": 10, "description": "Recibir de espaldas, girar y tirar con suavidad", "category": "Finalizacion"},
            {"name": "Rebote defensivo", "sets": 3 * factor, "reps": 15, "description": "Simular rebote, salida rápida y pase", "category": "Habilidades defensivas"},
            {"name": "Pase largo", "sets": 3 * factor, "reps": 10, "description": "Pase de salida a campo abierto, precisión", "category": "Manejo del balon"},
            {"name": "Tiro gancho", "sets": 3 * factor, "reps": 8, "description": "Tiro en gancho, con la mano más alejada de la canasta", "category": "Finalizacion"},
        ],
    }

    ejercicios = ejercicios_base.get(position, ejercicios_base["Base"])
    return [
        {
            "name": ex["name"],
            "sets": ex["sets"],
            "reps": ex["reps"],
            "description": ex["description"],
            "category": ex["category"],
        }
        for ex in ejercicios
    ][:5]


def analizar_progreso_con_ia(
    total_rutinas: int,
    total_ejecuciones: int,
    esfuerzo_promedio: float,
    racha_dias: int,
    total_metas: int,
    total_alcanzadas: int,
    categorias_mas_practicadas: list,
    esfuerzo_categorias: list,
    nombre_usuario: str = "Jugador",
    posicion: str = "Base",
    nivel: str = "Intermedio",
) -> str:
    if not client:
        return "La IA no esta disponible en este momento. Intenta mas tarde."

    cats_texto = ""
    for c in categorias_mas_practicadas:
        cats_texto += f"- {c['nombre']}: {c['total']} veces\n"

    esfuerzo_texto = ""
    for e in esfuerzo_categorias:
        esfuerzo_texto += f"- {e['categoria']}: {e['esfuerzo_promedio']}/5\n"

    prompt = f"""
Eres un entrenador personal de baloncesto con amplia experiencia. Debes analizar el progreso de un jugador y darle recomendaciones personalizadas.

**Datos del jugador:**
- Nombre: {nombre_usuario}
- Posicion: {posicion}
- Nivel: {nivel}
- Total de rutinas creadas: {total_rutinas}
- Total de ejecuciones: {total_ejecuciones}
- Esfuerzo promedio: {esfuerzo_promedio}/5
- Racha actual: {racha_dias} dia(s) consecutivo(s)
- Metas creadas: {total_metas}
- Metas alcanzadas: {total_alcanzadas}

**Categorias mas practicadas:**
{cats_texto if cats_texto else "Sin datos aun"}

**Esfuerzo promedio por categoria:**
{esfuerzo_texto if esfuerzo_texto else "Sin datos aun"}

**Instrucciones:**
1. Analiza el progreso del jugador (maximo 3 parrafos).
2. Menciona sus puntos fuertes y areas de mejora.
3. Recomienda que categoria deberia entrenar mas y por que.
4. Da un consejo motivacional final.
5. Escribe TODO en ESPAÑOL, en un tono motivador y profesional.
6. NO uses markdown, solo texto plano con saltos de linea.
7. Se conciso (maximo 250 palabras).
"""

    for modelo in obtener_modelos_preferidos():
        try:
            response = client.models.generate_content(model=modelo, contents=prompt)
            return response.text.strip()
        except Exception as error:
            mensaje = str(error)
            if "503" in mensaje or "UNAVAILABLE" in mensaje or "429" in mensaje:
                time.sleep(2)
                continue
            continue

    return "No se pudo generar el analisis en este momento. Intenta de nuevo mas tarde."