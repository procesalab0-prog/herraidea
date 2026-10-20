"""Música y diseño sonoro del video Riverack, sincronizados con scripts/video-riverack/video.py.

Reutiliza los sintetizadores del video HRD 1616 (pad, bajo, golpes modales, chasquidos, barridos)
con otra armonía y un pulso más marcado. Los golpes del armado salen de eventos5.json, que genera
video.py con EVENTOS=... al hornear el despiece del modelo.

Uso:  python3 scripts/video-riverack/audio.py salida.wav eventos5.json
"""
import json
import math
import os
import sys

import numpy as np
from scipy.io import wavfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'video-hrd-1616'))
import audio as A  # noqa: E402

FPS = 24
TOMAS = {1: 60, 2: 62, 3: 58, 4: 56, 5: 78, 6: 96}
INICIO, _acum = {}, 0
for _t, _n in TOMAS.items():
    INICIO[_t] = _acum; _acum += _n
DURACION = _acum / FPS
LOGO = 58                                   # cuadro local de la toma 6 en que entra el logotipo
rng = np.random.default_rng(2026)


def seg(toma, cuadro):
    return (INICIO[toma] + cuadro - 1) / FPS


def musica(p):
    acordes = {
        1: ('E2', ['E3', 'G3', 'B3', 'D4', 'F#4'], 1200),
        2: ('C2', ['C3', 'E3', 'G3', 'B3', 'D4'], 1300),
        3: ('A1', ['A2', 'C3', 'E3', 'G3', 'B3'], 1400),
        4: ('D2', ['D3', 'F#3', 'A3', 'C4', 'E4'], 1500),
        5: ('B1', ['B2', 'E3', 'F#3', 'A3', 'C#4'], 1900),
        6: ('E2', ['E3', 'B3', 'F#4', 'G4', 'B4'], 1800),
    }
    for toma, (b, ns, corte) in acordes.items():
        t0 = INICIO[toma] / FPS
        dur = TOMAS[toma] / FPS + (.9 if toma < 6 else 2.6)
        pad = A.colchon(ns, dur, corte * .75)
        e = A.fundido(len(pad), .06 if toma > 1 else .5, .9 if toma < 6 else 2.4)
        t = np.arange(len(pad)) / A.SR
        profundidad = {1: .15, 2: .15, 3: .25, 4: .25, 5: .35, 6: .2}[toma]
        e = e * (1 - profundidad * (0.5 + 0.5 * np.cos(math.tau * 4 * t)) ** 3)      # corcheas a 120
        p.poner(t0 - (.06 if toma > 1 else 0), pad * e[:, None], .8)
        dur_b = int(dur * A.SR)
        bj = A.bajo(b, dur) * A.fundido(dur_b, .02, .9 if toma < 6 else 2.4)
        golpeo = 1 - .55 * (np.arange(dur_b) / A.SR * 2 % 1)                          # bajo en negras
        p.poner(t0, bj * golpeo, .26)


