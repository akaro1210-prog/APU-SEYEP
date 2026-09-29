"""
pdf_generator.py — Generador nativo de PDF en memoria (BytesIO) usando fpdf2.
Replica exactamente el diseño corporativo de SEYEP SAS (7 páginas en Formato A y 1 página en Formato B),
con encabezado/pie de página personalizados y tablas de Oferta Económica.
"""
import os
import base64
from io import BytesIO
from fpdf import FPDF
from PIL import Image, ImageChops
from calculator import calc_item, calc_resumen_general, fmt_cop, fmt_pct

try:
    from state import LOGO_B64
except ImportError:
    LOGO_B64 = ""

SEY_NAVY = (23, 0, 172)         # #1700AC
SEY_TABLE_HEAD = (83, 141, 213) # #538DD5
SEY_GRAY = (217, 217, 217)      # #D9D9D9
TEXT_DARK = (17, 17, 17)

PAGE_W_MM = 210.0
PAGE_H_MM = 297.0
MARGIN_X_MM = 24.0
CONTENT_W_MM = 162.0  # 210 - 2 * 24 (márgenes editoriales idénticos al documento de referencia)


def _clean_latin1(text: str) -> str:
    """Limpia caracteres Unicode fuera de Latin-1 para evitar errores en fuentes core de fpdf2."""
    if text is None:
        return ""
    replacements = {
        "•": "\xb7",
        "–": "-",
        "—": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
    }
    s = str(text)
    for k, v in replacements.items():
        s = s.replace(k, v)
    return s.encode("latin-1", "replace").decode("latin-1")


def safe_decode_b64_image(b64_str: str | None) -> bytes | None:
    """Decodifica una cadena Base64 (con o sin prefijo data:image/...) y verifica que sea una imagen válida."""
    if not b64_str:
        return None
    try:
        raw = b64_str.split(",")[1] if "," in b64_str else b64_str
        raw = "".join(raw.split())
        rem = len(raw) % 4
        if rem == 1:
            raw = raw[:-1]
        elif rem in (2, 3):
            raw += "=" * (4 - rem)

        data = base64.b64decode(raw, validate=False)
        img = Image.open(BytesIO(data))
        img.verify()
        return data
    except Exception:
        return None


def safe_decode_logo(logo_b64: str | None = None) -> bytes | None:
    for filename in ("logo.png", "logo.jpg", "logo.jpeg"):
        if os.path.exists(filename):
            try:
                with open(filename, "rb") as f:
                    return f.read()
            except Exception:
                pass
    b64_source = logo_b64 if logo_b64 is not None else LOGO_B64
    return safe_decode_b64_image(b64_source)


def _prepare_banner_image(img_bytes: bytes | None) -> tuple[bytes | None, float, float]:
    """
    Aplana transparencias sobre blanco y recorta bordes blancos sobrantes para que
    el encabezado y pie de página ajusten con precisión al ancho de la hoja.
    """
    if not img_bytes:
        return None, 0.0, 0.0
    try:
        with Image.open(BytesIO(img_bytes)) as im:
            if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
                rgba = im.convert("RGBA")
                bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
                rgb = Image.alpha_composite(bg, rgba).convert("RGB")
            else:
                rgb = im.convert("RGB")

            white_bg = Image.new("RGB", rgb.size, (255, 255, 255))
            diff = ImageChops.difference(rgb, white_bg).convert("L")
            diff = diff.point(lambda p: 255 if p > 12 else 0)
            bbox = diff.getbbox()
            if bbox:
                pad = 2
                left = max(0, bbox[0] - pad)
                top = max(0, bbox[1] - pad)
                right = min(rgb.width, bbox[2] + pad)
                bottom = min(rgb.height, bbox[3] + pad)
                if (right - left) > 40 and (bottom - top) > 10:
                    rgb = rgb.crop((left, top, right, bottom))

            out = BytesIO()
            rgb.save(out, format="PNG")
            return out.getvalue(), float(rgb.width), float(rgb.height)
    except Exception:
        return img_bytes, 180.0, 30.0


def _calc_banner_dims_mm(
    px_w: float,
    px_h: float,
    target_w_mm: float,
    max_h_mm: float,
) -> tuple[float, float]:
    if px_w <= 0 or px_h <= 0:
        return target_w_mm, 28.0
    aspect = px_w / px_h
    w_mm = target_w_mm
    h_mm = w_mm / aspect
    if h_mm > max_h_mm:
        h_mm = max_h_mm
        w_mm = min(target_w_mm, h_mm * aspect)
    return w_mm, h_mm


