import os
import httpx
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

_client = httpx.Client(
    base_url=BASE_URL,
    timeout=60.0,
    limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
)


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def login(email: str, password: str) -> dict:
    r = _client.post("/auth/login", data={"username": email, "password": password})
    r.raise_for_status()
    return r.json()


def register(email: str, password: str, name: str, meta_objetivo: str, **kwargs) -> dict:
    payload = {
        "email": email,
        "password": password,
        "name": name,
        "meta_objetivo": meta_objetivo,
        "target_days_per_week": 3,
    }
    payload.update({k: v for k, v in kwargs.items() if v is not None})
    r = _client.post("/auth/register", json=payload)
    r.raise_for_status()
    return r.json()


def get_me(token: str) -> dict:
    r = _client.get("/auth/me", headers=_auth_headers(token))
    r.raise_for_status()
    return r.json()


def update_user(token: str, data: dict) -> dict:
    r = _client.patch("/auth/update", json=data, headers=_auth_headers(token))
    r.raise_for_status()
    return r.json()


def get_routines(token: str) -> list:
    r = _client.get("/routines/", headers=_auth_headers(token))
    r.raise_for_status()
    return r.json()


def get_routine(token: str, routine_id: str) -> dict:
    r = _client.get(f"/routines/{routine_id}", headers=_auth_headers(token))
    r.raise_for_status()
    return r.json()


def generate_routine(
    token: str,
    position: str,
    level: str,
    objective: str,
    time_minutes: int,
    title: str = None,
) -> dict:
    payload = {
        "position": position,
        "level": level,
        "objective": objective,
        "time_minutes": time_minutes,
    }
    if title:
        payload["title"] = title
    r = _client.post("/routines/generate", json=payload, headers=_auth_headers(token))
    r.raise_for_status()
    return r.json()


def create_manual_routine(token: str, title: str, exercises: list) -> dict:
    from datetime import date
    r = _client.post(
        "/routines/manual",
        json={
            "title": title,
            "scheduled_date": date.today().isoformat(),
            "exercises": exercises,
        },
        headers=_auth_headers(token),
    )
    r.raise_for_status()
    return r.json()


def execute_routine(
    token: str,
    routine_id: str,
    effort_rating: int,
    routine_exercise_id: str = None,
) -> dict:
    payload = {"effort_rating": effort_rating}
    if routine_exercise_id:
        payload["routine_exercise_id"] = routine_exercise_id
    r = _client.patch(f"/routines/{routine_id}/execute", json=payload, headers=_auth_headers(token))
    r.raise_for_status()
    return r.json()


def delete_routine(token: str, routine_id: str) -> dict:
    r = _client.delete(f"/routines/{routine_id}", headers=_auth_headers(token))
    r.raise_for_status()
    return r.json()


def get_dashboard(token: str) -> dict:
    r = _client.get("/estadisticas/dashboard", headers=_auth_headers(token))
    r.raise_for_status()
    return r.json()


def get_resumen(token: str) -> dict:
    r = _client.get("/estadisticas/resumen", headers=_auth_headers(token))
    r.raise_for_status()
    return r.json()


def get_evolucion(token: str, metric_type: str, days: int = 30) -> list:
    r = _client.get(
        f"/estadisticas/evolucion/{metric_type}",
        params={"days": days},
        headers=_auth_headers(token),
    )
    r.raise_for_status()
    return r.json()


def get_esfuerzo_por_categoria(token: str) -> list:
    r = _client.get("/estadisticas/esfuerzo-por-categoria", headers=_auth_headers(token))
    r.raise_for_status()
    return r.json()


def get_meta_info(token: str) -> dict:
    r = _client.get("/estadisticas/meta-info", headers=_auth_headers(token))
    r.raise_for_status()
    return r.json()


def analizar_progreso_ia(token: str) -> dict:
    r = _client.get("/estadisticas/analizar-ia", headers=_auth_headers(token))
    r.raise_for_status()
    return r.json()