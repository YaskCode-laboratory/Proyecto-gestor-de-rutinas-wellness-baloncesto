import flet as ft
from api import get_me
from state import auth
from views import (
    CrearEntrenamientoV,
    CrearPlanV,
    CrearPerfilV,
    CrearAuthV,
    CrearEjecutarRutinaV,
    CrearEjerciciosV,
    CrearRutinaManualV,
    CrearEstadisticasV,
    CrearGenerarAutomaticaV,
    CrearEditarPerfilV,  
)

MAIN_ROUTES = [
    ("/inicio", "Inicio", ft.Icons.HOME, CrearEntrenamientoV),
    ("/rutinas", "Rutinas", ft.Icons.FORMAT_LIST_BULLETED, CrearPlanV),
    ("/ejercicios", "Ejercicios", ft.Icons.FITNESS_CENTER, CrearEjerciciosV),
    ("/estadisticas", "Progreso", ft.Icons.TRENDING_UP, CrearEstadisticasV),
    ("/carrera", "Carrera", ft.Icons.ASSESSMENT, CrearPerfilV),
]

AUTH_ROUTES = {
    "/login": lambda p: CrearAuthV(p, is_login=True),
    "/register": lambda p: CrearAuthV(p, is_login=False),
}

async def main(page: ft.Page):
    page.title = "Rutinas Wellness Basquet"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.BLACK
    page.padding = 0
    page.width = 400
    page.height = 800

    await auth.load(page)
    if auth.token:
        try:
            auth.user = get_me(auth.token)
            start_route = "/inicio"
        except Exception:
            auth.token = None
            start_route = "/login"
    else:
        start_route = "/login"

    nav_bar = ft.NavigationBar(
        bgcolor=ft.Colors.BLACK,
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(icon=icon, label=label)
            for _, label, icon, _ in MAIN_ROUTES
        ],
    )

    def route_change(_):
        page.views.clear()
        route = "/inicio" if page.route == "/" else page.route

        if route in AUTH_ROUTES:
            page.views.append(AUTH_ROUTES[route](page))
            page.navigation_bar = None
            page.update()
            return

        if route.startswith("/ejecutar/"):
            routine_id = route.split("/")[-1]
            page.views.append(CrearEjecutarRutinaV(page, routine_id))
            page.navigation_bar = None
            page.update()
            return

        if route == "/crear-manual":
            page.views.append(CrearRutinaManualV(page))
            page.navigation_bar = None
            page.update()
            return

        if route == "/generar-automatica":
            page.views.append(CrearGenerarAutomaticaV(page))
            page.navigation_bar = None
            page.update()
            return

        if route == "/editar-perfil":
            page.views.append(CrearEditarPerfilV(page))
            page.navigation_bar = None
            page.update()
            return

        found = False
        for i, (r, _, _, factory) in enumerate(MAIN_ROUTES):
            if route == r:
                page.views.append(factory(page))
                nav_bar.selected_index = i
                found = True
                break

        if not found:
            page.navigate("/inicio")
            return

        page.navigation_bar = nav_bar
        page.update()

    def bottom_nav_change(e: ft.Event[ft.NavigationBar]):
        page.navigate(MAIN_ROUTES[e.control.selected_index][0])

    nav_bar.on_change = bottom_nav_change
    page.on_route_change = route_change
    page.navigate(start_route)

if __name__ == "__main__":
    ft.run(main)