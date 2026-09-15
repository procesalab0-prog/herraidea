#!/usr/bin/env python3
"""Genera la página pública de la familia Postes desde details.json."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "content/catalog/details.json"
OUTPUT = ROOT / "familias/postes.html"
DOMAIN = "https://www.herraidea.com"


def slugify(value: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value.lower()))


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def group_for(code: str) -> str:
    normalized = code.upper()
    if re.search(r"HRD 120|HRD 1216|HRD 1220", normalized):
        return "mini"
    if re.search(r"HRD 1515|HRD 1516|HRD 1517|HRD 1518", normalized):
        return "tubo"
    if re.search(r"HRD 1519|HRD 1520|HRD 1525|HRD 1526", normalized):
        return "clips"
    if re.search(r"HRD 1221|HRD 1223|HRD 1715|HRD 1716|HRD 1717", normalized):
        return "solera"
    if re.search(r"HRD 1615|HRD 1616", normalized):
        return "cuadrados"
    return "especiales"


def render_card(product: dict) -> str:
    code = product["code"]
    searchable = f"{code} {product['name']} {product.get('description', '')}".lower()
    return f"""<a class="post-card" href="/productos/{slugify(code)}" data-group="{group_for(code)}" data-search="{escape(searchable)}">
      <figure><img src="/content/catalog/{escape(product['image'])}" alt="{escape(product['name'])} {escape(code)}" loading="lazy"></figure>
      <div><b>{escape(code)}</b><h3>{escape(product['name'])}</h3><p>{escape(product.get('description', ''))}</p><span>Ver ficha técnica →</span></div>
    </a>"""


def main() -> None:
    products = [item for item in json.loads(CATALOG.read_text(encoding="utf-8")) if item.get("category") == "Postes"]
    cards = "\n".join(render_card(product) for product in products)
    schema = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Postes para barandal | Herraidea",
            "description": "Postes y minipostes de acero inoxidable para sistemas de barandal con clips, pines, cable y brazos de solera.",
            "url": f"{DOMAIN}/familias/postes",
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
    whatsapp = quote("Hola Herraidea, necesito ayuda para elegir postes para un barandal.")
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(
        f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="description" content="Postes y minipostes de acero inoxidable Herraidea para barandales con clips, pines, cable y brazos de solera. Consulta {len(products)} modelos y sus fichas técnicas.">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="theme-color" content="#ffffff">
  <link rel="canonical" href="{DOMAIN}/familias/postes">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Herraidea">
  <meta property="og:title" content="Postes para barandal | Herraidea">
  <meta property="og:description" content="Explora postes por sistema, función y código HRD.">
  <meta property="og:url" content="{DOMAIN}/familias/postes">
  <meta property="og:image" content="{DOMAIN}/assets/projects/clip-system/portada-estudio.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/assets/brand/apple-touch-icon.png">
  <title>Postes para barandal | Herraidea</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&family=Archivo+Narrow:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/family-page.css?v=1-34-0">
  <script type="application/ld+json">{schema}</script>
</head>
<body>
  <header class="family-header">
    <a class="family-brand" href="/" aria-label="Herraidea, inicio"><img src="/assets/logo-gray-nodot.png" alt="Herraidea"><i aria-hidden="true"></i></a>
    <nav><a href="/sistemas">Sistemas</a><a href="/#calculadora">Calculadora</a><a href="/#catalogo">Catálogo</a><a class="header-contact" href="https://wa.me/524772561695?text={whatsapp}" target="_blank" rel="noopener">Cotizar</a></nav>
  </header>
  <main>
    <section class="family-hero">
      <div class="family-hero-copy"><span class="eyebrow">Familia 02 · {len(products)} modelos</span><h1>Postes para<br><em>barandal.</em></h1><p>Explora postes de acero inoxidable por sistema y función. Abre cada modelo para revisar su fotografía, medidas disponibles y ficha PDF.</p><div class="hero-actions"><a class="primary-action" href="#modelos">Explorar modelos <span>↓</span></a><a class="secondary-action" href="/#asesoria">Necesito asesoría</a></div></div>
      <div class="family-hero-visual"><figure class="hero-main"><img src="/content/catalog/images/postes-hrd-1525-inicio-final-v2.jpg" alt="Poste Herraidea HRD 1525 con clips de acero inoxidable"></figure><figure class="hero-detail"><img src="/content/catalog/images/postes-hrd-1221-solera-continua-v2.jpg" alt="Poste Herraidea HRD 1221 con brazos de solera"></figure><div class="hero-index"><b>02</b><span>Postes</span></div></div>
    </section>

    <section class="system-section" aria-labelledby="systems-title">
      <div class="section-heading"><span class="eyebrow">Elige un punto de partida</span><h2 id="systems-title">Cuatro sistemas,<br><em>una familia.</em></h2><p>Estas agrupaciones ayudan a explorar el catálogo. La selección final debe revisarse según medidas, montaje y condiciones del proyecto.</p></div>
      <div class="system-grid">
        <button class="system-card" type="button" data-family-filter="clips"><figure><img src="/content/catalog/images/postes-hrd-1525-inicio-final-v2.jpg" alt="Poste con clips de acero inoxidable"></figure><span>01</span><h3>Clips + vidrio</h3><p>Postes de inicio, final e intermedios con clips de acero inoxidable o Zamak.</p><b>Ver modelos →</b></button>
        <button class="system-card" type="button" data-family-filter="tubo"><figure><img src="/content/catalog/images/postes-hrd-1518-intermedio-3-pines-v2.jpg" alt="Poste tubular con tres pines"></figure><span>02</span><h3>Tubo + pines</h3><p>Configuraciones intermedias, laterales y cacheteadas para sistemas de tubo.</p><b>Ver modelos →</b></button>
        <button class="system-card" type="button" data-family-filter="cuadrados"><figure><img src="/content/catalog/images/postes-hrd-1616.jpg" alt="Poste cuadrado para sistema con cable"></figure><span>03</span><h3>Cuadrado + cable</h3><p>Postes cuadrados para soluciones de barandal con líneas de cable de acero.</p><b>Ver modelos →</b></button>
        <button class="system-card" type="button" data-family-filter="solera"><figure><img src="/content/catalog/images/postes-hrd-1221-solera-continua-v2.jpg" alt="Poste con brazos planos de solera"></figure><span>04</span><h3>Postes de solera</h3><p>Postes con brazos planos, conectores y configuraciones opuestas a 180 grados.</p><b>Ver modelos →</b></button>
      </div>
      <div class="system-links"><a href="/#proyectos">Explorar soluciones 3D <span>→</span></a><a href="/#calculadora">Calcular distribución de postes <span>→</span></a></div>
    </section>

    <section class="models-section" id="modelos">
      <div class="models-heading"><div><span class="eyebrow">Catálogo técnico</span><h2>Encuentra tu poste.</h2></div><p>Filtra por tipo o escribe un código HRD. Cada resultado abre su página técnica independiente.</p></div>
      <div class="models-tools">
        <label class="family-search"><span>Buscar por código o nombre</span><input id="post-search" type="search" placeholder="Ej. HRD 1525 o solera" autocomplete="off"></label>
        <div class="family-filters" aria-label="Filtrar postes">
          <button class="active" type="button" data-family-filter="all" aria-pressed="true">Todos</button><button type="button" data-family-filter="mini" aria-pressed="false">Minipostes</button><button type="button" data-family-filter="tubo" aria-pressed="false">Tubo y pines</button><button type="button" data-family-filter="clips" aria-pressed="false">Clips</button><button type="button" data-family-filter="solera" aria-pressed="false">Solera</button><button type="button" data-family-filter="cuadrados" aria-pressed="false">Cuadrados</button><button type="button" data-family-filter="especiales" aria-pressed="false">Especiales</button>
        </div>
        <p class="result-status" aria-live="polite"><strong id="post-result-count">{len(products)}</strong> modelos</p>
      </div>
      <div class="posts-grid" id="posts-grid">{cards}</div>
      <div class="no-results" id="post-no-results" hidden><b>No encontramos ese modelo.</b><p>Prueba otro código o solicita ayuda para identificar la pieza.</p></div>
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
    print(f"Generada página de Postes con {len(products)} modelos")


if __name__ == "__main__":
    main()
