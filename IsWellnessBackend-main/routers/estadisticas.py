from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from datetime import datetime, timedelta, date

from database import get_db
from models import User, Routine, RoutineExercise, Exercise, Category, Metric, Goal, ExecutionLog
from auth import get_current_user
from logger import log_action
from services.ia_service import analizar_progreso_con_ia

router = APIRouter(prefix="/estadisticas", tags=["estadisticas"])


def _calcular_racha(db: Session, user_id: str) -> int:
    fechas_raw = db.query(
        func.date(ExecutionLog.executed_at).label("fecha")
    ).filter(
        ExecutionLog.user_id == user_id
    ).distinct().order_by(
        func.date(ExecutionLog.executed_at).desc()
    ).all()

    fechas = []
    for f in fechas_raw:
        valor = f.fecha if hasattr(f, "fecha") else f[0]
        if isinstance(valor, str):
            try:
                fechas.append(date.fromisoformat(valor))
            except ValueError:
                continue
        else:
            fechas.append(valor)

    fechas_set = set(fechas)
    hoy = date.today()
    dia = hoy if hoy in fechas_set else hoy - timedelta(days=1)
    racha = 0
    while dia in fechas_set:
        racha += 1
        dia -= timedelta(days=1)
    return racha


def _categorias_mas_practicadas(db: Session, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    filas = db.query(
        Category.name,
        func.count(RoutineExercise.id).label("total"),
    ).join(
        Exercise, Exercise.category_id == Category.id
    ).join(
        RoutineExercise, RoutineExercise.exercise_id == Exercise.id
    ).join(
        Routine, Routine.id == RoutineExercise.routine_id
    ).filter(
        Routine.user_id == user_id,
        Routine.is_deleted == False,
        RoutineExercise.is_deleted == False,
    ).group_by(Category.name).order_by(
        func.count(RoutineExercise.id).desc()
    ).limit(limit).all()
    return [{"nombre": f.name, "total": f.total} for f in filas]


def _esfuerzo_por_categoria(db: Session, user_id: str) -> List[Dict[str, Any]]:
    filas = db.query(
        Category.name,
        func.avg(RoutineExercise.effort_rating).label("avg_effort"),
    ).join(
        Exercise, Exercise.category_id == Category.id
    ).join(
        RoutineExercise, RoutineExercise.exercise_id == Exercise.id
    ).join(
        Routine, Routine.id == RoutineExercise.routine_id
    ).filter(
        Routine.user_id == user_id,
        Routine.is_deleted == False,
        RoutineExercise.is_deleted == False,
        RoutineExercise.effort_rating.isnot(None),
    ).group_by(Category.name).all()
    return [
        {"categoria": f.name, "esfuerzo_promedio": round(f.avg_effort, 2)}
        for f in filas if f.avg_effort is not None
    ]


def _resumen_data(db: Session, user_id: str) -> Dict[str, Any]:
    total_rutinas = db.query(Routine).filter(
        Routine.user_id == user_id,
        Routine.is_deleted == False,
    ).count()

    total_ejecuciones = db.query(ExecutionLog).filter(
        ExecutionLog.user_id == user_id,
    ).count()

    avg_effort = db.query(func.avg(ExecutionLog.effort_rating)).filter(
        ExecutionLog.user_id == user_id,
    ).scalar() or 0.0

    return {
        "total_rutinas": total_rutinas,
        "total_ejecuciones": total_ejecuciones,
        "esfuerzo_promedio": round(avg_effort, 2),
        "categorias_mas_practicadas": _categorias_mas_practicadas(db, user_id),
    }


def _meta_info_data(db: Session, user_id: str) -> Dict[str, Any]:
    goals = db.query(Goal).filter(
        Goal.user_id == user_id,
    ).order_by(Goal.created_at.desc()).all()

    historial = [
        {
            "id": g.id,
            "objetivo": g.objective,
            "is_active": g.is_active,
            "alcanzada": not g.is_active,
            "created_at": g.created_at.isoformat() if g.created_at else None,
            "updated_at": g.updated_at.isoformat() if g.updated_at else None,
        }
        for g in goals
    ]

    return {
        "historial": historial,
        "total_metas": len(goals),
        "total_alcanzadas": sum(1 for g in goals if not g.is_active),
        "racha_dias": _calcular_racha(db, user_id),
    }


@router.get("/dashboard")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    log_action(current_user.id, "Consulta", "Dashboard de estadisticas")
    return {
        "resumen": _resumen_data(db, current_user.id),
        "esfuerzo_categorias": _esfuerzo_por_categoria(db, current_user.id),
        "meta_info": _meta_info_data(db, current_user.id),
    }


@router.get("/resumen")
def get_resumen(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    log_action(current_user.id, "Consulta", "Estadisticas de resumen")
    return _resumen_data(db, current_user.id)


@router.get("/evolucion/{metric_type}")
def get_evolucion(
    metric_type: str,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    desde = datetime.now() - timedelta(days=days)
    filas = db.query(
        Metric.recorded_date,
        func.avg(Metric.value).label("avg_value"),
    ).filter(
        Metric.user_id == current_user.id,
        Metric.metric_type == metric_type,
        Metric.recorded_date >= desde.date(),
        Metric.is_deleted == False,
    ).group_by(Metric.recorded_date).order_by(Metric.recorded_date).all()

    log_action(current_user.id, "Consulta", f"Evolucion de metrica: {metric_type}")

    return [
        {"fecha": f.recorded_date.isoformat(), "valor": round(f.avg_value, 2)}
        for f in filas
    ]


@router.get("/esfuerzo-por-categoria")
def get_esfuerzo_por_categoria(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    log_action(current_user.id, "Consulta", "Esfuerzo por categoria")
    return _esfuerzo_por_categoria(db, current_user.id)


@router.get("/meta-info")
def get_meta_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    log_action(current_user.id, "Consulta", "Informacion de metas y racha")
    return _meta_info_data(db, current_user.id)


@router.get("/analizar-ia")
def analizar_progreso(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    resumen = _resumen_data(db, current_user.id)
    meta = _meta_info_data(db, current_user.id)

    analisis = analizar_progreso_con_ia(
        total_rutinas=resumen["total_rutinas"],
        total_ejecuciones=resumen["total_ejecuciones"],
        esfuerzo_promedio=resumen["esfuerzo_promedio"],
        racha_dias=meta["racha_dias"],
        total_metas=meta["total_metas"],
        total_alcanzadas=meta["total_alcanzadas"],
        categorias_mas_practicadas=resumen["categorias_mas_practicadas"],
        esfuerzo_categorias=_esfuerzo_por_categoria(db, current_user.id),
        nombre_usuario=current_user.name or "Jugador",
        posicion=current_user.position or "Base",
        nivel=current_user.level or "Intermedio",
    )

    log_action(current_user.id, "Consulta", "Analisis de progreso con IA")

    return {"analisis": analisis}