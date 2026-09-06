# -*- coding: utf-8 -*-
"""
Gera a trilha sonora do video do desenho da Vitoria.

Musiquinha instrumental original, no estilo caixinha de musica / piano de
brinquedo, sintetizada do zero (sem sample nem musica de terceiros).
Tem 21 s e e' dividida no mesmo ritmo do video, a 120 bpm (1 compasso = 2 s):

  compasso 0        (0-2 s)   introducao suave, junto com o titulo
  compassos 1-5     (2-12 s)  melodia enquanto o desenho vai sendo feito
  compassos 6-9    (12-20 s)  melodia mais animada, com chocalho e bumbo,
                              quando o desenho ganha vida
  compasso 10      (20-21 s)  acorde final

Uso:  python3 gerar_musica.py [saida.wav]
Requer: numpy
"""
import math
import os
import sys
import wave

import numpy as np

SR = 44100
BPM = 120.0
SPB = 60.0 / BPM          # segundos por tempo (0,5 s)
DURATION = 21.0

NOTES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi(name):
    """'C5' -> numero midi (C4 = 60)."""
    return NOTES[name[0]] + 12 * (int(name[1:]) + 1)


def freq(name):
    return 440.0 * 2 ** ((midi(name) - 69) / 12.0)


# ------------------------------------------------------------------- partitura
# (tempo inicial em batidas, duracao em batidas, nota, volume)
MELODIA = [
    # compasso 0 - introducao
    (0.0, 0.5, "C5", 0.30), (0.5, 0.5, "E5", 0.32), (1.0, 0.5, "G5", 0.34),
    (1.5, 1.5, "C6", 0.36), (3.0, 1.0, "G5", 0.22),
    # compasso 1 (C)
    (4.0, 0.5, "G4", 0.42), (4.5, 0.5, "C5", 0.46), (5.0, 1.0, "E5", 0.52),
    (6.0, 1.0, "D5", 0.48), (7.0, 1.0, "C5", 0.46),
    # compasso 2 (G)
    (8.0, 1.0, "D5", 0.48), (9.0, 1.0, "E5", 0.50), (10.0, 2.0, "D5", 0.46),
    # compasso 3 (Am)
    (12.0, 0.5, "C5", 0.46), (12.5, 0.5, "E5", 0.48), (13.0, 1.0, "A5", 0.54),
    (14.0, 1.0, "G5", 0.50), (15.0, 1.0, "E5", 0.46),
    # compasso 4 (F)
    (16.0, 1.0, "F5", 0.50), (17.0, 1.0, "E5", 0.48), (18.0, 2.0, "D5", 0.46),
    # compasso 5 (G) - ponte para a parte animada
    (20.0, 1.0, "D5", 0.46), (21.0, 1.0, "C5", 0.46), (22.0, 1.0, "D5", 0.48),
    (23.0, 1.0, "E5", 0.50),
    # compasso 6 (C) - o desenho ganha vida
    (24.0, 0.5, "E5", 0.56), (24.5, 0.5, "G5", 0.58), (25.0, 1.0, "C6", 0.62),
    (26.0, 0.5, "B5", 0.54), (26.5, 0.5, "A5", 0.54), (27.0, 1.0, "G5", 0.56),
    # compasso 7 (F)
    (28.0, 0.5, "A5", 0.56), (28.5, 0.5, "F5", 0.54), (29.0, 1.0, "A5", 0.58),
    (30.0, 1.0, "G5", 0.56), (31.0, 1.0, "F5", 0.54),
    # compasso 8 (G)
    (32.0, 0.5, "G5", 0.56), (32.5, 0.5, "B5", 0.58), (33.0, 1.0, "D6", 0.62),
    (34.0, 1.0, "C6", 0.58), (35.0, 1.0, "B5", 0.56),
    # compasso 9 (C)
    (36.0, 1.0, "C6", 0.60), (37.0, 1.0, "A5", 0.56), (38.0, 0.5, "G5", 0.54),
    (38.5, 0.5, "E5", 0.52), (39.0, 1.0, "G5", 0.54),
    # compasso 10 - acorde final
    (40.0, 2.0, "C6", 0.58), (40.0, 2.0, "E5", 0.40), (40.0, 2.0, "G5", 0.40),
    (40.0, 2.0, "C5", 0.44),
]

# acordes por compasso (compasso 0 = silencio)
ACORDES = {
    1: ("C4", "E4", "G4"), 2: ("B3", "D4", "G4"), 3: ("A3", "C4", "E4"),
    4: ("A3", "C4", "F4"), 5: ("B3", "D4", "G4"), 6: ("C4", "E4", "G4"),
    7: ("A3", "C4", "F4"), 8: ("B3", "D4", "G4"), 9: ("C4", "E4", "G4"),
}
BAIXO = {1: "C3", 2: "G2", 3: "A2", 4: "F2", 5: "G2",
         6: "C3", 7: "F2", 8: "G2", 9: "C3", 10: "C3"}

