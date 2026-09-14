#!/usr/bin/env python3
"""Genera una ficha PDF individual a partir de los datos e imágenes del catálogo web."""

from __future__ import annotations

import json
import re
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "content/catalog/details.json"
OUTPUT_DIR = ROOT / "output/pdf/fichas"
W, H = letter
INK = HexColor("#0B0D10")
RED = HexColor("#FA1418")
PAPER = HexColor("#F4F6F7")
MID = HexColor("#687078")
LINE = HexColor("#DCE1E4")


def slug(value: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value.lower()))


def paragraph(c, text, style, x, y_top, width, height):
    item = Paragraph(text, style)
    _, used = item.wrap(width, height)
    item.drawOn(c, x, y_top - used)
    return used


def image_reader(path: Path):
    source = ImageOps.exif_transpose(Image.open(path))
    source.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
    if source.mode not in ("RGB", "RGBA"):
        source = source.convert("RGBA" if "transparency" in source.info else "RGB")
    buffer = BytesIO()
    source.save(buffer, format="PNG" if source.mode == "RGBA" else "JPEG", quality=90, optimize=True)
    buffer.seek(0)
    reader = ImageReader(buffer)
    return reader, reader.getSize(), buffer


def draw_contain(c, path: Path, x, y, width, height, pad=18):
    c.setFillColor(white)
    c.roundRect(x, y, width, height, 14, fill=1, stroke=0)
    reader, (iw, ih), buffer = image_reader(path)
    scale = min((width - pad * 2) / iw, (height - pad * 2) / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(reader, x + (width - dw) / 2, y + (height - dh) / 2, dw, dh, mask="auto")
    return buffer


def product_path(value: str) -> Path:
    return ROOT / value.lstrip("/")


def choose_technical_image(product: dict) -> Path | None:
    paths = [product_path(item) for item in product.get("detailImages", [])]
    existing = [path for path in paths if path.exists()]
    if not existing:
        return None
    pngs = [path for path in existing if path.suffix.lower() == ".png"]
    return (pngs or existing)[-1]


def generate(code: str) -> Path:
    products = json.loads(DATA.read_text(encoding="utf-8"))
    product = next((item for item in products if item.get("code", "").lower() == code.lower()), None)
    if not product:
        raise SystemExit(f"Producto no encontrado: {code}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / f"{slug(product['code'])}.pdf"
    c = canvas.Canvas(str(output), pagesize=letter, pageCompression=1)
    c.setTitle(f"{product['code']} - {product['name']} | Herraidea")
    c.setAuthor("Herraidea / ProcesaLab")

    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(RED)
    c.rect(0, 0, 8, H, fill=1, stroke=0)

    logo = ROOT / "assets/logo-gray-nodot.png"
    logo_reader, (lw, lh), logo_buffer = image_reader(logo)
    logo_w = 178
    logo_h = logo_w * lh / lw
    c.drawImage(logo_reader, 38, H - 42 - logo_h, logo_w, logo_h, mask="auto")
    c.setFillColor(RED)
    c.circle(38 + logo_w * 0.625, H - 42 - logo_h + logo_h * 0.9, 2.6, fill=1, stroke=0)

    c.setFillColor(MID)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawRightString(W - 38, H - 49, "FICHA DE PRODUCTO 2026")
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(38, H - 112, product["code"].upper())
    title_style = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=31, leading=31, textColor=INK)
    paragraph(c, product["name"], title_style, 38, H - 132, W - 76, 72)

    image_y = 305
    image_h = 300
    gap = 12
    image_w = (W - 76 - gap) / 2
    primary = ROOT / "content/catalog" / product["image"]
    buffers = [logo_buffer, draw_contain(c, primary, 38, image_y, image_w, image_h)]

    technical = choose_technical_image(product)
    if technical:
        buffers.append(draw_contain(c, technical, 38 + image_w + gap, image_y, image_w, image_h, 12))
    else:
        c.setFillColor(white)
        c.roundRect(38 + image_w + gap, image_y, image_w, image_h, 14, fill=1, stroke=0)

    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(50, image_y + 15, "PRODUCTO")
    c.drawString(50 + image_w + gap, image_y + 15, "VISTA / PLANO TÉCNICO")

    c.setFillColor(white)
    c.roundRect(38, 92, W - 76, 190, 14, fill=1, stroke=0)
    c.setFillColor(RED)
    c.rect(38, 260, 72, 4, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(56, 234, product.get("description", "Información técnica"))

    specs = []
    for item in product.get("specifications", []):
        if item not in specs and "verificar" not in item.lower() and "acotaciones" not in item.lower():
            specs.append(item)
    y = 205
    for item in specs:
        c.setFillColor(RED)
        c.circle(59, y + 3, 3, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica", 10)
        c.drawString(72, y, item)
        y -= 25

    c.setStrokeColor(LINE)
    c.line(38, 68, W - 38, 68)
    c.setFillColor(MID)
    c.setFont("Helvetica", 7)
    c.drawString(38, 48, "Las acotaciones se expresan en milímetros. Verifica físicamente la pieza antes de instalar y perforar.")
    c.setFont("Helvetica-Bold", 7)
    c.drawString(38, 31, "WWW.HERRAIDEA.COM")
    c.drawCentredString(W / 2, 31, "Creado por ProcesaLab")
    c.drawRightString(W - 38, 31, "SIN PRECIOS")
    c.showPage()
    c.save()
    return output


if __name__ == "__main__":
    requested_code = " ".join(sys.argv[1:]).strip() or "HRD 1101"
    print(generate(requested_code))
