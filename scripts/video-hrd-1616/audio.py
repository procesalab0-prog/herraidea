"""Música y diseño sonoro del video HRD 1616, sincronizados con las tomas de video.py.

Todo se sintetiza aquí (sin bibliotecas de sonidos): acordes de fondo que cambian en cada corte,
golpes metálicos por síntesis modal, chasquidos de rosca, barridos de aire y un impacto final.

Uso:  python3 scripts/video-hrd-1616/audio.py salida.wav
"""
import math
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
FPS = 24
TOMAS = {1: 62, 2: 62, 3: 58, 4: 68, 5: 74, 6: 60}  # igual que video.py
INICIO = {}
_acum = 0
for _t, _n in TOMAS.items():
    INICIO[_t] = _acum
    _acum += _n
DURACION = _acum / FPS
rng = np.random.default_rng(1616)


def seg(toma, cuadro):
    """Segundo absoluto del cuadro local (1 = primer cuadro de la toma)."""
    return (INICIO[toma] + cuadro - 1) / FPS


def nota(nombre):
    tonos = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'Ab': 8, 'A': 9, 'Bb': 10, 'B': 11}
    n, o = nombre[:-1], int(nombre[-1])
    return 440.0 * 2 ** ((tonos[n] + 12 * (o + 1) - 69) / 12)


class Pista:
    def __init__(self, segundos):
        self.x = np.zeros((int(segundos * SR) + SR * 3, 2))

    def poner(self, t, sonido, ganancia=1.0, pan=0.0):
        """Suma un sonido mono o estéreo en el segundo t con paneo (-1 izquierda, 1 derecha)."""
        i = int(t * SR)
        if i >= len(self.x):
            return
        s = sonido if sonido.ndim == 2 else np.stack([sonido * math.sqrt((1 - pan) / 2), sonido * math.sqrt((1 + pan) / 2)], 1)
        n = min(len(s), len(self.x) - i)
        self.x[i:i + n] += s[:n] * ganancia


def filtro(x, tipo, f, orden=4):
    sos = butter(orden, f, btype=tipo, fs=SR, output='sos')
    return sosfilt(sos, x, axis=0)


def env(n, ataque, caida):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(ataque, 1e-4)) * np.exp(-t / caida)


# ---------------------------------------------------------------- música
def colchon(notas, dur, corte=1600, brillo=1.0, desafinar=(-7, 0, 7)):
    """Acorde tipo pad: ondas de sierra sin aliasing (aditivas) con filtro paso bajo suave."""
    n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for k, nom in enumerate(notas):
        f0 = nota(nom)
        for j, cents in enumerate(desafinar):
            f = f0 * 2 ** (cents / 1200)
            fase = rng.uniform(0, math.tau)
            onda = np.zeros(n)
            for h in range(1, int(min(48, 9000 / f)) + 1):
                a = 1 / h / math.sqrt(1 + (h * f / (corte * brillo)) ** 4)
                if a < 2e-4:
                    break
                onda += a * np.sin(math.tau * f * h * t + fase * h)
            pan = (j - 1) * .55 + (k - len(notas) / 2) * .06
            out[:, 0] += onda * math.sqrt((1 - pan) / 2); out[:, 1] += onda * math.sqrt((1 + pan) / 2)
    vibr = 1 + .04 * np.sin(math.tau * .35 * t)[:, None]
    return out * vibr / (len(notas) * len(desafinar))


def bajo(nom, dur):
    n = int(dur * SR); t = np.arange(n) / SR; f = nota(nom)
    s = np.sin(math.tau * f * t) + .25 * np.sin(math.tau * 2 * f * t) + .08 * np.sin(math.tau * 3 * f * t)
    return np.tanh(1.4 * s) * .6


def fundido(n, entra, sale):
    e = np.ones(n)
    a, b = int(entra * SR), int(sale * SR)
    if a:
        e[:a] = np.sin(np.linspace(0, math.pi / 2, a)) ** 2
    if b:
        e[-b:] = np.cos(np.linspace(0, math.pi / 2, b)) ** 2
    return e


def musica(p):
    acordes = {   # (bajo, notas del pad, corte del filtro)
        1: ('D2', ['D3', 'F3', 'A3', 'C4', 'E4'], 1300),
        2: ('Bb1', ['Bb2', 'D3', 'F3', 'A3', 'C4'], 1400),
        3: ('G2', ['G2', 'Bb2', 'D3', 'F3', 'A3'], 1500),
        4: ('F2', ['F3', 'A3', 'C4', 'E4', 'G4'], 1900),
        5: ('C2', ['C3', 'F3', 'G3', 'Bb3', 'D4'], 2300),
        6: ('D2', ['D3', 'A3', 'E4', 'F4', 'A4'], 2000),
    }
    for toma, (b, ns, corte) in acordes.items():
        t0 = INICIO[toma] / FPS
        dur = TOMAS[toma] / FPS + (.9 if toma < 6 else 2.6)
        pad = colchon(ns, dur, corte * .72)
        e = fundido(len(pad), .06 if toma > 1 else .5, .9 if toma < 6 else 2.4)
        if toma in (4, 5):   # pulso de corcheas que empuja hacia el armado
            t = np.arange(len(pad)) / SR
            e = e * (1 - .32 * (0.5 + 0.5 * np.cos(math.tau * 4 * t)) ** 3)
        p.poner(t0 - (.06 if toma > 1 else 0), pad * e[:, None], .8)
        bj = bajo(b, dur) * fundido(int(dur * SR), .02, .9 if toma < 6 else 2.4)
        p.poner(t0, bj, .24)


