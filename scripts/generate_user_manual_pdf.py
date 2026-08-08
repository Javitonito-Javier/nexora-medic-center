from __future__ import annotations

from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "manual_uso_clinicapharma_mvp.pdf"


class Divider(Flowable):
    def __init__(self, width: float = 6.5 * inch, color=colors.HexColor("#00796B")):
        super().__init__()
        self.width = width
        self.height = 8
        self.color = color

    def draw(self) -> None:
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(1.2)
        self.canv.line(0, 4, self.width, 4)


def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ManualTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=29,
            textColor=colors.HexColor("#00695C"),
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "subtitle": ParagraphStyle(
            "ManualSubtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#455A64"),
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "h1": ParagraphStyle(
            "ManualH1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#00695C"),
            spaceBefore=8,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "ManualH2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=16,
            textColor=colors.HexColor("#263238"),
            spaceBefore=8,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "ManualBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#263238"),
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "ManualSmall",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.2,
            leading=11,
            textColor=colors.HexColor("#455A64"),
            spaceAfter=4,
        ),
        "callout": ParagraphStyle(
            "ManualCallout",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.3,
            leading=13,
            textColor=colors.HexColor("#263238"),
            backColor=colors.HexColor("#E0F2F1"),
            borderColor=colors.HexColor("#80CBC4"),
            borderWidth=0.5,
            borderPadding=8,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=4,
            spaceAfter=10,
        ),
    }


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def bullets(items: list[str], style: ParagraphStyle) -> ListFlowable:
    return ListFlowable(
        [ListItem(p(item, style), leftIndent=12) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=18,
        bulletFontName="Helvetica",
        bulletFontSize=8,
    )


def steps(items: list[str], style: ParagraphStyle) -> ListFlowable:
    return ListFlowable(
        [ListItem(p(item, style), leftIndent=14) for item in items],
        bulletType="1",
        leftIndent=18,
        bulletFontName="Helvetica-Bold",
        bulletFontSize=8,
    )


def section(title: str, body: list[Flowable], styles: dict[str, ParagraphStyle]) -> list[Flowable]:
    return [p(title, styles["h1"]), Divider(), *body, Spacer(1, 6)]


def make_table(rows: list[list[str]], styles: dict[str, ParagraphStyle], widths: list[float] | None = None) -> Table:
    data = [[p(cell, styles["small"]) for cell in row] for row in rows]
    table = Table(data, colWidths=widths, hAlign="LEFT", repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00695C")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7FBFA")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B0BEC5")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def header_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#607D8B"))
    canvas.drawString(doc.leftMargin, 0.42 * inch, "Clinicapharma MVP - Manual de uso")
    canvas.drawRightString(letter[0] - doc.rightMargin, 0.42 * inch, f"Pagina {doc.page}")
    canvas.restoreState()


