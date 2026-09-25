import flet as ft
from state import auth, Cache
from api import update_user
from ._shared import ACCENT, BOLD_WHITE, GREY, spacer, create_base_view


def CrearEditarPerfilV(page: ft.Page) -> ft.View:
    info = auth.user or {}
    active_goal = info.get("active_goal")
    error_text = ft.Text("", color=ft.Colors.RED, size=14)

    name_field = ft.TextField(
        label="Nombre",
        value=info.get("name", ""),
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        label_style=ft.TextStyle(color=ft.Colors.WHITE),
    )
    position_field = ft.Dropdown(
        label="Posicion",
        options=[
            ft.dropdown.Option("Base"),
            ft.dropdown.Option("Alero"),
            ft.dropdown.Option("Pivot"),
            ft.dropdown.Option("Escolta"),
            ft.dropdown.Option("Ala-Pivot"),
        ],
        value=info.get("position"),
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        label_style=ft.TextStyle(color=ft.Colors.WHITE),
    )
    level_field = ft.Dropdown(
        label="Nivel",
        options=[
            ft.dropdown.Option("Principiante"),
            ft.dropdown.Option("Intermedio"),
            ft.dropdown.Option("Avanzado"),
        ],
        value=info.get("level"),
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        label_style=ft.TextStyle(color=ft.Colors.WHITE),
    )
    age_field = ft.TextField(
        label="Edad",
        value=str(info.get("age", "")) if info.get("age") else "",
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        label_style=ft.TextStyle(color=ft.Colors.WHITE),
    )
    height_field = ft.TextField(
        label="Altura (cm)",
        value=str(info.get("height", "")) if info.get("height") else "",
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        label_style=ft.TextStyle(color=ft.Colors.WHITE),
    )
    weight_field = ft.TextField(
        label="Peso (kg)",
        value=str(info.get("weight", "")) if info.get("weight") else "",
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        label_style=ft.TextStyle(color=ft.Colors.WHITE),
    )

    meta_field = ft.TextField(
        label="Meta",
        value=active_goal.get("objetivo", "") if active_goal else "",
        hint_text="Ej: Mejorar tiro de 3 puntos",
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        label_style=ft.TextStyle(color=ft.Colors.WHITE),
    )

    async def guardar(e):
        data = {
            "name": name_field.value,
            "position": position_field.value,
            "level": level_field.value,
            "age": int(age_field.value) if age_field.value else None,
            "height": float(height_field.value) if height_field.value else None,
            "weight": float(weight_field.value) if weight_field.value else None,
            "meta_objetivo": meta_field.value.strip() if meta_field.value else None,
        }
        data = {k: v for k, v in data.items() if v is not None}
        try:
            if auth.token:
                result = update_user(auth.token, data)
                auth.user = result
                await auth.save(page)
                Cache.invalidate("dashboard")
                Cache.invalidate("meta_info")
                page.snack_bar = ft.SnackBar(
                    ft.Text("Perfil actualizado correctamente"),
                    bgcolor=ft.Colors.GREEN_700,
                    duration=3000,
                )
                page.snack_bar.open = True
                page.navigate("/carrera")
        except Exception as e:
            error_text.value = f"Error al actualizar: {str(e)}"
            page.update()

    def volver(e):
        page.navigate("/carrera")

    content = ft.Column(
        controls=[
            ft.Row(
                controls=[ft.TextButton("← Volver", on_click=volver)],
                alignment=ft.MainAxisAlignment.START,
            ),
            spacer(5),
            ft.Text("Editar perfil", size=32, style=BOLD_WHITE),
            spacer(15),
            name_field,
            spacer(5),
            position_field,
            spacer(5),
            level_field,
            spacer(5),
            age_field,
            spacer(5),
            height_field,
            spacer(5),
            weight_field,
            spacer(5),
            ft.Divider(height=1, color=ft.Colors.GREY_400),
            spacer(5),
            ft.Text("Meta", style=BOLD_WHITE, size=18),
            meta_field,
            spacer(10),
            error_text,
            spacer(10),
            ft.Button(
                content=ft.Text("Guardar", size=14),
                on_click=guardar,
                bgcolor=ACCENT,
                color=ft.Colors.WHITE,
                width=200,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )

    return create_base_view(
        "/editar-perfil",
        "Editar perfil",
        content,
        scroll=False,
    )