"""Explorador de lugares · Flet 1.0.5. Sin base de datos ni clave API."""
from datetime import datetime
from urllib.parse import urlencode

import flet as ft

PRIMARY = "#1957B8"
INK = "#14243C"
MUTED = "#536479"
TEAL = "#087D70"
MODOS = {
    "walking": "A pie",
    "driving": "En carro",
    "bicycling": "En bicicleta",
    "transit": "Transporte público",
}
MAX_HISTORIAL = 10


def maps_url(accion, **datos):
    """Construye solo URLs oficiales; nunca acepta un dominio del usuario."""
    if accion not in {"search", "dir"}:
        raise ValueError("Acción no permitida.")
    url = f"https://www.google.com/maps/{accion}/?{urlencode({'api': '1', **datos})}"
    if len(url) > 2048:
        raise ValueError("La consulta es demasiado larga. Usa una dirección más corta.")
    return url


def main(page: ft.Page):
    page.title = "Explora · Lugares y rutas"
    page.bgcolor = "#F3F6FA"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=PRIMARY, use_material3=True)
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    # Todo el estado pertenece a esta sesión. No imprime direcciones en consola.
    historial = []
    generados = 0
    total = ft.Text("0 enlaces generados", color="#FFFFFF", size=16)
    guardados = ft.Text("0 de 10 enlaces guardados", color=MUTED, size=14)
    lista = ft.Column(spacing=10)
    estado_lugar = ft.Text("Escribe un lugar y genera su enlace.", color=MUTED, size=14)
    estado_ruta = ft.Text("Elige cómo viajar y genera la ruta.", color=MUTED, size=14)

    def campo(label, value="", icon=None):
        return ft.TextField(
            label=label, value=value, prefix_icon=icon,
            text_size=16, border_radius=10, border_color="#8997A9",
            focused_border_color=PRIMARY, filled=True, fill_color="#FAFBFD",
            content_padding=16, width=float("inf"),
        )

    lugar = campo("Lugar, dirección o coordenadas",
                  "Museo del Oro, Bogotá, Colombia", ft.Icons.LOCATION_ON_OUTLINED)
    origen = campo("Origen", "Museo del Oro, Bogotá", ft.Icons.TRIP_ORIGIN)
    destino = campo("Destino", "Museo Nacional de Colombia, Bogotá",
                    ft.Icons.LOCATION_ON_OUTLINED)
    modo = ft.Dropdown(
        label="Modo de viaje", value="walking",
        options=[ft.DropdownOption(key=k, text=v) for k, v in MODOS.items()],
        text_size=16, content_padding=16, width=float("inf"),
    )
    boton_style = ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=10),
        text_style=ft.TextStyle(size=15, weight=ft.FontWeight.W_600),
        padding=16,
    )
    abrir_lugar = ft.OutlinedButton(
        content="Abrir lugar en Maps", icon=ft.Icons.OPEN_IN_NEW,
        disabled=True, height=48, width=float("inf"), style=boton_style,
    )
    abrir_ruta = ft.OutlinedButton(
        content="Abrir ruta en Maps", icon=ft.Icons.OPEN_IN_NEW,
        disabled=True, height=48, width=float("inf"), style=boton_style,
    )
    vaciar = ft.TextButton(content="Vaciar historial", disabled=True, height=44)

    def invalidar_lugar(e=None):
        abrir_lugar.url = None
        abrir_lugar.disabled = True
        lugar.error = None  # Flet 1.0.5: error, no error_text.
        estado_lugar.value = "Genera el enlace para el lugar actual."
        estado_lugar.color = MUTED
        page.update()

    def invalidar_ruta(e=None):
        abrir_ruta.url = None
        abrir_ruta.disabled = True
        origen.error = destino.error = None
        estado_ruta.value = "Genera otra vez la ruta con estos datos."
        estado_ruta.color = MUTED
        page.update()

    def validar(control, mensaje):
        valor = (control.value or "").strip()
        control.error = mensaje if not valor else (
            "Usa como máximo 300 caracteres." if len(valor) > 300 else None
        )
        return valor if control.error is None else None

    def restaurar(item):
        if item["tipo"] == "Lugar":
            lugar.value = item["lugar"]
            invalidar_lugar()
            estado_lugar.value = "Lugar recuperado. Pulsa Generar búsqueda."
        else:
            origen.value, destino.value = item["origen"], item["destino"]
            modo.value = item["modo"]
            invalidar_ruta()
            estado_ruta.value = "Ruta recuperada. Pulsa Generar ruta."
        page.update()

    def render_historial():
        lista.controls.clear()
        guardados.value = f"{len(historial)} de {MAX_HISTORIAL} enlaces guardados"
        vaciar.disabled = not historial
        if not historial:
            lista.controls.append(ft.Container(
                padding=24, bgcolor="#F3F6FA", border_radius=10,
                content=ft.Column([
                    ft.Icon(ft.Icons.HISTORY, color=MUTED, size=28),
                    ft.Text("Tu próxima exploración empieza aquí", color=INK,
                            size=16, weight=ft.FontWeight.W_600),
                    ft.Text("Genera una búsqueda o una ruta para verla en este espacio.",
                            color=MUTED, size=14),
                ], spacing=8),
            ))
            return
        for item in historial:
            etiqueta = item["tipo"]
            if item["tipo"] == "Ruta":
                etiqueta += f" · {MODOS[item['modo']]}"
            lista.controls.append(ft.Container(
                padding=16, bgcolor="#F7F9FC", border_radius=10,
                border=ft.Border.all(1, "#E0E7F0"),
                content=ft.Column([
                    ft.Text(f"{etiqueta}  ·  {item['hora']}", size=14, color=TEAL,
                            weight=ft.FontWeight.W_600),
                    ft.Text(item["titulo"], size=16, color=INK),
                    ft.Row([
                        ft.TextButton(content="Reutilizar", height=44,
                                      on_click=lambda e, x=item: restaurar(x)),
                        ft.TextButton(content="Abrir en Maps", icon=ft.Icons.OPEN_IN_NEW,
                                      height=44, url=ft.Url(item["url"], target="_blank")),
                    ], wrap=True, spacing=8),
                ], spacing=6),
            ))

    def registrar(item):
        nonlocal generados
        generados += 1
        total.value = f"{generados} enlace{'s' if generados != 1 else ''} generado{'s' if generados != 1 else ''}"
        item["hora"] = datetime.now().strftime("%H:%M")  # Hora del servidor.
        # Una URL repetida pasa al inicio, sin duplicar filas.
        historial[:] = [x for x in historial if x["url"] != item["url"]]
        historial.insert(0, item)
        del historial[MAX_HISTORIAL:]
        render_historial()

    def generar_lugar(e=None):
        abrir_lugar.url = None
        abrir_lugar.disabled = True
        texto = validar(lugar, "Ingresa un lugar para continuar.")
        estado_lugar.value = "Revisa el campo señalado." if texto is None else ""
        estado_lugar.color = "#B3261E" if texto is None else TEAL
        if texto is not None:
            try:
                url = maps_url("search", query=texto)
                abrir_lugar.url = ft.Url(url, target="_blank")
                abrir_lugar.disabled = False
                estado_lugar.value = "Enlace listo. Ábrelo cuando quieras."
                registrar({"tipo": "Lugar", "titulo": texto, "lugar": texto, "url": url})
            except ValueError as exc:
                lugar.error = str(exc)
                estado_lugar.value = "Acorta la consulta e inténtalo de nuevo."
                estado_lugar.color = "#B3261E"
        page.update()

    def generar_ruta(e=None):
        abrir_ruta.url = None
        abrir_ruta.disabled = True
        inicio = validar(origen, "Ingresa el punto de partida.")
        fin = validar(destino, "Ingresa el destino.")
        estado_ruta.color = "#B3261E"
        estado_ruta.value = "Revisa los campos señalados."
        if inicio is not None and fin is not None:
            if " ".join(inicio.split()).casefold() == " ".join(fin.split()).casefold():
                destino.error = "El destino debe ser diferente del origen."
            elif modo.value not in MODOS:
                estado_ruta.value = "Selecciona un modo de viaje válido."
            else:
                try:
                    url = maps_url("dir", origin=inicio, destination=fin,
                                   travelmode=modo.value)
                    abrir_ruta.url = ft.Url(url, target="_blank")
                    abrir_ruta.disabled = False
                    estado_ruta.color = TEAL
                    estado_ruta.value = f"Ruta lista · {MODOS[modo.value]}."
                    registrar({"tipo": "Ruta", "titulo": f"{inicio} → {fin}",
                               "origen": inicio, "destino": fin,
                               "modo": modo.value, "url": url})
                except ValueError as exc:
                    estado_ruta.value = str(exc)
        page.update()

    def intercambiar(e):
        origen.value, destino.value = destino.value, origen.value
        invalidar_ruta()

    def ejemplo(texto):
        lugar.value = texto
        invalidar_lugar()

    def limpiar_lugar(e):
        lugar.value = ""
        invalidar_lugar()

    def confirmar_vaciado(e):
        def cerrar(e):
            page.pop_dialog()

        def borrar(e):
            historial.clear()
            render_historial()
            page.pop_dialog()
            page.update()

        page.show_dialog(ft.AlertDialog(
            modal=True, title=ft.Text("¿Vaciar el historial?"),
            content=ft.Text("Se borrarán los enlaces de esta sesión, no el contador total."),
            actions=[ft.TextButton(content="Cancelar", on_click=cerrar),
                     ft.TextButton(content="Vaciar", on_click=borrar)],
        ))

    lugar.on_change = invalidar_lugar
    lugar.on_submit = generar_lugar
    origen.on_change = destino.on_change = invalidar_ruta
    destino.on_submit = generar_ruta
    modo.on_select = invalidar_ruta
    vaciar.on_click = confirmar_vaciado

    def titulo_card(numero, titulo, detalle, icono):
        return ft.Column([
            ft.Row([
                ft.Container(content=ft.Icon(icono, color=PRIMARY, size=24),
                             bgcolor="#EAF1FC", padding=12, border_radius=10),
                ft.Text(f"{numero} / {titulo}", size=22, color=INK,
                        weight=ft.FontWeight.BOLD, expand=True),
            ], spacing=12),
            ft.Text(detalle, size=15, color=MUTED),
        ], spacing=12)

    def tarjeta(contenido, col=12):
        return ft.Container(
            content=ft.Column(contenido, spacing=16,
                              horizontal_alignment=ft.CrossAxisAlignment.STRETCH), padding=24,
            bgcolor="#FFFFFF", border_radius=12,
            border=ft.Border.all(1, "#DFE6EF"), col=col,
        )

    buscar = tarjeta([
        titulo_card("01", "Descubre un lugar", "Una dirección, un museo o unas coordenadas.",
                    ft.Icons.EXPLORE_OUTLINED),
        lugar,
        ft.Row([
            ft.TextButton(content="Museo del Oro", height=44,
                          on_click=lambda e: ejemplo("Museo del Oro, Bogotá, Colombia")),
            ft.TextButton(content="Monserrate", height=44,
                          on_click=lambda e: ejemplo("Cerro de Monserrate, Bogotá, Colombia")),
            ft.TextButton(content="Limpiar", height=44, on_click=limpiar_lugar),
        ], wrap=True, spacing=4),
        ft.Button(content="Generar búsqueda", icon=ft.Icons.SEARCH,
                  on_click=generar_lugar, bgcolor=PRIMARY, color="#FFFFFF",
                  height=48, width=float("inf"), style=boton_style),
        abrir_lugar, estado_lugar,
        ft.Container(padding=16, bgcolor="#EAF6F2", border_radius=10,
                     content=ft.Text("Consejo: incluye la ciudad y el país para precisar la búsqueda.",
                                     color="#136555", size=14)),
    ], col={"xs": 12, "md": 6})
    rutas = tarjeta([
        titulo_card("02", "Traza tu ruta", "Prepara el recorrido antes de salir.",
                    ft.Icons.ALT_ROUTE),
        origen, destino,
        ft.TextButton(content="Intercambiar origen y destino", icon=ft.Icons.SWAP_VERT,
                      height=44, on_click=intercambiar),
        modo,
        ft.Button(content="Generar ruta", icon=ft.Icons.DIRECTIONS,
                  on_click=generar_ruta, bgcolor=PRIMARY, color="#FFFFFF",
                  height=48, width=float("inf"), style=boton_style),
        abrir_ruta, estado_ruta,
    ], col={"xs": 12, "md": 6})
    header = ft.Container(
        padding=28, bgcolor="#142D50", border_radius=12,
        content=ft.Column([
            ft.Text("PROYECTO 03  /  PYTHON + FLET", size=14, color="#BCD4F3",
                    weight=ft.FontWeight.W_600),
            ft.Text("Explora tu próximo destino.", size=34,
                    weight=ft.FontWeight.BOLD, color="#FFFFFF"),
            ft.Text("Encuentra lugares. Prepara rutas. Sigue explorando.",
                    size=17, color="#D5E3F5"),
            ft.Divider(color="#3C5575", height=16),
            ft.Row([ft.Icon(ft.Icons.LINK, color="#FFFFFF", size=20), total],
                   wrap=True, spacing=10),
        ], spacing=12),
    )
    render_historial()
    panel_historial = tarjeta([
        ft.Row([
            ft.Text("Exploraciones recientes", size=22, weight=ft.FontWeight.BOLD,
                    color=INK), vaciar,
        ], wrap=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        guardados, lista,
        ft.Text("Solo en esta sesión · Máximo 10 enlaces únicos · Hora del servidor. Derechos Reservados : Jannez Urrego 2026",
                size=14, color=MUTED),
    ])
    raiz = ft.Container(
            width=min(page.width or 1120, 1120), padding=ft.Padding.symmetric(horizontal=16, vertical=24),
            content=ft.Column([
                header,
                ft.ResponsiveRow([buscar, rutas], spacing=20, run_spacing=20),
                panel_historial,
                ft.Container(padding=16, content=ft.Text(
                    "Sin clave API · Los mapas se abren en Google Maps. Usa lugares públicos: "
                    "al abrir un enlace se envía la consulta a Google. No se valida la existencia "
                    "del lugar ni se calculan tiempos aquí; la disponibilidad de rutas depende de Maps.",
                    size=14, color=MUTED)),
            ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
        )

    def redimensionar(e):
        raiz.width = min(page.width or 1120, 1120)
        page.update()

    page.on_resize = redimensionar
    page.add(ft.SafeArea(content=ft.Row([raiz], alignment=ft.MainAxisAlignment.CENTER)))


if __name__ == "__main__":
    ft.run(main)
