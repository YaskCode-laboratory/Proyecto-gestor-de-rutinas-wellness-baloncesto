import flet as ft
import httpx
import os
from datetime import datetime
from dotenv import load_dotenv
from state import auth, Cache
from api import get_me
from ._shared import ACCENT, BOLD_WHITE, GREY, spacer, create_base_view

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def CrearPerfilV(page: ft.Page) -> ft.View:
    meta_info = {
        "historial": [],
        "total_metas": 0,
        "total_alcanzadas": 0,
        "racha_dias": 0,
    }
    contenedor_meta = ft.Column(spacing=10)
    meta_valor_texto = ft.Text("", style=BOLD_WHITE, size=16)
    estado_valor_texto = ft.Text("", weight=ft.FontWeight.BOLD, size=15)
    meta_container = ft.Container(
        bgcolor="#2C2C2E",
        border_radius=12,
        padding=15,
        content=ft.Column(
            controls=[
                meta_valor_texto,
                ft.Row(
                    controls=[
                        ft.Text("Estado: ", color=ft.Colors.GREY, size=15),
                        estado_valor_texto,
                    ],
                    spacing=5,
                ),
            ],
        ),
    )

    async def _on_logout(e):
        if auth.token:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{BASE_URL}/auth/logout",
                        headers={"Authorization": f"Bearer {auth.token}"},
                        timeout=5.0,
                    )
            except Exception:
                pass
        await auth.clear(page)
        page.navigate("/login")

    async def _marcar_meta_alcanzada(goal_id: str):
        try:
            if not auth.token:
                return
            async with httpx.AsyncClient() as client:
                resp = await client.patch(
                    f"{BASE_URL}/auth/goal/{goal_id}/achieve",
                    headers={"Authorization": f"Bearer {auth.token}"},
                )
                resp.raise_for_status()

            auth.user = get_me(auth.token)
            await auth.save(page)

            meta_valor_texto.value = "Meta: (sin meta activa)"
            estado_valor_texto.value = "🏆 Alcanzada"
            estado_valor_texto.color = ft.Colors.GREEN
            meta_container.bgcolor = "#1E3A1E"

            Cache.invalidate("dashboard")
            cargar_meta_info()

            page.snack_bar = ft.SnackBar(
                ft.Text("Meta marcada como alcanzada!"),
                bgcolor=ft.Colors.GREEN_700,
                duration=3000,
            )
            page.snack_bar.open = True
            page.update()
        except Exception as e:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Error: {str(e)}"),
                bgcolor=ft.Colors.RED_700,
                duration=3000,
            )
            page.snack_bar.open = True
            page.update()

    def cargar_meta_info():
        try:
            if not auth.token:
                return
            data = Cache.get("meta_info")
            if not data:
                from api import get_meta_info
                data = get_meta_info(auth.token)
                Cache.set("meta_info", data, ttl=30)
            meta_info.update(data)
            actualizar_seccion_meta()
        except Exception as e:
            print(f"Error al cargar meta info: {e}")

    def actualizar_seccion_meta():
        contenedor_meta.controls.clear()

        historial = meta_info.get("historial", [])
        total_metas = meta_info.get("total_metas", 0)
        total_alcanzadas = meta_info.get("total_alcanzadas", 0)
        racha = meta_info.get("racha_dias", 0)

        meta_activa = next((g for g in historial if g["is_active"]), None)

        if meta_activa:
            mensaje_motivacional = "Estas trabajando en tu meta. Sigue asi!"
            color_msg = ft.Colors.BLUE_300
        elif historial:
            mensaje_motivacional = f"Has alcanzado {total_alcanzadas} meta(s). Crea una nueva para seguir mejorando!"
            color_msg = ft.Colors.GREEN_300
        else:
            mensaje_motivacional = "Crea una meta para empezar tu camino."
            color_msg = ft.Colors.GREY

        contenedor_meta.controls.append(
            ft.Container(
                content=ft.Text(mensaje_motivacional, size=15, color=color_msg, italic=True),
                padding=ft.Padding.only(bottom=5),
            )
        )

        if racha > 0:
            fuego = "🔥" if racha >= 3 else "💪"
            contenedor_meta.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(fuego, size=28),
                            ft.Column(
                                controls=[
                                    ft.Text("Racha actual", color=ft.Colors.GREY, size=13),
                                    ft.Text(f"{racha} dia(s) consecutivo(s)", size=16, style=BOLD_WHITE),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    bgcolor="#2C2C2E",
                    border_radius=12,
                    padding=12,
                )
            )

        contenedor_meta.controls.append(
            ft.Row(
                controls=[
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Metas creadas", color=ft.Colors.GREY, size=13, text_align=ft.TextAlign.CENTER),
                                    ft.Text(str(total_metas), size=24, style=BOLD_WHITE, text_align=ft.TextAlign.CENTER),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=2,
                            ),
                            padding=12,
                            width=150,
                        ),
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Alcanzadas", color=ft.Colors.GREY, size=13, text_align=ft.TextAlign.CENTER),
                                    ft.Text(str(total_alcanzadas), size=24, style=BOLD_WHITE, text_align=ft.TextAlign.CENTER),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=2,
                            ),
                            padding=12,
                            width=150,
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            )
        )

        if historial:
            contenedor_meta.controls.append(spacer(5))
            contenedor_meta.controls.append(ft.Text("Historial de metas", size=16, style=BOLD_WHITE))
            for g in historial[:10]:
                alcanzada = g.get("alcanzada", False)
                color_estado = ft.Colors.GREEN if alcanzada else ft.Colors.ORANGE
                texto_estado = "🏆 Alcanzada" if alcanzada else "En progreso"

                fecha_str = ""
                if g.get("created_at"):
                    try:
                        fecha = datetime.fromisoformat(g["created_at"].replace("Z", "+00:00"))
                        fecha_str = fecha.strftime("%d/%m/%Y")
                    except Exception:
                        fecha_str = ""

                contenedor_meta.controls.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(g["objetivo"], size=15, style=BOLD_WHITE, expand=True),
                                        ft.Text(texto_estado, size=12, color=color_estado, weight=ft.FontWeight.BOLD),
                                    ],
                                    spacing=5,
                                ),
                                ft.Text(f"Creada: {fecha_str}" if fecha_str else "", size=12, color=ft.Colors.GREY),
                            ],
                            spacing=2,
                        ),
                        bgcolor="#2C2C2E",
                        border_radius=8,
                        padding=10,
                    )
                )

        page.update()

    if auth.token:
        info = auth.user or {}
        active_goal = info.get("active_goal")

        if active_goal:
            meta = active_goal.get("objetivo", "No definida")
            meta_alcanzada = active_goal.get("alcanzada", False)
        else:
            meta = "No definida"
            meta_alcanzada = False

        color_meta = ft.Colors.GREEN if meta_alcanzada else ft.Colors.RED
        estado_texto = "🏆 Alcanzada" if meta_alcanzada else "⏳ No alcanzada"

        meta_valor_texto.value = f"Meta: {meta}"
        estado_valor_texto.value = estado_texto
        estado_valor_texto.color = color_meta
        meta_container.bgcolor = "#1E3A1E" if meta_alcanzada else "#2C2C2E"

        def _get_value(value, default="No especificado"):
            if value is None or value == "":
                return default
            return value

        perfil_items = [
            ("Nombre", _get_value(info.get("name"))),
            ("Email", _get_value(info.get("email"))),
            ("Rol", _get_value(info.get("role"))),
            ("Edad", f"{_get_value(info.get('age'))} años" if info.get('age') else _get_value(info.get('age'))),
            ("Altura", f"{_get_value(info.get('height'))} cm" if info.get('height') else _get_value(info.get('height'))),
            ("Peso", f"{_get_value(info.get('weight'))} kg" if info.get('weight') else _get_value(info.get('weight'))),
            ("Posicion", _get_value(info.get("position"))),
            ("Nivel", _get_value(info.get("level"))),
        ]

        info_controls = []
        for label, value in perfil_items:
            info_controls.append(
                ft.Row(
                    controls=[
                        ft.Text(f"{label}:", color=ft.Colors.GREY, size=16, width=110),
                        ft.Text(value, color=ft.Colors.WHITE, size=16, weight=ft.FontWeight.W_500),
                    ],
                    spacing=10,
                )
            )

        BOTON_ANCHO = 190

        contenido_scrollable = ft.Column(
            controls=[
                ft.Text("Perfil", size=32, style=BOLD_WHITE),
                spacer(20),
                ft.Container(
                    bgcolor="#2C2C2E",
                    border_radius=12,
                    padding=20,
                    content=ft.Column(controls=info_controls),
                ),
                spacer(10),
                ft.Button(
                    content=ft.Text("Editar perfil", size=14),
                    on_click=lambda _: page.navigate("/editar-perfil"),
                    bgcolor=ft.Colors.GREY_800,
                    color=ft.Colors.WHITE,
                    width=BOTON_ANCHO,
                ),
                spacer(25),
                ft.Text("Meta activa", size=18, style=BOLD_WHITE),
                spacer(5),
                meta_container,
                spacer(10),
                ft.Button(
                    content=ft.Text("Meta alcanzada", size=14),
                    on_click=lambda e: page.run_task(_marcar_meta_alcanzada, active_goal["id"]) if active_goal else None,
                    bgcolor=ft.Colors.GREEN_700,
                    color=ft.Colors.WHITE,
                    width=BOTON_ANCHO,
                    disabled=not active_goal or active_goal.get("alcanzada", False),
                ),
                spacer(25),
                ft.Text("Sobre tus metas", size=18, style=BOLD_WHITE),
                spacer(5),
                contenedor_meta,
                spacer(20),
                ft.Button(
                    content=ft.Text("Cerrar sesion", size=14),
                    on_click=_on_logout,
                    bgcolor=ft.Colors.RED_900,
                    color=ft.Colors.WHITE,
                    width=BOTON_ANCHO,
                ),
                spacer(20),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=5,
        )

        cargar_meta_info()

        return create_base_view(
            "/carrera",
            "Perfil",
            [contenido_scrollable],
            scroll=False,
        )
    else:
        controls = [
            ft.Text("Perfil", size=32, style=BOLD_WHITE),
            spacer(20),
            ft.Text("Inicia sesion para ver tu perfil.", style=GREY, size=16),
            spacer(10),
            ft.Button(
                content=ft.Text("Iniciar sesion", size=14),
                on_click=lambda _: page.navigate("/login"),
                bgcolor=ACCENT,
                color=ft.Colors.WHITE,
            ),
        ]
        return create_base_view("/carrera", "Perfil", controls, scroll=True)