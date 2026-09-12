#!/usr/bin/env python3
"""Genera el adelanto editorial del catálogo Herraidea 2026."""

from __future__ import annotations

import json
import math
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps
from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/pdf/catalogo-herraidea-2026-adelanto.pdf"
DATA = ROOT / "content/catalog/details.json"

W, H = letter
INK = HexColor("#0B0D10")
RED = HexColor("#FA1418")
PAPER = HexColor("#F5F6F7")
MID = HexColor("#687078")
LINE = HexColor("#DDE1E4")
SOFT = HexColor("#E9ECEE")

MARGIN = 42
CONTENT_W = W - MARGIN * 2
IMAGE_CACHE = {}


def pstyle(name, size, leading=None, color=INK, font="Helvetica", **kwargs):
    return ParagraphStyle(
        name,
        fontName=font,
        fontSize=size,
        leading=leading or size * 1.18,
        textColor=color,
        alignment=TA_LEFT,
        spaceAfter=0,
        **kwargs,
    )


BODY = pstyle("body", 9.2, 13.5, MID)
SMALL = pstyle("small", 7.2, 10, MID)
CARD_NAME = pstyle("card-name", 11, 12.5, INK, "Helvetica-Bold")
CARD_DESC = pstyle("card-desc", 7.6, 10.2, MID)


def draw_paragraph(c, text, style, x, y_top, width, height):
    paragraph = Paragraph(text, style)
    _, used_h = paragraph.wrap(width, height)
    paragraph.drawOn(c, x, y_top - used_h)
    return used_h


def image_size(path):
    key = str(path)
    if key not in IMAGE_CACHE:
        source = ImageOps.exif_transpose(Image.open(path))
        source.thumbnail((1100, 1100), Image.Resampling.LANCZOS)
        has_alpha = source.mode in ("RGBA", "LA") or "transparency" in source.info
        if has_alpha:
            source = source.convert("RGBA")
        elif source.mode != "RGB":
            source = source.convert("RGB")
        buffer = BytesIO()
        if has_alpha:
            source.save(buffer, format="PNG", optimize=True)
        else:
            source.save(buffer, format="JPEG", quality=82, optimize=True)
        buffer.seek(0)
        reader = ImageReader(buffer)
        IMAGE_CACHE[key] = (reader, reader.getSize(), buffer)
    reader, size, _ = IMAGE_CACHE[key]
    return reader, size


def draw_image_cover(c, path, x, y, width, height, opacity=1.0, align_x=0.5, align_y=0.5):
    if not Path(path).exists():
        c.setFillColor(SOFT)
        c.rect(x, y, width, height, fill=1, stroke=0)
        return
    img, (iw, ih) = image_size(path)
    scale = max(width / iw, height / ih)
    dw, dh = iw * scale, ih * scale
    dx = x - (dw - width) * align_x
    dy = y - (dh - height) * align_y
    c.saveState()
    clip = c.beginPath()
    clip.rect(x, y, width, height)
    c.clipPath(clip, stroke=0, fill=0)
    if opacity < 1:
        c.setFillAlpha(opacity)
    c.drawImage(img, dx, dy, dw, dh, preserveAspectRatio=True, mask="auto")
    c.restoreState()


def draw_image_contain(c, path, x, y, width, height, pad=6):
    c.setFillColor(white)
    c.rect(x, y, width, height, fill=1, stroke=0)
    if not Path(path).exists():
        c.setFillColor(SOFT)
        c.rect(x + pad, y + pad, width - 2 * pad, height - 2 * pad, fill=1, stroke=0)
        return
    img, (iw, ih) = image_size(path)
    scale = min((width - 2 * pad) / iw, (height - 2 * pad) / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(
        img,
        x + (width - dw) / 2,
        y + (height - dh) / 2,
        dw,
        dh,
        preserveAspectRatio=True,
        mask="auto",
    )


def draw_brand(c, light=False, width=150):
    logo = ROOT / ("assets/logo-light-nodot.png" if light else "assets/logo-gray-nodot.png")
    img, (iw, ih) = image_size(logo)
    height = width * ih / iw
    y = H - MARGIN - height
    c.drawImage(img, MARGIN, y, width, height, mask="auto")
    c.setFillColor(RED)
    c.roundRect(MARGIN + width * 0.61, y + height * 0.785, width * 0.031, height * 0.208, 1.4, fill=1, stroke=0)


def red_edge(c, width=7):
    c.setFillColor(RED)
    c.rect(0, 0, width, H, fill=1, stroke=0)


def footer(c, page_num, dark=False):
    color = Color(1, 1, 1, alpha=0.58) if dark else MID
    c.setFillColor(color)
    c.setFont("Helvetica", 6.5)
    c.drawString(MARGIN, 22, "HERRAIDEA · ADELANTO DE CATÁLOGO · 2026")
    c.drawCentredString(W / 2, 22, "Creado por ProcesaLab")
    c.drawRightString(W - MARGIN, 22, f"{page_num:02d}")


def eyebrow(c, text, x, y, color=RED):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 7.4)
    c.drawString(x, y, text.upper())