def build_story() -> list[Flowable]:
    styles = build_styles()
    today = date.today().strftime("%d/%m/%Y")
    story: list[Flowable] = [
        Spacer(1, 0.4 * inch),
        p("Manual de Uso - Clinicapharma MVP", styles["title"]),
        p(
            f"Guia operativa hasta el avance actual del sistema. Fecha: {today}. "
            "Tecnologias: Flutter Web, FastAPI y PostgreSQL local.",
            styles["subtitle"],
        ),
        p(
            "Este manual explica como operar el sistema en su estado actual. Algunas funciones "
            "son base de MVP y seguiran creciendo, especialmente facturacion fiscal completa, "
            "archivos adjuntos reales para evidencia, puntos avanzados y reporteria ampliada.",
            styles["callout"],
        ),
    ]

    story += section(
        "1. Alcance Actual",
        [
            bullets(
                [
                    "Dashboard con resumen de clinica, farmacia, alertas de stock, lotes por vencer y ventas.",
                    "Gestion de pacientes/clientes con busqueda por nombre, identidad y telefono.",
                    "Citas, consulta, expediente clinico, recetas y flujo basico de atencion.",
                    "Inventario por producto, presentaciones, lotes, bodega, tienda, vencimiento, costo y viñeta.",
                    "Farmacia POS con busqueda de producto, busqueda de cliente, descuentos, recibo/factura y caja.",
                    "Cajas con cierre por usuario/cajero y desglose por efectivo, tarjeta y transferencia.",
                ],
                styles["body"],
            )
        ],
        styles,
    )

    story += section(
        "2. Inicio de Sesion",
        [
            steps(
                [
                    "Abrir la webapp de Clinicapharma en el navegador.",
                    "Ingresar usuario y contrasena. En desarrollo normalmente se usa el usuario administrador inicial.",
                    "Al entrar, el sistema muestra el dashboard segun el area y permisos del usuario.",
                    "Usar el menu lateral para cambiar entre Dashboard, Pacientes, Citas, Consulta, Personal, Farmacia POS, Inventario, Cajas y Reportes.",
                ],
                styles["body"],
            ),
            p("Nota: el login ya permite trabajar con usuarios/roles. El administrador puede crear personal y luego se ampliara el control fino por permisos.", styles["callout"]),
        ],
        styles,
    )

    story += section(
        "3. Dashboard",
        [
            p("La pantalla principal sirve para ver rapidamente el estado del negocio y la clinica.", styles["body"]),
            make_table(
                [
                    ["Elemento", "Uso"],
                    ["Citas de hoy y pendientes", "Permite ver actividad de consulta del dia."],
                    ["Consultas pagadas", "Resume pagos de servicios clinicos registrados."],
                    ["Ventas farmacia dia/mes", "Muestra movimiento comercial de farmacia."],
                    ["Utilidad farmacia", "Calculada con venta menos costo real de lotes vendidos."],
                    ["Bajo stock y vencimientos", "Ayuda a reponer o rotar productos antes de perder dinero."],
                ],
                styles,
                [2.0 * inch, 4.2 * inch],
            ),
        ],
        styles,
    )

    story += section(
        "4. Pacientes y Clientes",
        [
            steps(
                [
                    "Entrar a Pacientes.",
                    "Usar el buscador para filtrar por nombre, identidad o telefono.",
                    "Para registrar uno nuevo, llenar nombre, identidad/RTN, telefono, fecha de nacimiento, sexo, direccion, alergias y antecedentes.",
                    "Guardar paciente.",
                    "Abrir expediente con el boton de flecha del paciente para ver historial, consultas y recetas.",
                ],
                styles["body"],
            ),
            p("El paciente tambien funciona como cliente de farmacia, por eso aparece en POS para aplicar descuentos y puntos.", styles["callout"]),
        ],
        styles,
    )

    story += section(
        "5. Citas",
        [
            steps(
                [
                    "Entrar a Citas.",
                    "Buscar y seleccionar paciente. La busqueda filtra aunque la lista sea grande.",
                    "Elegir fecha, hora, medico/enfermera si aplica, motivo y estado.",
                    "Guardar la cita.",
                    "Desde el listado se puede abrir expediente o iniciar consulta.",
                ],
                styles["body"],
            ),
            p("El sistema esta pensado para pequenas clinicas y tambien para crecer con varios doctores/enfermeras en turno.", styles["body"]),
        ],
        styles,
    )

    story += section(
        "6. Consulta y Expediente",
        [
            bullets(
                [
                    "El expediente guarda multiples consultas del mismo paciente. Si vino 25 veces en un ano, se debe poder ver cada fecha.",
                    "La enfermera puede anotar signos vitales y datos previos; si no hay enfermera, el doctor puede llenar esa informacion.",
                    "La consulta registra motivo, signos vitales, historia clinica, diagnostico, tratamiento y proxima cita.",
                    "La receta se genera desde el expediente o desde la consulta del paciente.",
                ],
                styles["body"],
            ),
            make_table(
                [
                    ["Campo clinico", "Para que sirve"],
                    ["Signos vitales", "Presion, frecuencia, SPO2, peso, temperatura u otros datos base."],
                    ["Historia clinica", "Descripcion de sintomas, evolucion y observaciones."],
                    ["Diagnostico", "Conclusiones medicas de la visita."],
                    ["Tratamiento", "Indicaciones del medico."],
                    ["Receta", "Documento para imprimir o exportar cuando aplique."],
                ],
                styles,
                [2.0 * inch, 4.2 * inch],
            ),
        ],
        styles,
    )

    story.append(PageBreak())

    story += section(
        "7. Inventario: Crear Producto y Lote",
        [
            p("Inventario maneja productos por presentacion y por lote. Esto es importante porque cada lote puede tener costo distinto, precio distinto y vencimiento distinto.", styles["body"]),
            steps(
                [
                    "Entrar a Inventario.",
                    "Llenar Producto, Codigo/SKU y Codigo de barra general.",
                    "Elegir tipo: pastilla/blister/caja, frasco/caja o guantes unidad/par/caja.",
                    "Llenar Unidad base, Laboratorio y Proveedor.",
                    "Definir conversiones: unidades por blister/par y blisters o unidades por caja.",
                    "Ingresar Venta unidad, Venta blister/par y Venta caja. Estos son los precios normales al publico.",
                    "Ingresar Vineta unidad, Vineta blister/par y Vineta caja. Esta es la base legal para tercera/cuarta edad.",
                    "Ingresar Stock minimo.",
                    "Ingresar Lote, Codigo lote, Estante y Vencimiento.",
                    "Ingresar Bodega y Tienda. Bodega es reserva; Tienda es lo disponible para vender en POS.",
                    "Ingresar Costo unidad del lote para calcular utilidad real.",
                    "Guardar producto.",
                ],
                styles["body"],
            ),
            p("Regla practica: si el medicamento trae precio impreso o recomendado, ese precio va en Viñeta. Si la farmacia vende mas barato al publico general, ese precio va en Venta.", styles["callout"]),
        ],
        styles,
    )

    story += section(
        "8. Inventario: Bodega, Tienda, Traslados y Mermas",
        [
            make_table(
                [
                    ["Accion", "Como usarla"],
                    ["Trasladar", "Mueve unidades de Bodega a Tienda sin contarlo como venta. Debe hacerse por lote."],
                    ["Lista surtido", "Indica que lote sacar primero segun FEFO/FIFO, mostrando estante, lote y vencimiento."],
                    ["Merma", "Registra perdida por vencimiento, dano, robo, error o ajuste. Se carga al lote afectado."],
                    ["Conteo ciclico", "Por ahora se maneja como verificacion manual y ajustes/mermas. Luego puede crecer a modulo formal."],
                ],
                styles,
                [1.55 * inch, 4.65 * inch],
            ),
            p("FEFO/FIFO: el sistema prioriza el lote que vence primero y luego el mas antiguo. Fisicamente conviene poner lo nuevo atras y lo viejo al frente.", styles["callout"]),
        ],
        styles,
    )

    story += section(
        "9. Farmacia POS: Venta Normal",
        [
            steps(
                [
                    "Entrar a Farmacia POS.",
                    "Buscar producto por nombre, SKU, codigo de barra general o codigo de lote.",
                    "Seleccionar presentacion: unidad, blister/par, frasco o caja segun el producto.",
                    "El producto pasa al carrito.",
                    "Buscar cliente si esta registrado. Si no, puede quedar como consumidor final.",
                    "Elegir cajero, documento (recibo o factura) y forma de pago: efectivo, tarjeta o transferencia.",
                    "Cobrar.",
                    "El sistema descuenta stock de Tienda automaticamente y genera el recibo.",
                ],
                styles["body"],
            ),
            p("Si se escanea el codigo general del producto, el sistema vende usando FEFO/FIFO. Si se escanea codigo de lote, descuenta exactamente ese lote fisico.", styles["callout"]),
        ],
        styles,
    )

    story += section(
        "10. Farmacia POS: Cliente, Descuentos y Puntos",
        [
            make_table(
                [
                    ["Tipo", "Regla actual"],
                    ["Descuento general", "Se puede escribir manualmente en el campo descuento."],
                    ["Tercera edad", "Aplica 25% sobre precio de viñeta, no sobre el precio normal rebajado."],
                    ["Cuarta edad", "Aplica 35% sobre precio de viñeta y exige evidencia de receta/DNI antes de cobrar."],
                    ["Puntos", "Se pueden usar como descuento cuando el cliente tenga minimo L 50.00 disponibles."],
                ],
                styles,
                [1.7 * inch, 4.5 * inch],
            ),
            p("Ejemplo: si viñeta es L 1,500 y venta normal es L 1,400, tercera edad se calcula contra L 1,500. El sistema registra el descuento necesario para que el total final cumpla la regla.", styles["callout"]),
        ],
        styles,
    )

    story.append(PageBreak())

    story += section(
        "11. Cajas y Cierre",
        [
            bullets(
                [
                    "Cajas muestra ventas de farmacia por fecha y cajero.",
                    "El resumen separa subtotal, descuento, total, costo real, utilidad, efectivo, tarjeta y transferencia.",
                    "Sirve para cierre por usuario/cajero.",
                    "Clinica y farmacia pueden manejar cajas separadas segun el modulo.",
                ],
                styles["body"],
            ),
            p("La utilidad se calcula usando el costo real del lote vendido, por eso es importante registrar bien el costo unidad en cada entrada.", styles["callout"]),
        ],
        styles,
    )

    story += section(
        "12. Reportes Actuales y Pendientes",
        [
            make_table(
                [
                    ["Reporte", "Estado"],
                    ["Dashboard", "Disponible con metricas principales."],
                    ["Cajas farmacia", "Disponible con cierre por fecha/cajero."],
                    ["Inventario", "Disponible con stock, lote, vencimiento, bodega y tienda."],
                    ["Puntos clientes", "Base visible en pacientes/POS; falta modulo completo de movimientos."],
                    ["Facturacion fiscal SAR", "Planeado como modulo aparte para venderlo tambien a usuarios que si lo requieran."],
                    ["PDF/WhatsApp", "Recibos y recetas pueden exportarse; WhatsApp se puede hacer manual al inicio."],
                ],
                styles,
                [2.0 * inch, 4.2 * inch],
            ),
        ],
        styles,
    )

    story += section(
        "13. Recomendaciones de Operacion Diaria",
        [
            bullets(
                [
                    "Registrar cada compra como lote con costo real, vencimiento, estante y cantidad en bodega/tienda.",
                    "No vender desde bodega; primero trasladar a tienda.",
                    "Usar codigo de lote si se quiere trazabilidad estricta.",
                    "Revisar vencimientos y bajo stock desde dashboard.",
                    "Hacer cierre por cajero al final del turno.",
                    "Registrar evidencia cuando se aplique cuarta edad.",
                    "Revisar fisicamente que lo viejo este al frente y lo nuevo atras.",
                ],
                styles["body"],
            )
        ],
        styles,
    )

    story += section(
        "14. Pendientes Recomendados para Siguiente Fase",
        [
            bullets(
                [
                    "Adjuntar foto real o escaneo de DNI/receta en descuentos especiales.",
                    "Modulo completo de puntos: acumulacion, redencion, historial y anulaciones.",
                    "Modulo formal de facturacion SAR independiente.",
                    "Impresion termica con perfiles de papel configurables.",
                    "Reportes PDF/Excel de ventas, utilidad, inventario, vencimientos y pacientes.",
                    "Auditoria de acciones por usuario.",
                    "Ajustes manuales de inventario con aprobacion administrativa.",
                ],
                styles["body"],
            )
        ],
        styles,
    )

    story += [
        Spacer(1, 12),
        p(
            "Fin del manual. Este documento refleja el avance del MVP hasta la fecha indicada.",
            styles["subtitle"],
        ),
    ]
    return story


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.68 * inch,
        bottomMargin=0.72 * inch,
        title="Manual de Uso Clinicapharma MVP",
        author="Clinicapharma",
    )
    doc.build(build_story(), onFirstPage=header_footer, onLaterPages=header_footer)
    print(OUTPUT)


if __name__ == "__main__":
    main()
