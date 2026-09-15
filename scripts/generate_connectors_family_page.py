#!/usr/bin/env python3
"""Genera la página pública de la familia Conectores desde details.json."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "content/catalog/details.json"
OUTPUT = ROOT / "familias/conectores.html"
DOMAIN = "https://www.herraidea.com"


def slugify(value: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value.lower()))


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def group_for(code: str) -> str:
    normalized = code.upper()
    groups = []
    if re.search(r"HRD 13(0[2-9]|1[0-3])|HRD 2020", normalized):
        groups.append("muro")
    if "HRD 1301" in normalized:
        groups.append("vidrio")
    if re.search(r"HRD 14(0[1-9]|1[0178])", normalized):
        groups.append("tubo")
    if re.search(r"HRD 1401|HRD 1410|HRD 1411|HRD 1418", normalized):
        groups.append("pasamanos")
    if re.search(r"HRD 1407|HRD 1408", normalized):
        groups.append("velas")
    if re.search(r"HRD 1402|HRD 1403|HRD 1409", normalized):
        groups.append("tapas")
    if re.search(r"HRD 1501|HRD 1502|HRD 2020", normalized):
        groups.append("puerta")
    if re.search(r"HRD 1410|HRD 1411|HRD 1418", normalized):
        groups.append("ajustables")
    return " ".join(groups)


def render_card(product: dict) -> str:
    code = product["code"]
    searchable = f"{code} {product['name']} {product.get('description', '')}".lower()
    return f"""<a class="post-card" href="/productos/{slugify(code)}" data-group="{group_for(code)}" data-search="{escape(searchable)}">
      <figure><img src="/content/catalog/{escape(product['image'])}" alt="{escape(product['name'])} {escape(code)}" loading="lazy"></figure>
      <div><b>{escape(code)}</b><h3>{escape(product['name'])}</h3><p>{escape(product.get('description', ''))}</p><span>Ver ficha técnica →</span></div>
    </a>"""


def main() -> None:
    products = [item for item in json.loads(CATALOG.read_text(encoding="utf-8")) if item.get("category") == "Conectores"]
    cards = "\n".join(render_card(product) for product in products)
    schema = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Conectores para vidrio y barandal | Herraidea",
            "description": "Conectores de acero inoxidable para vidrio, tubo, pasamanos y puertas en sistemas de barandal.",
            "url": f"{DOMAIN}/familias/conectores",
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
    whatsapp = quote("Hola Herraidea, necesito ayuda para elegir conectores para un proyecto de vidrio o barandal.")
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(
        f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="description" content="Conectores de acero inoxidable Herraidea para vidrio, tubo, pasamanos y puertas. Consulta {len(products)} modelos y sus fichas técnicas.">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="theme-color" content="#ffffff">
  <link rel="canonical" href="{DOMAIN}/familias/conectores">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Herraidea">
  <meta property="og:title" content="Conectores para vidrio y barandal | Herraidea">
  <meta property="og:description" content="Explora conectores por aplicación, función y código HRD.">
  <meta property="og:url" content="{DOMAIN}/familias/conectores">
  <meta property="og:image" content="{DOMAIN}/content/catalog/images/conectores-hrd-1301.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/assets/brand/apple-touch-icon.png">
  <title>Conectores para vidrio y barandal | Herraidea</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&family=Archivo+Narrow:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/family-page.css?v=1-34-0">
  <script type="application/ld+json">{schema}</script>
</head>
<body class="family-conectores">
  <header class="family-header">
    <a class="family-brand" href="/" aria-label="Herraidea, inicio"><img src="/assets/logo-gray-nodot.png" alt="Herraidea"><i aria-hidden="true"></i></a>
    <nav><a href="/#proyectos">Soluciones 3D</a><a href="/#calculadora">Calculadora</a><a href="/#catalogo">Catálogo</a><a class="header-contact" href="https://wa.me/524772561695?text={whatsapp}" target="_blank" rel="noopener">Cotizar</a></nav>
  </header>
  <main>
    <section class="family-hero">
      <div class="family-hero-copy"><span class="eyebrow">Familia 03 · {len(products)} modelos</span><h1>Conectores para<br><em>cada unión.</em></h1><p>Explora herrajes de acero inoxidable para vidrio, tubo, pasamanos y puertas. Abre cada modelo para revisar su fotografía, medidas y ficha PDF.</p><div class="hero-actions"><a class="primary-action" href="#modelos">Explorar modelos <span>↓</span></a><a class="secondary-action" href="/#asesoria">Necesito asesoría</a></div></div>
      <div class="family-hero-visual"><figure class="hero-main"><img src="/content/catalog/images/conectores-hrd-1301.jpg" alt="Botón conector Herraidea HRD 1301 para vidrio"></figure><figure class="hero-detail"><img src="/content/catalog/images/conectores-hrd-1408.jpg" alt="Vela articulada Herraidea HRD 1408 para tubo"></figure><div class="hero-index"><b>03</b><span>Conectores</span></div></div>
    </section>

    <section class="system-section" aria-labelledby="systems-title">
      <div class="section-heading"><span class="eyebrow">Elige un punto de partida</span><h2 id="systems-title">Cuatro aplicaciones,<br><em>una familia.</em></h2><p>Empieza por la superficie o el elemento que necesitas unir. La selección final debe revisarse según medidas, vidrio, tubo y condiciones del montaje.</p></div>
      <div class="system-grid">
        <button class="system-card" type="button" data-family-filter="muro"><figure><img src="/content/catalog/images/conectores-hrd-1302.jpg" alt="Conector para vidrio a muro"></figure><span>01</span><h3>Vidrio a muro</h3><p>Botones y conectores en distintas medidas para fijar vidrio templado.</p><b>Ver modelos →</b></button>
        <button class="system-card" type="button" data-family-filter="tubo"><figure><img src="/content/catalog/images/conectores-hrd-1404.jpg" alt="Conector intermedio para tubo de dos pulgadas"></figure><span>02</span><h3>Tubo de 2 pulgadas</h3><p>Conectores intermedios, tapones, bridas y velas para tubo.</p><b>Ver modelos →</b></button>
        <button class="system-card" type="button" data-family-filter="pasamanos"><figure><img src="/content/catalog/images/conectores-hrd-1410.jpg" alt="Soporte ajustable para barandal"></figure><span>03</span><h3>Pasamanos</h3><p>Soportes para relacionar vidrio, muro, tubo y pasamanos.</p><b>Ver modelos →</b></button>
        <button class="system-card" type="button" data-family-filter="puerta"><figure><img src="/content/catalog/images/conectores-hrd-2020.jpg" alt="Bisagra para puerta de vidrio"></figure><span>04</span><h3>Puertas de vidrio</h3><p>Pomos conectores y bisagra muro-vidrio para accesos.</p><b>Ver modelos →</b></button>
      </div>
      <div class="system-links"><a href="/#catalogo">Ver catálogo completo <span>→</span></a><a href="/#asesoria">Revisar mi proyecto <span>→</span></a></div>
    </section>

    <section class="models-section" id="modelos">
      <div class="models-heading"><div><span class="eyebrow">Catálogo técnico</span><h2>Encuentra tu conector.</h2></div><p>Filtra por aplicación o función; también puedes escribir un código HRD. Cada resultado abre su ficha técnica.</p></div>
      <div class="models-tools">
        <label class="family-search"><span>Buscar por código o nombre</span><input id="post-search" type="search" placeholder="Ej. HRD 1408 o pasamanos" autocomplete="off"></label>
        <div class="family-filters" aria-label="Filtrar conectores">
          <button class="active" type="button" data-family-filter="all" aria-pressed="true">Todos</button><button type="button" data-family-filter="muro" aria-pressed="false">Vidrio a muro</button><button type="button" data-family-filter="vidrio" aria-pressed="false">Vidrio a vidrio</button><button type="button" data-family-filter="tubo" aria-pressed="false">Tubo 2 pulgadas</button><button type="button" data-family-filter="pasamanos" aria-pressed="false">Pasamanos</button><button type="button" data-family-filter="velas" aria-pressed="false">Velas</button><button type="button" data-family-filter="tapas" aria-pressed="false">Tapones y bridas</button><button type="button" data-family-filter="puerta" aria-pressed="false">Puertas</button><button type="button" data-family-filter="ajustables" aria-pressed="false">Ajustables</button>
        </div>
        <p class="result-status" aria-live="polite"><strong id="post-result-count">{len(products)}</strong> modelos</p>
      </div>
      <div class="posts-grid" id="posts-grid">{cards}</div>
      <div class="no-results" id="post-no-results" hidden><b>No encontramos ese conector.</b><p>Prueba otro código o solicita ayuda para identificar la pieza.</p></div>
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
    print(f"Generada página de Conectores con {len(products)} modelos")


if __name__ == "__main__":
    main()
