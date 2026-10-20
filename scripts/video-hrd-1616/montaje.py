"""Monta el video HRD 1616: escala los cuadros a 1080 × 1920, añade el cierre con el logotipo y une el audio.

Uso:  python3 scripts/video-hrd-1616/montaje.py CUADROS/ AUDIO.wav SALIDA.mp4
"""
import glob
import io
import math
import os
import subprocess
import sys

import imageio_ffmpeg
import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio import FPS, TOMAS  # noqa: E402

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ANCHO, ALTO = 1080, 1920
ROJO = (241, 0, 1)


def fuente(archivo, tam):
    """Las tipografías del proyecto vienen en WOFF2; se convierten en memoria para PIL."""
    f = TTFont(os.path.join(RAIZ, 'admin-prototipo', 'fuentes', archivo)); f.flavor = None
    datos = io.BytesIO(); f.save(datos); datos.seek(0)
    return ImageFont.truetype(datos, tam)


def suave(t):
    t = min(1.0, max(0.0, t))
    return 1 - (1 - t) ** 3


def texto_espaciado(dibujo, centro_x, y, texto, letra, espacio, color):
    anchos = [dibujo.textlength(c, font=letra) for c in texto]
    total = sum(anchos) + espacio * (len(texto) - 1)
    x = centro_x - total / 2
    for c, a in zip(texto, anchos):
        dibujo.text((x, y), c, font=letra, fill=color)
        x += a + espacio


class Cierre:
    """Logotipo de Herraidea con el punto rojo de la i que cae y rebota, como en la pantalla de entrada."""

    def __init__(self):
        logo = Image.open(os.path.join(RAIZ, 'assets', 'brand', 'logo-intro.png')).convert('RGBA')
        ancho = 640
        self.logo = logo.resize((ancho, round(logo.height * ancho / logo.width)), Image.LANCZOS)
        w, h = self.logo.size
        self.punto = (round(w * .61), round(h * .009), round(w * .0305), round(h * .21))
        self.titulo = fuente('archivo-latin-800-normal.woff2', 66)
        self.sub = fuente('archivo-narrow-latin-600-normal.woff2', 29)
        self.web = fuente('archivo-narrow-latin-600-normal.woff2', 27)

    def aplicar(self, cuadro, c):
        """c = cuadro local de la toma 6 (1 en adelante)."""
        capa = Image.new('RGBA', (ANCHO, ALTO), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = suave((c - 14) / 12)
        if a <= 0:
            return cuadro
        w, h = self.logo.size
        x0, y0 = (ANCHO - w) // 2, 250 + round(22 * (1 - a))
        logo = self.logo.copy(); logo.putalpha(logo.getchannel('A').point(lambda v: int(v * a)))
        capa.alpha_composite(logo, (x0, y0))
        # punto de la i: cae desde arriba y rebota dos veces
        u = (c - 22) / 10
        if u > 0:
            if u < .55:
                caida = -1 + (u / .55) ** 2
            elif u < .82:
                k = (u - .55) / .27; caida = -.16 * math.sin(math.pi * k)
            elif u < 1:
                k = (u - .82) / .18; caida = -.05 * math.sin(math.pi * k)
            else:
                caida = 0
            px, py, pw, ph = self.punto
            y = y0 + py + caida * 120
            d.rectangle((x0 + px, y, x0 + px + pw, y + ph), fill=ROJO + (255,))
        b = suave((c - 28) / 12)
        if b > 0:
            texto_espaciado(d, ANCHO / 2, 392 + round(14 * (1 - b)), 'HRD 1616', self.titulo, 4, (255, 255, 255, int(255 * b)))
            texto_espaciado(d, ANCHO / 2, 486 + round(14 * (1 - b)), 'POSTE CUADRADO + CABLE DE ACERO', self.sub, 7, (255, 255, 255, int(190 * b)))
        e = suave((c - 34) / 12)
        if e > 0:
            texto_espaciado(d, ANCHO / 2, 1790, 'HERRAIDEA.COM', self.web, 9, (255, 255, 255, int(200 * e)))
        return Image.alpha_composite(cuadro.convert('RGBA'), capa).convert('RGB')


def principal(carpeta, audio, salida):
    cierre = Cierre()
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    proc = subprocess.Popen([ff, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{ANCHO}x{ALTO}', '-r', str(FPS), '-i', '-',
                             '-i', audio, '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                             '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', salida], stdin=subprocess.PIPE)
    rng = np.random.default_rng(7)
    total = 0
    for toma, n in TOMAS.items():
        cuadros = sorted(glob.glob(os.path.join(carpeta, f'toma{toma}_*.png')))
        if len(cuadros) < n:
            print(f'toma {toma}: {len(cuadros)}/{n} cuadros; se rellena con el último disponible' if cuadros else f'toma {toma}: sin cuadros, se omite')
        if not cuadros:
            continue
        for c in range(1, n + 1):
            im = Image.open(cuadros[min(c, len(cuadros)) - 1]).convert('RGB')
            if im.size != (ANCHO, ALTO):
                im = im.resize((ANCHO, ALTO), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 40, 2))
            if toma == 6:
                im = cierre.aplicar(im, c)
            px = np.asarray(im, dtype=np.float32)
            px += rng.normal(0, 1.6, px.shape[:2])[..., None]          # grano fino: evita bandas en el degradado rojo
            proc.stdin.write(np.clip(px, 0, 255).astype(np.uint8).tobytes())
            total += 1
    proc.stdin.close(); proc.wait()
    print(f'{salida}: {total} cuadros, {total / FPS:.2f} s')


if __name__ == '__main__':
    principal(*sys.argv[1:4])
