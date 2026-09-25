import flet as ft
import asyncio
from state import auth, Cache
from api import generate_routine
from ._shared import ACCENT, BOLD_WHITE, GREY, spacer, create_base_view


def CrearGenerarAutomaticaV(page: ft.Page) -> ft.View:
    estado_texto = ft.Text("", color=ACCENT, size=14, text_align=ft.TextAlign.CENTER)
    error_text = ft.Text("", color=ft.Colors.RED, size=14)
    progress_ring = ft.ProgressRing(width=20, height=20, stroke_width=2, color=ACCENT, visible=False)

    title_field = ft.TextField(
        label="Nombre de la rutina (opcional)",
        hint_text="Ej: Mi rutina de tiro",
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        label_style=ft.TextStyle(color=ft.Colors.WHITE),
    )
    objective_field = ft.TextField(
        label="Objetivo de la rutina",
        hint_text="Ej: Mejorar tiro de 3 puntos",
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        label_style=ft.TextStyle(color=ft.Colors.WHITE),
    )
    time_field = ft.TextField(
        label="Tiempo disponible (minutos)",
        hint_text="30",
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        label_style=ft.TextStyle(color=ft.Colors.WHITE),
        value="30",
    )

    async def generar(e):
        title = title_field.value.strip() if title_field.value else None
        objective = objective_field.value.strip()
        time_str = time_field.value.strip()

        if not objective:
            error_text.value = "Ingresa un objetivo"
            page.update()
            return
        try:
            minutes = int(time_str)
            if minutes < 5 or minutes > 120:
                error_text.value = "El tiempo debe estar entre 5 y 120 minutos"
                page.update()
                return
        except ValueError:
            error_text.value = "Ingresa un numero valido para el tiempo"
            page.update()
            return

        error_text.value = ""
        estado_texto.value = "Generando tu rutina con IA... por favor espera."
        estado_texto.color = ACCENT
        progress_ring.visible = True
        page.update()

        await asyncio.sleep(0.5)

        try:
            result = await asyncio.to_thread(
                generate_routine,
                auth.token,
                "Base",
                "Intermedio",
                objective,
                minutes,
                title,
            )

            origen = result.get("generado_por", "desconocido")

            if origen == "ia":
                estado_texto.value = f"Rutina generada con IA: {result.get('title', '')}"
                estado_texto.color = ft.Colors.GREEN_400
            elif origen == "fallback":
                estado_texto.value = f"Rutina generada con modo de respaldo: {result.get('title', '')}"
                estado_texto.color = ft.Colors.ORANGE_400
            else:
                estado_texto.value = f"Rutina generada: {result.get('title', '')}"
                estado_texto.color = ACCENT

            progress_ring.visible = False
            Cache.invalidate("dashboard")
            page.update()

            await asyncio.sleep(1.5)
            page.navigate("/rutinas")

        except Exception as ex:
            progress_ring.visible = False
            estado_texto.value = f"Error al generar: {str(ex)}"
            estado_texto.color = ft.Colors.RED_400
            page.update()

    def volver(e):
        page.navigate("/rutinas")

    estado_row = ft.Row(
        controls=[progress_ring, estado_texto],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    content = ft.Column(
        controls=[
            ft.Row(
                controls=[ft.TextButton("← Volver", on_click=volver)],
                alignment=ft.MainAxisAlignment.START,
            ),
            spacer(5),
            ft.Text("Generar rutina automatica", size=32, style=BOLD_WHITE),
            spacer(15),
            ft.Text("Completa la informacion para generar tu rutina:", color=ft.Colors.WHITE, size=16),
            spacer(10),
            title_field,
            spacer(10),
            objective_field,
            spacer(10),
            time_field,
            spacer(10),
            error_text,
            spacer(5),
            estado_row,
            spacer(10),
            ft.Row(
                controls=[
                    ft.Button(
                        content=ft.Text("Generar", color=ft.Colors.WHITE, size=14),
                        on_click=generar,
                        bgcolor=ACCENT,
                        width=200,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    return create_base_view(
        "/generar-automatica",
        "Generar rutina automatica",
        content,
        scroll=False,
    )