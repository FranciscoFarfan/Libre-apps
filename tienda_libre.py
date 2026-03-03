import flet as ft
import json
import subprocess
import sys
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
#  Rutas
# ─────────────────────────────────────────────────────────────────────────────

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):      # PyInstaller --onefile
        return Path(sys._MEIPASS)          # carpeta temporal donde se extraen los archivos
    return Path(__file__).parent

def get_fotos_dir() -> Path:
    return get_base_dir() / "fotos"

def get_json_path() -> Path:
    return get_base_dir() / "programas.json"


# ─────────────────────────────────────────────────────────────────────────────
#  Utilidades de fotos
# ─────────────────────────────────────────────────────────────────────────────

EXTS = (".jpg", ".jpeg", ".png", ".webp")

def obtener_fotos(prog_id: str) -> list[Path]:
    """
    Busca archivos {id}_1.jpg, {id}_2.jpg, ... en la carpeta fotos/.
    Acepta jpg, jpeg, png, webp. Sin límite de cantidad.
    """
    carpeta = get_fotos_dir()
    if not carpeta.exists():
        return []
    fotos = []
    i = 1
    while True:
        encontrada = None
        for ext in EXTS:
            candidato = carpeta / f"{prog_id}_{i}{ext}"
            if candidato.exists():
                encontrada = candidato
                break
        if encontrada:
            fotos.append(encontrada)
            i += 1
        else:
            break
    return fotos


# ─────────────────────────────────────────────────────────────────────────────
#  Paleta de colores
# ─────────────────────────────────────────────────────────────────────────────

BG_DARK  = "#0D0F1A"
BG_CARD  = "#13162A"
BG_CARD2 = "#1A1E33"
ACCENT   = "#6C63FF"
ACCENT2  = "#A78BFA"
TEXT_PRI = "#F0F2FF"
TEXT_SEC = "#9BA3BF"
SUCCESS  = "#22C55E"
WARNING  = "#F59E0B"
BORDER   = "#252840"


# ─────────────────────────────────────────────────────────────────────────────
#  Datos
# ─────────────────────────────────────────────────────────────────────────────

def cargar_programas() -> list[dict]:
    p = get_json_path()
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────────────────
#  Abrir URL — UrlLauncher async (correcto en Flet 0.81.0)
# ─────────────────────────────────────────────────────────────────────────────

def abrir_url(url: str, page: ft.Page):
    async def _abrir():
        await ft.UrlLauncher().launch_url(url)
    page.run_task(_abrir)


# ─────────────────────────────────────────────────────────────────────────────
#  Componentes reutilizables
# ─────────────────────────────────────────────────────────────────────────────

def badge(texto: str, color: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(texto, size=11, color=color, weight=ft.FontWeight.W_600),
        bgcolor=f"{color}22",
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=10, vertical=3),
    )

def chip_tag(texto: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(f"#{texto}", size=11, color=TEXT_SEC),
        bgcolor=BG_DARK,
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=8, vertical=2),
        border=ft.border.all(1, BORDER),
    )

def fila_info(etiqueta: str, valor) -> ft.Row:
    val_ctrl = (
        ft.Text(valor, size=13, color=TEXT_PRI, selectable=True, expand=True)
        if isinstance(valor, str)
        else valor
    )
    return ft.Row(controls=[ft.Text(etiqueta, size=13, color=TEXT_SEC, width=150), val_ctrl])


# ─────────────────────────────────────────────────────────────────────────────
#  Carrusel de fotos
# ─────────────────────────────────────────────────────────────────────────────

