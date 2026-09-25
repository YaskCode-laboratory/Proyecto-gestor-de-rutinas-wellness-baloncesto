import flet as ft
from views._shared import ACCENT


def Button(
    text: str,
    icon: ft.IconData,
    variant: str = "primary",
    on_click=None,
) -> ft.Container:
    is_primary = variant == "primary"
    return ft.Container(
        bgcolor=ACCENT if is_primary else None,
        border=ft.Border.all(1, ACCENT) if not is_primary else None,
        border_radius=12,
        padding=ft.Padding.symmetric(vertical=14, horizontal=16),
        ink=True,
        on_click=on_click,
        content=ft.Row(
            controls=[
                ft.Icon(icon, color=ft.Colors.WHITE if is_primary else ACCENT, size=20),
                ft.Text(
                    text,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                    size=16,
                ),
            ],
            spacing=12,
        ),
    )


def AIPromptInput(on_submit=None) -> ft.Container:
    field = ft.TextField(
        hint_text="Ask the AI coach…",
        hint_style=ft.TextStyle(color=ft.Colors.GREY),
        text_style=ft.TextStyle(color=ft.Colors.WHITE),
        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
        border_radius=24,
        border=ft.InputBorder.NONE,
        filled=True,
        content_padding=ft.Padding.symmetric(horizontal=16, vertical=14),
        on_submit=on_submit,
        expand=True,
    )

    return ft.Container(
        border_radius=24,
        padding=2,
        content=ft.Row(
            controls=[
                field,
                ft.IconButton(
                    icon=ft.Icons.SEND,
                    icon_color=ACCENT,
                    on_click=on_submit,
                ),
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )
