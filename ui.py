# -*- coding: utf-8 -*-
"""Habillage visuel : thème professionnel, icônes SVG, en-tête 3D, cartes KPI, panneau d'audit, graphiques."""

from __future__ import annotations

import html

import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Palette (thème sombre « console d'entreprise »)
BG = "#0A1020"
SURFACE = "#101A2E"
SURFACE_2 = "#15213A"
BORDER = "rgba(148,163,184,.16)"
INK = "#E6EBF5"
INK_2 = "#A3AEC4"
INK_3 = "#6B7895"
ACCENT = "#3B82F6"
ACCENT_2 = "#38BDF8"
GOLD = "#F59E0B"
# Couleurs de statut (toujours accompagnées d'un libellé + icône)
GOOD, WARNING, CRITICAL = "#16A34A", "#F59E0B", "#DC2626"
SERIES_1 = "#3B82F6"

FONTS = ("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800"
         "&family=JetBrains+Mono:wght@500&display=swap")

# =============================================================================
# ICÔNES SVG (tracés de type Lucide, licence ISC)
# =============================================================================

ICONS = {
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/>',
    "table": '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M12 3v18"/>',
    "receipt": '<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/><path d="M12 17.5v-11"/>',
    "sparkles": '<path d="M9.94 14.5A2 2 0 0 0 8.5 13.06l-6.13-1.58a.5.5 0 0 1 0-.96L8.5 8.94A2 2 0 0 0 9.94 7.5l1.58-6.13a.5.5 0 0 1 .96 0L14.06 7.5A2 2 0 0 0 15.5 8.94l6.13 1.58a.5.5 0 0 1 0 .96L15.5 13.06a2 2 0 0 0-1.44 1.44l-1.58 6.13a.5.5 0 0 1-.96 0z"/>',
    "check": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "x": '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
    "help": '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/>',
    "layers": '<path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
    "package": '<path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"/><path d="M12 22V12"/><path d="m3.3 7 8.7 5 8.7-5"/>',
    "scale": '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
    "weight": '<circle cx="12" cy="5" r="3"/><path d="M6.5 8a2 2 0 0 0-1.905 1.46L2.1 18.5A2 2 0 0 0 4 21h16a2 2 0 0 0 1.925-2.54L19.4 9.5A2 2 0 0 0 17.48 8Z"/>',
    "banknote": '<rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/>',
    "building": '<rect width="16" height="20" x="4" y="2" rx="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>',
    "list": '<path d="M3 12h.01M3 18h.01M3 6h.01M8 12h13M8 18h13M8 6h13"/>',
    "hash": '<line x1="4" x2="20" y1="9" y2="9"/><line x1="4" x2="20" y1="15" y2="15"/><line x1="10" x2="8" y1="3" y2="21"/><line x1="16" x2="14" y1="3" y2="21"/>',
    "sigma": '<path d="M18 7V5a1 1 0 0 0-1-1H6.5a.5.5 0 0 0-.4.8l4.5 6a2 2 0 0 1 0 2.4l-4.5 6a.5.5 0 0 0 .4.8H17a1 1 0 0 0 1-1v-2"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "truck": '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "cog": '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>',
}
EMOJI_ICON = {
    "📂": "upload", "📥": "upload", "📗": "table", "🧾": "receipt", "📑": "file", "🏭": "building", "❓": "help",
    "⚠️": "alert", "✅": "check", "💶": "banknote", "⚖️": "scale", "📦": "package", "🪶": "weight", "🔢": "sigma",
    "🚚": "truck", "🗂️": "layers", "📝": "list", "🎯": "target", "⚙️": "cog", "🧠": "sparkles", "📊": "download",
    "📋": "list", "🔍": "search", "🌍": "globe", "🛡️": "shield", "🔖": "hash", "🔁": "layers",
}


def icon(name: str, size: int = 18, stroke: float = 1.9) -> str:
    """Icône SVG en ligne ; accepte un nom d'icône ou un emoji historique."""
    key = EMOJI_ICON.get(name, name)
    path = ICONS.get(key)
    if path is None:
        return f'<span style="font-size:{size}px;line-height:1">{html.escape(name)}</span>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{path}</svg>')


# =============================================================================
# CSS GLOBAL
# =============================================================================

GLOBAL_CSS = f"""
<style>
@import url('{FONTS}');
:root {{
  --bg:{BG}; --surface:{SURFACE}; --surface2:{SURFACE_2}; --brd:{BORDER};
  --ink:{INK}; --ink2:{INK_2}; --ink3:{INK_3}; --accent:{ACCENT}; --accent2:{ACCENT_2};
  --good:{GOOD}; --warn:{WARNING}; --bad:{CRITICAL};
}}
html, body, [class*="css"], .stApp, .stMarkdown, button, input, textarea, select {{
  font-family:'Inter', system-ui, sans-serif !important; font-feature-settings:"tnum" 1, "cv11" 1;
}}
h1, h2, h3, h4 {{ letter-spacing:-.015em; font-weight:700 !important; }}
.stApp {{ background:
  radial-gradient(1200px 500px at 15% -10%, rgba(59,130,246,.10), transparent 60%),
  radial-gradient(900px 400px at 100% 0%, rgba(56,189,248,.06), transparent 60%), var(--bg); }}
.block-container {{ padding-top:1rem !important; padding-bottom:3rem; max-width:1400px; }}
header[data-testid="stHeader"] {{ background:transparent; }}
#MainMenu, footer, [data-testid="stDecoration"] {{ display:none !important; }}

/* Barre latérale */
section[data-testid="stSidebar"] {{ background:#0C1426; border-right:1px solid var(--brd); }}
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {{ font-size:.92rem !important; color:var(--ink); }}
.side-brand {{ display:flex; align-items:center; gap:.75rem; padding:.2rem 0 1rem; border-bottom:1px solid var(--brd); margin-bottom:1rem; }}
.side-brand .logo {{ width:40px; height:40px; border-radius:10px; display:grid; place-items:center; color:#fff;
  background:linear-gradient(135deg,#1D4ED8,#3B82F6); box-shadow:0 6px 18px -6px rgba(59,130,246,.7); }}
.side-brand b {{ display:block; color:var(--ink); font-size:.95rem; letter-spacing:.01em; }}
.side-brand span {{ color:var(--ink3); font-size:.7rem; letter-spacing:.12em; text-transform:uppercase; }}
.side-cap {{ display:flex; align-items:center; gap:.4rem; font-size:.68rem; letter-spacing:.14em; text-transform:uppercase;
  color:var(--ink3); margin:1.1rem 0 .5rem; font-weight:600; }}
.side-pill {{ display:flex; gap:.55rem; align-items:center; font-size:.8rem; padding:.5rem .7rem; border-radius:8px;
  border:1px solid var(--brd); background:var(--surface); color:var(--ink2); margin:.35rem 0 .7rem; line-height:1.3; }}
.side-pill i {{ width:8px; height:8px; border-radius:50%; display:inline-block; flex:none; }}
.side-note {{ font-size:.74rem; color:var(--ink3); line-height:1.45; margin:.2rem 0 .6rem; }}

/* Sélecteur de module */
div.st-key-module [data-testid="stWidgetLabel"] {{ display:none; }}
div.st-key-module [role="radiogroup"] {{ gap:.4rem; width:100%; display:flex; flex-direction:column; }}
div.st-key-module [role="radiogroup"] > div, div.st-key-module {{ width:100% !important; }}
div.st-key-module [data-testid="stRadioOption"], div.st-key-module [role="radiogroup"] > label {{
  width:100%; margin:0; padding:.65rem .8rem; border-radius:10px; border:1px solid var(--brd);
  background:var(--surface); transition:border-color .2s, background .2s; cursor:pointer; }}
div.st-key-module [data-testid="stRadioOption"]:hover {{ border-color:rgba(59,130,246,.45); }}
div.st-key-module [data-testid="stRadioOption"][data-selected="true"], div.st-key-module [role="radiogroup"] > label:has(input:checked) {{
  background:rgba(59,130,246,.14); border-color:rgba(59,130,246,.7); box-shadow:inset 3px 0 0 var(--accent); }}
div.st-key-module [data-testid="stRadioOption"] p {{ font-weight:600; font-size:.84rem; color:var(--ink); }}
div.st-key-module [data-testid="stRadioOption"] > div > div:first-child:not([data-testid]) {{ display:none; }}

/* Cartes (conteneurs à clé « card… ») */
div[class*="st-key-card"] {{
  background:var(--surface); border:1px solid var(--brd); border-radius:14px; padding:1.05rem 1.15rem .95rem;
  box-shadow:0 1px 0 rgba(255,255,255,.03) inset, 0 12px 30px -20px rgba(0,0,0,.8);
  transition:border-color .2s, box-shadow .2s; animation:rise .45s ease-out both; }}
div[class*="st-key-card_upl"]:hover {{ border-color:rgba(59,130,246,.45); }}
@keyframes rise {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:none; }} }}
.card-title {{ display:flex; gap:.8rem; align-items:center; margin-bottom:.55rem; }}
.card-title .ico {{ width:38px; height:38px; border-radius:10px; display:grid; place-items:center; flex:none; color:#93C5FD;
  background:rgba(59,130,246,.12); border:1px solid rgba(59,130,246,.25); }}
.card-title b {{ color:var(--ink); font-size:.98rem; display:block; }}
.card-title span {{ color:var(--ink2); font-size:.8rem; }}
.doc-tags {{ display:flex; flex-wrap:wrap; gap:.3rem; margin:.1rem 0 .55rem; }}
.doc-tags em {{ font-style:normal; font-size:.7rem; color:var(--ink2); padding:.14rem .5rem; border-radius:6px;
  border:1px solid var(--brd); background:var(--surface2); }}

[data-testid="stFileUploaderDropzone"] {{ background:var(--bg) !important; border:1.5px dashed rgba(148,163,184,.3) !important;
  border-radius:10px !important; transition:border-color .2s, background .2s; }}
[data-testid="stFileUploaderDropzone"]:hover {{ border-color:var(--accent) !important; background:rgba(59,130,246,.05) !important; }}
[data-testid="stFileUploader"] label {{ display:none; }}

/* Boutons */
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {{
  background:linear-gradient(180deg,#3B82F6,#2563EB) !important; border:1px solid #1D4ED8 !important; color:#fff !important;
  font-weight:600 !important; border-radius:10px !important; min-height:2.9rem;
  box-shadow:0 8px 20px -10px rgba(37,99,235,.9), inset 0 1px 0 rgba(255,255,255,.18); transition:filter .15s, transform .15s !important; }}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {{ filter:brightness(1.08); transform:translateY(-1px); }}
.stButton > button[kind="primary"]:disabled {{ background:var(--surface2) !important; border-color:var(--brd) !important;
  color:var(--ink3) !important; box-shadow:none; }}
.stDownloadButton > button[kind="primary"] {{ background:linear-gradient(180deg,#16A34A,#15803D) !important;
  border-color:#166534 !important; box-shadow:0 8px 20px -10px rgba(22,163,74,.9), inset 0 1px 0 rgba(255,255,255,.18); }}
.stButton > button[kind="secondary"] {{ border-radius:10px; border:1px solid var(--brd); background:var(--surface); }}

/* Progression */
.stProgress > div > div > div {{ background:rgba(255,255,255,.06) !important; border-radius:99px; height:8px !important; }}
.stProgress > div > div > div > div {{ background:linear-gradient(90deg,#2563EB,#38BDF8) !important; border-radius:99px; }}

/* Onglets */
.stTabs [role="tablist"] {{ gap:.25rem; border-bottom:1px solid var(--brd); width:100%; overflow-x:auto; }}
.stTabs [role="tab"] {{ border-radius:8px 8px 0 0; padding:.55rem .95rem; color:var(--ink2); height:auto; }}
.stTabs [role="tab"]:hover {{ color:var(--ink); background:rgba(255,255,255,.03); }}
.stTabs [role="tab"][aria-selected="true"] {{ color:#fff !important; box-shadow:inset 0 -2px 0 var(--accent); background:rgba(59,130,246,.08); }}
.stTabs [role="tab"] p {{ font-weight:600; font-size:.88rem; }}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"], .stTabs .react-aria-SelectionIndicator {{ display:none !important; }}

/* Divers */
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {{ border-radius:10px; overflow:hidden; border:1px solid var(--brd); }}
[data-testid="stExpander"] {{ border:1px solid var(--brd) !important; border-radius:10px !important; background:var(--surface); }}
.section-h {{ display:flex; align-items:center; gap:.55rem; margin:1.5rem 0 .65rem; color:var(--ink); }}
.section-h .si {{ color:#93C5FD; display:grid; place-items:center; }}
.section-h b {{ font-size:1.02rem; font-weight:700; }}
.section-h span.ln {{ flex:1; height:1px; background:var(--brd); }}
.status-banner {{ display:flex; gap:.9rem; align-items:center; padding:.85rem 1.05rem; border-radius:12px; margin:.8rem 0;
  border:1px solid; background:var(--surface); }}
.status-banner .big {{ display:grid; place-items:center; }}
.status-banner b {{ font-size:.98rem; display:block; }}
.status-banner span {{ color:var(--ink2); font-size:.85rem; }}
.status-ok {{ border-color:rgba(22,163,74,.45); box-shadow:inset 4px 0 0 var(--good); }} .status-ok .big, .status-ok b {{ color:#4ADE80; }}
.status-warn {{ border-color:rgba(245,158,11,.45); box-shadow:inset 4px 0 0 var(--warn); }} .status-warn .big, .status-warn b {{ color:#FBBF24; }}
.status-ko {{ border-color:rgba(220,38,38,.5); box-shadow:inset 4px 0 0 var(--bad); }} .status-ko .big, .status-ko b {{ color:#F87171; }}
.chip {{ display:inline-flex; align-items:center; gap:.3rem; font-size:.72rem; font-weight:600; padding:.15rem .5rem;
  border-radius:999px; border:1px solid; white-space:nowrap; }}
.chip.ok {{ color:#4ADE80; border-color:rgba(22,163,74,.45); background:rgba(22,163,74,.10); }}
.chip.warn {{ color:#FBBF24; border-color:rgba(245,158,11,.45); background:rgba(245,158,11,.10); }}
.chip.ko {{ color:#F87171; border-color:rgba(220,38,38,.5); background:rgba(220,38,38,.10); }}
.chip.info {{ color:#93C5FD; border-color:rgba(59,130,246,.45); background:rgba(59,130,246,.10); }}
.audit {{ width:100%; border-collapse:separate; border-spacing:0; font-size:.82rem; border:1px solid var(--brd);
  border-radius:10px; overflow:hidden; }}
.audit th {{ text-align:left; color:var(--ink3); font-weight:600; font-size:.7rem; letter-spacing:.06em; text-transform:uppercase;
  padding:.55rem .7rem; background:var(--surface2); border-bottom:1px solid var(--brd); }}
.audit td {{ padding:.55rem .7rem; color:var(--ink); border-bottom:1px solid var(--brd); vertical-align:middle; }}
.audit tr:last-child td {{ border-bottom:0; }}
.audit td.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
.audit td.mut {{ color:var(--ink2); }}
.audit .mono {{ font-family:'JetBrains Mono', monospace; font-size:.78rem; }}
.sgrid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(310px,1fr)); gap:.7rem; margin:.3rem 0 .4rem; }}
.scard {{ background:var(--surface); border:1px solid var(--brd); border-radius:12px; padding:.85rem .95rem .75rem; position:relative;
  box-shadow:0 10px 26px -22px rgba(0,0,0,.9); transition:border-color .15s, transform .15s; }}
.scard:hover {{ border-color:rgba(59,130,246,.45); transform:translateY(-2px); }}
.scard::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:3px; border-radius:12px 0 0 12px; background:var(--accent); }}
.scard.crit::before {{ background:var(--bad); }} .scard.warn::before {{ background:var(--warn); }} .scard.ok::before {{ background:var(--good); }}
.scard .sh {{ display:flex; justify-content:space-between; gap:.5rem; align-items:flex-start; }}
.scard .sn {{ color:var(--ink); font-weight:700; font-size:.9rem; line-height:1.25; word-break:break-word; }}
.scard .sm {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.4rem; margin-top:.7rem; }}
.scard .sm b {{ display:block; color:#fff; font-size:1.02rem; font-variant-numeric:tabular-nums; letter-spacing:-.01em; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.scard .sm span {{ color:var(--ink3); font-size:.68rem; text-transform:uppercase; letter-spacing:.06em; }}
.scard .sf {{ color:var(--ink3); font-size:.74rem; margin-top:.55rem; }}
.flist {{ width:100%; border-collapse:separate; border-spacing:0; font-size:.82rem; border:1px solid var(--brd); border-radius:10px; overflow:hidden; margin:.2rem 0 .3rem; }}
.flist td {{ padding:.42rem .7rem; border-bottom:1px solid var(--brd); color:var(--ink); }}
.flist tr:last-child td {{ border-bottom:0; }} .flist td.mut {{ color:var(--ink2); }}
.foot {{ display:flex; justify-content:center; gap:.5rem; align-items:center; color:var(--ink3); font-size:.76rem;
  margin-top:2.5rem; padding-top:1rem; border-top:1px solid var(--brd); text-align:center; }}
.foot b {{ color:var(--ink2); }}
.stAlert {{ border-radius:10px; }}
</style>
"""


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# =============================================================================
# EN-TÊTE (scène 3D : camion-remorque TIMAR, parallaxe souris)
# =============================================================================

def _cuboid(cls: str, w: int, h: int, d: int, faces: dict | None = None) -> str:
    faces = faces or {}
    names = ["front", "back", "right", "left", "top", "bottom"]
    inner = "".join(f'<div class="f {n}">{faces.get(n, "")}</div>' for n in names)
    return f'<div class="cub {cls}" style="--w:{w}px;--h:{h}px;--d:{d}px">{inner}</div>'


def hero_3d(stats: dict | None = None, badge: str = "TIMAR TANGER · DÉDOUANEMENT IMPORT",
            title: str = "Ventilation automatique", highlight: str = "Groupage ALSTOM Fez",
            desc: str = "Factures, packing lists, CMR et manifestes lus automatiquement dans toutes les langues, "
                        "chaque ligne contrôlée et rapprochée de votre référentiel NGP, classeur Excel prêt pour la déclaration.",
            ai_label: str = ""):
    side_logo = ('<div class="brand"><div class="tl">TIMAR</div>'
                 '<div class="ts">INTERNATIONAL TRANSPORT · TANGER</div></div>')
    trailer = _cuboid("trailer", 300, 118, 96, {"front": side_logo, "back": side_logo,
                                                  "left": '<div class="doors"></div>'})
    cab = _cuboid("cab", 78, 98, 96, {"right": '<div class="wind"></div><div class="grill"></div>',
                                       "front": '<div class="win-s"></div>', "back": '<div class="win-s"></div>'})
    wheels = "".join(f'<div class="wheel" style="left:{x}px;transform:translateZ({z}px)"></div>'
                     for x in (22, 62, 230, 340) for z in (49, -50))
    chips = "".join(f'<div class="stat"><b>{html.escape(str(v))}</b><span>{html.escape(k)}</span></div>'
                    for k, v in (stats or {}).items())
    ai_html = (f'<div class="ai">{icon("sparkles", 14)}<span>{html.escape(ai_label)}</span></div>' if ai_label else "")
    page = f"""
<!doctype html><html><head><meta charset="utf-8"><link href="{FONTS}" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:transparent;overflow:hidden;font-family:Inter,system-ui,sans-serif;color:{INK}}}
.hero{{position:relative;height:296px;border-radius:16px;overflow:hidden;display:grid;grid-template-columns:1.15fr 1fr;
  background:linear-gradient(120deg,#0F1B33 0%,#0C1528 60%,#0B1A2C 100%);border:1px solid {BORDER};
  box-shadow:0 20px 50px -30px rgba(0,0,0,.9)}}
.hero::before{{content:"";position:absolute;inset:0;background:
  radial-gradient(600px 260px at 85% 40%,rgba(59,130,246,.18),transparent 70%),
  linear-gradient(rgba(148,163,184,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(148,163,184,.05) 1px,transparent 1px);
  background-size:auto,32px 32px,32px 32px;-webkit-mask-image:linear-gradient(90deg,transparent 30%,#000 75%);pointer-events:none}}
.left{{position:relative;z-index:2;padding:30px 0 26px 34px;display:flex;flex-direction:column;justify-content:center}}
.top{{display:flex;gap:8px;align-items:center;flex-wrap:wrap}}
.badge{{font-size:10.5px;letter-spacing:.16em;font-weight:600;color:{INK_2};padding:6px 10px;border-radius:6px;
  border:1px solid {BORDER};background:rgba(255,255,255,.03)}}
.ai{{display:inline-flex;gap:6px;align-items:center;font-size:11px;font-weight:600;color:#BFDBFE;padding:6px 10px;border-radius:6px;
  border:1px solid rgba(59,130,246,.45);background:rgba(59,130,246,.14)}}
h1{{font-size:31px;line-height:1.12;margin:14px 0 10px;letter-spacing:-.02em;font-weight:800}}
h1 .g{{color:#93C5FD}}
p{{color:{INK_2};font-size:13.5px;line-height:1.55;max-width:540px}}
.stats{{display:flex;gap:8px;margin-top:18px;flex-wrap:wrap}}
.stat{{padding:8px 12px;border-radius:8px;background:rgba(255,255,255,.035);border:1px solid {BORDER};min-width:96px}}
.stat b{{display:block;font-size:16px;color:#fff;font-variant-numeric:tabular-nums}}
.stat span{{font-size:10.5px;color:{INK_3};letter-spacing:.06em;text-transform:uppercase}}
.stage{{position:relative;z-index:1;perspective:1100px;perspective-origin:50% 35%}}
.scene{{position:absolute;left:50%;top:58%;width:0;height:0;transform-style:preserve-3d;
  transform:scale(.86) rotateX(calc(-15deg + var(--my,0deg))) rotateY(calc(-32deg + var(--mx,0deg)));transition:transform .3s ease-out}}
.float{{transform-style:preserve-3d;animation:float 6s ease-in-out infinite}}
@keyframes float{{50%{{transform:translateY(-4px)}}}}
.truck{{position:absolute;transform-style:preserve-3d;transform:translate3d(-215px,-150px,0)}}
.cub{{position:absolute;transform-style:preserve-3d;width:var(--w);height:var(--h)}}
.f{{position:absolute;left:0;top:0}}
.front,.back{{width:var(--w);height:var(--h)}}
.front{{transform:translateZ(calc(var(--d)/2))}} .back{{transform:rotateY(180deg) translateZ(calc(var(--d)/2))}}
.right,.left{{width:var(--d);height:var(--h);left:calc((var(--w) - var(--d))/2)}}
.right{{transform:rotateY(90deg) translateZ(calc(var(--w)/2))}} .left{{transform:rotateY(-90deg) translateZ(calc(var(--w)/2))}}
.top,.bottom{{width:var(--w);height:var(--d);top:calc((var(--h) - var(--d))/2)}}
.cub .top{{transform:rotateX(90deg) translateZ(calc(var(--h)/2))}} .bottom{{transform:rotateX(-90deg) translateZ(calc(var(--h)/2))}}
.trailer .f{{background:linear-gradient(180deg,#F4F7FC,#CBD5E1);border:1px solid #94A3B8}}
.trailer .top{{background:linear-gradient(90deg,#E2E8F0,#F8FAFC)}}
.trailer .right,.trailer .left{{background:linear-gradient(180deg,#CBD5E1,#94A3B8)}}
.trailer .front::after,.trailer .back::after{{content:"";position:absolute;left:0;right:0;bottom:0;height:10px;background:#1E3A8A}}
.brand{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center}}
.tl{{font-weight:800;font-size:38px;letter-spacing:.14em;color:#1E3A8A}}
.ts{{font-size:8px;letter-spacing:.22em;color:#334E7E;margin-top:2px;font-weight:600}}
.doors{{position:absolute;inset:8px;background:linear-gradient(90deg,transparent 49.5%,#94A3B8 50%,transparent 50.5%)}}
.cab{{transform:translate3d(306px,20px,0)}}
.cab .f{{background:linear-gradient(180deg,#2563EB,#1E3A8A);border:1px solid #1E3A8A}} .cab .top{{background:#3B82F6}}
.wind{{position:absolute;left:8px;right:8px;top:8px;height:38px;border-radius:4px;background:linear-gradient(135deg,#BFDBFE,#38BDF8 45%,#0C4A6E)}}
.grill{{position:absolute;left:14px;right:14px;bottom:12px;height:18px;border-radius:2px;background:repeating-linear-gradient(0deg,#0B1530 0 3px,#334E7E 3px 5px)}}
.win-s{{position:absolute;right:8px;top:8px;width:34px;height:30px;border-radius:3px;background:linear-gradient(135deg,#BFDBFE,#0C4A6E)}}
.wheel{{position:absolute;top:104px;width:34px;height:34px;border-radius:50%;
  background:radial-gradient(circle,#CBD5E1 0 22%,#0B1020 24% 60%,#1E293B 62%);box-shadow:0 0 0 3px #0B1020}}
.road{{position:absolute;width:760px;height:220px;left:-380px;top:-110px;transform:rotateX(90deg) translateZ(-140px);
  background:linear-gradient(90deg,transparent,rgba(30,41,70,.85) 15%,rgba(30,41,70,.85) 85%,transparent);
  -webkit-mask-image:radial-gradient(ellipse at center,#000 45%,transparent 72%)}}
.road::before{{content:"";position:absolute;left:0;right:0;top:50%;height:5px;margin-top:-2px;
  background:repeating-linear-gradient(90deg,rgba(245,158,11,.75) 0 46px,transparent 46px 92px);animation:lane 1.4s linear infinite}}
@keyframes lane{{to{{background-position:92px 0}}}}
.shadow{{position:absolute;width:460px;height:150px;left:-230px;top:-75px;transform:rotateX(90deg) translateZ(-139px);
  background:radial-gradient(ellipse,rgba(0,0,0,.55),transparent 65%)}}
@media (max-width:860px){{.hero{{grid-template-columns:1fr}}.stage{{display:none}}h1{{font-size:25px}}.left{{padding:24px}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style></head><body>
<div class="hero">
  <div class="left">
    <div class="top"><div class="badge">{html.escape(badge)}</div>{ai_html}</div>
    <h1>{html.escape(title)}<br><span class="g">{html.escape(highlight)}</span></h1>
    <p>{html.escape(desc)}</p>
    <div class="stats">{chips}</div>
  </div>
  <div class="stage"><div class="scene" id="scene"><div class="float">
    <div class="shadow"></div><div class="road"></div><div class="truck">{trailer}{cab}{wheels}</div>
  </div></div></div>
</div>
<script>
const sc=document.getElementById('scene'),hero=document.querySelector('.hero');
hero.addEventListener('mousemove',e=>{{const r=hero.getBoundingClientRect();
  const x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;
  sc.style.setProperty('--mx',(x*18)+'deg');sc.style.setProperty('--my',(-y*8)+'deg');}});
hero.addEventListener('mouseleave',()=>{{sc.style.setProperty('--mx','0deg');sc.style.setProperty('--my','0deg');}});
</script></body></html>"""
    components.html(page, height=304)


# =============================================================================
# ÉTAPES / TITRES / BANNIÈRES
# =============================================================================

def steps_strip(active: int, steps: list | None = None):
    """active : 0 = rien, 1 = fichiers déposés, 2 = traitement fait."""
    steps = steps or [("upload", "Importer", "Dossier PDF + référentiel NGP"),
                      ("sparkles", "Lire & contrôler", "Lecture multilingue, contrôles croisés"),
                      ("download", "Exporter", "Classeur Excel de contrôle")]
    cells = []
    for i, (ico, t, d) in enumerate(steps):
        state = "done" if i < active else ("cur" if i == active else "")
        mark = icon("check", 18) if state == "done" else icon(ico, 18)
        cells.append(f'<div class="stp {state}"><div class="n">{mark}</div><div><b>{i + 1}. {html.escape(t)}</b>'
                     f'<span>{html.escape(d)}</span></div></div>')
    st.markdown(f"""
<style>
.steps{{display:grid;grid-template-columns:repeat(3,1fr);gap:.6rem;margin:.9rem 0 1rem}}
.stp{{display:flex;gap:.75rem;align-items:center;padding:.7rem .9rem;border-radius:10px;background:var(--surface);
  border:1px solid var(--brd);position:relative;overflow:hidden}}
.stp .n{{width:36px;height:36px;border-radius:9px;display:grid;place-items:center;color:var(--ink3);
  background:var(--surface2);border:1px solid var(--brd);flex:none}}
.stp b{{display:block;color:var(--ink);font-size:.86rem}} .stp span{{color:var(--ink3);font-size:.75rem}}
.stp.cur{{border-color:rgba(59,130,246,.6)}} .stp.cur .n{{color:#fff;background:#2563EB;border-color:#2563EB}}
.stp.done .n{{color:#4ADE80;background:rgba(22,163,74,.12);border-color:rgba(22,163,74,.45)}}
.stp::after{{content:"";position:absolute;left:0;bottom:0;height:2px;width:0;background:var(--accent)}}
.stp.done::after{{width:100%;background:var(--good)}} .stp.cur::after{{width:50%}}
@media (max-width:760px){{.steps{{grid-template-columns:1fr}}}}
</style><div class="steps">{''.join(cells)}</div>""", unsafe_allow_html=True)