def efectos(p, eventos):
    # 1 · tornillo con brida en la placa de la cabeza
    p.poner(0.0, A.golpe_sordo(68, .9, 1.0), .55)
    p.poner(0.0, A.barrido(.9, 250, 2400), .3, .3)
    A_giro(p, 1, 1, 48, 3.5, 6, 2800, .6, .15)
    p.poner(seg(1, 48), A.tintineo(1450, .35, .7), .7, .15); p.poner(seg(1, 48), A.golpe_sordo(85, .35, .9), .7)
    # 2 · recorrido por el calado RIVERACK
    p.poner(seg(2, 1) - .15, A.barrido(2.8, 180, 1100, 1.0), .32, -.6)
    p.poner(seg(2, 1), A.destello(2.6), .35)
    # 3 · la funda corre sobre el tubo interior y se atornilla
    p.poner(seg(3, 1), A.deslizamiento(39 / FPS, 1700), .55, .2)
    p.poner(seg(3, 40), A.tintineo(900, .6, .7), .6); p.poner(seg(3, 40), A.golpe_sordo(70, .45, 1.0), .75)
    for c0, pan in ((36, -.2), (41, .2)):
        A_giro(p, 3, c0, c0 + 14, 3, 6, 3200, .45, pan)
        p.poner(seg(3, c0 + 14), A.tintineo(1600, .3, .7), .45, pan)
    # 4 · la pieza superior sube y se asegura
    p.poner(seg(4, 1), A.deslizamiento(29 / FPS, 1300), .5, -.2)
    p.poner(seg(4, 30), A.tintineo(780, .55, .7), .55); p.poner(seg(4, 30), A.golpe_sordo(62, .4, .9), .7)
    A_giro(p, 4, 32, 48, 3, 6, 3000, .5, .3)
    p.poner(seg(4, 48), A.tintineo(1500, .3, .7), .5, .3)
    # 5 · armado completo, golpes en el cuadro exacto en que cada pieza llega
    p.poner(seg(5, 1) - .1, A.barrido(1.2, 150, 1200, .9), .35)
    por_cuadro = {}
    for c, tipo, _ in eventos:
        por_cuadro.setdefault((c, tipo), 0); por_cuadro[(c, tipo)] += 1
    for (c, tipo), n in sorted(por_cuadro.items()):
        t = seg(5, c)
        if tipo == 'tornillo':
            for k in range(n):                                   # ráfaga de tornillos que entran juntos
                p.poner(t - .25 + .25 * k / n, A.chasquido(3600 * rng.uniform(.85, 1.15), .7), .35, rng.uniform(-.8, .8))
            p.poner(t, A.tintineo(2100, .3, .7), .5)
        elif tipo == 'travesano':
            p.poner(t, A.tintineo(560, 1.1, .8), .75); p.poner(t, A.golpe_sordo(55, .5, 1.0), .8)
        else:
            f0 = 700 + 25 * min(n, 16)
            p.poner(t, A.tintineo(f0, .6, .75), .5 + .02 * n); p.poner(t, A.golpe_sordo(65, .4, .8), .6)
    p.poner(seg(5, 56), A.subida(seg(6, 1) - seg(5, 56)), .35)
    # 6 · se abre y se cierra a lo ancho; luego el logotipo
    p.poner(seg(6, 1), A.golpe_sordo(60, .6, .8), .5)
    for c0, c1 in ((10, 30), (42, 60)):
        dur = (c1 - c0) / FPS
        p.poner(seg(6, c0), A.deslizamiento(dur, 1500), .4, -.5); p.poner(seg(6, c0), A.deslizamiento(dur, 1650), .4, .5)
        p.poner(seg(6, c1), A.tintineo(820, .5, .7), .45, -.4); p.poner(seg(6, c1) + .012, A.tintineo(860, .5, .7), .45, .4)
        p.poner(seg(6, c1), A.golpe_sordo(65, .35, .8), .55)
    p.poner(seg(6, LOGO - 18), A.subida(18 / FPS), .3)
    p.poner(seg(6, LOGO), A.impacto(), .95)
    p.poner(seg(6, LOGO), A.tintineo(880, 1.6, .7), .35)
    p.poner(seg(6, LOGO + 2), A.destello(3.0), .9)
    for c, fuerza in ((LOGO + 13.5, 1.0), (LOGO + 16.2, .45), (LOGO + 18.0, .2)):
        p.poner(seg(6, c), A.tintineo(4200, .12, .6), .35 * fuerza); p.poner(seg(6, c), A.chasquido(6000, fuerza), .5)


def A_giro(p, toma, c0, c1, vueltas, por_vuelta, f, fuerza, pan):
    """Igual que audio.giro, con la línea de tiempo de este video."""
    t0, t1 = seg(toma, c0), seg(toma, c1)
    total = int(vueltas * por_vuelta)
    for k in range(1, total + 1):
        u = 1 - (1 - k / total) ** (1 / 3)
        p.poner(t0 + (t1 - t0) * u, A.chasquido(f * rng.uniform(.9, 1.1), fuerza * rng.uniform(.6, 1.0)), 1, pan + rng.uniform(-.1, .1))
    p.poner(t0, A.deslizamiento(t1 - t0, f * .7) * np.linspace(1, .2, int((t1 - t0) * A.SR)), .25 * fuerza, pan)


def principal(salida, eventos):
    musica_p = A.Pista(DURACION); musica(musica_p)
    sfx = A.Pista(DURACION); efectos(sfx, json.load(open(eventos)))
    mezcla = A.reverberar(musica_p.x, 2.6, .35) * .8 + A.reverberar(sfx.x, 1.4, .18)
    mezcla = A.filtro(mezcla, 'high', 48, 2)
    n = int((DURACION + .05) * A.SR)
    mezcla = mezcla[:n] * A.fundido(n, .01, .7)[:, None]
    mezcla = np.tanh(mezcla / np.abs(mezcla).max() * 1.25) / math.tanh(1.25) * .89
    wavfile.write(salida, A.SR, (mezcla * 32767).astype(np.int16))
    print(f'{salida}: {n / A.SR:.2f} s')


if __name__ == '__main__':
    principal(*sys.argv[1:3])