# ---------------------------------------------------------------- efectos
def ruido(n):
    return rng.standard_normal(n)


def barrido(dur, f0, f1, ancho=.6, subir=False):
    """Golpe de aire: ruido con banda que recorre de f0 a f1; la envolvente sube y baja, o solo sube."""
    n = int(dur * SR); x = ruido(n)
    salida = np.zeros(n); bloque = 1024
    zi = None
    for i in range(0, n, bloque):
        u = i / n
        fc = f0 * (f1 / f0) ** u
        lo, hi = max(40, fc * (1 - ancho / 2)), min(SR / 2 - 100, fc * (1 + ancho / 2))
        sos = butter(2, [lo, hi], btype='band', fs=SR, output='sos')
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        salida[i:i + bloque], zi = sosfilt(sos, x[i:i + bloque], zi=zi)
    u = np.linspace(0, 1, n)
    forma = u ** 2.2 if subir else np.sin(np.pi * u) ** 1.6
    return salida * forma * 3.0


def tintineo(f0, decaimiento=.5, brillo=1.0, razones=(1, 2.76, 5.40, 8.93, 13.34)):
    """Golpe metálico por síntesis modal (barra libre de acero) con transitorio de contacto."""
    n = int((decaimiento * 3 + .05) * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for k, r in enumerate(razones):
        f = f0 * r * (1 + rng.uniform(-.006, .006))
        if f > SR / 2 - 500:
            break
        s += (brillo ** k) / (k + 1) ** .7 * np.sin(math.tau * f * t + rng.uniform(0, 6.28)) * np.exp(-t / (decaimiento / (1 + .55 * k)))
    golpe = filtro(ruido(int(.006 * SR)), 'high', 2500) * np.linspace(1, 0, int(.006 * SR))
    s[:len(golpe)] += golpe * .6
    return s * .5


def chasquido(f=4200, fuerza=1.0):
    """Chasquido corto de rosca o trinquete."""
    n = int(.03 * SR); t = np.arange(n) / SR
    x = filtro(ruido(n), 'band', [f * .6, min(f * 1.6, 20000)], 2) * np.exp(-t / .0025)
    x += .35 * np.sin(math.tau * f * .5 * t) * np.exp(-t / .008)
    return x * fuerza


def golpe_sordo(f=75, dur=.35, fuerza=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    fr = f * (1 + 1.2 * np.exp(-t / .02))
    s = np.sin(math.tau * np.cumsum(fr) / SR) * np.exp(-t / (dur / 3.5))
    s += filtro(ruido(n), 'low', 400) * np.exp(-t / .02) * .5
    return s * fuerza


def impacto(dur=2.2):
    n = int(dur * SR); t = np.arange(n) / SR
    fr = 46 + 70 * np.exp(-t / .12)
    s = np.sin(math.tau * np.cumsum(fr) / SR) * np.exp(-t / .7)
    s += filtro(ruido(n), 'low', 900) * np.exp(-t / .09) * .6
    return np.tanh(s * 1.6)


def subida(dur):
    """Ruido que sube de tono y volumen: prepara el corte."""
    return barrido(dur, 300, 6000, .8, subir=True) * .5


def deslizamiento(dur, f=3200):
    """Roce metálico (cable o tubo que entra): ruido resonante con eco corto en peine."""
    n = int(dur * SR); x = filtro(ruido(n), 'band', [f * .5, f * 1.6], 2)
    retardo = int(SR / 610)
    y = x.copy()
    for k in range(1, 6):
        y[k * retardo:] += x[:-k * retardo] * (.6 ** k)
    u = np.linspace(0, 1, n)
    return y * np.sin(np.pi * u) ** 1.2 * .35


def destello(dur=2.0):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for f in (nota('A5'), nota('D6'), nota('E6'), nota('A6')):
        s += np.sin(math.tau * f * t + rng.uniform(0, 6)) * np.exp(-t / .9)
    return s * np.minimum(1, t / .08) * .12


def giro(p, toma, c0, c1, vueltas, por_vuelta, f, fuerza, pan):
    """Chasquidos de rosca que se espacian al final, igual que la curva de giro de la animación."""
    t0, t1 = seg(toma, c0), seg(toma, c1)
    total = int(vueltas * por_vuelta)
    for k in range(1, total + 1):
        v = k / total                                     # fracción girada
        u = 1 - (1 - v) ** (1 / 3)                        # invierte s = 1 - (1 - u)^3
        t = t0 + (t1 - t0) * u
        p.poner(t, chasquido(f * rng.uniform(.9, 1.1), fuerza * rng.uniform(.6, 1.0)), 1, pan + rng.uniform(-.1, .1))
    friccion = deslizamiento(t1 - t0, f * .7) * np.linspace(1, .2, int((t1 - t0) * SR))
    p.poner(t0, friccion, .25 * fuerza, pan)


def efectos(p):
    # 1 · tornillo avellanado
    p.poner(0.0, golpe_sordo(68, .9, 1.0), .55)
    p.poner(0.0, barrido(.9, 250, 2400), .32, -.3)
    giro(p, 1, 1, 52, 4.2, 8, 3600, .55, .1)
    p.poner(seg(1, 52), tintineo(2350, .45), .8, .1); p.poner(seg(1, 52), golpe_sordo(90, .3, .7), .6)
    # 2 · tuerca
    p.poner(seg(2, 1) - .12, barrido(.55, 600, 3500), .4, .5)
    p.poner(seg(2, 12), chasquido(5200, 1.2), .9, .2)
    giro(p, 2, 12, 50, 7.5, 6, 5000, .5, .2)
    p.poner(seg(2, 50), tintineo(3100, .38, .9), .75, .2); p.poner(seg(2, 50), golpe_sordo(110, .25, .5), .5)
    # 3 · soporte y pasamanos
    p.poner(seg(3, 1) - .1, barrido(1.0, 200, 1500), .35, -.2)
    p.poner(seg(3, 26), tintineo(1750, .55), .7); p.poner(seg(3, 26), golpe_sordo(80, .35, .8), .65)
    p.poner(seg(3, 24) - .1, barrido(.95, 150, 900, .9), .45, .3)
    p.poner(seg(3, 44), tintineo(640, 1.3, .8), .9, .25); p.poner(seg(3, 44), golpe_sordo(60, .5, 1.0), .75)
    # 4 · poste flotando
    p.poner(seg(4, 1) - .2, barrido(2.6, 180, 900, 1.0), .28, -.4)
    p.poner(seg(4, 1), destello(2.4), .5)
    p.poner(seg(4, 40), subida(seg(5, 1) - seg(4, 40)), .3)
    # 5 · armado
    for tramo, desfase, pan in (('A', 0, .45), ('B', 5, -.45)):
        for i in range(7):
            r = i * 3 + desfase
            p.poner(seg(5, 1 + r), deslizamiento((25) / FPS, 2600 + 180 * i), .22, pan)
            p.poner(seg(5, 26 + r), chasquido(3400 + 120 * i, .9), .7, pan)
            p.poner(seg(5, 52 + r // 2), tintineo(3000 + 60 * i, .18, .7), .22, pan * 1.2)
    for k, pan in enumerate((-.5, 0, .5)):
        p.poner(seg(5, 44) + k * .015, tintineo(1700 + 90 * k, .5), .45, pan)
    p.poner(seg(5, 44), golpe_sordo(85, .3, .6), .5)
    for k, (c, pan) in enumerate(((62, .4), (66, -.4))):
        p.poner(seg(5, c), tintineo(620 + 25 * k, 1.2, .8), .7, pan); p.poner(seg(5, c), golpe_sordo(58, .45, .9), .6)
    p.poner(seg(5, 50), subida(seg(6, 1) - seg(5, 50)), .4)
    # 6 · final con logotipo
    p.poner(seg(6, 1), impacto(), .95)
    p.poner(seg(6, 1), tintineo(880, 1.6, .7), .35)
    p.poner(seg(6, 16), destello(3.0), .9)
    for c, fuerza in ((27.5, 1.0), (30.2, .45), (32.0, .2)):   # el punto de la i cae y rebota
        p.poner(seg(6, c), tintineo(4200, .12, .6), .35 * fuerza); p.poner(seg(6, c), chasquido(6000, fuerza), .5)


def reverberar(x, segundos=2.0, mezcla=.28):
    n = int(segundos * SR); t = np.arange(n) / SR
    ir = np.stack([filtro(ruido(n), 'low', 4500) * np.exp(-t / (segundos / 6.9)) for _ in range(2)], 1)
    ir[:int(.012 * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum(0))
    mojado = np.stack([fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in range(2)], 1)
    return x * (1 - mezcla) + mojado * mezcla * 2.2


def principal(salida):
    musica_p = Pista(DURACION); musica(musica_p)
    sfx = Pista(DURACION); efectos(sfx)
    mezcla = reverberar(musica_p.x, 2.6, .35) * .8 + reverberar(sfx.x, 1.4, .18)
    mezcla = filtro(mezcla, 'high', 48, 2)
    n = int((DURACION + .05) * SR)
    mezcla = mezcla[:n]
    mezcla *= fundido(n, .01, .7)[:, None]
    pico = np.abs(mezcla).max()
    mezcla = np.tanh(mezcla / pico * 1.25) / math.tanh(1.25) * .89    # limitador suave a -1 dBFS
    wavfile.write(salida, SR, (mezcla * 32767).astype(np.int16))
    print(f'{salida}: {n / SR:.2f} s')


if __name__ == '__main__':
    principal(sys.argv[1])