def card_title(ico: str, title: str, subtitle: str, tags: list[str] | None = None):
    tag_html = "".join(f"<em>{html.escape(t)}</em>" for t in (tags or []))
    st.markdown(f'<div class="card-title"><div class="ico">{icon(ico, 19)}</div><div><b>{html.escape(title)}</b>'
                f'<span>{html.escape(subtitle)}</span></div></div>'
                + (f'<div class="doc-tags">{tag_html}</div>' if tag_html else ""), unsafe_allow_html=True)


def section(title: str, ico: str = ""):
    ic = f'<span class="si">{icon(ico, 17)}</span>' if ico else ""
    st.markdown(f'<div class="section-h">{ic}<b>{html.escape(title)}</b><span class="ln"></span></div>',
                unsafe_allow_html=True)


def status_banner(kind: str, _legacy_icon: str, title: str, detail: str):
    ico = {"ok": "check", "warn": "alert", "ko": "x"}.get(kind, "help")
    st.markdown(f'<div class="status-banner status-{kind}"><div class="big">{icon(ico, 24)}</div><div><b>{html.escape(title)}</b>'
                f'<span>{html.escape(detail)}</span></div></div>', unsafe_allow_html=True)


def chip(text: str, tone: str = "info") -> str:
    ico = {"ok": "check", "warn": "alert", "ko": "x", "info": "sparkles"}.get(tone, "")
    return f'<span class="chip {tone}">{icon(ico, 12, 2.2) if ico else ""}{html.escape(text)}</span>'


