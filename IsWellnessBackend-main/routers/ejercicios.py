from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Category, Exercise, User
from schemas.routine import ExerciseResponse
from auth import get_current_user
from logger import log_action

router = APIRouter(prefix="/ejercicios", tags=["ejercicios"])


@router.get("/categorias", response_model=List[dict])
def get_categorias(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    categorias = db.query(Category).filter(Category.is_deleted == False).all()
    log_action(current_user.id, "Consulta", "Listado de categorías de ejercicios")
    return [
        {
            "id": cat.id,
            "nombre": cat.name,
            "icono": _obtener_icono_por_nombre(cat.name),
        }
        for cat in categorias
    ]


@router.get("/categoria/{categoria_id}", response_model=List[ExerciseResponse])
def get_ejercicios_por_categoria(
    categoria_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    categoria = db.query(Category).filter(
        Category.id == categoria_id,
        Category.is_deleted == False
    ).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    ejercicios = db.query(Exercise).filter(
        Exercise.category_id == categoria_id,
        Exercise.is_deleted == False
    ).all()
    log_action(current_user.id, "Consulta", f"Ejercicios de categoría: {categoria.name}")
    return ejercicios


@router.get("/", response_model=List[ExerciseResponse])
def get_todos_ejercicios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ejercicios = db.query(Exercise).filter(Exercise.is_deleted == False).all()
    log_action(current_user.id, "Consulta", "Listado completo de ejercicios")
    return ejercicios


def _obtener_icono_por_nombre(nombre: str) -> str:
    mapa = {
        "Finalizacion": "sports_basketball",
        "Manejo del balon": "sports_handball",
        "Regate": "directions_run",
        "Tiro": "sports_tennis",
        "Habilidades defensivas": "shield",
    }
    return mapa.get(nombre, "extension")