def crear_carrusel(fotos: list[Path], color: str) -> ft.Control | None:
    """
    Devuelve un widget de carrusel o None si no hay fotos.
    Las fotos son capturas de pantalla FullHD (16:9), se muestran
    a ancho completo con altura fija de 420px.
    """
    if not fotos:
        return None

    total = len(fotos)
    indice = {"actual": 0}

    # Imagen principal
    img = ft.Image(
        src=str(fotos[0]),
        fit=ft.BoxFit.CONTAIN,
        width=None,
        expand=True,
        border_radius=10,
    )

    # Indicadores de puntos
    def punto(i: int) -> ft.Container:
        activo = i == indice["actual"]
        return ft.Container(
            width=8 if not activo else 22,
            height=8,
            bgcolor=color if activo else f"{color}55",
            border_radius=4,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )

    puntos_row = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=6,
        controls=[punto(i) for i in range(total)],
    )

    # Contador de fotos
    contador = ft.Text(f"1 / {total}", size=12, color=TEXT_SEC)

    def actualizar_imagen():
        img.src = str(fotos[indice["actual"]])
        puntos_row.controls = [punto(i) for i in range(total)]
        contador.value = f"{indice['actual'] + 1} / {total}"
        img.update()
        puntos_row.update()
        contador.update()

    def anterior(e):
        indice["actual"] = (indice["actual"] - 1) % total
        actualizar_imagen()

    def siguiente(e):
        indice["actual"] = (indice["actual"] + 1) % total
        actualizar_imagen()

    btn_prev = ft.IconButton(
        icon=ft.Icons.CHEVRON_LEFT_ROUNDED,
        icon_color=ft.Colors.WHITE,
        icon_size=28,
        on_click=anterior,
        style=ft.ButtonStyle(
            bgcolor="#00000055",
            shape=ft.CircleBorder(),
        ),
        visible=total > 1,
    )
    btn_next = ft.IconButton(
        icon=ft.Icons.CHEVRON_RIGHT_ROUNDED,
        icon_color=ft.Colors.WHITE,
        icon_size=28,
        on_click=siguiente,
        style=ft.ButtonStyle(
            bgcolor="#00000055",
            shape=ft.CircleBorder(),
        ),
        visible=total > 1,
    )

    return ft.Container(
        border_radius=12,
        border=ft.border.all(1, BORDER),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        bgcolor=BG_DARK,
        content=ft.Column(
            spacing=0,
            controls=[
                # Imagen con botones superpuestos
                ft.Stack(
                    height=420,
                    controls=[
                        # Imagen de fondo
                        ft.Container(expand=True, content=img),
                        # Botón anterior (izquierda)
                        ft.Container(
                            left=10,
                            top=0,
                            bottom=0,
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[btn_prev],
                            ),
                        ),
                        # Botón siguiente (derecha)
                        ft.Container(
                            right=10,
                            top=0,
                            bottom=0,
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[btn_next],
                            ),
                        ),
                    ],
                ),
                # Barra inferior con puntos y contador
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            puntos_row,
                            contador,
                        ],
                    ),
                ),
            ],
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Card de la lista principal
# ─────────────────────────────────────────────────────────────────────────────

