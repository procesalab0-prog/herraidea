"""Arma content/projects/domo-geodesico/visor-privado.html: un solo archivo con Three.js + el GLB incrustado (sin internet).
Uso: python3 scripts/domo-geodesico/armar_visor.py  (requiere Node; usa `npx esbuild`)."""
import base64, subprocess, pathlib
V = pathlib.Path(__file__).resolve().parent
RAIZ = V.parent.parent
js = subprocess.run(['npx', '--yes', 'esbuild@0.28', str(V / 'visor.js'), '--bundle', '--minify', '--format=iife', '--log-level=warning'],
                    check=True, capture_output=True, text=True).stdout
b64 = base64.b64encode((RAIZ / 'assets/projects/domo-geodesico/domo-geodesico.glb').read_bytes()).decode()
html = f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<title>Domo geodésico · glamping (modelo 3D preliminar)</title>
<style>
:root{{--ink:#0b0d10;--red:#fa1418;--line:#dfe3e8}}
*{{box-sizing:border-box;margin:0}}
html,body{{height:100%;overflow:hidden;background:linear-gradient(180deg,#dde2e8,#f4f5f7);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink)}}
canvas{{position:fixed;inset:0;width:100%;height:100%;touch-action:none;outline:0}}
header{{position:fixed;left:0;right:0;top:0;padding:max(16px,env(safe-area-inset-top)) 20px 0;display:flex;justify-content:space-between;align-items:flex-start;pointer-events:none;gap:16px}}
h1{{font-size:clamp(22px,4.2vw,34px);line-height:1;letter-spacing:-.045em;font-weight:900}}
h1 em{{font-style:normal;color:var(--red)}}
.sub{{margin-top:8px;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#59616a;font-weight:600}}
.priv{{font-size:11px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;border:1px solid var(--ink);padding:7px 10px;white-space:nowrap}}
nav{{position:fixed;left:50%;transform:translateX(-50%);bottom:max(18px,env(safe-area-inset-bottom));display:flex;gap:8px;flex-wrap:wrap;justify-content:center;width:min(96vw,900px)}}
nav button{{appearance:none;border:1px solid var(--line);background:#ffffffe6;backdrop-filter:blur(8px);color:var(--ink);font:700 12px/1 inherit;letter-spacing:.1em;text-transform:uppercase;padding:12px 15px;border-radius:999px;cursor:pointer;box-shadow:0 8px 24px #0b0d1014}}
nav button:hover{{border-color:var(--ink)}}
nav button.on{{background:var(--ink);color:#fff;border-color:var(--ink)}}
nav i{{width:1px;background:var(--line);margin:0 2px}}
.nota{{position:fixed;left:20px;bottom:132px;max-width:300px;font-size:11px;line-height:1.5;color:#59616a}}
#carga{{position:fixed;inset:0;display:grid;place-items:center;font-size:13px;letter-spacing:.2em;text-transform:uppercase;color:#59616a;font-weight:700}}
nav button:disabled{{opacity:.35;cursor:wait}}
.despiece{{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(max(18px,env(safe-area-inset-bottom)) + 58px);display:flex;align-items:center;gap:10px;padding:6px 8px 6px 6px;border-radius:999px;background:#ffffffe6;backdrop-filter:blur(8px);border:1px solid var(--line);box-shadow:0 8px 24px #0b0d1014;width:min(92vw,560px)}}
.despiece button{{appearance:none;border:0;background:transparent;color:#59616a;font:700 12px/1 inherit;letter-spacing:.1em;text-transform:uppercase;padding:11px 14px;border-radius:999px;cursor:pointer;white-space:nowrap}}
.despiece button::before{{content:"+";display:inline-grid;width:18px;height:18px;margin-right:7px;place-items:center;border:1px solid #adb4b9;border-radius:50%;font-weight:500;vertical-align:-1px}}
.despiece #armar::before{{content:"✓";font-size:10px}}
.despiece button.on{{background:#fff;color:var(--ink);box-shadow:0 3px 12px #17202716}}
.despiece button.on::before{{border-color:var(--red);background:var(--red);color:#fff}}
.despiece button:disabled{{opacity:.35;cursor:wait}}
.despiece label{{flex:1;display:flex;align-items:center;gap:8px;font:700 11px/1 inherit;letter-spacing:.1em;text-transform:uppercase;color:#59616a;min-width:0}}
.despiece input{{flex:1;min-width:60px;accent-color:var(--red)}}
.despiece output{{width:48px;text-align:right;color:var(--ink);white-space:nowrap}}
@media(max-width:720px){{.nota{{display:none}}nav{{gap:6px}}nav i{{display:none}}nav button{{padding:11px 12px;font-size:11px}}.despiece{{bottom:calc(max(18px,env(safe-area-inset-bottom)) + 104px);flex-wrap:wrap;border-radius:22px;justify-content:center}}.despiece label{{flex-basis:100%;padding:0 10px 6px}}}}
</style></head><body>
<canvas id="c"></canvas>
<header><div><h1>Domo geodésico<em>.</em></h1><div class="sub">Glamping 3V 5/8 · 7 m · despiece · <span id="stats"></span></div></div><div class="priv">Privado · no publicar</div></header>
<div id="carga">Cargando modelo…</div>
<div class="nota">Domo 3V 5/8 de 7 m estimado a partir de imágenes de referencia; no son medidas de fabricación. Arrastra para girar, pellizca o usa la rueda para acercar.</div>
<div class="despiece" role="group" aria-label="Despiece del rack"><button id="desarmar" data-d type="button" disabled>Desarmar</button><button id="armar" data-d class="on" type="button" disabled>Armado</button><label for="rango">Separación <input id="rango" type="range" min="0" max="100" value="0" disabled><output id="rango-valor">0 %</output></label></div>
<nav>
<button data-v="exterior">Exterior</button><button data-v="interior">Interior</button><button data-v="frente">Frente</button><button data-v="planta">Planta</button>
<i></i><button id="capa-lona" class="on" aria-pressed="true">Lona</button><button id="capa-terraza" class="on" aria-pressed="true">Terraza</button>
<i></i><button id="rot">Girar</button><button id="foto">Captura</button>
</nav>
<script>window.__GLB__="{b64}";</script>
<script>{js}</script>
</body></html>'''
(RAIZ / 'content/projects/domo-geodesico/visor-privado.html').write_text(html)
print('visor:', round(len(html) / 1024), 'KB')
