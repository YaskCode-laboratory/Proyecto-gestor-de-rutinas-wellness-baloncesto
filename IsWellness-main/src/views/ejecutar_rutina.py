import flet as ft
import os
import asyncio
from dotenv import load_dotenv
from state import auth, Cache
from api import get_routine, execute_routine
from ._shared import ACCENT, BOLD_WHITE, GREY, spacer

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def CrearEjecutarRutinaV(page: ft.Page, routine_id: str) -> ft.View:
    error_text = ft.Text(color=ft.Colors.RED, size=14)

    effort_slider = ft.Slider(
        min=1, max=5, divisions=4, value=3,
        label="{value} / 5", active_color=ACCENT,
    )
    effort_display = ft.Text("3 / 5", style=BOLD_WHITE)
    effort_desc = ft.Text(
    "1 = Poco esfuerzo  |  3 = Moderado  |  5 = Máximo esfuerzo",
    color=ft.Colors.WHITE, size=14,
    )

    def actualizar_esfuerzo(e):
        effort_display.value = f"{int(effort_slider.value)} / 5"
        page.update()

    effort_slider.on_change = actualizar_esfuerzo

    async def cargar_rutina():
        try:
            if not auth.token:
                return
            routine_data = get_routine(auth.token, routine_id)
            ejercicios_texto = ""
            for idx, ex in enumerate(routine_data.get("exercises", []), 1):
                nombre = ex["exercise"]["name"]
                descripcion = ex["exercise"].get("description") or "Sin descripción disponible"
                sets = ex.get("sets", 3)
                reps = ex.get("reps", 10)
                ejercicios_texto += f"{idx}. {nombre} ({sets}x{reps})\n    {descripcion}\n\n"

            detalles.value = ejercicios_texto
            titulo.value = routine_data.get("title", "Rutina")
            page.update()
        except Exception:
            error_text.value = "Error al cargar la rutina"
            page.update()

    async def ejecutar_y_valorar(e):
        try:
            effort = int(effort_slider.value)
            if not auth.token:
                return
            execute_routine(auth.token, routine_id, effort)

            Cache.invalidate("dashboard")

            mensaje = f"Rutina completada con esfuerzo {effort}/5"
            page.snack_bar = ft.SnackBar(
                ft.Text(mensaje),
                bgcolor=ft.Colors.GREEN_700,
                duration=3000,
            )
            page.snack_bar.open = True
            page.update()

            await asyncio.sleep(1)
            page.navigate("/rutinas")
        except Exception as e:
            error_text.value = f"Error al ejecutar: {str(e)}"
            page.update()

    titulo = ft.Text("Cargando...", size=24, style=BOLD_WHITE)
    detalles = ft.Text("", color=ft.Colors.WHITE, size=16)

    controls = [
        ft.Text("Ejecutar Rutina", size=32, style=BOLD_WHITE),
        spacer(15),
        titulo,
        spacer(10),
        ft.Text("Ejercicios:", size=16, style=BOLD_WHITE),
        detalles,
        spacer(20),
        ft.Divider(),
        spacer(15),
        ft.Text("Valora tu esfuerzo (1-5):", style=BOLD_WHITE),
        effort_slider,
        ft.Row(
            controls=[ft.Text("1", style=BOLD_WHITE), ft.Text("5", style=BOLD_WHITE)],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        effort_desc,
        effort_display,
        spacer(20),
        error_text,
        ft.Button(
            content=ft.Text("Finalizar y valorar"),
            on_click=ejecutar_y_valorar,
            bgcolor=ACCENT,
            color=ft.Colors.WHITE,
            width=200,
        ),
        ft.TextButton("Cancelar", on_click=lambda _: page.navigate("/rutinas")),
    ]

    page.run_task(cargar_rutina)

    return ft.View(
        route=f"/ejecutar/{routine_id}",
        bgcolor=ft.Colors.BLACK,
        padding=20,
        controls=controls,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )