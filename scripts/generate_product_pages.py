#!/usr/bin/env python3
"""Genera páginas HTML estáticas y encontrables para cada ficha del catálogo."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "content/catalog/details.json"
OUTPUT = ROOT / "productos"
DOMAIN = "https://www.herraidea.com"


def slugify(value: str) -> str:
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value.lower()))


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def image_url(path: str) -> str:
    if path.startswith("/"):
        return path
    return f"/content/catalog/{path}"


def gallery_images(product: dict) -> list[str]:
    paths = [image_url(product["image"])]
    paths.extend(image_url(path) for path in product.get("detailImages", []))
    return list(dict.fromkeys(paths))


def render(product: dict, family_items: list[dict]) -> str:
    code = product["code"]
    name = product["name"]
    slug = slugify(code)
    canonical = f"{DOMAIN}/productos/{slug}"
    images = gallery_images(product)
    primary = images[0]
    description = product.get("description", "")
    family_name = product.get("category", "")
    family_paths = {"Postes": "/familias/postes", "Pipetas": "/familias/pipetas", "Conectores": "/familias/conectores", "Jaladeras": "/familias/jaladeras"}
    family_path = family_paths.get(family_name)
    family_crumb = f'<a href="{family_path}"><b>{escape(family_name)}</b></a>' if family_path else f"<b>{escape(family_name)}</b>"
    meta_description = f"{code}: {description} Consulta imágenes, especificaciones y ficha PDF de Herraidea."
    whatsapp = quote(f"Hola Herraidea, me interesa cotizar {code} — {name}.")
    specs = "".join(f"<li>{escape(item)}</li>" for item in product.get("specifications", []))
    gallery_parts = []
    technical_number = 0
    for index, src in enumerate(images):
        figure_class = " primary" if index == 0 else ""
        is_cad = "/technical/" in src
        alt_suffix = "" if index == 0 else (" — plano CAD" if is_cad else " — vista técnica")
        loading = 'fetchpriority="high"' if index == 0 else 'loading="lazy"'
        if index == 0:
            caption = "Fotografía principal"
        elif is_cad:
            caption = "Plano CAD"
        else:
            technical_number += 1
            caption = f"Vista técnica {technical_number}"
        gallery_parts.append(
            f'<figure class="product-page-image{figure_class}">'
            f'<img src="{escape(src)}" alt="{escape(name)} {escape(code)}{alt_suffix}" {loading}>'
            f'<figcaption>{caption}</figcaption></figure>'
        )
    gallery = "".join(gallery_parts)
    related = "".join(
        f'<a href="/productos/{slugify(item["code"])}"><b>{escape(item["code"])}</b><span>{escape(item["name"])}</span></a>'
        for item in family_items[:4]
    )
    breadcrumb_items = [
        {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{DOMAIN}/"},
    ]
    if family_path:
        breadcrumb_items.append(
            {"@type": "ListItem", "position": 2, "name": family_name, "item": f"{DOMAIN}{family_path}"}
        )
    breadcrumb_items.append(
        {"@type": "ListItem", "position": len(breadcrumb_items) + 1, "name": f"{code} — {name}", "item": canonical}
    )
    schema = json.dumps(
        {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Product",
                    "@id": f"{canonical}#product",
                    "name": f"{code} — {name}",
                    "description": description,
                    "sku": code,
                    "category": family_name,
                    "image": [f"{DOMAIN}{src}" for src in images],
                    "brand": {"@type": "Brand", "name": "Herraidea"},
                    "url": canonical,
                },
                {
                    "@type": "BreadcrumbList",
                    "@id": f"{canonical}#breadcrumb",
                    "itemListElement": breadcrumb_items,
                },
            ],
        },
        ensure_ascii=False,
    ).replace("</", r"<\/")
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="description" content="{escape(meta_description)}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="theme-color" content="#ffffff">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="product">
  <meta property="og:site_name" content="Herraidea">
  <meta property="og:title" content="{escape(code)} | {escape(name)} | Herraidea">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{DOMAIN}{escape(primary)}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/assets/brand/apple-touch-icon.png">
  <title>{escape(code)} | {escape(name)} | Herraidea</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&family=Archivo+Narrow:wght@500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/product-page.css?v=1-30-0">
  <script type="application/ld+json">{schema}</script>
  <!-- Vercel Web Analytics and Speed Insights -->
  <script>
    window.va = window.va || function () {{ (window.vaq = window.vaq || []).push(arguments); }};
    window.si = window.si || function () {{ (window.siq = window.siq || []).push(arguments); }};
  </script>
  <script defer src="/_vercel/insights/script.js"></script>
  <script defer src="/_vercel/speed-insights/script.js"></script>
</head>
<body>
  <header class="product-header">
    <a class="product-brand" href="/" aria-label="Herraidea, inicio"><img src="/assets/logo-gray-nodot.png" alt="Herraidea"></a>
    <nav><a href="/#catalogo">Catálogo</a><a class="header-contact" href="https://wa.me/524772561695?text={whatsapp}" target="_blank" rel="noopener">Cotizar</a></nav>
  </header>
  <main>
    <div class="product-breadcrumb"><a href="/">Inicio</a><span>→</span><a href="/#catalogo">Catálogo</a><span>→</span>{family_crumb}</div>
    <article class="product-sheet">
      <section class="product-gallery" aria-label="Imágenes de {escape(code)}">{gallery}</section>
      <section class="product-copy">
        <span class="eyebrow">{escape(product.get("category", ""))} · {escape(code)}</span>
        <h1>{escape(name)}</h1>
        <p class="product-description">{escape(description)}</p>
        <div class="section-label">Información técnica disponible</div>
        <ul class="product-specs">{specs}</ul>
        <div class="product-actions">
          <a class="primary-action" href="https://wa.me/524772561695?text={whatsapp}" target="_blank" rel="noopener">Solicitar cotización <span>→</span></a>
          <a class="secondary-action" href="/output/pdf/fichas/{slug}.pdf" download>Descargar ficha PDF</a>
        </div>
        <small class="technical-note">Las acotaciones se expresan en milímetros. Verifica físicamente la pieza antes de instalar y perforar.</small>
      </section>
    </article>
    <section class="family-more">
      <span class="eyebrow">Más de la familia</span><h2>{escape(product.get("category", ""))}</h2>
      <div class="family-links">{related}</div>
      <a class="back-link" href="/#catalogo">Ver catálogo completo <span>→</span></a>
    </section>
  </main>
  <footer><a href="/"><img src="/assets/logo-light-nodot.png" alt="Herraidea"></a><span>León, Guanajuato · Desde 2013</span><small>Creado por ProcesaLab</small></footer>
</body>
</html>
"""


def main() -> None:
    products = json.loads(CATALOG.read_text(encoding="utf-8"))
    OUTPUT.mkdir(exist_ok=True)
    product_slugs = {slugify(product["code"]) for product in products}
    for stale in OUTPUT.glob("*.html"):
        if stale.stem not in product_slugs:
            stale.unlink()
    for index, product in enumerate(products):
        family = [
            item
            for item in products[index + 1 :] + products[:index]
            if item.get("category") == product.get("category") and item["code"] != product["code"]
        ]
        (OUTPUT / f"{slugify(product['code'])}.html").write_text(render(product, family), encoding="utf-8")

    urls = [f"  <url><loc>{DOMAIN}/</loc></url>", f"  <url><loc>{DOMAIN}/sistemas</loc></url>", f"  <url><loc>{DOMAIN}/familias/pipetas</loc></url>", f"  <url><loc>{DOMAIN}/familias/postes</loc></url>", f"  <url><loc>{DOMAIN}/familias/conectores</loc></url>", f"  <url><loc>{DOMAIN}/familias/jaladeras</loc></url>"]
    urls.extend(f"  <url><loc>{DOMAIN}/productos/{slugify(product['code'])}</loc></url>" for product in products)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n",
        encoding="utf-8",
    )
    print(f"Generadas {len(products)} páginas de producto y sitemap.xml")


if __name__ == "__main__":
    main()
