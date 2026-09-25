import flet as ft
from api import login as api_login
from api import register as api_register
from state import auth
from ._shared import ACCENT, BOLD_WHITE, spacer

def CrearAuthV(page: ft.Page, is_login: bool = True) -> ft.View:
    email_field = ft.TextField(
        label="Email",
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
    )
    password_field = ft.TextField(
        label="Contraseña",
        password=True,
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
    )
    
    name_field = ft.TextField(
        label="Nombre",
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
    )
    meta_field = ft.TextField(
        label="Meta (ej. 'Mejorar tiro de 3 puntos')",
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
    )
    age_field = ft.TextField(
        label="Edad",
        expand=True,
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
    )
    height_field = ft.TextField(
        label="Altura (cm)",
        expand=True,
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
    )
    weight_field = ft.TextField(
        label="Peso (kg)",
        expand=True,
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
    )
    position_field = ft.Dropdown(
        label="Posición",
        options=[
            ft.dropdown.Option("Base"),
            ft.dropdown.Option("Alero"),
            ft.dropdown.Option("Pívot"),
            ft.dropdown.Option("Escolta"),
            ft.dropdown.Option("Ala-Pívot"),
        ],
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
    )
    level_field = ft.Dropdown(
        label="Nivel de juego",
        options=[
            ft.dropdown.Option("Principiante"),
            ft.dropdown.Option("Intermedio"),
            ft.dropdown.Option("Avanzado"),
        ],
        expand=True,
        filled=True,
        bgcolor="#2C2C2E",
        border_radius=8,
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
    )

    error_text = ft.Text(color=ft.Colors.RED, size=14)

    async def handle_submit(_):
        error_text.value = ""
        page.update()
        try:
            if is_login:
                data = api_login(email_field.value, password_field.value)
            else:
                data = api_register(
                    email=email_field.value,
                    password=password_field.value,
                    name=name_field.value,
                    meta_objetivo=meta_field.value,
                    age=int(age_field.value) if age_field.value else None,
                    height=float(height_field.value) if height_field.value else None,
                    weight=float(weight_field.value) if weight_field.value else None,
                    position=position_field.value,
                    level=level_field.value,
                )
            auth.token = data["access_token"]
            auth.user = data["user"]
            await auth.save(page)
            page.navigate("/training")
        except Exception as e:
            error_text.value = "Credenciales inválidas" if is_login else f"Error al registrarse: {str(e)}"
            page.update()

    controls = [
        ft.Text("Wellness" if is_login else "Crear cuenta", size=36, style=BOLD_WHITE),
        spacer(40),
    ]

    if not is_login:
        controls.extend([
            name_field,
            spacer(12),
            meta_field,
            spacer(12),
            age_field,
            spacer(12),
            height_field,
            spacer(12),
            weight_field,
            spacer(12),
            position_field,
            spacer(12),
            level_field,
            spacer(12),
        ])

    controls.extend([
        email_field,
        spacer(12),
        password_field,
        spacer(12),
        error_text,
        ft.Button(
            content=ft.Text("Iniciar sesión" if is_login else "Registrarse"),
            on_click=handle_submit,
            width=200,
            bgcolor=ACCENT,
            color=ft.Colors.WHITE,
        ),
        spacer(30),
        ft.TextButton(
            "¿No tienes cuenta? Regístrate" if is_login else "¿Ya tienes cuenta? Inicia sesión",
            on_click=lambda _: page.navigate("/register" if is_login else "/login"),
        ),
    ])

    return ft.View(
        route="/login" if is_login else "/register",
        bgcolor=ft.Colors.BLACK,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        controls=controls,
    )