def crear_card(prog: dict, on_ver, page: ft.Page) -> ft.Container:
    color = prog.get("color", ACCENT)
    link_descarga = prog.get("link_descarga", "")

    card = ft.Container(
        content=ft.Column(
            spacing=0,
            controls=[
                ft.Container(
                    height=4,
                    bgcolor=color,
                    border_radius=ft.BorderRadius(top_left=12, top_right=12, bottom_left=0, bottom_right=0),
                ),
                ft.Container(
                    padding=ft.padding.all(18),
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            # Encabezado
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=12,
                                        controls=[
                                            ft.Container(
                                                content=ft.Text(prog["icono"], size=32),
                                                bgcolor=f"{color}22",
                                                border_radius=12,
                                                padding=ft.padding.all(10),
                                            ),
                                            ft.Column(
                                                spacing=2,
                                                controls=[
                                                    ft.Text(prog["nombre"], size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRI),
                                                    ft.Text(f"v{prog['version']}", size=12, color=TEXT_SEC),
                                                ],
                                            ),
                                        ],
                                    ),
                                    badge(prog["categoria"], color),
                                ],
                            ),
                            # Descripción corta
                            ft.Text(
                                prog["descripcion_corta"],
                                size=13,
                                color=TEXT_SEC,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            # Tags
                            ft.Row(
                                wrap=True,
                                spacing=6,
                                controls=[chip_tag(t) for t in prog.get("tags", [])[:4]],
                            ),
                            ft.Divider(height=1, color=BORDER),
                            # Footer
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(
                                        f"📦 {prog.get('tamano_mb', '?')} MB",
                                        size=12,
                                        color=TEXT_SEC,
                                    ),
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.TextButton(
                                                "Ver más",
                                                on_click=lambda e, p=prog: on_ver(p),
                                                style=ft.ButtonStyle(color=ACCENT2),
                                            ),
                                            ft.ElevatedButton(
                                                "Descargar",
                                                icon=ft.Icons.DOWNLOAD_ROUNDED,
                                                on_click=lambda e, u=link_descarga: abrir_url(u, page),
                                                disabled=not link_descarga,
                                                style=ft.ButtonStyle(
                                                    color=ft.Colors.WHITE,
                                                    bgcolor=color if link_descarga else TEXT_SEC,
                                                    shape=ft.RoundedRectangleBorder(radius=8),
                                                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                                ),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        ),
        bgcolor=BG_CARD,
        border_radius=12,
        border=ft.border.all(1, BORDER),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )

    def on_hover(e):
        card.border = ft.border.all(1, color) if e.data == "true" else ft.border.all(1, BORDER)
        card.update()

    card.on_hover = on_hover
    return card


# ─────────────────────────────────────────────────────────────────────────────
#  Vista de detalle
# ─────────────────────────────────────────────────────────────────────────────

def crear_detalle(prog: dict, on_back, page: ft.Page) -> ft.Control:
    color         = prog.get("color", ACCENT)
    link_proyecto = prog.get("link_proyecto", prog.get("pagina_web", ""))
    link_descarga = prog.get("link_descarga", "")
    reemplaza_a   = prog.get("reemplaza_a", "")

    # Fotos del programa
    fotos     = obtener_fotos(prog["id"])
    carrusel  = crear_carrusel(fotos, color)

    caract_items = [
        ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, color=color, size=18),
                ft.Text(c, size=14, color=TEXT_PRI, expand=True),
            ],
        )
        for c in prog.get("caracteristicas", [])
    ]

    # Sección "Reemplaza a"
    seccion_reemplaza = []
    if reemplaza_a:
        seccion_reemplaza.append(
            ft.Container(
                padding=ft.padding.all(20),
                bgcolor=f"{color}14",
                border_radius=12,
                border=ft.border.all(1, f"{color}44"),
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Icon(ft.Icons.SWAP_HORIZ_ROUNDED, color=color, size=22),
                                ft.Text("Reemplaza a:", size=16, weight=ft.FontWeight.BOLD, color=color),
                            ],
                        ),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=14, vertical=10),
                            bgcolor=BG_DARK,
                            border_radius=8,
                            content=ft.Text(reemplaza_a, size=14, color=TEXT_PRI, selectable=True),
                        ),
                    ],
                ),
            )
        )

    # Info técnica
    filas_info = []
    if link_proyecto:
        filas_info.append(fila_info("Proyecto oficial:", ft.TextButton(
            link_proyecto,
            icon=ft.Icons.OPEN_IN_NEW_ROUNDED,
            on_click=lambda e, u=link_proyecto: abrir_url(u, page),
            style=ft.ButtonStyle(color=ACCENT2, padding=ft.padding.all(0)),
        )))
    if link_descarga:
        filas_info.append(fila_info("Descarga:", ft.TextButton(
            link_descarga,
            icon=ft.Icons.CLOUD_DOWNLOAD_ROUNDED,
            on_click=lambda e, u=link_descarga: abrir_url(u, page),
            style=ft.ButtonStyle(color=SUCCESS, padding=ft.padding.all(0)),
        )))
    if prog.get("tamano_mb"):
        filas_info.append(fila_info("Tamaño aprox.:", f"{prog['tamano_mb']} MB"))
    filas_info.append(fila_info("Versión:", prog["version"]))

    # Sección de carrusel (solo si hay fotos)
    seccion_carrusel = []
    if carrusel:
        seccion_carrusel.append(
            ft.Container(
                padding=ft.padding.all(20),
                bgcolor=BG_CARD,
                border_radius=12,
                border=ft.border.all(1, BORDER),
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Text("Capturas de pantalla", size=16, weight=ft.FontWeight.BOLD, color=ACCENT2),
                        carrusel,
                    ],
                ),
            )
        )

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=0,
        controls=[
            # ── Hero banner ───────────────────────────────────────────────────
            ft.Container(
                padding=ft.padding.all(30),
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(x=-1, y=-1),
                    end=ft.Alignment(x=1, y=1),
                    colors=[color, BG_DARK],
                ),
                border_radius=ft.BorderRadius(top_left=0, top_right=0, bottom_left=20, bottom_right=20),
                content=ft.Column(
                    spacing=16,
                    controls=[
                        ft.TextButton(
                            content=ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.ARROW_BACK_IOS_ROUNDED, size=16, color=ft.Colors.WHITE),
                                    ft.Text("Volver a la tienda", color=ft.Colors.WHITE, size=14),
                                ],
                            ),
                            on_click=on_back,
                        ),
                        ft.Row(
                            spacing=20,
                            controls=[
                                ft.Container(
                                    content=ft.Text(prog["icono"], size=56),
                                    bgcolor="#ffffff22",
                                    border_radius=20,
                                    padding=ft.padding.all(16),
                                ),
                                ft.Column(
                                    spacing=8,
                                    controls=[
                                        ft.Text(prog["nombre"], size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                        ft.Text(
                                            f"Versión {prog['version']}  ·  {prog['categoria']}",
                                            size=14,
                                            color="#ffffffBB",
                                        ),
                                        ft.Row(
                                            spacing=8,
                                            controls=[
                                                ft.ElevatedButton(
                                                    "Descargar",
                                                    icon=ft.Icons.CLOUD_DOWNLOAD_ROUNDED,
                                                    on_click=lambda e, u=link_descarga: abrir_url(u, page),
                                                    disabled=not link_descarga,
                                                    style=ft.ButtonStyle(
                                                        color=color,
                                                        bgcolor=ft.Colors.WHITE,
                                                        shape=ft.RoundedRectangleBorder(radius=8),
                                                    ),
                                                ),
                                                *(
                                                    [ft.OutlinedButton(
                                                        "Sitio web",
                                                        icon=ft.Icons.OPEN_IN_NEW_ROUNDED,
                                                        on_click=lambda e, u=link_proyecto: abrir_url(u, page),
                                                        style=ft.ButtonStyle(
                                                            color=ft.Colors.WHITE,
                                                            side=ft.BorderSide(1.5, "#ffffff88"),
                                                            shape=ft.RoundedRectangleBorder(radius=8),
                                                        ),
                                                    )]
                                                    if link_proyecto else []
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ),
            # ── Cuerpo ────────────────────────────────────────────────────────
            ft.Container(
                padding=ft.padding.symmetric(horizontal=30, vertical=24),
                content=ft.Column(
                    spacing=24,
                    controls=[
                        # Carrusel de fotos (si hay)
                        *seccion_carrusel,
                        # Descripción
                        ft.Container(
                            padding=ft.padding.all(20),
                            bgcolor=BG_CARD,
                            border_radius=12,
                            border=ft.border.all(1, BORDER),
                            content=ft.Column(
                                spacing=12,
                                controls=[
                                    ft.Text("Descripción", size=16, weight=ft.FontWeight.BOLD, color=ACCENT2),
                                    ft.Text(prog["descripcion"], size=14, color=TEXT_PRI, selectable=True),
                                ],
                            ),
                        ),
                        # Características
                        ft.Container(
                            padding=ft.padding.all(20),
                            bgcolor=BG_CARD,
                            border_radius=12,
                            border=ft.border.all(1, BORDER),
                            content=ft.Column(
                                spacing=12,
                                controls=[
                                    ft.Text("Características", size=16, weight=ft.FontWeight.BOLD, color=ACCENT2),
                                    ft.Column(spacing=10, controls=caract_items),
                                ],
                            ),
                        ),
                        # Reemplaza a
                        *seccion_reemplaza,
                        # ¿Por qué libre?
                        ft.Container(
                            padding=ft.padding.all(20),
                            bgcolor=f"{color}18",
                            border_radius=12,
                            border=ft.border.all(1, f"{color}44"),
                            content=ft.Column(
                                spacing=12,
                                controls=[
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Icon(ft.Icons.VOLUNTEER_ACTIVISM_ROUNDED, color=color, size=22),
                                            ft.Text("¿Por qué usar esta versión libre?", size=16, weight=ft.FontWeight.BOLD, color=color),
                                        ],
                                    ),
                                    ft.Text(prog["por_que_libre"], size=14, color=TEXT_PRI, selectable=True),
                                ],
                            ),
                        ),
                        # Info técnica
                        ft.Container(
                            padding=ft.padding.all(20),
                            bgcolor=BG_CARD2,
                            border_radius=12,
                            border=ft.border.all(1, BORDER),
                            content=ft.Column(
                                spacing=10,
                                controls=[
                                    ft.Text("Información técnica", size=16, weight=ft.FontWeight.BOLD, color=ACCENT2),
                                    *filas_info,
                                ],
                            ),
                        ),
                    ],
                ),
            ),
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Aplicación principal
# ─────────────────────────────────────────────────────────────────────────────

def main(page: ft.Page):
    page.title = "Tienda de Programas Libres"
    page.bgcolor = BG_DARK
    page.padding = 0
    page.window.width = 1100
    page.window.height = 780
    page.window.min_width = 800
    page.window.min_height = 600

    programas = cargar_programas()

    estado = {
        "vista": "lista",
        "prog": None,
        "categoria": "Todos",
    }

    area = ft.Container(expand=True, bgcolor=BG_DARK)

    def go_detalle(prog):
        estado["vista"] = "detalle"
        estado["prog"] = prog
        render()

    def go_lista(e=None):
        estado["vista"] = "lista"
        render()

    # ── Renderizado ───────────────────────────────────────────────────────────
    def render():
        if estado["vista"] == "lista":
            cat = estado["categoria"]
            filtrados = [p for p in programas if cat == "Todos" or p["categoria"] == cat]

            if not filtrados:
                area.content = ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("📭", size=64),
                        ft.Text("No hay programas en esta categoría", size=18, color=TEXT_SEC),
                    ],
                )
            else:
                filas = []
                for i in range(0, len(filtrados), 2):
                    par = filtrados[i : i + 2]
                    cols = [
                        ft.Container(content=crear_card(p, go_detalle, page), expand=True)
                        for p in par
                    ]
                    if len(cols) == 1:
                        cols.append(ft.Container(expand=True))
                    filas.append(ft.Row(spacing=16, controls=cols))

                area.content = ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                    controls=[
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=20, vertical=16),
                            content=ft.Column(spacing=16, controls=filas),
                        )
                    ],
                )

        elif estado["vista"] == "detalle":
            area.content = crear_detalle(estado["prog"], go_lista, page)

        page.update()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    categorias = ["Todos"] + sorted({p["categoria"] for p in programas})
    cat_btns: list[ft.TextButton] = []

    def cambiar_cat(cat: str):
        estado["categoria"] = cat
        for btn in cat_btns:
            activo = btn.data == cat
            btn.style = ft.ButtonStyle(
                color=ft.Colors.WHITE if activo else TEXT_SEC,
                bgcolor=ACCENT if activo else "transparent",
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=14, vertical=8),
            )
        render()

    def hacer_cat_btn(cat: str) -> ft.TextButton:
        btn = ft.TextButton(
            cat,
            data=cat,
            on_click=lambda e, c=cat: cambiar_cat(c),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE if cat == "Todos" else TEXT_SEC,
                bgcolor=ACCENT if cat == "Todos" else "transparent",
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=14, vertical=8),
            ),
        )
        cat_btns.append(btn)
        return btn

    sidebar = ft.Container(
        width=190,
        bgcolor=BG_CARD,
        border=ft.border.only(right=ft.BorderSide(1, BORDER)),
        content=ft.Column(
            spacing=4,
            controls=[
                ft.Container(height=14),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=14),
                    content=ft.Text("CATEGORÍAS", size=10, color=TEXT_SEC, weight=ft.FontWeight.W_700),
                ),
                ft.Container(height=6),
                *[hacer_cat_btn(c) for c in categorias],
            ],
        ),
    )

    # ── Topbar ────────────────────────────────────────────────────────────────
    topbar = ft.Container(
        height=64,
        bgcolor=BG_CARD,
        border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
        padding=ft.padding.symmetric(horizontal=24),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Text("🐧", size=26),
                    bgcolor=f"{ACCENT}22",
                    border_radius=10,
                    padding=ft.padding.all(6),
                ),
                ft.Container(width=12),
                ft.Column(
                    spacing=0,
                    controls=[
                        ft.Text("Software Libre", size=17, weight=ft.FontWeight.BOLD, color=TEXT_PRI),
                        ft.Text("Tienda de aplicaciones gratuitas", size=11, color=TEXT_SEC),
                    ],
                ),
            ],
        ),
    )

    # ── Layout ────────────────────────────────────────────────────────────────
    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[
                topbar,
                ft.Row(
                    expand=True,
                    spacing=0,
                    controls=[sidebar, area],
                ),
            ],
        )
    )

    render()


ft.run(main)