class CotizacionPDF(FPDF):
    def __init__(
        self,
        cot_data: dict,
        logo_bytes: bytes | None = None,
        header_bytes: bytes | None = None,
        footer_bytes: bytes | None = None,
    ):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.cot = cot_data
        self.logo_bytes = logo_bytes
        self.set_font("Times", "", 10.5)
        self.set_margins(left=MARGIN_X_MM, top=35.0, right=MARGIN_X_MM)

        raw_hdr = header_bytes or safe_decode_b64_image(cot_data.get("headerImgB64"))
        raw_ftr = footer_bytes or safe_decode_b64_image(cot_data.get("footerImgB64"))

        self.header_bytes, self.hdr_px_w, self.hdr_px_h = _prepare_banner_image(raw_hdr)
        self.footer_bytes, self.ftr_px_w, self.ftr_px_h = _prepare_banner_image(raw_ftr)

        # El encabezado en el PDF de referencia abarca aprox 182 mm centrado arriba (x=14 a x=196)
        if self.header_bytes:
            self.hdr_w_mm, self.hdr_h_mm = _calc_banner_dims_mm(
                self.hdr_px_w, self.hdr_px_h, target_w_mm=182.0, max_h_mm=44.0
            )
            self.set_top_margin(8.0 + self.hdr_h_mm + 8.0)
        else:
            self.hdr_w_mm, self.hdr_h_mm = 0.0, 0.0
            self.set_top_margin(38.0)

        # El pie de página en el PDF de referencia va pegado abajo a la izquierda (x=0, ancho ~202 mm)
        if self.footer_bytes:
            self.ftr_w_mm, self.ftr_h_mm = _calc_banner_dims_mm(
                self.ftr_px_w, self.ftr_px_h, target_w_mm=202.0, max_h_mm=38.0
            )
            self.set_auto_page_break(auto=True, margin=self.ftr_h_mm + 10.0)
        else:
            self.ftr_w_mm, self.ftr_h_mm = 0.0, 0.0
            self.set_auto_page_break(auto=True, margin=28.0)

    def cell(self, w=None, h=None, text="", *args, **kwargs):
        if not self.font_family:
            self.set_font("Times", "", 10.5)
        return super().cell(w, h, _clean_latin1(text), *args, **kwargs)

    def multi_cell(self, w, h=None, text="", *args, **kwargs):
        if not self.font_family:
            self.set_font("Times", "", 10.5)
        return super().multi_cell(w, h, _clean_latin1(text), *args, **kwargs)

    def header(self):
        if not self.font_family:
            self.set_font("Times", "", 10.5)
        if self.header_bytes:
            try:
                x_pos = (PAGE_W_MM - self.hdr_w_mm) / 2.0
                self.image(
                    BytesIO(self.header_bytes),
                    x=x_pos,
                    y=8.0,
                    w=self.hdr_w_mm,
                    h=self.hdr_h_mm,
                )
                y_line = 8.0 + self.hdr_h_mm + 2.0
                self.set_draw_color(20, 20, 20)
                self.set_line_width(0.4)
                self.line(20.0, y_line, 190.0, y_line)
                self.set_y(y_line + 6.0)
                return
            except Exception:
                pass

        # Encabezado corporativo predeterminado
        logo_rendered = False
        if self.logo_bytes:
            try:
                self.image(BytesIO(self.logo_bytes), x=24, y=12, h=16)
                logo_rendered = True
            except Exception:
                logo_rendered = False

        if not logo_rendered:
            self.set_xy(24, 13)
            self.set_font("Helvetica", "B", 18)
            self.set_text_color(*SEY_NAVY)
            self.cell(32, 7, "SEYEP")
            self.set_font("Helvetica", "B", 8.5)
            self.cell(0, 4, "SERVICIOS ELÉCTRICOS Y ELECTRÓNICA DE POTENCIA", new_x="LMARGIN", new_y="NEXT")
            self.set_x(56)
            self.set_font("Courier", "", 8)
            self.set_text_color(40, 40, 40)
            self.cell(0, 4, "Acciones que generan desarrollo", new_x="LMARGIN", new_y="NEXT")

        self.set_draw_color(20, 20, 20)
        self.set_line_width(0.4)
        self.line(20.0, 31.0, 190.0, 31.0)
        self.set_y(37.0)

    def footer(self):
        if self.footer_bytes:
            try:
                y_pos = PAGE_H_MM - self.ftr_h_mm
                self.image(
                    BytesIO(self.footer_bytes),
                    x=0.0,
                    y=y_pos,
                    w=self.ftr_w_mm,
                    h=self.ftr_h_mm,
                )
                return
            except Exception:
                pass

        self.set_y(-18)
        self.set_x(0.0)
        self.set_fill_color(*SEY_NAVY)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "", 8.5)
        web = self.cot.get("web", "www.seyep.com.co")
        tel = self.cot.get("tel", "320 9398839")
        ig = self.cot.get("ig", "@seyepsas")
        footer_text = f"Web: {web}     |     Tel: {tel}     |     Instagram: {ig}"
        self.cell(185.0, 14.0, footer_text, border=0, align="C", fill=True)

    def section_bar(self, num_str: str, title: str):
        """Barra gris numerada (ej. '1.    OBJETO') idéntica al PDF de referencia."""
        self.ln(4)
        self.set_fill_color(*SEY_GRAY)
        self.set_text_color(*TEXT_DARK)
        self.set_font("Times", "B", 11)
        self.cell(CONTENT_W_MM, 6.5, f"{num_str}     {title.upper()}", border=0, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2.5)

    def subheading_level2(self, num_str: str, title: str):
        """Subtítulo nivel 2 (ej. '1.1.   EXCLUSIONES' o '3.1.   ESTUDIOS SIMPLIFICADOS...')."""
        self.ln(2.5)
        self.set_text_color(*TEXT_DARK)
        self.set_font("Times", "", 10.5)
        self.cell(CONTENT_W_MM, 5.5, f"{num_str}    {title.upper()}", new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)

    def subheading_level3(self, num_str: str, title: str):
        """Subtítulo nivel 3 con sangría (ej. '3.1.1.     INSUMOS DEL CLIENTE')."""
        self.ln(2)
        self.set_x(MARGIN_X_MM + 4.0)
        self.set_text_color(*TEXT_DARK)
        self.set_font("Times", "", 10.5)
        self.cell(CONTENT_W_MM - 4.0, 5.5, f"{num_str}       {title.upper()}", new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)

    def body_paragraph(self, text: str):
        """Renderiza párrafos justificados y líneas con guiones '-' respetando sangría."""
        if not text or not text.strip():
            return
        self.set_text_color(*TEXT_DARK)
        self.set_font("Times", "", 10.5)
        for raw_line in text.split("\n"):
            line = raw_line.strip()
            if not line:
                self.ln(2.5)
                continue
            if line.startswith("-") or line.startswith("•"):
                clean_item = line.lstrip("-•").strip()
                self.set_x(MARGIN_X_MM + 6.0)
                self.cell(6.0, 5.2, "-")
                self.multi_cell(CONTENT_W_MM - 12.0, 5.2, clean_item, align="J")
            else:
                self.set_x(MARGIN_X_MM)
                self.multi_cell(CONTENT_W_MM, 5.2, line, align="J")
                self.ln(1.2)

    def bullet_list(self, text: str, marker: str = "-"):
        """Renderiza cada salto de línea como un elemento de lista con sangría."""
        if not text or not text.strip():
            return
        self.set_text_color(*TEXT_DARK)
        self.set_font("Times", "", 10.5)
        for raw_line in text.split("\n"):
            line = raw_line.strip().lstrip("-•").strip()
            if not line:
                continue
            self.set_x(MARGIN_X_MM + 6.0)
            self.cell(6.0, 5.4, marker)
            self.multi_cell(CONTENT_W_MM - 12.0, 5.4, line, align="J")
            self.ln(0.8)


