"""Tema visual L3ST3R: vestíbulo de un banco clásico + capa tecnológica estilo JARVIS.

Todo el diseño se genera con código (SVG y CSS): no hay imágenes externas que subir.
"""
import base64
import math
import random

import streamlit as st

# ----------------------------------------------------------------------------
# Fondo: vestíbulo de banco en perspectiva (SVG generado)
# ----------------------------------------------------------------------------
_F, _CX, _CY = 900.0, 800.0, 380.0          # cámara: "focal", centro de fuga
_XW, _XC = 3.5, 3.1                          # X de la pared y de las columnas
_YC, _YF = -2.6, 1.6                         # altura del techo y del piso
_ZN, _ZF = 2.2, 14.0                         # profundidad cercana y fondo del salón
_COLS_Z = [4.0, 6.6, 9.2, 11.8]              # profundidad de cada columna


def _p(x, y, z):
    return _CX + _F * x / z, _CY + _F * y / z


def _pts(lista):
    return " ".join(f"{a:.1f},{b:.1f}" for a, b in lista)


def _poly(lista, **atr):
    extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in atr.items())
    return f'<polygon points="{_pts(lista)}" {extra}/>'


def _lobby_svg() -> str:
    o = []
    o.append("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMin slice">
<defs>
 <linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b1120"/><stop offset=".55" stop-color="#1d160d"/><stop offset="1" stop-color="#0a0c12"/></linearGradient>
 <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b1d27"/><stop offset=".45" stop-color="#15120e"/><stop offset="1" stop-color="#07080c"/></linearGradient>
 <linearGradient id="ceil" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#04060b"/><stop offset="1" stop-color="#241a0c"/></linearGradient>
 <linearGradient id="shaft" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2a2317"/><stop offset=".2" stop-color="#b8a377"/><stop offset=".42" stop-color="#f0e4c5"/><stop offset=".7" stop-color="#8e7e5b"/><stop offset="1" stop-color="#211b11"/></linearGradient>
 <linearGradient id="gold" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7d6119"/><stop offset=".5" stop-color="#f5df9d"/><stop offset="1" stop-color="#7d6119"/></linearGradient>
 <linearGradient id="win" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1c2f52"/><stop offset=".6" stop-color="#5b4a52"/><stop offset="1" stop-color="#d79a52"/></linearGradient>
 <linearGradient id="refl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f0e4c5" stop-opacity=".30"/><stop offset="1" stop-color="#f0e4c5" stop-opacity="0"/></linearGradient>
 <linearGradient id="steel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8a909c"/><stop offset=".5" stop-color="#3a3e48"/><stop offset="1" stop-color="#1b1d24"/></linearGradient>
 <radialGradient id="glow"><stop offset="0" stop-color="#ffe2a3" stop-opacity=".95"/><stop offset=".35" stop-color="#ffb347" stop-opacity=".28"/><stop offset="1" stop-color="#ffb347" stop-opacity="0"/></radialGradient>
 <radialGradient id="pool"><stop offset="0" stop-color="#ffcf7a" stop-opacity=".42"/><stop offset="1" stop-color="#ffcf7a" stop-opacity="0"/></radialGradient>
 <radialGradient id="holo"><stop offset="0" stop-color="#4fd8ff" stop-opacity=".30"/><stop offset="1" stop-color="#4fd8ff" stop-opacity="0"/></radialGradient>
</defs>
<rect width="1600" height="900" fill="url(#wall)"/>
""")

    # --- Muro del fondo con la bóveda ---
    x0, y0 = _p(-_XW, _YC, _ZF)
    x1, y1 = _p(_XW, _YF, _ZF)
    o.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}" fill="#17120b" stroke="#c9a24b" stroke-opacity=".5" stroke-width="2"/>')
    o.append(f'<ellipse cx="{_CX}" cy="{_CY+20}" rx="260" ry="190" fill="url(#glow)" opacity=".55"/>')
    vy = _p(0, 0.3, _ZF)[1]
    o.append(f'<circle cx="{_CX}" cy="{vy:.1f}" r="78" fill="#1a1710" stroke="url(#gold)" stroke-width="5"/>')
    o.append(f'<circle cx="{_CX}" cy="{vy:.1f}" r="68" fill="url(#steel)"/>')
    o.append(f'<circle cx="{_CX}" cy="{vy:.1f}" r="54" fill="none" stroke="#d4af37" stroke-width="2.5"/>')
    o.append(f'<circle cx="{_CX}" cy="{vy:.1f}" r="40" fill="none" stroke="#d4af37" stroke-opacity=".6" stroke-width="1.5"/>')
    for k in range(6):
        a = k * math.pi / 3
        o.append(f'<line x1="{_CX+12*math.cos(a):.1f}" y1="{vy+12*math.sin(a):.1f}" x2="{_CX+52*math.cos(a):.1f}" y2="{vy+52*math.sin(a):.1f}" stroke="#d4af37" stroke-width="4" stroke-linecap="round"/>')
    for k in range(16):
        a = k * math.pi / 8
        o.append(f'<circle cx="{_CX+62*math.cos(a):.1f}" cy="{vy+62*math.sin(a):.1f}" r="2.2" fill="#e9d38c"/>')
    o.append(f'<circle cx="{_CX}" cy="{vy:.1f}" r="13" fill="url(#gold)" stroke="#4a3a0c" stroke-width="1.5"/>')
    o.append(f'<circle cx="{_CX}" cy="{vy:.1f}" r="96" fill="none" stroke="#4fd8ff" stroke-opacity=".55" stroke-width="1.5" stroke-dasharray="3 9"/>')
    o.append(f'<circle cx="{_CX}" cy="{vy:.1f}" r="108" fill="none" stroke="#4fd8ff" stroke-opacity=".28" stroke-width="1" stroke-dasharray="30 12 4 12"/>')

    # --- Paredes laterales ---
    for lado in (-1, 1):
        o.append(_poly([_p(lado * _XW, _YC, _ZN), _p(lado * _XW, _YF, _ZN), _p(lado * _XW, _YF, _ZF), _p(lado * _XW, _YC, _ZF)],
                       fill="#14100a", fill_opacity=".92"))
        # ventanales con arco entre columnas
        for i in range(len(_COLS_Z) - 1):
            za, zb = _COLS_Z[i] + 0.55, _COLS_Z[i + 1] - 0.55
            zm, dz = (za + zb) / 2, (zb - za) / 2
            pts = [_p(lado * _XW, 0.55, za), _p(lado * _XW, -0.9, za)]
            for k in range(0, 13):
                t = math.pi * k / 12
                pts.append(_p(lado * _XW, -0.9 - 1.0 * math.sin(t), zm - dz * math.cos(t)))
            pts += [_p(lado * _XW, -0.9, zb), _p(lado * _XW, 0.55, zb)]
            o.append(_poly(pts, fill="url(#win)", stroke="#d4af37", stroke_width="2", stroke_opacity=".85"))
            o.append(_poly(pts, fill="url(#glow)", fill_opacity=".35"))
            a1, a2 = _p(lado * _XW, 0.55, zm), _p(lado * _XW, -1.9, zm)
            o.append(f'<line x1="{a1[0]:.1f}" y1="{a1[1]:.1f}" x2="{a2[0]:.1f}" y2="{a2[1]:.1f}" stroke="#d4af37" stroke-opacity=".7" stroke-width="1.5"/>')
            b1, b2 = _p(lado * _XW, -0.3, za), _p(lado * _XW, -0.3, zb)
            o.append(f'<line x1="{b1[0]:.1f}" y1="{b1[1]:.1f}" x2="{b2[0]:.1f}" y2="{b2[1]:.1f}" stroke="#d4af37" stroke-opacity=".6" stroke-width="1.5"/>')
        # cornisas doradas
        for y, op in ((_YC, .9), (_YC + 0.35, .55), (_YF - 0.0, .4)):
            a, b = _p(lado * _XW, y, _ZN), _p(lado * _XW, y, _ZF)
            o.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#d4af37" stroke-opacity="{op}" stroke-width="2"/>')

    # --- Techo con casetones y franja de luz ---
    o.append(_poly([_p(-_XW, _YC, _ZN), _p(_XW, _YC, _ZN), _p(_XW, _YC, _ZF), _p(-_XW, _YC, _ZF)], fill="url(#ceil)"))
    for x in (-_XW, -_XW / 2, 0, _XW / 2, _XW):
        a, b = _p(x, _YC, _ZN), _p(x, _YC, _ZF)
        o.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#d4af37" stroke-opacity=".34" stroke-width="1.5"/>')
    z = _ZN
    while z <= _ZF:
        a, b = _p(-_XW, _YC, z), _p(_XW, _YC, z)
        o.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#d4af37" stroke-opacity=".30" stroke-width="1.5"/>')
        z += 1.3
    o.append(_poly([_p(-0.45, _YC, _ZN), _p(0.45, _YC, _ZN), _p(0.45, _YC, _ZF), _p(-0.45, _YC, _ZF)], fill="#ffd68a", fill_opacity=".18"))

    # --- Piso de mármol (damero) con reflejos ---
    o.append(_poly([_p(-_XW, _YF, _ZN), _p(_XW, _YF, _ZN), _p(_XW, _YF, _ZF), _p(-_XW, _YF, _ZF)], fill="url(#floor)"))
    nx, paso = 8, 2 * _XW / 8
    z = _ZN
    fila = 0
    while z < _ZF - 0.01:
        z2 = min(z + 0.9, _ZF)
        for c in range(nx):
            xa, xb = -_XW + c * paso, -_XW + (c + 1) * paso
            claro = (c + fila) % 2 == 0
            o.append(_poly([_p(xa, _YF, z), _p(xb, _YF, z), _p(xb, _YF, z2), _p(xa, _YF, z2)],
                           fill="#f0e4c5" if claro else "#000000", fill_opacity=".05" if claro else ".22",
                           stroke="#d4af37", stroke_opacity=".16", stroke_width="1"))
        z, fila = z2, fila + 1
    o.append(f'<ellipse cx="{_CX}" cy="{_p(0, _YF, 6.5)[1]:.1f}" rx="620" ry="86" fill="url(#pool)"/>')
    # anillos holográficos sobre el piso (capa "JARVIS")
    py = _p(0, _YF, 6.5)[1]
    for rx, ry, dash, op in ((380, 50, "4 10", .55), (290, 38, "18 8 3 8", .4), (205, 27, "2 8", .55)):
        o.append(f'<ellipse cx="{_CX}" cy="{py:.1f}" rx="{rx}" ry="{ry}" fill="none" stroke="#4fd8ff" stroke-opacity="{op}" stroke-width="1.6" stroke-dasharray="{dash}"/>')
    o.append(f'<ellipse cx="{_CX}" cy="{py:.1f}" rx="380" ry="50" fill="url(#holo)" opacity=".5"/>')
    o.append(f'<line x1="{_CX-420}" y1="{py:.1f}" x2="{_CX+420}" y2="{py:.1f}" stroke="#4fd8ff" stroke-opacity=".3" stroke-width="1"/>')

    # --- Arañas (candelabros) ---
    for zc in (11.0, 7.8, 4.6):
        px, ptop = _p(0, _YC, zc)
        bx, by = _p(0, -1.7, zc)
        r = _F * 0.30 / zc
        o.append(f'<line x1="{px:.1f}" y1="{ptop:.1f}" x2="{bx:.1f}" y2="{by - r*0.4:.1f}" stroke="#d4af37" stroke-opacity=".8" stroke-width="{max(1, r*0.06):.1f}"/>')
        o.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{r*6:.1f}" fill="url(#glow)"/>')
        o.append(f'<ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="{r*1.7:.1f}" ry="{r*0.55:.1f}" fill="none" stroke="url(#gold)" stroke-width="{max(1.2, r*0.12):.1f}"/>')
        for k in range(9):
            a = math.pi * (k / 8)
            cxk = bx + r * 1.6 * math.cos(a) * (1 if k % 2 == 0 else 0.8)
            o.append(f'<line x1="{cxk:.1f}" y1="{by + r*0.45:.1f}" x2="{cxk:.1f}" y2="{by + r*(1.2 + 0.3 * math.sin(k)):.1f}" stroke="#ffe9b8" stroke-opacity=".85" stroke-width="{max(.8, r*0.07):.1f}"/>')
        o.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{r*0.6:.1f}" fill="#fff4d1"/>')

    # --- Columnas de mármol (de lejos a cerca) ---
    for zc in reversed(_COLS_Z):
        bruma = min(0.55, (zc - 4.0) / 16.0)
        for lado in (-1, 1):
            xc, yb = _p(lado * _XC, _YF, zc)
            _, yt = _p(lado * _XC, _YC, zc)
            rp = _F * 0.30 / zc
            hc = _F * 0.40 / zc
            o.append(f'<rect x="{xc-rp:.1f}" y="{yb:.1f}" width="{2*rp:.1f}" height="{(yb-yt)*0.17:.1f}" fill="url(#refl)"/>')
            o.append(f'<rect x="{xc-rp:.1f}" y="{yt:.1f}" width="{2*rp:.1f}" height="{yb-yt:.1f}" fill="url(#shaft)"/>')
            for fr in (0.22, 0.4, 0.6, 0.78):
                o.append(f'<line x1="{xc-rp+2*rp*fr:.1f}" y1="{yt+hc:.1f}" x2="{xc-rp+2*rp*fr:.1f}" y2="{yb-hc:.1f}" stroke="#000" stroke-opacity=".22" stroke-width="{max(.6, rp*0.035):.1f}"/>')
            o.append(f'<rect x="{xc-rp*1.5:.1f}" y="{yt:.1f}" width="{3*rp:.1f}" height="{hc:.1f}" fill="url(#gold)" stroke="#4a3a0c" stroke-opacity=".6" stroke-width="1"/>')
            o.append(f'<rect x="{xc-rp*1.7:.1f}" y="{yt:.1f}" width="{3.4*rp:.1f}" height="{hc*0.28:.1f}" fill="url(#gold)"/>')
            o.append(f'<rect x="{xc-rp*1.45:.1f}" y="{yb-hc*0.85:.1f}" width="{2.9*rp:.1f}" height="{hc*0.85:.1f}" fill="url(#gold)" stroke="#4a3a0c" stroke-opacity=".6" stroke-width="1"/>')
            # filo de luz cian en el borde interior (toque tecnológico)
            xi = xc + rp if lado < 0 else xc - rp
            o.append(f'<line x1="{xi:.1f}" y1="{yt+hc:.1f}" x2="{xi:.1f}" y2="{yb-hc:.1f}" stroke="#4fd8ff" stroke-opacity=".12" stroke-width="{max(4, rp*0.16):.1f}"/>')
            o.append(f'<line x1="{xi:.1f}" y1="{yt+hc:.1f}" x2="{xi:.1f}" y2="{yb-hc:.1f}" stroke="#7fe6ff" stroke-opacity=".7" stroke-width="{max(1, rp*0.03):.1f}"/>')
            if bruma > 0.02:
                o.append(f'<rect x="{xc-rp*1.7:.1f}" y="{yt:.1f}" width="{3.4*rp:.1f}" height="{yb-yt:.1f}" fill="#070a12" fill-opacity="{bruma:.2f}"/>')

    # --- Partículas (polvo de luz) ---
    rnd = random.Random(7)
    for _ in range(46):
        x, y = rnd.uniform(0, 1600), rnd.uniform(0, 760)
        col = "#ffe2a3" if rnd.random() < 0.6 else "#7fe6ff"
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(.8, 2.2):.1f}" fill="{col}" fill-opacity="{rnd.uniform(.25, .75):.2f}"/>')

    o.append("</svg>")
    return "".join(o)


@st.cache_data(show_spinner=False)
def fondo_base64() -> str:
    return base64.b64encode(_lobby_svg().encode("utf-8")).decode("ascii")


# ----------------------------------------------------------------------------
# Logotipo: frontón y columnas dentro de anillos de un HUD
# ----------------------------------------------------------------------------
LOGO_SVG = """
<svg class="hud-logo" width="84" height="84" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f5df9d"/><stop offset="1" stop-color="#9a7a22"/></linearGradient></defs>
  <circle cx="50" cy="50" r="47" fill="rgba(6,10,18,.65)" stroke="#d4af37" stroke-opacity=".5" stroke-width="1"/>
  <circle class="ring-a" cx="50" cy="50" r="43" fill="none" stroke="#4fd8ff" stroke-width="1.8" stroke-dasharray="7 5 30 5"/>
  <circle class="ring-b" cx="50" cy="50" r="37" fill="none" stroke="#d4af37" stroke-width="1.2" stroke-dasharray="2 6"/>
  <polygon points="27,42 50,27 73,42" fill="none" stroke="url(#lg)" stroke-width="2.4" stroke-linejoin="round"/>
  <rect x="29" y="42" width="42" height="3.6" fill="url(#lg)"/>
  <rect x="33" y="47.5" width="4.2" height="19" fill="url(#lg)"/><rect x="42.2" y="47.5" width="4.2" height="19" fill="url(#lg)"/>
  <rect x="53.6" y="47.5" width="4.2" height="19" fill="url(#lg)"/><rect x="62.8" y="47.5" width="4.2" height="19" fill="url(#lg)"/>
  <rect x="28" y="67" width="44" height="4" fill="url(#lg)"/>
  <circle class="core" cx="50" cy="35.5" r="2.6" fill="#4fd8ff"/>
</svg>
"""


def header_html(nombre: str, lema: str) -> str:
    return f"""
    <div class="hud-header">
        {LOGO_SVG}
        <div>
            <div class="hud-brand">{nombre}</div>
            <div class="hud-sub">{lema}</div>
        </div>
        <div class="hud-status">SISTEMAS EN LÍNEA</div>
    </div>
    <div class="hud-line"><span>◆</span></div>
    """


# ----------------------------------------------------------------------------
# Hoja de estilos
# ----------------------------------------------------------------------------
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;900&family=Cormorant+Garamond:wght@600;700&family=Exo+2:wght@400;500;600&family=Share+Tech+Mono&display=swap');

:root { --gold:#d4af37; --gold-l:#f3dc9a; --gold-d:#8a6d1f; --ivory:#efe8d8; --mute:#a3acbf;
        --cyan:#4fd8ff; --navy:#07090f; --line:rgba(212,175,55,.34); --line-c:rgba(79,216,255,.34);
        --panel:rgba(9,13,23,.80); --up:#5eead4; }

/* ---------- Fondo: vestíbulo del banco ---------- */
.stApp {
    background-color: var(--navy);
    background-image:
        radial-gradient(ellipse at 50% 38%, rgba(4,6,12,0) 0%, rgba(4,6,12,.55) 70%, rgba(2,3,7,.92) 100%),
        linear-gradient(180deg, rgba(4,6,12,.08) 0%, rgba(4,6,12,.38) 45%, rgba(4,6,12,.82) 100%),
        url("data:image/svg+xml;base64,__FONDO__");
    background-size: cover, cover, cover;
    background-position: center top, center top, center top;
    background-attachment: fixed, fixed, fixed;
    background-repeat: no-repeat;
    font-family: 'Exo 2', sans-serif; font-size: 1rem; color: var(--ivory);
}
[data-testid="stHeader"] { background: transparent; }
::selection { background: rgba(212,175,55,.35); }
* { scrollbar-width: thin; scrollbar-color: rgba(212,175,55,.45) transparent; }

/* Marcas de esquina (HUD) y barrido de luz */
.stApp::before {
    content:""; position:fixed; inset:10px; pointer-events:none; z-index:998;
    background:
      linear-gradient(var(--cyan),var(--cyan)) top left/30px 2px no-repeat, linear-gradient(var(--cyan),var(--cyan)) top left/2px 30px no-repeat,
      linear-gradient(var(--cyan),var(--cyan)) top right/30px 2px no-repeat, linear-gradient(var(--cyan),var(--cyan)) top right/2px 30px no-repeat,
      linear-gradient(var(--cyan),var(--cyan)) bottom left/30px 2px no-repeat, linear-gradient(var(--cyan),var(--cyan)) bottom left/2px 30px no-repeat,
      linear-gradient(var(--cyan),var(--cyan)) bottom right/30px 2px no-repeat, linear-gradient(var(--cyan),var(--cyan)) bottom right/2px 30px no-repeat;
    opacity:.55;
}
.stApp::after {
    content:""; position:fixed; left:0; right:0; top:-180px; height:180px; pointer-events:none; z-index:997;
    background: linear-gradient(180deg, transparent, rgba(79,216,255,.05), transparent);
    animation: barrido 11s linear infinite;
}
@keyframes barrido { from { transform: translateY(0); } to { transform: translateY(calc(100vh + 180px)); } }

/* ---------- Encabezado ---------- */
.hud-header { display:flex; align-items:center; gap:20px; margin: 4px 0 2px 0; animation: subir .7s ease both; }
.hud-logo { filter: drop-shadow(0 0 10px rgba(79,216,255,.45)) drop-shadow(0 0 6px rgba(212,175,55,.35)); flex-shrink:0; }
.ring-a { animation: giro 18s linear infinite; transform-box: fill-box; transform-origin:center; }
.ring-b { animation: giro 11s linear infinite reverse; transform-box: fill-box; transform-origin:center; }
.core { animation: latido 2.6s ease-in-out infinite; transform-box: fill-box; transform-origin:center; }
@keyframes giro { to { transform: rotate(360deg); } }
@keyframes latido { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:.45; transform:scale(.7); } }
@keyframes subir { from { opacity:0; transform: translateY(8px); } to { opacity:1; transform:none; } }
@keyframes brillo { to { background-position: 200% center; } }
.hud-brand {
    font-family:'Cinzel', 'Cormorant Garamond', serif; font-weight:900; font-size:3rem; line-height:1;
    letter-spacing:.3em; padding-left:.1em;
    background: linear-gradient(100deg, #8a6d1f 0%, #f3dc9a 30%, #fff6d2 48%, #d4af37 66%, #8a6d1f 100%);
    background-size: 220% auto; -webkit-background-clip:text; background-clip:text;
    -webkit-text-fill-color: transparent; color: transparent;
    animation: brillo 7s linear infinite; filter: drop-shadow(0 2px 12px rgba(212,175,55,.35));
}
.hud-sub { font-weight:500; color: var(--cyan); letter-spacing:.24em; text-transform:uppercase; font-size:.7rem; margin-top:9px; }
.hud-status { margin-left:auto; font-family:'Share Tech Mono', monospace; font-size:.72rem; color: var(--up);
              border:1px solid rgba(94,234,212,.4); border-radius:2px; padding:5px 12px; white-space:nowrap;
              background: rgba(8,30,28,.45); }
.hud-status:before { content:"●"; margin-right:7px; animation: latido 1.8s ease-in-out infinite; display:inline-block; }
.hud-line { position:relative; height:1px; margin:16px 0 12px 0;
            background: linear-gradient(90deg, var(--gold), var(--cyan) 55%, rgba(79,216,255,0)); }
.hud-line span { position:absolute; left:50%; top:-8px; font-size:.7rem; color: var(--gold); transform: translateX(-50%);
                 background: #070a12; padding: 0 8px; }
@media (max-width: 640px) { .hud-status { display:none; } .hud-brand { font-size:1.9rem; letter-spacing:.2em; } }

/* ---------- Cinta de cotizaciones ---------- */
.ticker { overflow:hidden; white-space:nowrap; border-top:1px solid var(--line); border-bottom:1px solid var(--line);
          background: linear-gradient(180deg, rgba(212,175,55,.10), rgba(212,175,55,.02)); padding:8px 0; margin:0 0 20px 0;
          font-family:'Share Tech Mono', monospace; font-size:.84rem; box-shadow: 0 0 22px rgba(212,175,55,.08); }
.ticker-track { display:inline-block; animation: cinta 55s linear infinite; }
.ticker:hover .ticker-track { animation-play-state: paused; }
@keyframes cinta { from { transform: translateX(0); } to { transform: translateX(-25%); } }
.tk b { color: var(--gold-l); font-weight:400; letter-spacing:.14em; margin-right:7px; }
.tk i { color: var(--up); font-style:normal; }
.tk em { color: var(--mute); font-style:normal; }
.sep { color: var(--gold); margin: 0 26px; opacity:.8; }

/* ---------- Mensajes del chat ---------- */
[data-testid="stChatMessage"] {
    position: relative; background: var(--panel); border:1px solid var(--line);
    border-left:3px solid var(--cyan); border-radius:2px; backdrop-filter: blur(7px);
    box-shadow: 0 8px 26px rgba(0,0,0,.35); animation: subir .45s ease both;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { border-left-color: var(--gold); }
[data-testid="stChatMessage"]:before, [data-testid="stChatMessage"]:after { content:""; position:absolute; width:11px; height:11px; pointer-events:none; }
[data-testid="stChatMessage"]:before { top:-1px; right:-1px; border-top:2px solid var(--gold); border-right:2px solid var(--gold); }
[data-testid="stChatMessage"]:after { bottom:-1px; right:-1px; border-bottom:2px solid var(--gold); border-right:2px solid var(--gold); }

/* ---------- Barra lateral ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(8,11,19,.97), rgba(18,14,9,.97));
    border-right:1px solid var(--line); box-shadow: 6px 0 30px rgba(0,0,0,.45);
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-family:'Cinzel', serif; font-weight:700; color: var(--gold); letter-spacing:.2em; font-size:.76rem;
    text-transform:uppercase; padding-bottom:7px; border-bottom:1px solid transparent;
    border-image: linear-gradient(90deg, var(--gold), rgba(212,175,55,0)) 1;
}
[data-testid="stSidebar"] .stButton button, .stDownloadButton button {
    background: rgba(255,255,255,.015); color: var(--ivory); border:1px solid var(--line); border-radius:2px;
    font-family:'Exo 2', sans-serif; font-weight:500; text-align:left; transition: all .2s ease;
}
[data-testid="stSidebar"] .stButton button:hover, .stDownloadButton button:hover {
    background: rgba(212,175,55,.12); border-color: var(--gold); color:#fff;
    box-shadow: 0 0 14px rgba(212,175,55,.35), inset 0 0 12px rgba(212,175,55,.08);
}
[data-testid="stMetricValue"] { font-family:'Share Tech Mono', monospace; color: var(--gold-l); font-size:1.3rem; }
[data-testid="stMetricLabel"] { color: var(--mute); letter-spacing:.06em; }

/* ---------- Panel de bienvenida ---------- */
.brief { position:relative; border:1px solid var(--line); background: var(--panel); backdrop-filter: blur(7px);
         padding:26px 28px; margin-bottom:18px; border-radius:2px; box-shadow: 0 10px 34px rgba(0,0,0,.4); animation: subir .8s ease both; }
.brief:before { content:""; position:absolute; top:-1px; left:-1px; width:18px; height:18px; border-top:2px solid var(--gold); border-left:2px solid var(--gold); }
.brief:after { content:""; position:absolute; bottom:-1px; right:-1px; width:18px; height:18px; border-bottom:2px solid var(--gold); border-right:2px solid var(--gold); }
.brief-tag { font-family:'Share Tech Mono', monospace; font-size:.72rem; color: var(--up); letter-spacing:.18em; }
.brief-title { font-family:'Cinzel', serif; font-size:1.55rem; font-weight:700; color: var(--gold-l); margin:8px 0 10px 0; letter-spacing:.06em; }
.brief p { color: var(--ivory); opacity:.9; margin:0 0 16px 0; line-height:1.5; }
.cards { display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; margin-bottom:16px; }
@media (max-width: 640px) { .cards { grid-template-columns: 1fr; } }
.card { border:1px solid var(--line); border-top:2px solid var(--gold); padding:14px 15px; background: rgba(212,175,55,.045); }
.ci { font-family:'Cinzel', serif; color: var(--cyan); font-size:1.05rem; font-weight:700; letter-spacing:.1em; }
.ct { color: var(--gold-l); letter-spacing:.16em; text-transform:uppercase; font-size:.78rem; font-weight:600; margin:3px 0 5px 0; }
.cd { color: var(--mute); font-size:.88rem; line-height:1.4; }
.brief-hint { color: var(--cyan) !important; font-size:.85rem; letter-spacing:.06em; margin:0 !important; opacity:1 !important; }
.hud-foot { text-align:center; color:#7d8aa3; font-size:.68rem; margin:34px 0 8px 0; letter-spacing:.16em; }

/* ---------- Respaldo del tema oscuro (por si no se carga config.toml) ---------- */
.stApp { color: var(--ivory); }
[data-testid="stBottom"], [data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] { background: transparent !important; }
[data-testid="stChatInput"], [data-testid="stChatInput"] > div, [data-testid="stChatInput"] textarea {
    background: rgba(9,13,23,.92) !important; color: var(--ivory) !important; }
[data-testid="stChatInput"] { border:1px solid var(--gold); border-radius:2px; box-shadow: 0 0 20px rgba(212,175,55,.18); }
[data-testid="stChatInput"]:focus-within { border-color: var(--cyan); box-shadow: 0 0 22px rgba(79,216,255,.3); }
[data-testid="stChatInput"] textarea::placeholder { color:#8b97ad !important; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary *,
[data-testid="stStatus"] summary, [data-testid="stStatus"] summary *,
[data-testid="stCheckbox"] label *, [data-testid="stToggle"] label *,
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: var(--ivory) !important; }
[data-testid="stExpander"] { border-color: var(--line) !important; background: rgba(9,13,23,.55); }
</style>
"""


def css() -> str:
    return _CSS.replace("__FONDO__", fondo_base64())
