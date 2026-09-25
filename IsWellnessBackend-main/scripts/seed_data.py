import sys
import os
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE_DIR)
sys.path.append(BASE_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

from database import engine, sessionLocal
from models import Base, Category, Exercise

CATEGORIAS = [
    "Finalizacion",
    "Manejo del balon",
    "Regate",
    "Tiro",
    "Habilidades defensivas",
    "Pase",
]

EJERCICIOS = {
    "Finalizacion": [
        {"nombre": "Bandeja derecha", "descripcion": "Entrada a canasta con mano derecha, salto y bandeja."},
        {"nombre": "Bandeja izquierda", "descripcion": "Entrada a canasta con mano izquierda, salto y bandeja."},
        {"nombre": "Bandeja con pase", "descripcion": "Recibir pase en movimiento y finalizar en bandeja."},
        {"nombre": "Gancho", "descripcion": "Tiro en gancho con la mano más alejada del defensor."},
        {"nombre": "Palomita", "descripcion": "Tiro cercano al aro con toque suave y efecto."},
    ],
    "Manejo del balon": [
        {"nombre": "Bote en el lugar", "descripcion": "Bote controlado con ambas manos, manteniendo la cabeza arriba."},
        {"nombre": "Bote con cambio de mano", "descripcion": "Bote alternando manos, sin mirar el balón."},
        {"nombre": "Bote en zigzag", "descripcion": "Bote en zigzag entre conos, cambiando de dirección."},
        {"nombre": "Bote con protección", "descripcion": "Bote protegiendo el balón con el cuerpo y la mano libre."},
        {"nombre": "Bote en velocidad", "descripcion": "Bote en línea recta a máxima velocidad, manteniendo control."},
    ],
    "Regate": [
        {"nombre": "Regate simple", "descripcion": "Cambio de dirección rápido con bote y avance."},
        {"nombre": "Regate con finta", "descripcion": "Finta de pase o tiro seguida de cambio de dirección."},
        {"nombre": "Regate entre piernas", "descripcion": "Bote entre piernas para proteger el balón y cambiar de mano."},
        {"nombre": "Regate con salida", "descripcion": "Salida explosiva tras un regate, buscando el aro."},
        {"nombre": "Regate en espacio reducido", "descripcion": "Regate en un área pequeña, con cambios rápidos."},
    ],
    "Tiro": [
        {"nombre": "Tiro libre", "descripcion": "Tiro desde la línea de tiros libres, con mecánica correcta."},
        {"nombre": "Tiro en suspensión", "descripcion": "Tiro desde media distancia, saltando y soltando en el punto más alto."},
        {"nombre": "Tiro de 3 puntos", "descripcion": "Tiro desde la línea de 3, con potencia y arco adecuados."},
        {"nombre": "Tiro en movimiento", "descripcion": "Recibir y tirar en movimiento, sin pausa."},
        {"nombre": "Tiro con salto", "descripcion": "Tiro tras un salto vertical, con buena posición de brazos."},
    ],
    "Habilidades defensivas": [
        {"nombre": "Posición defensiva básica", "descripcion": "Posición de piernas abiertas, manos activas, visión del atacante."},
        {"nombre": "Deslizamiento lateral", "descripcion": "Deslizarse lateralmente manteniendo la posición defensiva."},
        {"nombre": "Defensa al bote", "descripcion": "Seguir al atacante que bota, manteniendo la distancia."},
        {"nombre": "Defensa al tiro", "descripcion": "Saltar para contestar el tiro, sin cometer falta."},
        {"nombre": "Rebote defensivo", "descripcion": "Posicionarse para capturar el rebote defensivo, cajoneando."},
    ],
     "Pase": [
        {"nombre": "Pase de pecho", "descripcion": "Pase con ambas manos desde el pecho, con extensión de brazos y paso adelante."},
        {"nombre": "Pase picado", "descripcion": "Pase que bota en el suelo antes de llegar al compañero, útil para evitar defensas."},
        {"nombre": "Pase de béisbol", "descripcion": "Pase largo con una mano, similar al lanzamiento de béisbol, para avanzar rápido."},
        {"nombre": "Pase de sobrecabeza", "descripcion": "Pase con ambas manos desde arriba de la cabeza, usado para pasar por encima de defensas."},
        {"nombre": "Pase con una mano", "descripcion": "Pase rápido y corto con una mano, sorpresivo y preciso."},
    ],
}

def seed():
    print("Directorio de trabajo actual:", os.getcwd())
    print("Base de datos esperada:", os.path.join(os.getcwd(), "wellness.db"))

    print("Verificando/Creando tablas...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tablas verificadas/creadas correctamente.")
    except Exception as e:
        print(f"Error al crear tablas: {e}")
        return

    db = sessionLocal()
    try:
        print("Verificando datos existentes...")
        
        categorias_existentes = {c.name for c in db.query(Category).all()}
        ejercicios_existentes = {e.name for e in db.query(Exercise).all()}
        categorias_creadas = {}

        for nombre in CATEGORIAS:
            if nombre not in categorias_existentes:
                cat = Category(id=str(uuid.uuid4()), name=nombre)
                db.add(cat)
                db.flush()
                categorias_creadas[nombre] = cat
                print(f"  Categoría creada: {nombre}")
            else:
                cat = db.query(Category).filter(Category.name == nombre).first()
                categorias_creadas[nombre] = cat
                print(f"  Categoría ya existe: {nombre}")

        total_insertados = 0
        for cat_nombre, ejercicios in EJERCICIOS.items():
            categoria = categorias_creadas.get(cat_nombre)
            if not categoria:
                print(f"  Categoría '{cat_nombre}' no encontrada, omitiendo ejercicios.")
                continue
            for ex_data in ejercicios:
                if ex_data["nombre"] not in ejercicios_existentes:
                    ejercicio = Exercise(
                        id=str(uuid.uuid4()),
                        category_id=categoria.id,
                        name=ex_data["nombre"],
                        description=ex_data["descripcion"],
                    )
                    db.add(ejercicio)
                    total_insertados += 1
                    print(f"    Ejercicio creado: {ex_data['nombre']} (categoría: {cat_nombre})")
                else:
                    print(f"    Ejercicio ya existe: {ex_data['nombre']}")

        db.commit()
        print(f"\n¡Datos insertados correctamente! Se añadieron {total_insertados} ejercicios nuevos.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("  POBLANDO BASE DE DATOS - CATÁLOGOS Y EJERCICIOS")
    print("=" * 50)
    seed()
    print("\nProceso completado. Puedes eliminar este script si deseas.")