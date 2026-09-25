import flet as ft

ACCENT = ft.Colors.ORANGE
BG_DARK = "#1C1C1E"
BG_CARD = "#2C2C2E"

BOLD_WHITE = ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
GREY = ft.TextStyle(color=ft.Colors.GREY)

VIEW_PAD = 20

def spacer(height):
    return ft.Divider(height=height, color=ft.Colors.TRANSPARENT)

def create_base_view(
    route,
    title,
    controls,
    *,
    scroll=False,
    padding=VIEW_PAD,
    bgcolor: ft.Colors | str = ft.Colors.BLACK,
):
    return ft.View(
        route=route,
        appbar=ft.AppBar(title=ft.Text(title), bgcolor=ft.Colors.BLACK),
        bgcolor=bgcolor,
        padding=padding,
        scroll=ft.ScrollMode.AUTO if scroll else None,
        controls=controls,
    )