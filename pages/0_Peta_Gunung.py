import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os
import re as _re
from pathlib import Path

st.set_page_config(
    page_title="HikeMetric · Peta Gunung Jawa",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────
#  LOAD DATA FROM JSON
# ─────────────────────────────────────────────────────────────────────

@st.cache_data
def load_jalur_data(path: str) -> dict:
    """Load trail data from JSON and index by mountain name."""
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return {item["gunung"]: item["jalur"] for item in raw}

# Cari JSON di beberapa lokasi umum
JSON_CANDIDATES = [
    "./dataset_41_gunung_semua_jalur.json",
    "./data/dataset_41_gunung_semua_jalur.json",
    os.path.join(os.path.dirname(__file__), "dataset_41_gunung_semua_jalur.json"),
]
JALUR_DB: dict = {}
for _p in JSON_CANDIDATES:
    if os.path.exists(_p):
        JALUR_DB = load_jalur_data(_p)
        break

# ─────────────────────────────────────────────────────────────────────
#  KOORDINAT & METADATA GUNUNG (expanded to cover JSON mountains)
# ─────────────────────────────────────────────────────────────────────

COORDS_DB = {
    # Jawa Barat
    "Gede Pangrango":  {"lat": -6.7818,  "lon": 107.0149, "mdpl": 3019, "provinsi": "Jawa Barat"},
    "Ciremai":         {"lat": -6.8916,  "lon": 108.4075, "mdpl": 3078, "provinsi": "Jawa Barat"},
    "Papandayan":      {"lat": -7.3194,  "lon": 107.7305, "mdpl": 2665, "provinsi": "Jawa Barat"},
    "Cikuray":         {"lat": -7.2358,  "lon": 107.8439, "mdpl": 2818, "provinsi": "Jawa Barat"},
    "Galunggung":      {"lat": -7.2554,  "lon": 108.0549, "mdpl": 2168, "provinsi": "Jawa Barat"},
    "Guntur":          {"lat": -7.1436,  "lon": 107.8381, "mdpl": 2249, "provinsi": "Jawa Barat"},
    "Halimun":         {"lat": -6.7280,  "lon": 106.5400, "mdpl": 1929, "provinsi": "Jawa Barat"},
    "Salak":           {"lat": -6.7228,  "lon": 106.7320, "mdpl": 2211, "provinsi": "Jawa Barat"},
    "Burangrang":      {"lat": -6.7009,  "lon": 107.4360, "mdpl": 2064, "provinsi": "Jawa Barat"},
    "Manglayang":      {"lat": -6.8870,  "lon": 107.7210, "mdpl": 1818, "provinsi": "Jawa Barat"},
    "Rakutak":         {"lat": -7.1200,  "lon": 107.5900, "mdpl": 1922, "provinsi": "Jawa Barat"},
    "Sanghyang":       {"lat": -6.7600,  "lon": 107.5900, "mdpl": 2195, "provinsi": "Jawa Barat"},
    "Patuha":          {"lat": -7.1500,  "lon": 107.4000, "mdpl": 2434, "provinsi": "Jawa Barat"},
    "Wayang":          {"lat": -7.2000,  "lon": 107.5200, "mdpl": 2181, "provinsi": "Jawa Barat"},
    "Malabar":         {"lat": -7.2200,  "lon": 107.6500, "mdpl": 2321, "provinsi": "Jawa Barat"},
    "Tangkuban Perahu":{"lat": -6.7700,  "lon": 107.6100, "mdpl": 2084, "provinsi": "Jawa Barat"},
    "Bongkok":         {"lat": -6.6200,  "lon": 107.3900, "mdpl": 1920, "provinsi": "Jawa Barat"},
    "Parang":          {"lat": -6.7100,  "lon": 107.4600, "mdpl": 1894, "provinsi": "Jawa Barat"},
    "Sanggabuana":     {"lat": -6.6600,  "lon": 107.2100, "mdpl": 1291, "provinsi": "Jawa Barat"},
    "Tampomas":        {"lat": -6.7700,  "lon": 107.9700, "mdpl": 1684, "provinsi": "Jawa Barat"},
    "Pulosari":        {"lat": -6.3500,  "lon": 105.9700, "mdpl": 1346, "provinsi": "Banten"},
    "Karang":          {"lat": -6.2700,  "lon": 105.9300, "mdpl": 1778, "provinsi": "Banten"},
    # Jawa Tengah
    "Merbabu":         {"lat": -7.4553,  "lon": 110.4342, "mdpl": 3145, "provinsi": "Jawa Tengah"},
    "Merapi":          {"lat": -7.5407,  "lon": 110.4457, "mdpl": 2968, "provinsi": "Jawa Tengah"},
    "Sindoro":         {"lat": -7.3036,  "lon": 109.9994, "mdpl": 3150, "provinsi": "Jawa Tengah"},
    "Sumbing":         {"lat": -7.3836,  "lon": 110.0628, "mdpl": 3371, "provinsi": "Jawa Tengah"},
    "Lawu":            {"lat": -7.6295,  "lon": 111.1927, "mdpl": 3265, "provinsi": "Jawa Tengah"},
    "Slamet":          {"lat": -7.2428,  "lon": 109.2082, "mdpl": 3428, "provinsi": "Jawa Tengah"},
    "Andong":          {"lat": -7.4244,  "lon": 110.3994, "mdpl": 1726, "provinsi": "Jawa Tengah"},
    "Bismo":           {"lat": -7.3397,  "lon": 109.9156, "mdpl": 2365, "provinsi": "Jawa Tengah"},
    "Ungaran":         {"lat": -7.1814,  "lon": 110.3322, "mdpl": 2050, "provinsi": "Jawa Tengah"},
    "Prau":            {"lat": -7.2260,  "lon": 109.9260, "mdpl": 2565, "provinsi": "Jawa Tengah"},
    "Telomoyo":        {"lat": -7.3200,  "lon": 110.4200, "mdpl": 1894, "provinsi": "Jawa Tengah"},
    "Muria":           {"lat": -6.5900,  "lon": 110.8800, "mdpl": 1602, "provinsi": "Jawa Tengah"},
    "Tapak":           {"lat": -7.1000,  "lon": 110.3500, "mdpl": 1495, "provinsi": "Jawa Tengah"},
    # Jawa Timur
    "Semeru":          {"lat": -8.1089,  "lon": 112.9224, "mdpl": 3676, "provinsi": "Jawa Timur"},
    "Arjuno":          {"lat": -7.7298,  "lon": 112.5952, "mdpl": 3339, "provinsi": "Jawa Timur"},
    "Welirang":        {"lat": -7.6431,  "lon": 112.5779, "mdpl": 3156, "provinsi": "Jawa Timur"},
    "Ijen":            {"lat": -8.0580,  "lon": 114.2422, "mdpl": 2799, "provinsi": "Jawa Timur"},
    "Argopuro":        {"lat": -7.9792,  "lon": 113.5651, "mdpl": 3088, "provinsi": "Jawa Timur"},
    "Anjasmoro":       {"lat": -7.7050,  "lon": 112.5470, "mdpl": 2277, "provinsi": "Jawa Timur"},
    "Kelud":           {"lat": -7.9330,  "lon": 112.3080, "mdpl": 1731, "provinsi": "Jawa Timur"},
    "Butak":           {"lat": -8.0640,  "lon": 112.3510, "mdpl": 2868, "provinsi": "Jawa Timur"},
    "Kembang":         {"lat": -7.8700,  "lon": 112.5700, "mdpl": 2609, "provinsi": "Jawa Timur"},
    "Penanggungan":    {"lat": -7.6230,  "lon": 112.6270, "mdpl": 1653, "provinsi": "Jawa Timur"},
    "Liman":           {"lat": -7.8800,  "lon": 111.6600, "mdpl": 2563, "provinsi": "Jawa Timur"},
    "Wilis":           {"lat": -7.8100,  "lon": 111.7500, "mdpl": 2169, "provinsi": "Jawa Timur"},
    "Kawi":            {"lat": -8.0200,  "lon": 112.4400, "mdpl": 2651, "provinsi": "Jawa Timur"},
    "Bromo":           {"lat": -7.9425,  "lon": 112.9530, "mdpl": 2329, "provinsi": "Jawa Timur"},
    "Raung":           {"lat": -8.1250,  "lon": 114.0440, "mdpl": 3332, "provinsi": "Jawa Timur"},
    "Telong":          {"lat": -7.8700,  "lon": 113.8500, "mdpl": 1748, "provinsi": "Jawa Timur"},
}

# ─────────────────────────────────────────────────────────────────────
#  KATEGORI KESULITAN → normalize from JSON field
# ─────────────────────────────────────────────────────────────────────

def normalize_kesulitan(jalur_list: list) -> str:
    """Derive overall difficulty from list of trails."""
    mapping = {"Pemula": 1, "Menengah": 2, "Ahli": 3}
    if not jalur_list:
        return "Sedang"
    max_level = max(mapping.get(j.get("kesulitan", "Menengah"), 2) for j in jalur_list)
    return {1: "Mudah", 2: "Sedang", 3: "Sulit"}[max_level]

def jalur_icon(kesulitan: str) -> str:
    return {"Mudah": "🟢", "Sedang": "🟡", "Sulit": "🔴"}.get(kesulitan, "⚪")

def gunung_icon(mdpl: int) -> str:
    if mdpl >= 3000: return "🌋"
    if mdpl >= 2000: return "⛰️"
    return "🏔️"

# ─────────────────────────────────────────────────────────────────────
#  BUILD COMBINED DATABASE  (JSON + coords)
# ─────────────────────────────────────────────────────────────────────

@st.cache_data
def build_gunung_db(jalur_db: dict, coords_db: dict) -> dict:
    db = {}
    for gunung_name, jalur_list in jalur_db.items():
        coords = coords_db.get(gunung_name)
        if not coords:
            continue  # skip gunung without coordinate data
        mdpl = coords["mdpl"]
        jalur_utama = jalur_list[0]["nama_jalur"] if jalur_list else "-"
        # estimasi from shortest trail
        first = jalur_list[0] if jalur_list else {}
        naik  = first.get("estimasi_naik", "-")
        turun = first.get("estimasi_turun", "-")
        kesulitan = normalize_kesulitan(jalur_list)
        db[gunung_name] = {
            "lat":           coords["lat"],
            "lon":           coords["lon"],
            "mdpl":          mdpl,
            "provinsi":      coords["provinsi"],
            "kesulitan":     kesulitan,
            "jalur_utama":   jalur_utama,
            "estimasi_naik": naik,
            "estimasi_turun": turun,
            "total_jalur":   len(jalur_list),
            "icon":          gunung_icon(mdpl),
            "jalur_list":    jalur_list,
        }
    return db

GUNUNG_DB = build_gunung_db(JALUR_DB, COORDS_DB)

KESULITAN_COLOR = {
    "Mudah":  "#22c55e",
    "Sedang": "#f59e0b",
    "Sulit":  "#ef4444",
}

KESULITAN_BG = {
    "Mudah":  "#dcfce7",
    "Sedang": "#fef3c7",
    "Sulit":  "#fee2e2",
}

# ─────────────────────────────────────────────────────────────────────
#  CSS / THEME
# ─────────────────────────────────────────────────────────────────────

def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

    :root {
        --bg:        #f0f7f0;
        --bg2:       #ffffff;
        --bg3:       #e8f5e9;
        --card:      #ffffff;
        --border:    #c8e6c9;
        --accent:    #2e7d32;
        --accent2:   #43a047;
        --accent-lt: #e8f5e9;
        --green:     #22c55e;
        --amber:     #f59e0b;
        --red:       #ef4444;
        --text:      #1b2e1c;
        --muted:     #6a8f6b;
        --radius:    16px;
        --shadow:    0 2px 12px rgba(46,125,50,0.08);
    }

    html, body, .stApp, [data-testid="stAppViewContainer"] {
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--bg2) !important;
        border-right: 1px solid var(--border) !important;
        box-shadow: 2px 0 12px rgba(46,125,50,0.06) !important;
    }
    [data-testid="stSidebar"] * { color: var(--text) !important; }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: var(--accent) !important; }
    [data-testid="stSidebar"] hr { border-color: var(--border) !important; }

    /* ── Inputs ── */
    .stTextInput > div > div {
        background: var(--bg2) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text) !important;
    }
    .stTextInput > div > div input { color: var(--text) !important; }
    .stTextInput > div > div:focus-within { border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(46,125,50,0.12) !important; }

    .stRadio label { color: var(--text) !important; }
    .stRadio [data-testid="stWidgetLabel"] { color: var(--muted) !important; font-size: 12px !important; }

    .stSelectbox > div > div,
    [data-baseweb="select"] > div {
        background: var(--bg2) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text) !important;
    }
    [data-baseweb="select"] span, [data-baseweb="select"] div { color: var(--text) !important; background: transparent !important; }
    [data-baseweb="popover"], [data-baseweb="menu"], ul[data-baseweb="menu"] {
        background: var(--bg2) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 24px rgba(46,125,50,0.12) !important;
    }
    [data-baseweb="menu"] li, [data-baseweb="menu"] [role="option"] {
        background: transparent !important; color: var(--text) !important; font-size: 14px !important;
    }
    [data-baseweb="menu"] li:hover, [data-baseweb="menu"] [aria-selected="true"] {
        background: var(--accent-lt) !important; color: var(--accent) !important; font-weight: 600 !important;
    }

    /* ── Buttons ── */
    div.stButton > button {
        background: linear-gradient(135deg, #2e7d32, #43a047) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; font-weight: 700 !important;
        font-size: 14px !important; padding: 10px 20px !important;
        width: 100%; transition: all 0.2s !important;
        box-shadow: 0 4px 14px rgba(46,125,50,0.25) !important;
    }
    div.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 18px rgba(46,125,50,0.35) !important; }

    /* ── Custom cards ── */
    .hm-navbar {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 60%, #43a047 100%);
        border-bottom: none;
        padding: 18px 28px;
        margin-bottom: 20px;
        display: flex; align-items: center; gap: 14px;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 20px rgba(27,94,32,0.2);
    }
    .hm-logo {
        font-size: 26px; font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
        text-shadow: 0 1px 4px rgba(0,0,0,0.15);
    }
    .hm-sub { font-size: 13px; color: rgba(255,255,255,0.75); font-weight: 500; }

    .stat-card {
        background: var(--bg2);
        border: 1.5px solid var(--border);
        border-radius: var(--radius);
        padding: 14px 16px;
        margin-bottom: 10px;
        display: flex; align-items: center; gap: 12px;
        box-shadow: var(--shadow);
        transition: box-shadow 0.2s;
    }
    .stat-card:hover { box-shadow: 0 4px 20px rgba(46,125,50,0.14); }
    .stat-icon { font-size: 22px; }
    .stat-label { font-size: 12px; color: var(--muted); font-weight: 500; }
    .stat-value { font-size: 18px; font-weight: 800; color: var(--accent); }

    .detail-panel {
        background: var(--card);
        border: 1.5px solid var(--border);
        border-radius: var(--radius);
        padding: 22px;
        box-shadow: var(--shadow);
        animation: slideUp 0.25s ease;
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .detail-name {
        font-size: 22px; font-weight: 800;
        color: var(--accent);
        margin: 0 0 2px 0;
    }
    .detail-sub { font-size: 13px; color: var(--muted); margin-bottom: 16px; }

    .badge {
        display: inline-flex; align-items: center; gap: 5px;
        border-radius: 20px; padding: 4px 12px;
        font-size: 12px; font-weight: 700;
        margin: 2px;
    }
    .badge-mdpl { background: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }
    .badge-easy { background: #dcfce7; color: #16a34a; }
    .badge-med  { background: #fef3c7; color: #d97706; }
    .badge-hard { background: #fee2e2; color: #dc2626; }

    .info-row {
        background: var(--accent-lt);
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
        font-size: 13px; color: var(--text);
        border-left: 3px solid var(--accent);
    }
    .info-row b { color: var(--accent); }

    .trail-chip {
        background: var(--bg3);
        border: 1.5px solid var(--border);
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 6px;
        font-size: 12px;
        transition: border-color 0.15s;
    }
    .trail-chip:hover { border-color: var(--accent); }
    .trail-name { font-weight: 700; color: var(--text); font-size: 13px; margin-bottom: 2px; }
    .trail-meta { color: var(--muted); }

    .list-item {
        background: var(--card);
        border: 1.5px solid var(--border);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 6px;
        cursor: pointer;
        transition: all 0.15s;
        box-shadow: var(--shadow);
    }
    .list-item:hover { border-color: var(--accent); background: var(--accent-lt); box-shadow: 0 4px 14px rgba(46,125,50,0.12); }
    .list-item-name { font-weight: 700; font-size: 14px; color: var(--text); }
    .list-item-sub  { font-size: 12px; color: var(--muted); }

    .legend-row { display: flex; gap: 16px; margin-top: 8px; flex-wrap: wrap; }
    .legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--muted); }
    .legend-dot  { width: 10px; height: 10px; border-radius: 50%; }

    .empty-state {
        background: var(--card);
        border: 1.5px solid var(--border);
        border-radius: var(--radius);
        padding: 40px 24px;
        text-align: center;
        box-shadow: var(--shadow);
    }
    .empty-icon { font-size: 52px; margin-bottom: 12px; }
    .empty-title { font-size: 17px; font-weight: 700; color: var(--accent); margin-bottom: 6px; }
    .empty-desc  { font-size: 13px; color: var(--muted); line-height: 1.7; }

    .prov-header {
        font-size: 11px; font-weight: 700; letter-spacing: 1px;
        color: var(--accent); text-transform: uppercase;
        margin: 14px 0 6px 2px;
        border-bottom: 1px solid var(--border);
        padding-bottom: 4px;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────

def build_popup(name: str, info: dict) -> str:
    color = KESULITAN_COLOR.get(info["kesulitan"], "#2e7d32")
    trails_preview = "".join(
        f"<div style='font-size:11px;color:#6a8f6b;margin-top:2px;'>• {j['nama_jalur']} ({j['jarak_km']} km)</div>"
        for j in info["jalur_list"][:3]
    )
    more = f"<div style='font-size:11px;color:#a5c8a6;margin-top:3px;'>+{len(info['jalur_list'])-3} jalur lainnya</div>" if len(info["jalur_list"]) > 3 else ""
    return f"""
    <div style="font-family:'Plus Jakarta Sans',sans-serif;min-width:220px;padding:4px;background:#ffffff;color:#1b2e1c;border-radius:10px;">
        <div style="font-size:16px;font-weight:800;color:#2e7d32;margin-bottom:2px;">{info['icon']} {name}</div>
        <div style="font-size:11px;color:#e65100;font-weight:600;margin-bottom:6px;">👆 Klik marker → panel detail</div>
        <div style="font-size:12px;color:#6a8f6b;margin-bottom:8px;">{info['provinsi']}</div>
        <div style="display:flex;gap:5px;flex-wrap:wrap;margin-bottom:8px;">
            <span style="background:#e8f5e9;color:#2e7d32;border-radius:8px;padding:2px 8px;font-size:11px;font-weight:700;border:1px solid #c8e6c9;">⛰️ {info['mdpl']:,} mdpl</span>
            <span style="background:{color}22;color:{color};border-radius:8px;padding:2px 8px;font-size:11px;font-weight:700;">● {info['kesulitan']}</span>
            <span style="background:#f1f8e9;color:#558b2f;border-radius:8px;padding:2px 8px;font-size:11px;font-weight:700;">🗺 {info['total_jalur']} jalur</span>
        </div>
        <div style="font-size:12px;color:#6a8f6b;font-weight:600;margin-bottom:4px;">Jalur tersedia:</div>
        {trails_preview}{more}
    </div>
    """


def find_gunung_by_coords(lat, lng, db, threshold=0.05):
    best_name, best_dist = None, threshold
    for name, info in db.items():
        dist = ((info["lat"] - lat) ** 2 + (info["lon"] - lng) ** 2) ** 0.5
        if dist < best_dist:
            best_dist, best_name = dist, name
    return best_name


def badge_class(k):
    return {"Mudah": "badge-easy", "Sedang": "badge-med", "Sulit": "badge-hard"}.get(k, "badge-med")


# ─────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────

if "selected_gunung" not in st.session_state:
    st.session_state["selected_gunung"] = None

# ─────────────────────────────────────────────────────────────────────
#  RENDER
# ─────────────────────────────────────────────────────────────────────

apply_theme()

# ── Navbar ──
st.markdown("""
<div class="hm-navbar">
    <span class="hm-logo">⛰ HikeMetric</span>
    <span class="hm-sub">Peta Interaktif Gunung Jawa &amp; Sekitarnya</span>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("<h2 style='margin-top:0;'>🔍 Filter</h2>", unsafe_allow_html=True)
    st.markdown("---")

    search_q = st.text_input("Cari gunung...", placeholder="contoh: Semeru, Prau…")

    kesulitan_filter = st.radio(
        "Kesulitan Maksimal",
        ["Semua", "Mudah", "Sedang", "Sulit"],
        horizontal=False,
    )

    provinsi_list = sorted(set(v["provinsi"] for v in GUNUNG_DB.values()))
    provinsi_filter = st.selectbox("Provinsi", ["Semua Provinsi"] + provinsi_list)

    st.markdown("---")
    st.markdown("### 📊 Ringkasan Data")

    total    = len(GUNUNG_DB)
    total_jalur = sum(v["total_jalur"] for v in GUNUNG_DB.values())
    sulit    = sum(1 for v in GUNUNG_DB.values() if v["kesulitan"] == "Sulit")
    mudah    = sum(1 for v in GUNUNG_DB.values() if v["kesulitan"] == "Mudah")

    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon">⛰️</div>
        <div><div class="stat-label">Total Gunung</div><div class="stat-value">{total}</div></div>
    </div>
    <div class="stat-card">
        <div class="stat-icon">🗺️</div>
        <div><div class="stat-label">Total Jalur</div><div class="stat-value">{total_jalur}</div></div>
    </div>
    <div class="stat-card">
        <div class="stat-icon">🟢</div>
        <div><div class="stat-label">Mudah / Sulit</div><div class="stat-value">{mudah} / {sulit}</div></div>
    </div>
    """, unsafe_allow_html=True)

    if not JALUR_DB:
        st.warning("⚠️ File JSON tidak ditemukan.\nLetakkan `dataset_41_gunung_semua_jalur.json` di folder yang sama dengan script ini.")

# ── Filter data ──
def passes_filter(name, info):
    if search_q and search_q.lower() not in name.lower():
        return False
    if kesulitan_filter != "Semua":
        order = {"Mudah": 1, "Sedang": 2, "Sulit": 3}
        if order.get(info["kesulitan"], 2) > order.get(kesulitan_filter, 3):
            return False
    if provinsi_filter != "Semua Provinsi" and info["provinsi"] != provinsi_filter:
        return False
    return True

filtered = {k: v for k, v in GUNUNG_DB.items() if passes_filter(k, v)}

# ── Layout ──
col_map, col_detail = st.columns([3, 1.25], gap="medium")

with col_map:
    # Map
    m = folium.Map(
        location=[-7.3, 110.0],
        zoom_start=7,
        tiles=None,
        prefer_canvas=True,
    )
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satelit",
        overlay=False,
        control=True,
    ).add_to(m)
    folium.TileLayer(
        tiles="CartoDB dark_matter",
        name="Dark Map",
        overlay=False,
        control=True,
    ).add_to(m)
    folium.TileLayer(
        tiles="CartoDB positron",
        name="Light Map",
        overlay=False,
        control=True,
    ).add_to(m)
    folium.LayerControl(position="topright").add_to(m)

    for name, info in filtered.items():
        color = KESULITAN_COLOR.get(info["kesulitan"], "#2e7d32")
        is_selected = st.session_state["selected_gunung"] == name
        border_color = "#1b5e20" if is_selected else "#ffffff"
        size = 38 if is_selected else 32
        shadow = f"0 0 16px {color}bb, 0 3px 8px rgba(0,0,0,0.2)" if is_selected else "0 3px 8px rgba(0,0,0,0.25)"

        icon_html = f"""
        <div style="
            background:{color};
            border:3px solid {border_color};
            border-radius:50%;
            width:{size}px;height:{size}px;
            display:flex;align-items:center;justify-content:center;
            font-size:16px;
            box-shadow:{shadow};
            cursor:pointer;
            transition:all 0.2s;
        ">{info['icon']}</div>
        """
        folium.Marker(
            location=[info["lat"], info["lon"]],
            icon=folium.DivIcon(
                html=icon_html,
                icon_size=(size, size),
                icon_anchor=(size // 2, size // 2),
                class_name="",
            ),
            popup=folium.Popup(
                folium.IFrame(build_popup(name, info), width=260, height=200),
                max_width=270,
            ),
            tooltip=folium.Tooltip(
                f"<b style='font-family:Plus Jakarta Sans,sans-serif;color:#2e7d32'>{name}</b>"
                f"<br><span style='font-size:11px;color:#6a8f6b'>{info['mdpl']:,} mdpl · {info['kesulitan']} · {info['total_jalur']} jalur</span>",
                sticky=True,
            ),
        ).add_to(m)

    map_data = st_folium(
        m, width="100%", height=580,
        returned_objects=["last_object_clicked", "last_object_clicked_tooltip"],
        key="main_map",
    )

    # Legend
    st.markdown("""
    <div class="legend-row">
        <div class="legend-item"><div class="legend-dot" style="background:#22c55e"></div>Mudah</div>
        <div class="legend-item"><div class="legend-dot" style="background:#f59e0b"></div>Sedang</div>
        <div class="legend-item"><div class="legend-dot" style="background:#ef4444"></div>Sulit</div>
        <div class="legend-item">🌋 = Volcano · ⛰️ = High · 🏔️ = Low</div>
        <div class="legend-item" style="margin-left:auto;">
            Menampilkan <b style="color:#2e7d32">""" + str(len(filtered)) + """</b> dari <b style="color:#2e7d32">""" + str(len(GUNUNG_DB)) + """</b> gunung
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Detect click ──
clicked_name = None
loc = map_data.get("last_object_clicked") if map_data else None
if loc and isinstance(loc, dict):
    clat = loc.get("lat") or loc.get("latitude")
    clng = loc.get("lng") or loc.get("longitude")
    if clat and clng:
        clicked_name = find_gunung_by_coords(clat, clng, filtered)
        if not clicked_name:
            clicked_name = find_gunung_by_coords(clat, clng, GUNUNG_DB)

if not clicked_name and map_data and map_data.get("last_object_clicked_tooltip"):
    raw = map_data["last_object_clicked_tooltip"]
    match = _re.search(r"<b[^>]*>(.*?)</b>", raw)
    if match:
        candidate = match.group(1).strip()
        if candidate in GUNUNG_DB:
            clicked_name = candidate

if clicked_name:
    st.session_state["selected_gunung"] = clicked_name

selected = st.session_state["selected_gunung"]

# ── Detail Panel ──
with col_detail:
    if selected and selected in GUNUNG_DB:
        info  = GUNUNG_DB[selected]
        color = KESULITAN_COLOR.get(info["kesulitan"], "#2e7d32")
        bc    = badge_class(info["kesulitan"])

        st.markdown(f"""
        <div class="detail-panel">
            <div class="detail-name">{info['icon']} {selected}</div>
            <div class="detail-sub">{info['provinsi']}</div>
            <div style="margin-bottom:14px;">
                <span class="badge badge-mdpl">⛰️ {info['mdpl']:,} mdpl</span>
                <span class="badge {bc}">● {info['kesulitan']}</span>
                <span class="badge" style="background:#f1f8e9;color:#558b2f;border:1px solid #c5e1a5;">
                    🗺 {info['total_jalur']} jalur
                </span>
            </div>
            <div class="info-row">
                <b>⏱ Estimasi Naik</b><br>{info['estimasi_naik']} (via {info['jalur_utama']})
            </div>
            <div class="info-row">
                <b>⬇️ Estimasi Turun</b><br>{info['estimasi_turun']}
            </div>
            <div style="font-size:12px;font-weight:700;color:#6a8f6b;text-transform:uppercase;letter-spacing:0.5px;margin:14px 0 8px 0;">
                Semua Jalur
            </div>
        """, unsafe_allow_html=True)

        for j in info["jalur_list"]:
            jc   = KESULITAN_COLOR.get(
                {"Pemula": "Mudah", "Menengah": "Sedang", "Ahli": "Sulit"}.get(j["kesulitan"], "Sedang"),
                "#f59e0b"
            )
            jlabel = {"Pemula": "Mudah", "Menengah": "Sedang", "Ahli": "Sulit"}.get(j["kesulitan"], j["kesulitan"])
            jicon  = {"Mudah": "🟢", "Sedang": "🟡", "Sulit": "🔴"}.get(jlabel, "⚪")
            st.markdown(f"""
            <div class="trail-chip">
                <div class="trail-name">{jicon} {j['nama_jalur']}</div>
                <div class="trail-meta">
                    📏 {j['jarak_km']} km &nbsp;·&nbsp;
                    ⬆️ {j['estimasi_naik']} &nbsp;·&nbsp;
                    <span style="color:{jc};font-weight:600;">{j['kesulitan']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns([4, 1])
        with col_a:
            if st.button(f"📊 Analisis {selected}", key="btn_analisis"):
                # Set session_state langsung — lebih andal daripada query_params
                # karena switch_page bisa race dengan query_params commit
                st.session_state["preselect_gunung"] = selected
                st.session_state["auto_run_gunung"]  = selected
                st.switch_page("pages/1_Pendakian.py")
        with col_b:
            if st.button("✕", key="btn_close"):
                st.session_state["selected_gunung"] = None
                st.rerun()

    else:
        # Empty state + mountain list
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🗺️</div>
            <div class="empty-title">Pilih Gunung</div>
            <div class="empty-desc">Klik marker di peta untuk melihat detail jalur dan memulai analisis pendakian.</div>
        </div>
        """, unsafe_allow_html=True)

        if filtered:
            st.markdown("<br>", unsafe_allow_html=True)
            # Group by provinsi
            by_prov: dict = {}
            for name, info in filtered.items():
                by_prov.setdefault(info["provinsi"], []).append((name, info))

            for prov in sorted(by_prov.keys()):
                st.markdown(f'<div class="prov-header">📍 {prov}</div>', unsafe_allow_html=True)
                for name, info in sorted(by_prov[prov], key=lambda x: -x[1]["mdpl"])[:8]:
                    c = KESULITAN_COLOR.get(info["kesulitan"], "#38bdf8")
                    st.markdown(f"""
                    <div class="list-item" style="border-left: 3px solid {c};">
                        <div class="list-item-name">{info['icon']} {name}</div>
                        <div class="list-item-sub">
                            {info['mdpl']:,} mdpl &nbsp;·&nbsp;
                            <span style="color:{c};">{info['kesulitan']}</span> &nbsp;·&nbsp;
                            {info['total_jalur']} jalur
                        </div>
                    </div>
                    """, unsafe_allow_html=True)