# gliçando curtinho quando o desenho ganha vida (12 s)
SPARKLE = [(23.4 + i * 0.15, 0.4, n, 0.20) for i, n in
           enumerate(["C5", "E5", "G5", "C6"])]


# ---------------------------------------------------------------- sintetizador
def env(n, attack, tau):
    t = np.arange(n) / SR
    e = np.exp(-t / tau)
    a = max(1, int(attack * SR))
    if a < n:
        e[:a] *= np.linspace(0.0, 1.0, a)
    return e


def caixinha(f, dur_s, vel):
    """Timbre de caixinha de musica: harmonicos com decaimento rapido."""
    n = int(min(dur_s + 1.6, 3.0) * SR)
    t = np.arange(n) / SR
    tau = max(0.28, min(1.15, dur_s * 0.55 + 0.32))
    out = np.zeros(n)
    for h, a, dt in ((1.0, 1.0, 1.0), (2.0, 0.38, 0.75), (3.0, 0.20, 0.55),
                     (4.2, 0.10, 0.40), (5.4, 0.05, 0.32)):
        out += a * np.sin(2 * math.pi * f * h * t) * env(n, 0.004, tau * dt)
    return out * vel * 0.30


def baixo(f, dur_s, vel):
    n = int(min(dur_s + 0.9, 2.2) * SR)
    t = np.arange(n) / SR
    e = env(n, 0.010, 0.55)
    out = np.sin(2 * math.pi * f * t) + 0.28 * np.sin(4 * math.pi * f * t)
    return out * e * vel * 0.30


def chocalho(vel):
    n = int(0.075 * SR)
    rng = np.random.default_rng(7)
    x = rng.normal(0, 1, n)
    x = np.convolve(x, [1.0, -0.72], mode="same")     # deixa mais agudo
    return x * env(n, 0.002, 0.022) * vel * 0.09


def bumbo(vel):
    n = int(0.20 * SR)
    t = np.arange(n) / SR
    f = 105 * np.exp(-t / 0.035) + 46
    x = np.sin(2 * math.pi * np.cumsum(f) / SR)
    return x * env(n, 0.003, 0.075) * vel * 0.42


def add(buf, sig, t0):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def eco(x, atrasos, ganhos):
    out = x.copy()
    for d, g in zip(atrasos, ganhos):
        k = int(d * SR)
        out[k:] += x[:-k] * g
    return out


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "trilha.wav")
    n = int(DURATION * SR)
    mel = np.zeros(n + SR)
    acomp = np.zeros(n + SR)
    perc = np.zeros(n + SR)

    for b, d, note, v in MELODIA + SPARKLE:
        add(mel, caixinha(freq(note), d * SPB, v), b * SPB)

    for bar, notas in ACORDES.items():
        base = bar * 4
        if bar <= 5:                                   # parte calma
            for beat in (0.0, 2.0):
                for k, nome in enumerate(notas):
                    add(acomp, caixinha(freq(nome), 1.4, 0.17 - 0.02 * k),
                        (base + beat + k * 0.045) * SPB)
        else:                                          # parte animada
            for i, beat in enumerate((0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5)):
                nome = notas[i % 3] if i % 2 == 0 else notas[(i + 2) % 3]
                add(acomp, caixinha(freq(nome), 0.45, 0.16),
                    (base + beat) * SPB)

    for bar, nome in BAIXO.items():
        base = bar * 4
        for beat in (0.0, 2.0):
            add(acomp, baixo(freq(nome), 1.2, 0.55 if beat == 0 else 0.40),
                (base + beat) * SPB)

    for bar in range(6, 10):                           # percussao leve
        base = bar * 4
        for i in range(8):
            add(perc, chocalho(1.0 if i % 2 == 0 else 0.55),
                (base + i * 0.5) * SPB)
        for beat in (0.0, 2.0):
            add(perc, bumbo(0.9 if beat == 0 else 0.7), (base + beat) * SPB)

    seco = mel + acomp + perc
    molhado = eco(seco, [0.090, 0.150, 0.235], [0.22, 0.13, 0.07])
    mix = (0.78 * seco + 0.34 * molhado)[:n]

    # estereo com uma leve abertura
    left = mix + 0.10 * np.concatenate([np.zeros(int(0.013 * SR)), mix])[:n]
    right = mix + 0.10 * np.concatenate([np.zeros(int(0.021 * SR)), mix])[:n]
    st = np.stack([left, right], axis=1)
    st /= max(1e-9, np.abs(st).max()) / 0.88

    fi, fo = int(0.30 * SR), int(1.30 * SR)
    st[:fi] *= np.linspace(0, 1, fi)[:, None]
    st[-fo:] *= (np.linspace(1, 0, fo) ** 1.6)[:, None]

    with wave.open(out_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())
    print(f"pronto: {out_path}  ({DURATION:.1f}s, pico {np.abs(st).max():.2f})")


if __name__ == "__main__":
    main()