def title(c, lines, x, y, size=42, color=INK, leading=None):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", size)
    leading = leading or size * 0.9
    current = y
    for line in lines:
        c.drawString(x, current, line)
        current -= leading
    return current


def cover(c):
    image = ROOT / "assets/hero-barandal-v2-night.png"
    draw_image_cover(c, image, 0, 0, W, H, align_x=0.52)
    c.setFillColor(Color(0.02, 0.025, 0.03, alpha=0.56))
    c.rect(0, 0, W, H, fill=1, stroke=0)
    red_edge(c, 9)
    draw_brand(c, light=True, width=242)
    eyebrow(c, "Catálogo de soluciones y productos", MARGIN, H * 0.57, white)
    title(c, ["Tu proyecto", "no termina en", "el catálogo."], MARGIN, H * 0.49, 43, white, 39)
    c.setFillColor(RED)
    c.rect(MARGIN, H * 0.285, 128, 7, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica", 12)
    c.drawString(MARGIN, H * 0.245, "Sistemas completos · Fabricación a la medida · Herrajes")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, 54, "ADELANTO DE CATÁLOGO · 2026")


def contents_page(c, page_num, counts):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    red_edge(c, 7)
    draw_brand(c, width=150)
    eyebrow(c, "Nueva estructura", MARGIN, H - 140)
    title(c, ["Soluciones", "primero.", "Productos después."], MARGIN, H - 180, 42, INK, 38)
    draw_paragraph(
        c,
        "Este adelanto 2026 reúne el contenido disponible en la web y presenta a Herraidea como una empresa que diseña y fabrica soluciones completas.",
        pstyle("intro", 11, 16.5, MID),
        MARGIN,
        H - 315,
        300,
        110,
    )
    sections = [
        ("01", "Diseño y fabricación", "Capacidades y fabricación a la medida"),
        ("02", "Sistemas completos", "HRD 1525, HRD 1518 y Futbolito Herraidea"),
        ("03", "Familias de producto", "Pipetas, postes, conectores y jaladeras"),
        ("04", "Contacto y cobertura", "León, Guanajuato · atención a proyectos"),
    ]
    y = 360
    for num, name, desc in sections:
        c.setStrokeColor(LINE)
        c.line(MARGIN, y + 40, W - MARGIN, y + 40)
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN, y + 15, num)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(MARGIN + 45, y + 10, name)
        c.setFillColor(MID)
        c.setFont("Helvetica", 8.5)
        c.drawRightString(W - MARGIN, y + 11, desc)
        y -= 66
    c.setFillColor(INK)
    c.roundRect(MARGIN, 72, CONTENT_W, 64, 0, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(MARGIN + 20, 105, f"{sum(counts.values())} productos y configuraciones")
    c.setFont("Helvetica", 7)
    c.drawString(MARGIN + 20, 86, "SOLUCIONES COMPLETAS · FAMILIAS · FABRICACIÓN A LA MEDIDA")
    footer(c, page_num)


def capabilities_page(c, page_num):
    c.setFillColor(white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    red_edge(c, 7)
    draw_image_cover(c, ROOT / "assets/fabricacion/torno-cnc-haas.jpg", 0, 0, W * 0.5, H, align_x=0.55)
    x = W * 0.5 + 34
    eyebrow(c, "Diseño y fabricación", x, H - 76)
    title(c, ["Del plano", "a la pieza."], x, H - 122, 36, INK, 34)
    draw_paragraph(c, "Una medida especial, un dibujo, una muestra o una necesidad concreta pueden ser el inicio de una solución.", pstyle("cap", 11, 16, MID), x, H - 220, W * 0.5 - 68, 90)
    items = ["4 equipos CNC Haas VF-3SS", "Maquinado de precisión", "Soldadura robotizada", "Corte láser", "Pulido de redondos y planos", "Acero inoxidable T-304 y T-316*"]
    y = H - 330
    for item in items:
        c.setFillColor(RED)
        c.circle(x + 3, y + 3, 3, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 16, y, item)
        y -= 34
    c.setFillColor(MID)
    c.setFont("Helvetica", 6.8)
    c.drawString(x, 54, "* Material y aplicación sujetos a confirmación por producto y proceso.")
    footer(c, page_num)


def solution_page(c, page_num, solution):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    red_edge(c, 7)
    image_h = H * 0.61
    draw_image_cover(c, ROOT / solution["image"], 0, H - image_h, W, image_h, align_x=solution.get("align_x", 0.5), align_y=solution.get("align_y", 0.5))
    c.setFillColor(Color(0, 0, 0, alpha=0.14))
    c.rect(0, H - image_h, W, image_h, fill=1, stroke=0)
    c.setFillColor(RED)
    c.rect(MARGIN, H - image_h - 5, 86, 5, fill=1, stroke=0)
    eyebrow(c, solution["kicker"], MARGIN, H - image_h - 46)
    title(c, solution["title"], MARGIN, H - image_h - 82, 35, INK, 32)
    draw_paragraph(c, solution["description"], BODY, W * 0.55, H - image_h - 47, W * 0.36, 100)
    c.setStrokeColor(LINE)
    c.line(MARGIN, 70, W - MARGIN, 70)
    c.setFillColor(MID)
    c.setFont("Helvetica-Bold", 7.2)
    c.drawString(MARGIN, 52, "SOLUCIÓN COMPLETA · EXPLORACIÓN 3D DISPONIBLE EN LA WEB")
    c.setFillColor(Color(0.98, 0.08, 0.09, alpha=0.08))
    c.setFont("Helvetica-Bold", 92)
    c.drawRightString(W - MARGIN, 88, solution["number"])
    footer(c, page_num)


def family_cover(c, page_num, index, category, count):
    dark = index % 2 == 0
    bg = INK if dark else PAPER
    fg = white if dark else INK
    c.setFillColor(bg)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    red_edge(c, 11)
    c.setFillColor(RED)
    c.rect(MARGIN, H - 116, 54, 6, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 150)
    c.setFillColor(Color(1, 1, 1, alpha=0.045) if dark else Color(0.05, 0.06, 0.07, alpha=0.04))
    c.drawRightString(W - 22, H * 0.29, f"{index:02d}")
    eyebrow(c, f"Familia {index:02d}", MARGIN, H - 156, RED)
    title(c, [category + "."], MARGIN, H - 220, 66, fg, 58)
    c.setFillColor(fg)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(MARGIN, 155, f"{count} modelos")
    c.setFillColor(Color(1, 1, 1, alpha=0.58) if dark else MID)
    c.setFont("Helvetica", 9)
    descriptions = {
        "Pipetas": "Conexiones para resolver encuentros entre vidrio, muro y tubo.",
        "Postes": "Configuraciones para barandales, pasamanos y sistemas completos.",
        "Conectores": "Herrajes de unión, soporte y fijación para diferentes aplicaciones.",
        "Jaladeras": "Soluciones de acceso fabricadas en acero inoxidable.",
    }
    c.drawString(MARGIN, 127, descriptions[category])
    footer(c, page_num, dark)


def clean_specs(specs):
    result = []
    for spec in specs or []:
        low = spec.lower()
        if "verificar" in low or "acotaciones" in low:
            continue
        if spec not in result:
            result.append(spec)
    return result[:3]


def product_card(c, product, x, y, width, height):
    c.setFillColor(white)
    c.setStrokeColor(LINE)
    c.rect(x, y, width, height, fill=1, stroke=1)
    image_h = height * 0.52
    image = ROOT / "content/catalog" / product["image"]
    draw_image_contain(c, image, x + 1, y + height - image_h - 1, width - 2, image_h, 8)
    c.setStrokeColor(LINE)
    c.line(x, y + height - image_h, x + width, y + height - image_h)
    tx = x + 12
    top = y + height - image_h - 15
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 7.4)
    c.drawString(tx, top, product.get("code", "SIN CÓDIGO").upper())
    used = draw_paragraph(c, product.get("name", "Producto"), CARD_NAME, tx, top - 11, width - 24, 42)
    desc_top = top - 17 - used
    draw_paragraph(c, product.get("description", ""), CARD_DESC, tx, desc_top, width - 24, 28)
    specs = clean_specs(product.get("specifications"))
    sy = y + 14 + (len(specs) - 1) * 11
    c.setFont("Helvetica", 6.5)
    for spec in specs:
        c.setFillColor(RED)
        c.circle(tx + 2, sy + 2, 1.5, fill=1, stroke=0)
        c.setFillColor(MID)
        label = spec if len(spec) <= 38 else spec[:35] + "..."
        c.drawString(tx + 8, sy, label)
        sy -= 11


def product_pages(c, page_num, category, products):
    per_page = 6
    cols, rows = 2, 3
    gap_x, gap_y = 12, 12
    header_h = 82
    card_w = (CONTENT_W - gap_x) / cols
    card_h = (H - 44 - header_h - MARGIN - gap_y * (rows - 1)) / rows
    total_pages = math.ceil(len(products) / per_page)
    for local_page in range(total_pages):
        c.setFillColor(PAPER)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        red_edge(c, 5)
        eyebrow(c, "Catálogo de productos", MARGIN, H - 50)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 21)
        c.drawString(MARGIN, H - 78, category)
        c.setFillColor(MID)
        c.setFont("Helvetica", 7.4)
        c.drawRightString(W - MARGIN, H - 72, f"{local_page + 1:02d} / {total_pages:02d}")
        subset = products[local_page * per_page : (local_page + 1) * per_page]
        for i, product in enumerate(subset):
            row, col = divmod(i, cols)
            x = MARGIN + col * (card_w + gap_x)
            y = H - header_h - (row + 1) * card_h - row * gap_y
            product_card(c, product, x, y, card_w, card_h)
        footer(c, page_num)
        page_num += 1
        c.showPage()
    return page_num