def _wrap_text_lines(pdf: FPDF, text: str, max_w_mm: float) -> list[str]:
    """Divide un texto en líneas que quepan dentro de max_w_mm según la fuente activa del PDF."""
    words = str(text or "").split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for w in words[1:]:
        candidate = f"{current} {w}"
        if pdf.get_string_width(_clean_latin1(candidate)) <= (max_w_mm - 2.5):
            current = candidate
        else:
            lines.append(current)
            current = w
    lines.append(current)
    return lines


def _render_tabla_oferta_economica_a(
    pdf: CotizacionPDF,
    rows_data: list[dict],
    sub: float,
    iva_pct: float,
    iva: float,
    rte_pct: float,
    rte: float,
    tot: float,
):
    """
    Dibuja una tabla de OFERTA ECONÓMICA en Formato A:
    - Si se llama con 1 elemento en rows_data, dibuja la tabla individual de ese ítem.
    - Si se llama con todos los elementos en rows_data, dibuja todos los ítems en la misma tabla
      y al final agrega las filas de 'Valor antes de IVA', 'IVA', 'RETEFUENTE' y 'Valor total de la oferta'.
    """
    needed_h = 32.0 + len(rows_data) * 7.0
    if pdf.get_y() + needed_h > 255:
        pdf.add_page()

    pdf.ln(3)
    widths = [11.0, 86.0, 12.0, 13.0, 20.0, 20.0]  # Suma = 162 mm (CONTENT_W_MM)
    total_w = sum(widths)

    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.25)

    # Fila 1: Título OFERTA ECONÓMICA
    pdf.set_fill_color(*SEY_TABLE_HEAD)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.cell(total_w, 4.8, "OFERTA ECONÓMICA", border=1, align="C", fill=True, new_x="LMARGIN", new_y="NEXT")

    # Fila 2: Encabezados de columna
    headers = ["ITEM", "ITEM DE PAGO", "Cant", "Und", "Valor Unidad", "Valor Total"]
    for w, h_txt in zip(widths, headers):
        pdf.cell(w, 6.0, h_txt, border=1, align="C", fill=True)
    pdf.ln()

    # Filas de ítems (con ajuste multilínea si el nombre es largo)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_fill_color(255, 255, 255)
    for r in rows_data:
        lines_nom = _wrap_text_lines(pdf, r["nombre"], widths[1])
        line_h = 4.0
        row_h = max(5.4, len(lines_nom) * line_h + 1.4)
        x0 = MARGIN_X_MM
        y0 = pdf.get_y()

        # Dibujar bordes de las 6 celdas
        cur_x = x0
        for w in widths:
            pdf.rect(cur_x, y0, w, row_h)
            cur_x += w

        y_mid = y0 + (row_h - line_h) / 2.0
        pdf.set_xy(x0, y_mid)
        pdf.cell(widths[0], line_h, str(r["idx"]), border=0, align="C")

        # Texto multilínea en ITEM DE PAGO
        y_text_start = y0 + (row_h - len(lines_nom) * line_h) / 2.0
        for idx_l, ln_txt in enumerate(lines_nom):
            pdf.set_xy(x0 + widths[0] + 1.0, y_text_start + idx_l * line_h)
            pdf.cell(widths[1] - 2.0, line_h, ln_txt, border=0, align="L")

        x_c2 = x0 + widths[0] + widths[1]
        pdf.set_xy(x_c2, y_mid)
        pdf.cell(widths[2], line_h, f"{float(r['cant']):g}", border=0, align="C")
        pdf.set_xy(x_c2 + widths[2], y_mid)
        pdf.cell(widths[3], line_h, str(r["und"]), border=0, align="C")
        pdf.set_xy(x_c2 + widths[2] + widths[3], y_mid)
        pdf.cell(widths[4], line_h, fmt_cop(r["valor_u"]), border=0, align="R")
        pdf.set_xy(x_c2 + widths[2] + widths[3] + widths[4], y_mid)
        pdf.cell(widths[5], line_h, fmt_cop(r["sub"]), border=0, align="R")

        pdf.set_xy(MARGIN_X_MM, y0 + row_h)

    # Filas de Totales alineadas a la derecha bajo 'Und + Valor Unidad' y 'Valor Total'
    left_empty_w = widths[0] + widths[1] + widths[2]
    label_box_w = widths[3] + widths[4]
    val_box_w = widths[5]

    tot_rows = [
        ("Valor antes de IVA", fmt_cop(sub), True),
        (f"IVA ({fmt_pct(iva_pct)})", fmt_cop(iva), True),
        (f"RETEFUENTE ({fmt_pct(rte_pct)})", fmt_cop(rte), True),
        ("Valor total de la oferta", fmt_cop(tot), True),
    ]
    for lbl, val_str, is_bold in tot_rows:
        pdf.set_x(MARGIN_X_MM + left_empty_w)
        pdf.set_font("Helvetica", "B" if is_bold else "", 7.5)
        pdf.cell(label_box_w, 4.8, lbl, border=1, align="C")
        pdf.set_font("Helvetica", "", 7.5)
        pdf.cell(val_box_w, 4.8, val_str, border=1, align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)


