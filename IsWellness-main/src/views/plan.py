import flet as ft
import os
from dotenv import load_dotenv
from state import auth, Cache
from api import get_routines, delete_routine
from ._shared import ACCENT, BG_DARK, BOLD_WHITE, GREY, spacer, create_base_view

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def CrearPlanV(page: ft.Page) -> ft.View:
    list_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    estado_texto = ft.Text("", color=ft.Colors.GREY, size=14)

    async def cargar_rutinas():
        try:
            if auth.token:
                routines = get_routines(auth.token)
                list_column.controls.clear()
                if not routines:
                    list_column.controls.append(
                        ft.Text(
                            "No tienes rutinas aun. Genera una desde aqui.",
                            color=ft.Colors.WHITE,
                            size=16,
                        )
                    )
                else:
                    for r in routines:
                        list_column.controls.append(
                            _crear_tarjeta_rutina(page, r, eliminar_y_recargar)
                        )
                page.update()
        except Exception as e:
            print(f"Error cargando rutinas: {e}")
            list_column.controls.clear()
            list_column.controls.append(
                ft.Text(
                    "Error al cargar las rutinas. Reintenta mas tarde.",
                    color=ft.Colors.RED,
                    size=16,
                )
            )
            page.update()

    async def eliminar_y_recargar(routine_id: str):
        try:
            if auth.token:
                delete_routine(auth.token, routine_id)
                Cache.invalidate("dashboard")
                await cargar_rutinas()
        except Exception as e:
            print(f"Error eliminando rutina: {e}")
            page.snack_bar = ft.SnackBar(
                ft.Text("Error al eliminar la rutina"),
                bgcolor=ft.Colors.RED_700,
            )
            page.snack_bar.open = True
            page.update()

    page.run_task(cargar_rutinas)

    return create_base_view(
        "/rutinas",
        "Rutinas",
        [
            ft.Row(
                controls=[
                    ft.Text("Mis Rutinas", size=28, style=BOLD_WHITE),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            spacer(5),
            ft.Row(
                controls=[
                    ft.Button(
                        content=ft.Text("Generar automatica", size=14),
                        on_click=lambda _: page.navigate("/generar-automatica"),
                        bgcolor=ACCENT,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Button(
                        content=ft.Text("Crear manual", size=14),
                        on_click=lambda _: page.navigate("/crear-manual"),
                        bgcolor=ACCENT,
                        color=ft.Colors.WHITE,
                    ),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
            ),
            spacer(5),
            estado_texto,
            spacer(10),
            ft.Divider(height=1, color=ft.Colors.GREY_400),
            spacer(10),
            ft.Text("Tus rutinas:", style=BOLD_WHITE, size=18),
            spacer(10),
            ft.Container(
                content=list_column,
                expand=True,
            ),
        ],
        scroll=False,
        bgcolor=BG_DARK,
    )


def _crear_tarjeta_rutina(page: ft.Page, routine: dict, on_delete_callback) -> ft.Container:
    ejercicios = routine.get("exercises", [])
    ejercicios_texto = ", ".join([ex["exercise"]["name"] for ex in ejercicios[:3]])
    if len(ejercicios) > 3:
        ejercicios_texto += f" +{len(ejercicios)-3} mas"

    def handle_delete(e):
        page.run_task(on_delete_callback, routine["id"])

    return ft.Container(
        bgcolor="#2C2C2E",
        border_radius=12,
        padding=15,
        margin=ft.Margin.only(bottom=10),
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(routine.get("title", "Sin titulo"), style=BOLD_WHITE, size=16),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(
                    f"Fecha: {routine.get('scheduled_date', '')}",
                    color=ft.Colors.WHITE,
                    size=14,
                ),
                ft.Text(
                    f"Ejercicios: {ejercicios_texto}",
                    color=ft.Colors.WHITE,
                    size=14,
                ),
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.PLAY_ARROW,
                            icon_color=ACCENT,
                            tooltip="Ejecutar rutina",
                            on_click=lambda e: page.navigate(f"/ejecutar/{routine['id']}"),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=ft.Colors.RED_400,
                            tooltip="Eliminar rutina",
                            on_click=handle_delete,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
        ),
    )