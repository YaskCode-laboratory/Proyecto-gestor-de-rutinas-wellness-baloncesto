import flet as ft
import random
import datetime
from state import auth
from api import get_resumen
from ._shared import ACCENT, BOLD_WHITE, GREY, spacer, create_base_view


def CrearEntrenamientoV(page: ft.Page) -> ft.View:
    resumen_data = {
        "total_rutinas": 0,
        "total_ejecuciones": 0,
        "esfuerzo_promedio": 0,
        "categorias_mas_practicadas": []
    }
    error_text = ft.Text("", color=ft.Colors.RED, size=14)
    contenido_principal = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)

    CONSEJOS = [
        "El éxito es la suma de pequeños esfuerzos repetidos día tras día.",
        "La práctica no hace la perfección, la práctica perfecta hace la perfección.",
        "Cada tiro cuenta, cada entrenamiento te acerca a tu meta.",
        "El baloncesto es un ritmo: encuéntralo y domínalo.",
        "La constancia vence al talento cuando el talento no es constante.",
        "No cuentes los días, haz que los días cuenten.",
        "El mejor jugador no es el que nunca falla, sino el que nunca se rinde.",
        "Entrena como si fueras el peor, juega como si fueras el mejor.",
        "La disciplina es el puente entre tus metas y tus logros.",
        "Cada gota de sudor en el entrenamiento es una gota de éxito en el partido.",
    ]

    nombre = "Jugador"
    if auth.user and auth.user.get("name"):
        nombre = auth.user.get("name").split()[0]

    hora = datetime.datetime.now().hour
    if hora < 12:
        saludo_texto = f"Buenos días, {nombre}"
    elif hora < 19:
        saludo_texto = f"Buenas tardes, {nombre}"
    else:
        saludo_texto = f"Buenas noches, {nombre}"

    frase_completa = f"{saludo_texto}, ¿listo para entrenar hoy?"

    def cargar_datos():
        try:
            if auth.token:
                data = get_resumen(auth.token)
                resumen_data.update(data)
                actualizar_vista()
        except Exception as e:
            error_text.value = f"Error al cargar datos: {str(e)}"
            page.update()

    def actualizar_vista():
        contenido_principal.controls.clear()

        contenido_principal.controls.append(
            ft.Text("Tu resumen", size=18, style=BOLD_WHITE)
        )
        contenido_principal.controls.append(spacer(5))
        contenido_principal.controls.append(
            ft.Row(
                controls=[
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Rutinas", color=ft.Colors.WHITE, size=13, text_align=ft.TextAlign.CENTER),
                                    ft.Text(str(resumen_data.get("total_rutinas", 0)), size=22, style=BOLD_WHITE, text_align=ft.TextAlign.CENTER),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=2,
                            ),
                            padding=15,
                            width=100,
                        ),
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Ejecuciones", color=ft.Colors.WHITE, size=13, text_align=ft.TextAlign.CENTER),
                                    ft.Text(str(resumen_data.get("total_ejecuciones", 0)), size=22, style=BOLD_WHITE, text_align=ft.TextAlign.CENTER),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=2,
                            ),
                            padding=15,
                            width=100,
                        ),
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Esfuerzo", color=ft.Colors.WHITE, size=13, text_align=ft.TextAlign.CENTER),
                                    ft.Text(f"{resumen_data.get('esfuerzo_promedio', 0):.1f}/5", size=22, style=BOLD_WHITE, text_align=ft.TextAlign.CENTER),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=2,
                            ),
                            padding=15,
                            width=100,
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                wrap=True,
            )
        )

        contenido_principal.controls.append(spacer(15))

        categorias = resumen_data.get("categorias_mas_practicadas", [])
        if categorias:
            favorita = categorias[0]
            contenido_principal.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER, size=24),
                            ft.Column(
                                controls=[
                                    ft.Text("Categoría favorita", color=ft.Colors.WHITE, size=13),
                                    ft.Text(f"{favorita['nombre']} ({favorita['total']} veces)", size=16, style=BOLD_WHITE),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    bgcolor="#2C2C2E",
                    border_radius=12,
                    padding=15,
                )
            )
            contenido_principal.controls.append(spacer(15))

        consejo = random.choice(CONSEJOS)
        contenido_principal.controls.append(
            ft.Text("Consejo del día", size=18, style=BOLD_WHITE)
        )
        contenido_principal.controls.append(spacer(5))
        contenido_principal.controls.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, color=ACCENT, size=24),
                        ft.Text(
                            consejo,
                            size=15,
                            color=ft.Colors.WHITE,
                            italic=True,
                            expand=True,
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                bgcolor="#2C2C2E",
                border_radius=12,
                padding=15,
            )
        )

        page.update()

    cargar_datos()

    return create_base_view(
        "/inicio",
        "Inicio",
        [
            ft.Text(frase_completa, size=24, style=BOLD_WHITE),
            spacer(15),
            contenido_principal,
            spacer(5),
            error_text,
        ],
        scroll=False,
    )