def generar_pdf_formato_a(
    state: dict,
    logo_b64: str | None = None,
    header_bytes: bytes | None = None,
    footer_bytes: bytes | None = None,
) -> bytes:
    cot = state["cot"]
    logo_bytes = safe_decode_logo(logo_b64)
    pdf = CotizacionPDF(cot, logo_bytes, header_bytes=header_bytes, footer_bytes=footer_bytes)
    pdf.alias_nb_pages()
    pdf.add_page()

    # ---- TABLA SUPERIOR DE DATOS DE LA OFERTA (Fondo blanco, bordes finos, igual al PDF de referencia) ----
    pdf.set_draw_color(40, 40, 40)
    pdf.set_line_width(0.25)
    w_lbl = 42.0
    w_val = CONTENT_W_MM - w_lbl

    # Fila 1: CLIENTE
    pdf.set_font("Times", "B", 10)
    pdf.cell(w_lbl, 7.0, "CLIENTE:", border=1, align="L")
    pdf.set_font("Times", "", 10)
    pdf.cell(w_val, 7.0, str(cot.get("cliente", "")), border=1, align="L", new_x="LMARGIN", new_y="NEXT")

    # Fila 2: OFERTA
    pdf.set_font("Times", "B", 10)
    pdf.cell(w_lbl, 9.5, "OFERTA:", border=1, align="L")
    pdf.set_font("Times", "", 10)
    pdf.cell(w_val, 9.5, str(cot.get("ofertaTitulo", "")), border=1, align="L", new_x="LMARGIN", new_y="NEXT")

    # Fila 3: REFERENCIA
    pdf.set_font("Times", "B", 10)
    pdf.cell(w_lbl, 7.0, "REFERENCIA:", border=1, align="L")
    pdf.set_font("Times", "", 10)
    pdf.cell(w_val, 7.0, str(cot.get("referencia", "")), border=1, align="L", new_x="LMARGIN", new_y="NEXT")

    # Fila 4: FECHA DE LA OFERTA
    y_f = pdf.get_y()
    x_f = pdf.get_x()
    pdf.set_font("Times", "B", 10)
    pdf.multi_cell(w_lbl, 5.0, "FECHA DE LA\nOFERTA:", border=1, align="L")
    h_f = pdf.get_y() - y_f
    pdf.set_xy(x_f + w_lbl, y_f)
    pdf.set_font("Times", "", 10)
    pdf.cell(w_val, h_f, str(cot.get("fecha", "")), border=1, align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # ---- 1. OBJETO ----
    pdf.section_bar("1.", "OBJETO")
    pdf.body_paragraph(cot.get("objeto", ""))

    if cot.get("exclusiones", "").strip():
        pdf.subheading_level2("1.1.", "EXCLUSIONES")
        pdf.body_paragraph(cot.get("exclusiones", ""))

    # ---- 2. DOCUMENTOS DE REFERENCIA ----
    pdf.section_bar("2.", "DOCUMENTOS DE REFERENCIA")
    if cot.get("documentosRefIntro", "").strip():
        pdf.body_paragraph(cot.get("documentosRefIntro", ""))
    pdf.bullet_list(cot.get("documentosRef", ""), marker="\xb7")

    # ---- 3. OFERTA TÉCNICA ----
    pdf.section_bar("3.", "OFERTA TÉCNICA")
    pdf.body_paragraph(cot.get("ofertaTecnica", ""))

    secciones_tec = cot.get("seccionesTecnicas", [])
    for idx_sec, sec in enumerate(secciones_tec, start=1):
        num_sec = f"3.{idx_sec}."
        pdf.subheading_level2(num_sec, sec.get("titulo", f"SERVICIO {idx_sec}"))
        pdf.body_paragraph(sec.get("descripcion", ""))

        if sec.get("insumosIntro", "").strip() or sec.get("insumos", "").strip():
            pdf.subheading_level3(f"3.{idx_sec}.1.", "INSUMOS DEL CLIENTE")
            if sec.get("insumosIntro", "").strip():
                pdf.body_paragraph(sec.get("insumosIntro", ""))
            if sec.get("insumos", "").strip():
                pdf.bullet_list(sec.get("insumos", ""), marker="-")

        if (
            sec.get("entregablesIntro", "").strip()
            or sec.get("entregablesLista", "").strip()
            or sec.get("entregablesCierre", "").strip()
        ):
            pdf.subheading_level3(f"3.{idx_sec}.2.", "ENTREGABLES")
            if sec.get("entregablesIntro", "").strip():
                pdf.body_paragraph(sec.get("entregablesIntro", ""))
            if sec.get("entregablesLista", "").strip():
                pdf.bullet_list(sec.get("entregablesLista", ""), marker="-")
            if sec.get("entregablesCierre", "").strip():
                pdf.ln(1.5)
                pdf.body_paragraph(sec.get("entregablesCierre", ""))

    # ---- 4. ORGANIZACIÓN ----
    pdf.section_bar("4.", "ORGANIZACIÓN")
    if cot.get("orgPersonal", "").strip() or cot.get("orgEquipos", "").strip() or cot.get("orgEticaLista", "").strip():
        pdf.subheading_level2("4.1.", "MEDIOS")
        if cot.get("orgPersonal", "").strip():
            pdf.subheading_level3("4.1.1.", "PERSONAL")
            pdf.body_paragraph(cot.get("orgPersonal", ""))
        if cot.get("orgEquiposIntro", "").strip() or cot.get("orgEquipos", "").strip():
            pdf.subheading_level3("4.1.2.", "EQUIPOS")
            if cot.get("orgEquiposIntro", "").strip():
                pdf.body_paragraph(cot.get("orgEquiposIntro", ""))
            if cot.get("orgEquipos", "").strip():
                pdf.bullet_list(cot.get("orgEquipos", ""), marker="-")
        if (
            cot.get("orgEticaIntro", "").strip()
            or cot.get("orgEticaLista", "").strip()
            or cot.get("orgEticaCierre", "").strip()
        ):
            pdf.subheading_level3("4.1.3.", "TRANSPARENCIA, ÉTICA Y CUMPLIMIENTO LEGAL.")
            if cot.get("orgEticaIntro", "").strip():
                pdf.body_paragraph(cot.get("orgEticaIntro", ""))
            if cot.get("orgEticaLista", "").strip():
                pdf.bullet_list(cot.get("orgEticaLista", ""), marker="-")
            if cot.get("orgEticaCierre", "").strip():
                pdf.body_paragraph(cot.get("orgEticaCierre", ""))
    elif cot.get("organizacion", "").strip():
        pdf.body_paragraph(cot.get("organizacion", ""))

    # ---- 5. OFERTA ECONÓMICA ----
    pdf.section_bar("5.", "OFERTA ECONÓMICA")
    intro_eco = cot.get(
        "ofertaEconomicaIntro",
        "A continuación, se presentarán por separado las tablas de costos para cada ítem ofertado, ya que cada ítem se manejará con una OC separada.",
    )
    pdf.body_paragraph(intro_eco)

    iva_pct = float(state["p"].get("iva", 0.19) or 0)
    rte_pct = float(state["p"].get("rte", 0.11) or 0)
    modo_tabla = cot.get("modoTablaOferta", "individual")

    all_rows_data = []
    for idx, item in enumerate(state.get("items", []), start=1):
        c = calc_item(item, state)
        cant = float(item.get("cantidad", 0) or 0)
        valor_u = c["venta"]
        sub_i = round(valor_u * cant)
        iva_i = round(sub_i * iva_pct)
        rte_i = round(sub_i * rte_pct)
        tot_i = sub_i + iva_i - rte_i
        row_dict = {
            "idx": idx,
            "nombre": str(item.get("nombre", "")),
            "cant": cant,
            "und": str(item.get("unidadEntrega", "GLB")),
            "tiempoTexto": str(item.get("tiempoTexto", "")),
            "valor_u": valor_u,
            "sub": sub_i,
            "iva": iva_i,
            "rte": rte_i,
            "tot": tot_i,
        }
        all_rows_data.append(row_dict)

    if modo_tabla == "consolidada" and all_rows_data:
        sub_total = sum(r["sub"] for r in all_rows_data)
        iva_total = round(sub_total * iva_pct)
        rte_total = round(sub_total * rte_pct)
        tot_total = sub_total + iva_total - rte_total
        _render_tabla_oferta_economica_a(
            pdf,
            rows_data=all_rows_data,
            sub=sub_total,
            iva_pct=iva_pct,
            iva=iva_total,
            rte_pct=rte_pct,
            rte=rte_total,
            tot=tot_total,
        )
    else:
        for r in all_rows_data:
            _render_tabla_oferta_economica_a(
                pdf,
                rows_data=[r],
                sub=r["sub"],
                iva_pct=iva_pct,
                iva=r["iva"],
                rte_pct=rte_pct,
                rte=r["rte"],
                tot=r["tot"],
            )

    if cot.get("notas", "").strip():
        pdf.ln(2)
        pdf.set_font("Times", "", 10.5)
        pdf.cell(CONTENT_W_MM, 5.5, "NOTAS:", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        pdf.bullet_list(cot.get("notas", ""), marker="\xb7")

    if cot.get("validez", "").strip():
        pdf.subheading_level2("5.1.", "VALIDEZ DE LA OFERTA")
        pdf.body_paragraph(cot.get("validez", ""))

    if cot.get("formaPago", "").strip():
        pdf.subheading_level2("5.2.", "FORMAS Y PROGRAMA DE PAGO")
        pdf.body_paragraph(cot.get("formaPago", ""))

    return bytes(pdf.output())


def _render_tabla_oferta_economica_b(
    pdf: CotizacionPDF,
    rows_b: list[dict],
    titulo_tabla: str,
    sub: float,
    iva_pct: float,
    iva: float,
    rte_pct: float,
    rte: float,
    mostrar_rete: bool = False,
):
    """
    Dibuja la tabla de Oferta Económica centrada dentro del cuadro de Formato B,
    idéntica a la captura de referencia (6 columnas: ITEM, ITEM DE PAGO, Cant, Und, Valor Unidad, Valor Total).
    """
    widths = [13.0, 53.0, 14.0, 14.0, 22.0, 22.0]  # Suma = 138 mm centrada en la hoja
    total_w = sum(widths)
    x_table = (PAGE_W_MM - total_w) / 2.0

    pdf.set_draw_color(30, 30, 30)
    pdf.set_line_width(0.25)

    # Fila 1: Título de la tabla (ej. OFERTA ECONÓMICA RUTA ACOMETIDA No.2)
    pdf.set_x(x_table)
    pdf.set_fill_color(*SEY_TABLE_HEAD)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.cell(
        total_w,
        4.5,
        (titulo_tabla or "OFERTA ECONÓMICA").upper(),
        border=1,
        align="C",
        fill=True,
        new_x="LMARGIN",
        new_y="NEXT",
    )

    # Fila 2: Encabezados de columna
    headers = ["ITEM", "ITEM DE PAGO", "Cant", "Und", "Valor Unidad", "Valor Total"]
    pdf.set_x(x_table)
    for w, h_txt in zip(widths, headers):
        pdf.cell(w, 6.2, h_txt, border=1, align="C", fill=True)
    pdf.ln()

    # Filas de ítems con soporte multilínea para ITEM DE PAGO
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_fill_color(255, 255, 255)
    for it in rows_b:
        lines_nom = _wrap_text_lines(pdf, it["nombre"], widths[1])
        line_h = 3.8
        row_h = max(7.2, len(lines_nom) * line_h + 1.6)
        y0 = pdf.get_y()

        cur_x = x_table
        for w in widths:
            pdf.rect(cur_x, y0, w, row_h)
            cur_x += w

        y_mid = y0 + (row_h - line_h) / 2.0
        pdf.set_xy(x_table, y_mid)
        pdf.cell(widths[0], line_h, str(it["idx"]), border=0, align="C")

        y_text_start = y0 + (row_h - len(lines_nom) * line_h) / 2.0
        for idx_l, ln_txt in enumerate(lines_nom):
            pdf.set_xy(x_table + widths[0] + 1.0, y_text_start + idx_l * line_h)
            pdf.cell(widths[1] - 2.0, line_h, ln_txt, border=0, align="L")

        x_c2 = x_table + widths[0] + widths[1]
        pdf.set_xy(x_c2, y_mid)
        pdf.cell(widths[2], line_h, f"{float(it['cantidad']):g}", border=0, align="C")
        pdf.set_xy(x_c2 + widths[2], y_mid)
        pdf.cell(widths[3], line_h, str(it["unidadEntrega"]), border=0, align="C")
        pdf.set_xy(x_c2 + widths[2] + widths[3], y_mid)
        pdf.cell(widths[4], line_h, fmt_cop(it["valorUnitario"]), border=0, align="R")
        pdf.set_xy(x_c2 + widths[2] + widths[3] + widths[4], y_mid)
        pdf.cell(widths[5], line_h, fmt_cop(it["valorTotal"]), border=0, align="R")

        pdf.set_xy(x_table, y0 + row_h)

    # Filas de Totales bajo 'Und + Valor Unidad' y 'Valor Total'
    left_empty_w = widths[0] + widths[1] + widths[2]
    label_box_w = widths[3] + widths[4]
    val_box_w = widths[5]

    # Fila 'Valor antes de IVA'
    pdf.set_x(x_table + left_empty_w)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.cell(label_box_w, 6.2, "Valor antes de IVA", border=1, align="C")
    pdf.set_font("Helvetica", "", 7.5)
    pdf.cell(val_box_w, 6.2, fmt_cop(sub), border=1, align="R", new_x="LMARGIN", new_y="NEXT")

    # Pequeña franja separadora como en la plantilla original
    pdf.set_x(x_table + left_empty_w)
    pdf.cell(label_box_w, 1.4, "", border=1)
    pdf.cell(val_box_w, 1.4, "", border=1, new_x="LMARGIN", new_y="NEXT")

    # Fila 'IVA'
    pdf.set_x(x_table + left_empty_w)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.cell(label_box_w, 4.6, f"IVA ({fmt_pct(iva_pct)})", border=1, align="C")
    pdf.set_font("Helvetica", "", 7.5)
    pdf.cell(val_box_w, 4.6, fmt_cop(iva), border=1, align="R", new_x="LMARGIN", new_y="NEXT")

    if mostrar_rete:
        pdf.set_x(x_table + left_empty_w)
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.cell(label_box_w, 4.6, f"RETEFUENTE ({fmt_pct(rte_pct)})", border=1, align="C")
        pdf.set_font("Helvetica", "", 7.5)
        pdf.cell(val_box_w, 4.6, fmt_cop(rte), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
        tot_final = sub + iva - rte
    else:
        tot_final = sub + iva

    # Fila 'Valor total de la oferta'
    pdf.set_x(x_table + left_empty_w)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.cell(label_box_w, 4.6, "Valor total de la oferta", border=1, align="C")
    pdf.set_font("Helvetica", "", 7.5)
    pdf.cell(val_box_w, 4.6, fmt_cop(tot_final), border=1, align="R", new_x="LMARGIN", new_y="NEXT")


def generar_pdf_formato_b(
    state: dict,
    logo_b64: str | None = None,
    header_bytes: bytes | None = None,
    footer_bytes: bytes | None = None,
) -> bytes:
    """
    Genera el PDF de Cotización Rápida de 1 Página (Formato B) replicando
    exactamente el cuadro con barra superior azul marino, encabezado con NIT,
    DATOS DE LA COTIZACIÓN, ALCANCE DE LA PROPUESTA, Observaciones, tabla centrada,
    COSTOS y CONDICIONES DE LA OFERTA.
    """
    cot = state["cot"]
    logo_bytes = safe_decode_logo(logo_b64)
    pdf = CotizacionPDF(cot, logo_bytes, header_bytes=header_bytes, footer_bytes=footer_bytes)
    pdf.alias_nb_pages()
    pdf.add_page()

    box_x = 15.0
    box_w = 180.0
    border_rgb = (95, 95, 95)
    pdf.set_draw_color(*border_rgb)
    pdf.set_line_width(0.25)
    pdf.set_text_color(*TEXT_DARK)
    pdf.set_font("Times", "", 10.5)

    # 1. Barra superior azul marino oscuro
    pdf.set_x(box_x)
    pdf.set_fill_color(5, 4, 122)
    pdf.cell(box_w, 6.5, "", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

    # 2. Cuadro de identificación centrado (Cotización, Fecha, Señores, NIT)
    y_hdr_start = pdf.get_y()
    pdf.ln(1.2)
    pdf.set_font("Times", "", 10.5)
    pdf.set_x(box_x)
    pdf.cell(box_w, 5.0, f"SEYEP SAS, Cotización {cot.get('referencia', '')}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(box_x)
    pdf.cell(box_w, 5.0, f"Fecha: {cot.get('fecha', '')}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(box_x)
    pdf.cell(box_w, 5.0, f"Señores: {cot.get('senores', '')}", align="C", new_x="LMARGIN", new_y="NEXT")
    if str(cot.get("nit", "")).strip():
        pdf.set_x(box_x)
        pdf.cell(box_w, 5.0, f"NIT: {cot.get('nit', '')}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.8)
    y_hdr_end = pdf.get_y()
    pdf.rect(box_x, y_hdr_start, box_w, y_hdr_end - y_hdr_start)

    # 3. Fila título: DATOS DE LA COTIZACIÓN
    pdf.set_xy(box_x, y_hdr_end)
    pdf.set_font("Times", "B", 10.5)
    pdf.cell(box_w, 5.6, "DATOS DE LA COTIZACIÓN", border=1, align="C", new_x="LMARGIN", new_y="NEXT")

    # 4. Fila: Nombre del trabajo: ...
    y_trab_start = pdf.get_y()
    pdf.set_xy(box_x + 2.0, y_trab_start + 0.8)
    lbl_trab = "Nombre del trabajo: "
    pdf.set_font("Times", "B", 10.5)
    lbl_w = pdf.get_string_width(_clean_latin1(lbl_trab)) + 1.0
    pdf.cell(lbl_w, 4.8, lbl_trab, border=0, align="L")
    pdf.set_font("Times", "", 10.5)
    pdf.multi_cell(box_w - lbl_w - 4.0, 4.8, str(cot.get("trabajo", "")), border=0, align="L")
    y_trab_end = max(y_trab_start + 6.0, pdf.get_y() + 0.8)
    pdf.rect(box_x, y_trab_start, box_w, y_trab_end - y_trab_start)
    pdf.set_y(y_trab_end)

    # 5. Fila título: ALCANCE DE LA PROPUESTA
    pdf.set_x(box_x)
    pdf.set_font("Times", "B", 10.5)
    pdf.cell(box_w, 5.6, "ALCANCE DE LA PROPUESTA", border=1, align="C", new_x="LMARGIN", new_y="NEXT")

    # 6. Contenido de ALCANCE DE LA PROPUESTA + Observaciones + Tabla(s) de Oferta Económica
    y_alc_start = pdf.get_y()
    pdf.ln(2.5)
    pdf.set_font("Times", "", 10.5)
    for raw_line in str(cot.get("alcanceRapido", "")).split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        pdf.set_x(box_x + 2.0)
        pdf.multi_cell(box_w - 4.0, 5.0, line, align="J")
        pdf.ln(1.0)

    obs_txt = str(cot.get("observacionesRapido", "")).strip()
    if obs_txt:
        pdf.ln(1.5)
        pdf.set_x(box_x + 2.0)
        pdf.set_font("Times", "B", 10.5)
        pdf.cell(box_w - 4.0, 5.2, "Observaciones:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Times", "", 10.5)
        for raw_obs in obs_txt.split("\n"):
            obs_line = raw_obs.strip().lstrip("-•").strip()
            if not obs_line:
                continue
            pdf.set_x(box_x + 8.0)
            pdf.cell(5.0, 5.0, "\xb7")
            pdf.multi_cell(box_w - 15.0, 5.0, obs_line, align="J")

    pdf.ln(3.0)

    resumen = calc_resumen_general(state)
    iva_pct = float(state["p"].get("iva", 0.19) or 0)
    rte_pct = float(state["p"].get("rte", 0.11) or 0)
    modo_tabla = cot.get("modoTablaOferta", "individual")
    titulo_tabla_b = cot.get("tituloTablaRapido", "OFERTA ECONÓMICA")
    mostrar_rete_b = bool(cot.get("mostrarReteRapido", False))

    if modo_tabla == "individual":
        for idx_t, it in enumerate(resumen["items"], start=1):
            sub_i = it["valorTotal"]
            iva_i = round(sub_i * iva_pct)
            rte_i = round(sub_i * rte_pct)
            tit_i = titulo_tabla_b if len(resumen["items"]) == 1 else f"{titulo_tabla_b} - ÍTEM {idx_t}"
            _render_tabla_oferta_economica_b(
                pdf,
                rows_b=[it],
                titulo_tabla=tit_i,
                sub=sub_i,
                iva_pct=iva_pct,
                iva=iva_i,
                rte_pct=rte_pct,
                rte=rte_i,
                mostrar_rete=mostrar_rete_b,
            )
            pdf.ln(1.5)
    else:
        _render_tabla_oferta_economica_b(
            pdf,
            rows_b=resumen["items"],
            titulo_tabla=titulo_tabla_b,
            sub=resumen["subtotal"],
            iva_pct=iva_pct,
            iva=resumen["iva"],
            rte_pct=rte_pct,
            rte=resumen["rte"],
            mostrar_rete=mostrar_rete_b,
        )

    y_alc_end = pdf.get_y() + 1.5
    pdf.set_draw_color(*border_rgb)
    pdf.rect(box_x, y_alc_start, box_w, y_alc_end - y_alc_start)
    pdf.set_y(y_alc_end)

    # 7. Fila título: COSTOS y fila inferior de COSTOS
    pdf.set_x(box_x)
    pdf.set_font("Times", "B", 10.5)
    pdf.cell(box_w, 5.6, "COSTOS", border=1, align="C", new_x="LMARGIN", new_y="NEXT")

    costos_nota = str(cot.get("costosNotaRapido", "")).strip()
    if costos_nota:
        y_cn_start = pdf.get_y()
        pdf.set_xy(box_x + 2.0, y_cn_start + 0.8)
        pdf.set_font("Times", "", 10.0)
        pdf.multi_cell(box_w - 4.0, 4.8, costos_nota, align="J")
        y_cn_end = max(y_cn_start + 5.6, pdf.get_y() + 0.8)
        pdf.rect(box_x, y_cn_start, box_w, y_cn_end - y_cn_start)
        pdf.set_y(y_cn_end)
    else:
        pdf.set_x(box_x)
        pdf.cell(box_w, 5.6, "", border=1, new_x="LMARGIN", new_y="NEXT")

    # 8. Fila título: CONDICIONES DE LA OFERTA
    pdf.set_x(box_x)
    pdf.set_font("Times", "B", 10.5)
    pdf.cell(box_w, 5.6, "CONDICIONES DE LA OFERTA", border=1, align="C", new_x="LMARGIN", new_y="NEXT")

    # 9. Lista numerada de CONDICIONES DE LA OFERTA
    y_cond_start = pdf.get_y()
    pdf.ln(0.8)
    cond_lines = [ln.strip() for ln in str(cot.get("condicionesRapido", "")).split("\n") if ln.strip()]
    for idx, line in enumerate(cond_lines, start=1):
        clean_cond = line.lstrip("0123456789.-) ").strip() or line
        pdf.set_x(box_x + 8.0)
        pdf.set_font("Times", "B", 10.5)
        pdf.cell(6.0, 5.0, f"{idx}.")
        pdf.set_font("Times", "", 10.5)
        pdf.multi_cell(box_w - 16.0, 5.0, clean_cond, align="J")
    y_cond_end = max(y_cond_start + 8.0, pdf.get_y() + 1.2)
    pdf.rect(box_x, y_cond_start, box_w, y_cond_end - y_cond_start)

    return bytes(pdf.output())
