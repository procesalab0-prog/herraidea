#!/usr/bin/env python3
"""Genera la página pública de la familia Pipetas desde details.json."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "content/catalog/details.json"
OUTPUT = ROOT / "familias/pipetas.html"
DOMAIN = "https://www.herraidea.com"


def slugify(value: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value.lower()))


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def group_for(code: str) -> str:
    normalized = code.upper()
    groups = []
    if re.search(r"HRD 110[1-4]|HRD 111[0-4]", normalized):
        groups.append("muro")
    if re.search(r"HRD 110[5-8]", normalized):
        groups.append("vidrio")
    if re.search(r"HRD 110[78]", normalized):
        groups.append("dobles")
    if re.search(r"HRD 111[0-4]", normalized):
        groups.append("ajustables")
    if re.search(r"HRD 1101|HRD 1105|HRD 1107", normalized):
        groups.append("chapeton")
    if re.search(r"HRD 1102|HRD 1104|HRD 1106|HRD 1108|HRD 1112", normalized):
        groups.append("avellanado")
    if "HRD 1103" in normalized:
        groups.append("allen")
    return " ".join(groups)


def render_card(product: dict) -> str:
    code = product["code"]
    searchable = f"{code} {product['name']} {product.get('description', '')}".lower()
    return f"""<a class="post-card" href="/productos/{slugify(code)}" data-group="{group_for(code)}" data-search="{escape(searchable)}">
      <figure><img src="/content/catalog/{escape(product['image'])}" alt="{escape(product['name'])} {escape(code)}" loading="lazy"></figure>
      <div><b>{escape(code)}</b><h3>{escape(product['name'])}</h3><p>{escape(product.get('description', ''))}</p><span>Ver ficha técnica →</span></div>
    </a>"""


def main() -> None:
    products = [item for item in json.loads(CATALOG.read_text(encoding="utf-8")) if item.get("category") == "Pipetas"]
    cards = "\n".join(render_card(product) for product in products)
    schema = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Pipetas para vidrio | Herraidea",
            "description": "Pipetas de acero inoxidable para conectar vidrio con muro o vidrio con vidrio en configuraciones fijas y ajustables.",
            "url": f"{DOMAIN}/familias/pipetas",
            "mainEntity": {
                "@type": "ItemList",
                "numberOfItems": len(products),
                "itemListElement": [
                    {"@type": "ListItem", "position": index, "url": f"{DOMAIN}/productos/{slugify(product['code'])}", "name": f"{product['code']} — {product['name']}"}
                    for index, product in enumerate(products, 1)
                ],
            },
        },
        ensure_ascii=False,
    ).replace("</", "<\/")
    whatsapp = quote("Hola Herraidea, necesito ayuda para elegir pipetas para un proyecto con vidrio.")
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(
        f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="description" content="Pipetas de acero inoxidable Herraidea para conectar vidrio con muro o vidrio con vidrio. Consulta {len(products)} modelos y sus fichas técnicas.">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="theme-color" content="#ffffff">
  <link rel="canonical" href="{DOMAIN}/familias/pipetas">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Herraidea">
  <meta property="og:title" content="Pipetas para vidrio | Herraidea">
  <meta property="og:description" content="Explora pipetas por montaje, ajuste y código HRD.">
  <meta property="og:url" content="{DOMAIN}/familias/pipetas">
  <meta property="og:image" content="{DOMAIN}/content/catalog/images/pipetas-hrd-1101.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/assets/brand/apple-touch-icon.png">
  <title>Pipetas para vidrio | Herraidea</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&family=Archivo+Narrow:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/family-page.css?v=1-33-0">
  <script type="application/ld+json">{schema}</script>
</head>
<body class="family-pipetas">
  <header class="family-header">
    <a class="family-brand" href="/" aria-label="Herraidea, inicio"><img src="/assets/logo-gray-nodot.png" alt="Herraidea"><i aria-hidden="true"></i></a>
    <nav><a href="/#proyectos">Soluciones 3D</a><a href="/#calculadora">Calculadora</a><a href="/#catalogo">Catálogo</a><a class="header-contact" href="https://wa.me/524772561695?text={whatsapp}" target="_blank" rel="noopener">Cotizar</a></nav>
  </header>
  <main>
    <section class="family-hero">
      <div class="family-hero-copy"><span class="eyebrow">Familia 01 · {len(products)} modelos</span><h1>Pipetas para<br><em>vidrio.</em></h1><p>Explora conectores de acero inoxidable por tipo de montaje, cabeza y ajuste. Abre cada modelo para revisar su fotografía, medidas y ficha PDF.</p><div class="hero-actions"><a class="primary-action" href="#modelos">Explorar modelos <span>↓</span></a><a class="secondary-action" href="/#asesoria">Necesito asesoría</a></div></div>
      <div class="family-hero-visual"><figure class="hero-main"><img src="/content/catalog/images/pipetas-hrd-1101.jpg" alt="Pipeta Herraidea HRD 1101 tipo chapetón"></figure><figure class="hero-detail"><img src="/content/catalog/images/pipetas-hrd-1113.jpg" alt="Pipeta ajustable Herraidea HRD 1113"></figure><div class="hero-index"><b>01</b><span>Pipetas</span></div></div>
    </section>

    <section class="system-section" aria-labelledby="systems-title">
      <div class="section-heading"><span class="eyebrow">Elige un punto de partida</span><h2 id="systems-title">Cuatro funciones,<br><em>una familia.</em></h2><p>Empieza por el tipo de unión o por el ajuste que necesita tu proyecto. La selección final debe revisarse según el vidrio, las perforaciones y el montaje.</p></div>
      <div class="system-grid">
        <button class="system-card" type="button" data-family-filter="muro"><figure><img src="/content/catalog/images/pipetas-hrd-1101.jpg" alt="Pipeta para conectar vidrio con muro"></figure><span>01</span><h3>Vidrio a muro</h3><p>Conectores para fijar vidrio templado a una superficie de soporte.</p><b>Ver modelos →</b></button>
        <button class="system-card" type="button" data-family-filter="vidrio"><figure><img src="/content/catalog/images/pipetas-hrd-1105.jpg" alt="Pipeta para conectar vidrio con vidrio"></figure><span>02</span><h3>Vidrio a vidrio</h3><p>Uniones a 90 grados y configuraciones dobles entre paneles de vidrio.</p><b>Ver modelos →</b></button>
        <button class="system-card" type="button" data-family-filter="dobles"><figure><img src="/content/catalog/images/pipetas-hrd-1107.jpg" alt="Pipeta de doble sujeción"></figure><span>03</span><h3>Doble sujeción</h3><p>Pipetas con dos puntos de fijación para unir paneles de vidrio.</p><b>Ver modelos →</b></button>
        <button class="system-card" type="button" data-family-filter="ajustables"><figure><img src="/content/catalog/images/pipetas-hrd-1113.jpg" alt="Pipeta ajustable en altura y profundidad"></figure><span>04</span><h3>Ajustables</h3><p>Opciones con ajuste en altura, profundidad o mediante conexión roscada.</p><b>Ver modelos →</b></button>
      </div>
      <div class="system-links"><a href="/#catalogo">Ver catálogo completo <span>→</span></a><a href="/#asesoria">Revisar mi proyecto <span>→</span></a></div>
    </section>

    <section class="models-section" id="modelos">
      <div class="models-heading"><div><span class="eyebrow">Catálogo técnico</span><h2>Encuentra tu pipeta.</h2></div><p>Filtra por montaje, ajuste o tipo de cabeza; también puedes escribir un código HRD. Cada resultado abre su ficha técnica.</p></div>
      <div class="models-tools">
        <label class="family-search"><span>Buscar por código o nombre</span><input id="post-search" type="search" placeholder="Ej. HRD 1105 o ajustable" autocomplete="off"></label>
        <div class="family-filters" aria-label="Filtrar pipetas">
          <button class="active" type="button" data-family-filter="all" aria-pressed="true">Todas</button><button type="button" data-family-filter="muro" aria-pressed="false">Vidrio a muro</button><button type="button" data-family-filter="vidrio" aria-pressed="false">Vidrio a vidrio</button><button type="button" data-family-filter="dobles" aria-pressed="false">Dobles</button><button type="button" data-family-filter="ajustables" aria-pressed="false">Ajustables</button><button type="button" data-family-filter="chapeton" aria-pressed="false">Chapetón</button><button type="button" data-family-filter="avellanado" aria-pressed="false">Avellanado</button><button type="button" data-family-filter="allen" aria-pressed="false">Allen</button>
        </div>
        <p class="result-status" aria-live="polite"><strong id="post-result-count">{len(products)}</strong> modelos</p>
      </div>
      <div class="posts-grid" id="posts-grid">{cards}</div>
      <div class="no-results" id="post-no-results" hidden><b>No encontramos esa pipeta.</b><p>Prueba otro código o solicita ayuda para identificar la pieza.</p></div>
    </section>

    <section class="family-cta"><div><span class="eyebrow">Fabricación a la medida</span><h2>¿Tu proyecto necesita otra configuración?</h2><p>Comparte medidas, fotografías, dibujos o una muestra. Herraidea puede revisar contigo el sistema y desarrollar piezas especiales.</p></div><a class="primary-action" href="https://wa.me/524772561695?text={whatsapp}" target="_blank" rel="noopener">Hablar con un asesor <span>→</span></a></section>
  </main>
  <footer><a class="family-footer-brand" href="/"><img src="/assets/logo-light-nodot.png" alt="Herraidea"><i aria-hidden="true"></i></a><nav><a href="/#catalogo">Catálogo completo</a><a href="/#recursos">Recursos</a><a href="/#contacto">Contacto</a></nav><small>Creado por ProcesaLab</small></footer>
  <script src="/family-page.js?v=1-33-0"></script>
</body>
</html>
""",
        encoding="utf-8",
    )
    print(f"Generada página de Pipetas con {len(products)} modelos")


if __name__ == "__main__":
    main()