def sidebar_brand():
    st.markdown(f'<div class="side-brand"><div class="logo">{icon("truck", 21)}</div><div><b>TIMAR Tanger</b>'
                '<span>Customs · Import · Export</span></div></div>', unsafe_allow_html=True)


def sidebar_cap(text: str, ico: str = ""):
    st.markdown(f'<div class="side-cap">{icon(ico, 13) if ico else ""}{html.escape(text)}</div>', unsafe_allow_html=True)


def sidebar_pill(color: str, text: str):
    st.markdown(f'<div class="side-pill"><i style="background:{color};box-shadow:0 0 6px {color}"></i>{text}</div>',
                unsafe_allow_html=True)


def footer(ai_active: bool = False):
    privacy = ("Lecture IA : les PDF sont transmis de façon chiffrée à l'API Anthropic (Claude) pour analyse"
               if ai_active else "Traitement 100 % local — aucun document n'est envoyé sur Internet")
    st.markdown(f'<div class="foot">{icon("shield", 14)}<span><b>TIMAR Tanger</b> · Import (ventilation groupage) &amp; '
                f'Export (BL / factures) ALSTOM · {html.escape(privacy)}</span></div>', unsafe_allow_html=True)


# =============================================================================
# PANNEAU D'AUDIT DES DOCUMENTS (lecture IA)
# =============================================================================

def _fmt_num(v, d=2) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return f"{v:,.{d}f}".replace(",", " ").replace(".", ",")


def audit_table(rows: list[dict]):
    """Tableau de synthèse : un document par ligne, statut des contrôles."""
    if not rows:
        return
    body = []
    for r in rows:
        n_iss = len(r.get("_issues") or [])
        status = chip("Vérifié", "ok") if not n_iss else chip(f"{n_iss} point(s)", "warn")
        conf = {"haute": "ok", "moyenne": "warn", "faible": "ko"}.get(r.get("Confiance", ""), "info")
        body.append(
            "<tr>"
            f'<td class="mut">{html.escape(str(r["Fichier"]))[:38]}<br><span class="mono">p. {html.escape(str(r["Pages"]))}</span></td>'
            f'<td>{chip(r["Type"], "info")}</td>'
            f'<td class="mono">{html.escape(str(r["N°"]) or "—")}</td>'
            f'<td>{html.escape(r["Fournisseur"] or "—")}<br><span class="mut" style="color:var(--ink3)">→ '
            f'{html.escape(r["Client"] or "—")}</span></td>'
            f'<td class="mut">{html.escape(r["Langue"] or "—")}</td>'
            f'<td class="num">{_fmt_num(r["Total HT"])} <span style="color:var(--ink3)">{html.escape(r["Devise"] or "")}</span></td>'
            f'<td class="num">{_fmt_num(r["Poids net (kg)"], 3)}<br><span style="color:var(--ink3)">'
            f'{_fmt_num(r["Poids brut (kg)"], 3)}</span></td>'
            f'<td class="num">{r["Lignes"]}</td>'
            f'<td>{chip(r.get("Confiance") or "?", conf)}</td>'
            f"<td>{status}</td></tr>")
    st.markdown(
        '<table class="audit"><thead><tr><th>Fichier</th><th>Type</th><th>N°</th><th>Fournisseur → Client</th>'
        '<th>Langue</th><th>Total HT</th><th>Net / Brut kg</th><th>Lignes</th><th>Confiance</th><th>Contrôles</th>'
        f'</tr></thead><tbody>{"".join(body)}</tbody></table>', unsafe_allow_html=True)


