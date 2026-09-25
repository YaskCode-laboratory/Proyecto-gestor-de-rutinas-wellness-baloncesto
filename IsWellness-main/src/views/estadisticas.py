import flet as ft
import os
import asyncio
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from state import auth, Cache
from api import get_dashboard, analizar_progreso_ia
from ._shared import ACCENT, BOLD_WHITE, GREY, spacer, create_base_view


def CrearEstadisticasV(page: ft.Page) -> ft.View:
    resumen_data = {
        "total_rutinas": 0,
        "total_ejecuciones": 0,
        "esfuerzo_promedio": 0,
        "categorias_mas_practicadas": [],
    }
    esfuerzo_categorias = []
    meta_info = {
        "total_metas": 0,
        "total_alcanzadas": 0,
        "racha_dias": 0,
    }
    error_text = ft.Text("", color=ft.Colors.RED, size=14)
    estado_texto = ft.Text("", color=ACCENT, size=14, text_align=ft.TextAlign.CENTER)
    analisis_container = ft.Container(
        content=ft.Column(controls=[], spacing=8),
        bgcolor="#2C2C2E",
        border_radius=12,
        padding=15,
        visible=False,
    )
    contenedor = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)

    def cargar_datos():
        try:
            if not auth.token:
                return
            data = Cache.get("dashboard")
            if not data:
                data = get_dashboard(auth.token)
                Cache.set("dashboard", data, ttl=30)

            resumen_data.update(data["resumen"])
            esfuerzo_categorias.clear()
            esfuerzo_categorias.extend(data["esfuerzo_categorias"])
            meta_info.update(data["meta_info"])
            actualizar_vista()
        except Exception as e:
            error_text.value = f"Error al cargar datos: {str(e)}"
            page.update()

    def generar_imagen_progreso() -> str:
        ancho, alto = 700, 900
        fondo = (28, 28, 30)
        card_bg = (44, 44, 46)
        blanco = (255, 255, 255)
        gris = (150, 150, 150)
        accent = (255, 140, 0)

        img = Image.new("RGB", (ancho, alto), fondo)
        draw = ImageDraw.Draw(img)

        try:
            font_titulo = ImageFont.truetype("arial.ttf", 32)
            font_subtitulo = ImageFont.truetype("arial.ttf", 22)
            font_texto = ImageFont.truetype("arial.ttf", 18)
            font_pequeno = ImageFont.truetype("arial.ttf", 14)
        except Exception:
            font_titulo = ImageFont.load_default()
            font_subtitulo = ImageFont.load_default()
            font_texto = ImageFont.load_default()
            font_pequeno = ImageFont.load_default()

        draw.text((ancho // 2, 30), "Mi Progreso Wellness", fill=blanco, font=font_titulo, anchor="mm")
        draw.text((ancho // 2, 70), "Baloncesto", fill=gris, font=font_pequeno, anchor="mm")
        draw.line([(40, 90), (ancho - 40, 90)], fill=accent, width=2)

        y = 120
        card_w, card_h = 180, 100
        for x, titulo, valor in [
            (50, "Rutinas", str(resumen_data.get("total_rutinas", 0))),
            (50 + card_w + 30, "Ejecuciones", str(resumen_data.get("total_ejecuciones", 0))),
            (50 + (card_w + 30) * 2, "Esfuerzo", f"{resumen_data.get('esfuerzo_promedio', 0):.1f}/5"),
        ]:
            draw.rounded_rectangle([x, y, x + card_w, y + card_h], radius=12, fill=card_bg)
            draw.text((x + card_w // 2, y + 30), titulo, fill=gris, font=font_pequeno, anchor="mm")
            draw.text((x + card_w // 2, y + 65), valor, fill=blanco, font=font_titulo, anchor="mm")

        y += card_h + 30
        racha = meta_info.get("racha_dias", 0)
        if racha > 0:
            draw.rounded_rectangle([50, y, ancho - 50, y + 60], radius=12, fill=card_bg)
            draw.text((ancho // 2, y + 30), f"Racha actual: {racha} dia(s) consecutivo(s)", fill=accent, font=font_texto, anchor="mm")
            y += 80

        categorias = resumen_data.get("categorias_mas_practicadas", [])
        if categorias:
            draw.text((50, y), "Categorias mas practicadas", fill=blanco, font=font_subtitulo)
            y += 40
            for cat in categorias[:5]:
                draw.text((60, y), f"- {cat['nombre']}: {cat['total']} veces", fill=gris, font=font_texto)
                y += 28
            y += 10

        if esfuerzo_categorias:
            draw.text((50, y), "Esfuerzo por categoria", fill=blanco, font=font_subtitulo)
            y += 40
            for item in esfuerzo_categorias:
                draw.text((60, y), item["categoria"], fill=blanco, font=font_texto)
                bar_x, bar_w, bar_h = 250, 320, 18
                draw.rounded_rectangle([bar_x, y, bar_x + bar_w, y + bar_h], radius=9, fill=card_bg)
                filled = int(bar_w * (item["esfuerzo_promedio"] / 5))
                if filled > 0:
                    draw.rounded_rectangle([bar_x, y, bar_x + filled, y + bar_h], radius=9, fill=accent)
                draw.text((bar_x + bar_w + 15, y), f"{item['esfuerzo_promedio']:.1f}/5", fill=gris, font=font_pequeno)
                y += 32
            y += 10

        draw.line([(40, alto - 60), (ancho - 40, alto - 60)], fill=gris, width=1)
        draw.text((ancho // 2, alto - 35), "Generado con Wellness Basket", fill=gris, font=font_pequeno, anchor="mm")

        home = Path.home()
        downloads = home / "Downloads"
        if not downloads.exists():
            downloads = home

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = downloads / f"mi_progreso_wellness_{timestamp}.png"
        img.save(filepath, "PNG")
        return str(filepath)

    async def compartir_progreso(e):
        estado_texto.value = "Generando imagen de progreso..."
        estado_texto.color = ACCENT
        analisis_container.visible = False
        page.update()

        await asyncio.sleep(0.5)

        try:
            filepath = await asyncio.to_thread(generar_imagen_progreso)
            estado_texto.value = f"Imagen guardada en:\n{filepath}"
            estado_texto.color = ft.Colors.GREEN_400
            page.update()
            await asyncio.sleep(6)
            estado_texto.value = ""
            page.update()
        except Exception as ex:
            estado_texto.value = f"Error al generar la imagen: {str(ex)}"
            estado_texto.color = ft.Colors.RED_400
            page.update()
            await asyncio.sleep(6)
            estado_texto.value = ""
            page.update()

    async def analizar_con_ia(e):
        estado_texto.value = "Analizando tu progreso con IA... esto puede tardar unos segundos."
        estado_texto.color = ACCENT
        analisis_container.visible = False
        page.update()

        await asyncio.sleep(0.5)

        try:
            if not auth.token:
                return
            result = await asyncio.to_thread(analizar_progreso_ia, auth.token)
            analisis = result.get("analisis", "Sin respuesta.")

            estado_texto.value = ""
            page.update()

            analisis_container.content.controls.clear()
            analisis_container.content.controls.append(
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.AUTO_AWESOME, color=ACCENT, size=22),
                        ft.Text("Analisis de tu progreso", size=18, style=BOLD_WHITE),
                    ],
                    spacing=8,
                )
            )
            analisis_container.content.controls.append(
                ft.Text(analisis, size=15, color=ft.Colors.WHITE, selectable=True)
            )
            analisis_container.visible = True
            page.update()
        except Exception as ex:
            estado_texto.value = f"Error al analizar: {str(ex)}"
            estado_texto.color = ft.Colors.RED_400
            page.update()
            await asyncio.sleep(6)
            estado_texto.value = ""
            page.update()

    def actualizar_vista():
        contenedor.controls.clear()

        contenedor.controls.append(
            ft.Row(
                controls=[
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Total rutinas", color=ft.Colors.WHITE, size=14, text_align=ft.TextAlign.CENTER),
                                    ft.Text(str(resumen_data.get("total_rutinas", 0)), size=24, style=BOLD_WHITE, text_align=ft.TextAlign.CENTER),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=20,
                            width=120,
                        ),
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Ejecuciones", color=ft.Colors.WHITE, size=14, text_align=ft.TextAlign.CENTER),
                                    ft.Text(str(resumen_data.get("total_ejecuciones", 0)), size=24, style=BOLD_WHITE, text_align=ft.TextAlign.CENTER),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=20,
                            width=120,
                        ),
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Esfuerzo promedio", color=ft.Colors.WHITE, size=14, text_align=ft.TextAlign.CENTER),
                                    ft.Text(f"{resumen_data.get('esfuerzo_promedio', 0):.1f}/5", size=24, style=BOLD_WHITE, text_align=ft.TextAlign.CENTER),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=20,
                            width=120,
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                wrap=True,
            )
        )

        racha = meta_info.get("racha_dias", 0)
        if racha > 0:
            contenedor.controls.append(spacer(10))
            contenedor.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[ft.Text(f"Racha actual: {racha} dia(s) consecutivo(s)", size=16, style=BOLD_WHITE)],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    bgcolor="#2C2C2E",
                    border_radius=12,
                    padding=12,
                )
            )

        if resumen_data.get("categorias_mas_practicadas"):
            contenedor.controls.append(ft.Divider())
            contenedor.controls.append(ft.Text("Categorias mas practicadas", size=18, style=BOLD_WHITE))
            for cat in resumen_data["categorias_mas_practicadas"]:
                contenedor.controls.append(
                    ft.Text(f"- {cat['nombre']}: {cat['total']} veces", size=16, color=ft.Colors.WHITE)
                )

        if esfuerzo_categorias:
            contenedor.controls.append(ft.Divider())
            contenedor.controls.append(ft.Text("Esfuerzo por categoria", size=18, style=BOLD_WHITE))
            for item in esfuerzo_categorias:
                barra = ft.ProgressBar(
                    value=item["esfuerzo_promedio"] / 5,
                    width=180,
                    color=ACCENT,
                    bgcolor="#2C2C2E",
                )
                contenedor.controls.append(
                    ft.Row(
                        controls=[
                            ft.Text(item["categoria"], width=150, size=16, color=ft.Colors.WHITE),
                            barra,
                            ft.Text(f"{item['esfuerzo_promedio']:.1f}/5", size=16, color=ft.Colors.WHITE),
                        ],
                        spacing=10,
                    )
                )

        if not resumen_data.get("categorias_mas_practicadas") and not esfuerzo_categorias:
            contenedor.controls.append(
                ft.Text("Aun no hay suficientes datos para mostrar estadisticas.", color=ft.Colors.WHITE, size=16)
            )

        page.update()

    cargar_datos()

    return create_base_view(
        "/estadisticas",
        "Progreso",
        [
            ft.Text("Estadisticas", size=32, style=BOLD_WHITE),
            spacer(10),
            ft.Row(
                controls=[
                    ft.Button(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.SHARE, color=ft.Colors.WHITE, size=18),
                                ft.Text("Compartir", color=ft.Colors.WHITE, size=14),
                            ],
                            spacing=6,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        on_click=compartir_progreso,
                        bgcolor=ACCENT,
                        width=170,
                    ),
                    ft.Button(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.AUTO_AWESOME, color=ft.Colors.WHITE, size=18),
                                ft.Text("Analizar IA", color=ft.Colors.WHITE, size=14),
                            ],
                            spacing=6,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        on_click=analizar_con_ia,
                        bgcolor=ACCENT,
                        width=170,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            spacer(5),
            ft.Row(controls=[estado_texto], alignment=ft.MainAxisAlignment.CENTER),
            spacer(10),
            analisis_container,
            spacer(10),
            contenedor,
            spacer(10),
            error_text,
        ],
        scroll=False,
    )