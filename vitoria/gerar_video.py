# -*- coding: utf-8 -*-
"""
Gera um video animado a partir do desenho da Vitoria.

O desenho original (feito no computador com formas: circulo, quadrados,
retangulos e triangulos) foi remontado aqui em vetores. O video mostra o
desenho sendo feito traco a traco e depois o personagem "ganhando vida".

Uso:  python3 gerar_video.py [saida.mp4]
Requer: pillow, imageio-ffmpeg  (pip install pillow imageio-ffmpeg)
"""
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

# ---------------------------------------------------------------- configuracao
W, H = 900, 1120          # resolucao final
SS = 2                    # supersampling (antialiasing)
FPS = 30
INK = (24, 24, 28)
RED = (222, 28, 28)
PAPER = (253, 252, 248)
BACKDROP = (238, 236, 231)

FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"
FONT_CANDIDATES = [
    os.path.join(FONT_DIR, "NothingYouCouldDo-Regular.ttf"),
    os.path.join(FONT_DIR, "Outfit-Bold.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def load_font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


# ------------------------------------------------- geometria (espaco original)
# Coordenadas medidas sobre o desenho original (imagem de ~628x733).
def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]


def ellipse_pts(cx, cy, rx, ry, n=160):
    return [(cx + rx * math.cos(2 * math.pi * i / n - math.pi / 2),
             cy + ry * math.sin(2 * math.pi * i / n - math.pi / 2))
            for i in range(n + 1)]


def rrect_pts(x0, y0, x1, y1, r, n=10):
    pts = []

    def arc(cx, cy, a0, a1):
        for i in range(n + 1):
            a = a0 + (a1 - a0) * i / n
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    pts.append((x0 + r, y0))
    pts.append((x1 - r, y0))
    arc(x1 - r, y0 + r, -math.pi / 2, 0.0)
    pts.append((x1, y1 - r))
    arc(x1 - r, y1 - r, 0.0, math.pi / 2)
    pts.append((x0 + r, y1))
    arc(x0 + r, y1 - r, math.pi / 2, math.pi)
    pts.append((x0, y0 + r))
    arc(x0 + r, y0 + r, math.pi, 3 * math.pi / 2)
    return pts


EYES_OPEN = [rect(304, 235, 325, 259), rect(310, 241, 319, 253),
             rect(366, 235, 387, 259), rect(372, 241, 381, 253)]
EYES_SHUT = [[(302, 248), (327, 248)], [(364, 248), (389, 248)]]

PARTS = [
    dict(key="cabeca", group="head", color=INK, w=4.2, dur=1.15,
         strokes=[ellipse_pts(340, 246, 68, 62)]),
    dict(key="olhos", group="head", color=INK, w=3.4, dur=0.85,
         strokes=EYES_OPEN),
    dict(key="aba", group="head", color=INK, w=4.2, dur=0.95,
         strokes=[rrect_pts(224, 148, 462, 221, 30)]),
    dict(key="chapeu", group="head", color=RED, w=4.2, dur=1.05,
         strokes=[[(347, 68), (455, 215), (238, 215), (347, 68)]]),
    dict(key="corpo", group="body", color=INK, w=4.2, dur=1.05,
         strokes=[rect(250, 318, 432, 533)]),
    dict(key="braco_esq", group="armL", color=INK, w=4.2, dur=0.7,
         strokes=[rrect_pts(156, 364, 274, 397, 16)]),
    dict(key="braco_dir", group="armR", color=INK, w=4.2, dur=0.7,
         strokes=[rrect_pts(410, 362, 517, 395, 16)]),
    dict(key="saia", group="body", color=INK, w=4.2, dur=1.0,
         strokes=[[(340, 425), (460, 595), (219, 595), (340, 425)]]),
    dict(key="perna_esq", group="legL", color=INK, w=4.2, dur=0.8,
         strokes=[rrect_pts(265, 516, 321, 684, 26)]),
    dict(key="perna_dir", group="legR", color=INK, w=4.2, dur=0.8,
         strokes=[rrect_pts(366, 516, 415, 684, 26)]),
]

GAP = 0.12          # respiro entre um traco e outro
T_TITLE = 1.35      # titulo aparecendo
T_PAUSE = 0.40      # pausa depois do desenho pronto
T_ALIVE = 8.0       # desenho "ganhando vida"
T_END = 1.0         # respiro final

T_DRAW0 = T_TITLE
DRAW_LEN = sum(p["dur"] + GAP for p in PARTS)
T_ALIVE0 = T_DRAW0 + DRAW_LEN + T_PAUSE
DURATION = T_ALIVE0 + T_ALIVE + T_END

# ------------------------------------------------------------------ transforms
SCALE = 1.30
SRC_C = (340.0, 375.0)
DST_C = (450.0, 582.0)


def to_canvas(p):
    return ((p[0] - SRC_C[0]) * SCALE + DST_C[0],
            (p[1] - SRC_C[1]) * SCALE + DST_C[1])


def rotate(p, c, ang):
    s, co = math.sin(ang), math.cos(ang)
    dx, dy = p[0] - c[0], p[1] - c[1]
    return (c[0] + dx * co - dy * s, c[1] + dx * s + dy * co)


SHOULDER_L = (274.0, 380.0)
SHOULDER_R = (410.0, 378.0)
HIP_L = (293.0, 520.0)
HIP_R = (390.0, 520.0)
NECK = (340.0, 312.0)


def anim_point(p, group, ta):
    """Transforma um ponto (espaco do desenho) na fase 'ganhando vida'."""
    if ta is None:
        return p
    ease = min(1.0, ta / 0.6)                       # entra suave
    hop = -11.0 * abs(math.sin(2 * math.pi * 0.85 * ta)) * ease
    wave = math.sin(2 * math.pi * 1.15 * ta) * ease
    sway = math.sin(2 * math.pi * 0.85 * ta) * ease

    if group == "armL":
        p = rotate(p, SHOULDER_L, math.radians(34.0) * wave)
    elif group == "armR":
        p = rotate(p, SHOULDER_R, math.radians(-34.0) * wave)
    elif group == "legL":
        p = rotate(p, HIP_L, math.radians(4.0) * sway)
    elif group == "legR":
        p = rotate(p, HIP_R, math.radians(-4.0) * sway)
    elif group == "head":
        p = rotate(p, NECK, math.radians(6.0) * sway)
        p = (p[0], p[1] - 4.0 * abs(math.sin(2 * math.pi * 0.85 * ta)) * ease)

    return (p[0], p[1] + hop)


# ------------------------------------------------------------------- desenho
def seg_lengths(pts):
    out, total = [], 0.0
    for a, b in zip(pts, pts[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        out.append(d)
        total += d
    return out, total


for part in PARTS:
    part["_len"] = []
    part["_tot"] = 0.0
    for s in part["strokes"]:
        L, tot = seg_lengths(s)
        part["_len"].append((L, tot))
        part["_tot"] += tot


def partial(pts, lens, want):
    """Recorta a polilinha nos primeiros `want` de comprimento."""
    if want <= 0:
        return []
    acc, out = 0.0, [pts[0]]
    for i, d in enumerate(lens):
        if acc + d >= want:
            f = (want - acc) / d if d else 1.0
            a, b = pts[i], pts[i + 1]
            out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
            return out
        acc += d
        out.append(pts[i + 1])
    return out


def paper_base():
    img = Image.new("RGBA", (W * SS, H * SS), BACKDROP + (255,))
    d = ImageDraw.Draw(img, "RGBA")
    m = 26 * SS
    # sombra suave da folha
    for i in range(14, 0, -1):
        a = int(7 * (1 - i / 14.0)) + 3
        d.rounded_rectangle([m - i, m - i + 6, W * SS - m + i, H * SS - m + i + 6],
                            radius=18 * SS + i, fill=(120, 116, 108, a))
    d.rounded_rectangle([m, m, W * SS - m, H * SS - m],
                        radius=18 * SS, fill=PAPER + (255,))
    return img


BASE = paper_base()
F_TITLE = load_font(int(62 * SS))
F_NAME = load_font(int(52 * SS))


def heart(cx, cy, s, ang=0.0):
    pts = []
    for i in range(41):
        th = 2 * math.pi * i / 40
        x = 16 * math.sin(th) ** 3
        y = -(13 * math.cos(th) - 5 * math.cos(2 * th)
              - 2 * math.cos(3 * th) - math.cos(4 * th))
        x, y = x * s / 16.0, y * s / 16.0
        c, sn = math.cos(ang), math.sin(ang)
        pts.append((cx + x * c - y * sn, cy + x * sn + y * c))
    return pts


HEART_COLORS = [(233, 76, 106), (247, 154, 60), (94, 176, 214),
                (126, 196, 116), (196, 118, 208)]


def draw_text(d, text, font, cx, y, color, alpha):
    if alpha <= 0.003:
        return
    box = d.textbbox((0, 0), text, font=font)
    d.text((cx - (box[2] - box[0]) / 2 - box[0], y), text, font=font,
           fill=color + (int(255 * min(1.0, alpha)),))


def render(t):
    img = BASE.copy()
    d = ImageDraw.Draw(img, "RGBA")

    alive = t >= T_ALIVE0
    ta = (t - T_ALIVE0) if alive else None

    # --- corações e brilhos subindo (fase final)
    if alive:
        for i in range(14):
            phase = (ta * 0.30 + i / 14.0) % 1.0
            if phase < 0.02:
                continue
            side = -1 if i % 2 else 1
            bx = 450 + side * (250 + 62 * abs(math.sin(i * 2.3)))
            by = 1030 - phase * 830
            bx += 34 * math.sin(phase * 5.0 + i)
            a = math.sin(math.pi * phase) * 0.85 * min(1.0, ta / 1.2)
            s = (26 + 12 * math.sin(i * 1.7)) * SS
            col = HEART_COLORS[i % len(HEART_COLORS)]
            pts = [(x * SS, y * SS) for x, y in
                   heart(bx, by, s / SS, math.sin(phase * 3 + i) * 0.35)]
            d.polygon(pts, fill=col + (int(255 * a),))

    # --- o desenho
    tip = None
    for i, part in enumerate(PARTS):
        t0 = T_DRAW0 + sum(p["dur"] + GAP for p in PARTS[:i])
        f = 0.0 if t <= t0 else min(1.0, (t - t0) / part["dur"])
        if f <= 0:
            continue
        f = f * f * (3 - 2 * f) if f < 1 else 1.0        # smoothstep

        strokes = part["strokes"]
        lens = part["_len"]
        if part["key"] == "olhos" and alive:
            blink = (ta % 2.6) < 0.15 or (ta % 2.6) > 2.5
            if blink:
                strokes = EYES_SHUT
                lens = [seg_lengths(s) for s in EYES_SHUT]

        want = f * sum(l[1] for l in lens)
        for pts, (L, tot) in zip(strokes, lens):
            take = max(0.0, min(tot, want))
            want -= take
            if take <= 0:
                continue
            sub = partial(pts, L, take)
            sub = [to_canvas(anim_point(p, part["group"], ta)) for p in sub]
            if len(sub) < 2:
                continue
            d.line([(x * SS, y * SS) for x, y in sub], fill=part["color"] + (255,),
                   width=int(round(part["w"] * SS)), joint="curve")
            if f < 1.0:
                tip = (sub[-1], part["color"])
            if want <= 0:
                break

    # --- pontinha do "lapis"
    if tip:
        (x, y), col = tip
        r = 9 * SS
        d.ellipse([x * SS - r, y * SS - r, x * SS + r, y * SS + r],
                  fill=col + (70,))
        r = 4.5 * SS
        d.ellipse([x * SS - r, y * SS - r, x * SS + r, y * SS + r],
                  fill=col + (255,))

    # --- textos
    a_title = min(1.0, t / T_TITLE)
    a_title = a_title * a_title * (3 - 2 * a_title)
    draw_text(d, "O desenho da Vitória", F_TITLE, W * SS / 2, 88 * SS,
              (52, 50, 58), a_title)
    if alive:
        draw_text(d, "feito com amor", F_NAME, W * SS / 2, 1012 * SS,
                  (196, 44, 74), min(1.0, max(0.0, (ta - 0.5) / 1.0)))

    return img.convert("RGB").resize((W, H), Image.LANCZOS)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "desenho-da-vitoria.mp4")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    nframes = int(DURATION * FPS)
    cmd = [ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for i in range(nframes):
        frame = render(i / FPS)
        proc.stdin.write(frame.tobytes())
        if i == int((T_ALIVE0 + 1.6) * FPS):
            frame.save(os.path.join(os.path.dirname(out), "capa.png"))
        if i % 60 == 0:
            print(f"  frame {i}/{nframes}", flush=True)
    proc.stdin.close()
    proc.wait()
    print(f"pronto: {out}  ({DURATION:.1f}s, {nframes} frames)")


if __name__ == "__main__":
    main()