def audit_details(rows: list[dict]):
    """Détail des anomalies et remarques du lecteur, document par document."""
    for r in rows:
        iss, notes = r.get("_issues") or [], r.get("_notes") or []
        if not iss and not notes:
            continue
        title = f"{r['Type']} {r['N°'] or ''} — {r['Fichier']} p.{r['Pages']}"
        with st.expander(title + (f"  ·  {len(iss)} point(s) à vérifier" if iss else "  ·  remarques"), expanded=bool(iss)):
            for i in iss:
                st.markdown(f"- :orange[**À vérifier**] {i}")
            for n in notes:
                st.markdown(f"- :blue[Remarque du lecteur] {n}")


# =============================================================================
# CARTES KPI (compteurs animés)
# =============================================================================

def kpi_cards(cards: list[dict]):
    """cards : {icon, label, value (int|float|str), sub, tone: blue|cyan|gold|good|warn|bad, decimals}"""
    tones = {"blue": ("#60A5FA", "rgba(59,130,246,.14)"), "cyan": ("#38BDF8", "rgba(56,189,248,.13)"),
             "gold": ("#FBBF24", "rgba(245,158,11,.13)"), "good": ("#4ADE80", "rgba(22,163,74,.14)"),
             "warn": ("#FBBF24", "rgba(245,158,11,.14)"), "bad": ("#F87171", "rgba(220,38,38,.15)")}
    items = []
    for i, c in enumerate(cards):
        col, soft = tones.get(c.get("tone", "blue"), tones["blue"])
        val = c["value"]
        is_num = isinstance(val, (int, float)) and not isinstance(val, bool)
        data = f'data-to="{val}" data-dec="{c.get("decimals", 0)}"' if is_num else ""
        shown = "0" if is_num else html.escape(str(val))
        items.append(f"""<div class="k" style="--c:{col};--s:{soft};animation-delay:{i * 50}ms">
  <div class="top"><div class="ic">{icon(c.get('icon', ''), 17)}</div><div class="lb">{html.escape(c['label'])}</div></div>
  <div class="v" {data}>{shown}</div><div class="sb">{html.escape(str(c.get('sub', '')))}</div></div>""")
    n = len(cards)
    page = f"""<!doctype html><html><head><meta charset="utf-8"><link href="{FONTS}" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}} html,body{{background:transparent;font-family:Inter,sans-serif;overflow:hidden}}
.g{{display:grid;grid-template-columns:repeat({min(n, 6)},1fr);gap:10px;padding:4px 2px 8px}}
.k{{position:relative;border-radius:12px;padding:14px 14px 12px;background:{SURFACE};border:1px solid {BORDER};
  box-shadow:0 10px 26px -20px rgba(0,0,0,.9);animation:in .45s ease-out both;transition:transform .15s,border-color .15s;overflow:hidden}}
.k::before{{content:"";position:absolute;left:0;top:0;right:0;height:2px;background:var(--c);opacity:.85}}
.k:hover{{transform:translateY(-2px);border-color:rgba(148,163,184,.3)}}
@keyframes in{{from{{opacity:0;transform:translateY(6px)}}}}
.top{{display:flex;align-items:center;gap:9px}}
.ic{{width:30px;height:30px;border-radius:8px;display:grid;place-items:center;background:var(--s);color:var(--c);flex:none}}
.lb{{color:{INK_2};font-size:12px;font-weight:600;line-height:1.25}}
.v{{font-size:25px;font-weight:700;color:#fff;margin:11px 0 1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  font-variant-numeric:tabular-nums;letter-spacing:-.01em}}
.sb{{color:{INK_3};font-size:11px;min-height:14px}}
@media (max-width:900px){{.g{{grid-template-columns:repeat(2,1fr)}}}}
</style></head><body><div class="g">{''.join(items)}</div>
<script>
const fmt=(v,d)=>v.toLocaleString('fr-FR',{{minimumFractionDigits:d,maximumFractionDigits:d}});
document.querySelectorAll('.v[data-to]').forEach(el=>{{const to=+el.dataset.to,d=+el.dataset.dec,t0=performance.now(),D=900;
  (function s(t){{const p=Math.min(1,(t-t0)/D),e=1-Math.pow(1-p,3);el.textContent=fmt(to*e,d);if(p<1)requestAnimationFrame(s);}})(t0);}});
</script></body></html>"""
    rows = 1 if n <= 6 else 2
    components.html(page, height=124 * rows)


# =============================================================================
# GRAPHIQUES (Altair)
# =============================================================================

def _chart_config(chart):
    return (chart.configure(background="transparent", font="Inter")
            .configure_view(stroke=None)
            .configure_axis(labelColor=INK_2, titleColor=INK_2, gridColor="rgba(148,163,184,.12)",
                            domainColor="rgba(148,163,184,.25)", tickColor="rgba(148,163,184,.25)",
                            labelFontSize=11, titleFontSize=11, titleFontWeight=500)
            .configure_legend(labelColor=INK_2, titleColor=INK_2))