def closing_page(c, page_num):
    c.setFillColor(INK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    red_edge(c, 9)
    draw_brand(c, light=True, width=230)
    eyebrow(c, "Cuéntanos qué necesitas", MARGIN, H - 190, RED)
    title(c, ["¿Tienes una medida,", "una muestra o", "un proyecto especial?"], MARGIN, H - 240, 41, white, 38)
    draw_paragraph(c, "Diseñamos y fabricamos barandales, herrajes y soluciones de acero inoxidable según las necesidades de cada proyecto.", pstyle("close", 11, 16, Color(1, 1, 1, alpha=0.68)), MARGIN, H - 370, 340, 100)
    c.setFillColor(RED)
    c.rect(MARGIN, 178, CONTENT_W, 2, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(MARGIN, 142, "León, Guanajuato")
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN, 118, "Oficina: +52 (477) 790 7594")
    c.drawString(MARGIN, 99, "WhatsApp: 477 256 1695")
    c.drawRightString(W - MARGIN, 118, "www.herraidea.com")
    c.drawRightString(W - MARGIN, 99, "México · Guatemala · Honduras · Sur de EE. UU.")
    footer(c, page_num, dark=True)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    products = json.loads(DATA.read_text(encoding="utf-8"))
    categories = ["Pipetas", "Postes", "Conectores", "Jaladeras"]
    grouped = {category: [p for p in products if p.get("category") == category] for category in categories}

    c = canvas.Canvas(str(OUTPUT), pagesize=letter, pageCompression=1)
    c.setTitle("Catálogo Herraidea 2026 - Adelanto")
    c.setAuthor("Herraidea · ProcesaLab")
    c.setSubject("Sistemas completos, fabricación a la medida y catálogo de productos")
    page = 1

    cover(c)
    c.showPage()
    page += 1
    contents_page(c, page, {k: len(v) for k, v in grouped.items()})
    c.showPage()
    page += 1
    capabilities_page(c, page)
    c.showPage()
    page += 1

    solutions = [
        {
            "number": "01",
            "kicker": "01 · HRD 1525 · Solución de barandal",
            "title": ["Postes con clips", "+ vidrio."],
            "description": "Postes, pinzas laterales, cristal, pasamanos y fijaciones trabajando como un sistema completo. La selección final depende de medidas, tipo de vidrio y condiciones de instalación.",
            "image": "assets/projects/clip-system/portada-estudio.jpg",
            "align_x": 0.58,
        },
        {
            "number": "02",
            "kicker": "02 · HRD 1518 · Sistema de tubo de 1/2 pulgada",
            "title": ["Poste HRD 1518.", "Un sistema completo."],
            "description": "Poste de acero inoxidable, pasamanos y tres barras reunidos en una solución que puede revisarse y explorarse pieza por pieza.",
            "image": "assets/projects/hrd-1518/portada-estudio.png",
        },
        {
            "number": "03",
            "kicker": "03 · Proyecto especial",
            "title": ["Futbolito", "Herraidea."],
            "description": "Un proyecto especial de cristal y acero inoxidable que demuestra la capacidad para desarrollar soluciones fuera del catálogo tradicional. El modelo interactivo contiene 190 piezas y conjuntos.",
            "image": "assets/projects/futbolito/portada-estudio.png",
        },
    ]
    for solution in solutions:
        solution_page(c, page, solution)
        c.showPage()
        page += 1

    for index, category in enumerate(categories, start=1):
        family_cover(c, page, index, category, len(grouped[category]))
        c.showPage()
        page += 1
        page = product_pages(c, page, category, grouped[category])

    closing_page(c, page)
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
