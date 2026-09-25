import flet as ft
import httpx
import os
from dotenv import load_dotenv
from state import auth
from ._shared import ACCENT, BOLD_WHITE, GREY, spacer, create_base_view

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

def CrearEjerciciosV(page: ft.Page) -> ft.View:
    categorias = []
    ejercicios = []
    titulo_seccion = ft.Text("Categorías", size=24, style=BOLD_WHITE)
    contenido_principal = ft.Column(spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)
    estado_mensaje = ft.Text("", color=ft.Colors.GREY)

    async def cargar_categorias():
        try:
            if not auth.token:
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
            contenido_principal.controls = [ft.Text(f"Error: {str(e)}", color=ft.Colors.RED)]
            page.update()

    def mostrar_categorias():
        contenido_principal.controls.clear()
        titulo_seccion.value = "Categorías"
        estado_mensaje.value = ""

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
                        on_click=lambda e, cat_id=cat["id"], cat_nombre=nombre: _on_categoria_click(cat_id, cat_nombre),
                        ink=True,
                    ),
                )
            )
        contenido_principal.controls.append(grid)
        page.update()

    def _on_categoria_click(categoria_id: str, categoria_nombre: str):
        page.run_task(mostrar_ejercicios, categoria_id, categoria_nombre)

    async def mostrar_ejercicios(categoria_id: str, categoria_nombre: str):
        try:
            if not auth.token:
                return
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{BASE_URL}/ejercicios/categoria/{categoria_id}",
                    headers={"Authorization": f"Bearer {auth.token}"},
                )
                resp.raise_for_status()
                data = resp.json()
                ejercicios.clear()
                ejercicios.extend(data)

                contenido_principal.controls.clear()
                titulo_seccion.value = f"Ejercicios - {categoria_nombre}"
                estado_mensaje.value = ""

                if not ejercicios:
                    contenido_principal.controls.append(
                        ft.Text("No hay ejercicios en esta categoría.", color=ft.Colors.WHITE, size=16)
                    )
                    page.update()
                    return

                for ex in ejercicios:
                    contenido_principal.controls.append(
                        ft.Container(
                            width=float('inf'),  
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Text(ex["name"], size=16, weight=ft.FontWeight.BOLD),
                                            ft.Text(ex["description"] or "Sin descripción", size=16, color=ft.Colors.WHITE),
                                        ],
                                        spacing=4,
                                    ),
                                    padding=16,
                                ),
                            ),
                        )
                    )

                contenido_principal.controls.append(
                    ft.TextButton("← Volver a categorías", on_click=lambda _: mostrar_categorias())
                )
                page.update()
        except Exception as e:
            contenido_principal.controls = [ft.Text(f"Error: {str(e)}", color=ft.Colors.RED)]
            page.update()

    page.run_task(cargar_categorias)

    return create_base_view(
        "/ejercicios",
        "Ejercicios",
        [
            titulo_seccion,
            spacer(10),
            estado_mensaje,
            contenido_principal,
        ],
        scroll=False,
    )