def chart_value_by_supplier(df: pd.DataFrame):
    """Barres horizontales : Valeur HT par fournisseur. Une devise = un panneau avec sa propre échelle."""
    data = (df.groupby(["Fournisseur / Expéditeur", "Devise"], dropna=False)["Valeur HT"].sum().reset_index())
    data["Devise"] = data["Devise"].replace("", "?").fillna("?")
    data["Fournisseur"] = data["Fournisseur / Expéditeur"].fillna("?").str.slice(0, 34)
    data["Libellé"] = data["Valeur HT"].map(lambda v: f"{v:,.2f}".replace(",", " ").replace(".", ",")) + " " + data["Devise"]
    base = alt.Chart().encode(
        y=alt.Y("Fournisseur:N", sort="-x", title=None, axis=alt.Axis(labelLimit=240)),
        x=alt.X("Valeur HT:Q", title=None, axis=alt.Axis(format=",.0f", tickCount=4), scale=alt.Scale(nice=True, padding=0)),
        tooltip=[alt.Tooltip("Fournisseur / Expéditeur:N", title="Fournisseur"), alt.Tooltip("Devise:N"),
                 alt.Tooltip("Valeur HT:Q", format=",.2f")])
    bars = base.mark_bar(color=SERIES_1, cornerRadiusTopRight=3, cornerRadiusBottomRight=3, height={"band": .62})
    labels = base.mark_text(align="left", dx=6, color=INK_2, fontSize=11).encode(text="Libellé:N")
    devises = list(data["Devise"].unique())
    for dev in devises:
        sub = data[data["Devise"] == dev]
        if len(devises) > 1:
            st.markdown(f'<div style="color:{INK};font-weight:600;font-size:.82rem;margin:.2rem 0 -.3rem">'
                        f'{html.escape(dev)}</div>', unsafe_allow_html=True)
        chart = alt.layer(bars, labels, data=sub).properties(height=max(60, 38 * len(sub)))
        st.altair_chart(_chart_config(chart), use_container_width=True, theme=None)


def chart_ngp_status(df: pd.DataFrame):
    """Statut du contrôle NGP : couleur de statut + libellé (jamais la couleur seule)."""
    order = [("OK", "OK", GOOD), ("À vérifier", "À vérifier", WARNING), ("ÉCART", "ÉCART", CRITICAL)]
    counts = df["Contrôle NGP"].value_counts()
    total = max(int(counts.sum()), 1)
    data = pd.DataFrame([{"Statut": lab, "Lignes": int(counts.get(key, 0)),
                          "Part": int(counts.get(key, 0)) / total} for lab, key, _ in order])
    base = alt.Chart(data).encode(
        y=alt.Y("Statut:N", sort=[o[0] for o in order], title=None),
        x=alt.X("Lignes:Q", title="Nombre de lignes", axis=alt.Axis(tickMinStep=1, format="d")),
        tooltip=[alt.Tooltip("Statut:N"), alt.Tooltip("Lignes:Q"), alt.Tooltip("Part:Q", format=".0%")])
    bars = base.mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3, height={"band": .62}).encode(
        color=alt.Color("Statut:N", scale=alt.Scale(domain=[o[0] for o in order], range=[o[2] for o in order]),
                        legend=None))
    labels = base.mark_text(align="left", dx=6, color=INK_2, fontSize=11).encode(text=alt.Text("Lignes:Q", format="d"))
    st.altair_chart(_chart_config((bars + labels).properties(height=140)), use_container_width=True, theme=None)


# =============================================================================
# CARTES PAR FOURNISSEUR / LISTE DES FICHIERS
# =============================================================================

def _fr(v, d=2) -> str:
    return f"{v:,.{d}f}".replace(",", " ").replace(".", ",")


def supplier_cards(items: list[dict]):
    """Une carte par fournisseur : nb d'articles, poids net (kg), valeur HT, alertes."""
    if not items:
        return
    cards = []
    for it in items:
        crit, warn = it.get("Critiques", 0), it.get("Avertissements", 0)
        tone = "crit" if crit else ("warn" if warn else "ok")
        chips = (chip(f"{crit} critique(s)", "ko") if crit else "") + (chip(f"{warn} à vérifier", "warn") if warn else "") \
            + ("" if crit or warn else chip("OK", "ok"))
        vals = " + ".join(f"{_fr(v)} {html.escape(c)}" for c, v in it["Valeur HT"].items() if v) or "—"
        cards.append(
            f'<div class="scard {tone}"><div class="sh"><span class="sn">{html.escape(str(it["Fournisseur"]))}</span>'
            f'<span style="white-space:nowrap">{chips}</span></div>'
            f'<div class="sm"><div><b>{it["Lignes"]}</b><span>articles</span></div>'
            f'<div><b>{_fr(it["Poids net (kg)"], 3)}</b><span>kg net</span></div>'
            f'<div><b title="{vals}">{vals}</b><span>valeur HT</span></div></div>'
            f'<div class="sf">{it["Factures"]} facture(s)'
            + (f' · poids brut {_fr(it["Poids brut (kg)"], 3)} kg' if it.get("Poids brut (kg)") else "") + "</div></div>")
    st.markdown(f'<div class="sgrid">{"".join(cards)}</div>', unsafe_allow_html=True)


def file_list(rows: list[dict]):
    """Contrôle des fichiers avant traitement : type, taille, statut (OK / problème + message)."""
    body = []
    for r in rows:
        status = chip("Prêt", "ok") if r["ok"] else chip("À corriger", "ko")
        msg = "" if r["ok"] else f' <span style="color:var(--ink2)">{html.escape(r["message"])}</span>'
        body.append(f'<tr><td>{html.escape(r["name"])[:60]}</td><td class="mut">{html.escape(r["type"])}</td>'
                    f'<td class="mut">{html.escape(r["size"])}</td><td>{status}{msg}</td></tr>')
    st.markdown(f'<table class="flist"><tbody>{"".join(body)}</tbody></table>', unsafe_allow_html=True)
