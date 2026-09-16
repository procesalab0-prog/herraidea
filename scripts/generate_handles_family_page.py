#!/usr/bin/env python3
"""Genera la página pública de la familia Jaladeras desde details.json."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "content/catalog/details.json"
OUTPUT = ROOT / "familias/jaladeras.html"
DOMAIN = "https://www.herraidea.com"


def slugify(value: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value.lower()))


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def group_for(code: str) -> str:
    normalized = code.upper()
    if "JH25" in normalized:
        return "diametro-25"
    if "JH32" in normalized:
        return "diametro-32"
    return ""


def render_card(product: dict) -> str:
    code = product["code"]
    searchable = f"{code} {product['name']} {product.get('description', '')}".lower()
    return f"""<a class="post-card" href="/productos/{slugify(code)}" data-group="{group_for(code)}" data-search="{escape(searchable)}">
      <figure><img src="/content/catalog/{escape(product['image'])}" alt="{escape(product['name'])} {escape(code)}" loading="lazy"></figure>
      <div><b>{escape(code)}</b><h3>{escape(product['name'])}</h3><p>{escape(product.get('description', ''))}</p><span>Ver ficha técnica →</span></div>
    </a>"""


def main() -> None:
    products = [item for item in json.loads(CATALOG.read_text(encoding="utf-8")) if item.get("category") == "Jaladeras"]
    cards = "\n".join(render_card(product) for product in products)
    schema = json.dumps(
        {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "CollectionPage",
                    "@id": f"{DOMAIN}/familias/jaladeras#collection",
                    "name": "Jaladeras para puertas de vidrio | Herraidea",
                    "description": "Jaladeras tipo H de acero inoxidable para puertas de vidrio templado en diámetros de 25 y 32 milímetros.",
                    "url": f"{DOMAIN}/familias/jaladeras",
                    "isPartOf": {"@id": f"{DOMAIN}/#website"},
                    "mainEntity": {
                        "@type": "ItemList",
                        "numberOfItems": len(products),
                        "itemListElement": [
                            {"@type": "ListItem", "position": index, "url": f"{DOMAIN}/productos/{slugify(product['code'])}", "name": f"{product['code']} — {product['name']}"}
                            for index, product in enumerate(products, 1)
                        ],
                    },
                },
                {
                    "@type": "BreadcrumbList",
                    "@id": f"{DOMAIN}/familias/jaladeras#breadcrumb",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{DOMAIN}/"},
                        {"@type": "ListItem", "position": 2, "name": "Jaladeras", "item": f"{DOMAIN}/familias/jaladeras"},
                    ],
                },
            ],
        },
        ensure_ascii=False,
    ).replace("</", r"<\/")
    whatsapp = quote("Hola Herraidea, necesito ayuda para elegir una jaladera para puerta de vidrio.")
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(
        f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="description" content="Jaladeras tipo H de acero inoxidable Herraidea para puertas de vidrio templado. Compara sus dos diámetros y consulta sus fichas técnicas.">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="theme-color" content="#ffffff">
  <link rel="canonical" href="{DOMAIN}/familias/jaladeras">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Herraidea">
  <meta property="og:title" content="Jaladeras para puertas de vidrio | Herraidea">
  <meta property="og:description" content="Compara jaladeras tipo H por diámetro y código HRD.">
  <meta property="og:url" content="{DOMAIN}/familias/jaladeras">
  <meta property="og:image" content="{DOMAIN}/content/catalog/images/jaladeras-hrd-jh25.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/assets/brand/apple-touch-icon.png">
  <title>Jaladeras para puertas de vidrio | Herraidea</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&family=Archivo+Narrow:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/family-page.css?v=1-34-0">
  <script type="application/ld+json">{schema}</script>
</head>
<body class="family-jaladeras">
  <header class="family-header">
    <a class="family-brand" href="/" aria-label="Herraidea, inicio"><img src="/assets/logo-gray-nodot.png" alt="Herraidea"><i aria-hidden="true"></i></a>
    <nav><a href="/sistemas">Sistemas</a><a href="/#calculadora">Calculadora</a><a href="/#catalogo">Catálogo</a><a class="header-contact" href="https://wa.me/524772561695?text={whatsapp}" target="_blank" rel="noopener">Cotizar</a></nav>
  </header>
  <main>
    <section class="family-hero">
      <div class="family-hero-copy"><span class="eyebrow">Familia 04 · {len(products)} modelos</span><h1>Jaladeras para<br><em>puertas de vidrio.</em></h1><p>Compara las dos jaladeras tipo H disponibles por diámetro de tubo. Abre cada modelo para revisar su fotografía, acabado y ficha PDF.</p><div class="hero-actions"><a class="primary-action" href="#modelos">Comparar modelos <span>↓</span></a><a class="secondary-action" href="/#asesoria">Necesito asesoría</a></div></div>
      <div class="family-hero-visual"><figure class="hero-main"><img src="/content/catalog/images/jaladeras-hrd-jh25.jpg" alt="Jaladera tipo H Herraidea HRD JH25"></figure><figure class="hero-detail"><img src="/content/catalog/images/jaladeras-hrd-jh32.jpg" alt="Jaladera tipo H Herraidea HRD JH32"></figure><div class="hero-index"><b>04</b><span>Jaladeras</span></div></div>
    </section>

    <section class="system-section" aria-labelledby="systems-title">
      <div class="section-heading"><span class="eyebrow">Elige por diámetro</span><h2 id="systems-title">Dos medidas,<br><em>un mismo lenguaje.</em></h2><p>Ambos modelos son jaladeras tipo H de calibre 18 para vidrio templado de 8 a 12 mm. Compara el diámetro y revisa las medidas finales del proyecto.</p></div>
      <div class="system-grid">
        <button class="system-card" type="button" data-family-filter="diametro-25"><figure><img src="/content/catalog/images/jaladeras-hrd-jh25.jpg" alt="Jaladera tipo H con tubo de 25 milímetros"></figure><span>01 · HRD JH25</span><h3>Tubo de 25 mm</h3><p>Jaladera de 1 pulgada disponible en acabado satín y negro mate.</p><b>Ver ficha →</b></button>
        <button class="system-card" type="button" data-family-filter="diametro-32"><figure><img src="/content/catalog/images/jaladeras-hrd-jh32.jpg" alt="Jaladera tipo H con tubo de 32 milímetros"></figure><span>02 · HRD JH32</span><h3>Tubo de 32 mm</h3><p>Jaladera de 1 1/4 pulgadas en acero inoxidable con acabado satín.</p><b>Ver ficha →</b></button>
      </div>
      <div class="system-links"><a href="/#catalogo">Ver catálogo completo <span>→</span></a><a href="/#asesoria">Revisar mi proyecto <span>→</span></a></div>
    </section>

    <section class="models-section" id="modelos">
      <div class="models-heading"><div><span class="eyebrow">Catálogo técnico</span><h2>Compara las jaladeras.</h2></div><p>Filtra por diámetro o escribe el código HRD. Cada resultado abre su ficha técnica independiente.</p></div>
      <div class="models-tools">
        <label class="family-search"><span>Buscar por código o nombre</span><input id="post-search" type="search" placeholder="Ej. JH25 o 32 mm" autocomplete="off"></label>
        <div class="family-filters" aria-label="Filtrar jaladeras">
          <button class="active" type="button" data-family-filter="all" aria-pressed="true">Todas</button><button type="button" data-family-filter="diametro-25" aria-pressed="false">25 mm</button><button type="button" data-family-filter="diametro-32" aria-pressed="false">32 mm</button>
        </div>
        <p class="result-status" aria-live="polite"><strong id="post-result-count">{len(products)}</strong> modelos</p>
      </div>
      <div class="posts-grid" id="posts-grid">{cards}</div>
      <div class="no-results" id="post-no-results" hidden><b>No encontramos esa jaladera.</b><p>Prueba otro código o solicita ayuda para identificar la pieza.</p></div>
    </section>

    <section class="family-cta"><div><span class="eyebrow">Fabricación a la medida</span><h2>¿Tu proyecto necesita otra configuración?</h2><p>Comparte medidas, fotografías, dibujos o una muestra. Herraidea puede revisar contigo el sistema y desarrollar piezas especiales.</p></div><a class="primary-action" href="https://wa.me/524772561695?text={whatsapp}" target="_blank" rel="noopener">Hablar con un asesor <span>→</span></a></section>
  </main>
  <footer><a class="family-footer-brand" href="/"><img src="/assets/logo-light-nodot.png" alt="Herraidea"><i aria-hidden="true"></i></a><nav><a href="/#catalogo">Catálogo completo</a><a href="/#recursos">Recursos</a><a href="/#contacto">Contacto</a></nav><small>Creado por ProcesaLab</small></footer>
  <script src="/family-page.js?v=1-34-0"></script>
</body>
</html>
""",
        encoding="utf-8",
    )
    print(f"Generada página de Jaladeras con {len(products)} modelos")


if __name__ == "__main__":
    main()
