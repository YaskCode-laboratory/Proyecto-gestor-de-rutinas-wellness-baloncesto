import flet as ft
import httpx
import os
from dotenv import load_dotenv
from state import auth
from api import create_manual_routine
from ._shared import ACCENT, BOLD_WHITE, GREY, spacer, create_base_view
from state import auth, Cache

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

ICONOS_CATEGORIAS = {
    "Finalizacion": ft.Icons.SPORTS_BASKETBALL,
    "Manejo del balon": ft.Icons.SPORTS_HANDBALL,
    "Regate": ft.Icons.DIRECTIONS_RUN,
    "Tiro": ft.Icons.SPORTS_TENNIS,
    "Habilidades defensivas": ft.Icons.SHIELD,
    "Pase": ft.Icons.SWAP_HORIZ,
}


def CrearRutinaManualV(page: ft.Page) -> ft.View:
    categorias = []
    ejercicios_actuales = []
    seleccionados = {}
    categoria_actual_id = None
    categoria_actual_nombre = ""

    titulo_seccion = ft.Text("Categorías", size=24, style=BOLD_WHITE)
    contador_seleccion = ft.Text("0 ejercicios seleccionados", color=ft.Colors.WHITE, size=16)
    error_text = ft.Text("", color=ft.Colors.RED, size=12)
    contenido_principal = ft.Column(spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)

    nombre_field = ft.TextField(
        label="Nombre de la rutina",
        hint_text="Ej: Mi rutina de tiro",
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        label_style=ft.TextStyle(color=ft.Colors.WHITE),
        on_change=lambda e: actualizar_boton_crear(),
    )

    btn_crear = ft.Button(
        content=ft.Text("Crear Rutina"),
        on_click=lambda e: crear_rutina(),
        bgcolor=ACCENT,
        color=ft.Colors.WHITE,
        disabled=True,
    )

    def volver_a_rutinas(e=None):
        page.navigate("/rutinas")

    async def cargar_categorias():
        try:
            if not auth.token:
                error_text.value = "No autenticado. Inicia sesión."
                page.update()
                return
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{BASE_URL}/ejercicios/categorias",
                    headers={"Authorization": f"Bearer {auth.token}"},
                )
                resp.raise_for_status()
                data = resp.json()
                categorias.clear()
                categorias.extend(data)
                mostrar_categorias()
        except Exception as e:
            error_text.value = f"Error al cargar categorías: {str(e)}"
            page.update()

    def mostrar_categorias():
        contenido_principal.controls.clear()
        titulo_seccion.value = "Selecciona una categoría"
        error_text.value = ""
        actualizar_boton_crear()

        grid = ft.GridView(
            max_extent=140,
            child_aspect_ratio=0.9,
            spacing=10,
            run_spacing=10,
            padding=10,
            expand=True,
        )
        for cat in categorias:
            nombre = cat["nombre"]
            icono = ICONOS_CATEGORIAS.get(nombre, ft.Icons.EXTENSION)
            grid.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(icono, size=40, color=ACCENT),
                                ft.Text(nombre, size=14, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        padding=16,
                        alignment=ft.Alignment.CENTER,
                        on_click=lambda e, cat_id=cat["id"], cat_nombre=nombre: _ir_a_ejercicios(cat_id, cat_nombre),
                        ink=True,
                    ),
                )
            )
        contenido_principal.controls.append(grid)
        page.update()

    def _ir_a_ejercicios(categoria_id: str, categoria_nombre: str):
        page.run_task(mostrar_ejercicios, categoria_id, categoria_nombre)

    async def mostrar_ejercicios(categoria_id: str, categoria_nombre: str):
        try:
            if not auth.token:
                error_text.value = "No autenticado"
                page.update()
                return

            nonlocal categoria_actual_id, categoria_actual_nombre
            categoria_actual_id = categoria_id
            categoria_actual_nombre = categoria_nombre

            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{BASE_URL}/ejercicios/categoria/{categoria_id}",
                    headers={"Authorization": f"Bearer {auth.token}"},
                )
                resp.raise_for_status()
                data = resp.json()

            ejercicios_actuales.clear()
            ejercicios_actuales.extend(data)

            contenido_principal.controls.clear()
            titulo_seccion.value = f"Selecciona ejercicios - {categoria_nombre}"
            error_text.value = ""

            if not ejercicios_actuales:
                contenido_principal.controls.append(
                    ft.Text("No hay ejercicios en esta categoría.", color=ft.Colors.GREY)
                )
                page.update()
                return

            contenido_principal.controls.append(
                ft.TextButton("← Volver a categorías", on_click=lambda _: mostrar_categorias())
            )

            for ex in ejercicios_actuales:
                esta_seleccionado = ex["id"] in seleccionados
                sets_val = seleccionados[ex["id"]]["sets"] if esta_seleccionado else 3
                reps_val = seleccionados[ex["id"]]["reps"] if esta_seleccionado else 10

                sets_field = ft.TextField(
                    value=str(sets_val),
                    width=60,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    filled=True,
                    bgcolor="#2C2C2E",
                    border_radius=8,
                    text_style=ft.TextStyle(color=ft.Colors.WHITE, size=12),
                    on_change=lambda e, ex_id=ex["id"]: actualizar_valor_ejercicio(ex_id, "sets", e.control.value),
                )
                reps_field = ft.TextField(
                    value=str(reps_val),
                    width=60,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    filled=True,
                    bgcolor="#2C2C2E",
                    border_radius=8,
                    text_style=ft.TextStyle(color=ft.Colors.WHITE, size=12),
                    on_change=lambda e, ex_id=ex["id"]: actualizar_valor_ejercicio(ex_id, "reps", e.control.value),
                )

                contenido_principal.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Checkbox(
                                                value=esta_seleccionado,
                                                on_change=lambda e, ex_id=ex["id"]: alternar_seleccion(ex_id),
                                                fill_color=ACCENT if esta_seleccionado else None,
                                            ),
                                            ft.Text(ex["name"], size=16, weight=ft.FontWeight.BOLD, expand=True),
                                        ],
                                        spacing=10,
                                    ),
                                    ft.Text(ex.get("description") or "Sin descripción", size=14, color=ft.Colors.WHITE),
                                    ft.Row(
                                        controls=[
                                            ft.Text("Series:", color=ft.Colors.WHITE, size=14),
                                            sets_field,
                                            ft.Text("Reps:", color=ft.Colors.WHITE, size=14),
                                            reps_field,
                                        ],
                                        spacing=5,
                                        wrap=False,
                                    ),
                                ],
                                spacing=8,
                            ),
                            padding=16,
                            width=float('inf'),
                            bgcolor=ft.Colors.GREEN_900 if esta_seleccionado else None,
                        ),
                    )
                )

            actualizar_boton_crear()
            page.update()

        except Exception as e:
            error_text.value = f"Error al cargar ejercicios: {str(e)}"
            page.update()

    def alternar_seleccion(exercise_id: str):
        if exercise_id in seleccionados:
            del seleccionados[exercise_id]
        else:
            seleccionados[exercise_id] = {"sets": 3, "reps": 10}
        actualizar_boton_crear()
        page.run_task(_refrescar_solo_checkboxes)

    async def _refrescar_solo_checkboxes():
        if categoria_actual_id:
            await mostrar_ejercicios(categoria_actual_id, categoria_actual_nombre)

    def actualizar_valor_ejercicio(exercise_id: str, campo: str, valor: str):
        if exercise_id in seleccionados:
            try:
                valor_int = int(valor) if valor and valor.strip() else 0
                if valor_int > 0:
                    seleccionados[exercise_id][campo] = valor_int
                actualizar_boton_crear()
            except ValueError:
                pass

    def actualizar_boton_crear():
        tiene_nombre = bool(nombre_field.value and nombre_field.value.strip())
        tiene_ejercicios = len(seleccionados) > 0
        btn_crear.disabled = not (tiene_nombre and tiene_ejercicios)
        contador_seleccion.value = f"{len(seleccionados)} ejercicios seleccionados"
        page.update()

    def crear_rutina():
        nombre = nombre_field.value.strip()
        if not nombre:
            error_text.value = "Ingresa un nombre para la rutina"
            actualizar_boton_crear()
            return
        if len(seleccionados) == 0:
            error_text.value = "Selecciona al menos un ejercicio"
            actualizar_boton_crear()
            return
        if not auth.token:
            error_text.value = "No autenticado"
            actualizar_boton_crear()
            return

        ejercicios_lista = [
            {"exercise_id": ex_id, "sets": datos["sets"], "reps": datos["reps"]}
            for ex_id, datos in seleccionados.items()
        ]

        try:
            create_manual_routine(auth.token, nombre, ejercicios_lista)
            Cache.invalidate("dashboard")
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Rutina '{nombre}' creada exitosamente"),
                bgcolor=ft.Colors.GREEN_700,
            )
            page.snack_bar.open = True
            page.navigate("/rutinas")
        except Exception as e:
            error_text.value = f"Error al crear rutina: {str(e)}"
            actualizar_boton_crear()

    page.run_task(cargar_categorias)

    return create_base_view(
        "/crear-manual",
        "Crear Rutina Manual",
        [
            ft.Row(
                controls=[
                    ft.TextButton("← Volver", on_click=volver_a_rutinas),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            spacer(5),
            titulo_seccion,
            spacer(5),
            contador_seleccion,
            spacer(5),
            ft.Row(
                controls=[
                    nombre_field,
                    btn_crear,
                ],
                spacing=10,
            ),
            spacer(5),
            error_text,
            spacer(10),
            contenido_principal,
        ],
        scroll=False,
    )