import streamlit as st
import datetime
import pandas as pd
import requests
import os
import json
import gpxpy
import folium
from streamlit_folium import folium_static
import re
import base64
import glob
try:
    import fitz  # PyMuPDF
    _PYMUPDF_OK = True
except ImportError:
    _PYMUPDF_OK = False

# ─────────────────────────────────────────────
#  SHARED THEME
# ─────────────────────────────────────────────
def apply_custom_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── GLOBAL ── */
    html, body, .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: #eef2f3 !important;
        color: #1a1a1a !important;
    }

    #MainMenu, footer, header { visibility: hidden; }

    [data-testid="stSidebarNav"] a span,
    [data-testid="stSidebarNav"] span,
    [data-testid="stSidebarNavItems"] span {
        color: #1a1a1a !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] span {
        color: #1B5E20 !important;
        font-weight: 700 !important;
    }

    /* ── CUSTOM NAVBAR ── */
    .hm-navbar {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
        color: white;
        padding: 18px 32px;
        font-size: 22px;
        font-weight: 800;
        letter-spacing: 0.5px;
        border-radius: 0 0 20px 20px;
        margin-bottom: 28px;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 4px 20px rgba(27,94,32,0.25);
    }

    /* ── CARD ── */
    .hm-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.07);
        border: 1px solid rgba(0,0,0,0.05);
    }
    .hm-card h2, .hm-card h3, .hm-card h4 {
        color: #1B5E20 !important;
        font-weight: 700;
        margin-top: 0;
    }

    /* ── ANALYSIS HEADER BANNER ── */
    .hm-analysis-banner {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 70%, #FF5722 100%);
        border-radius: 16px;
        padding: 22px 28px;
        color: white;
        margin-bottom: 20px;
    }
    .hm-analysis-banner h2 { color: white !important; margin: 0; font-size: 22px; }
    .hm-analysis-banner p  { color: rgba(255,255,255,0.85); margin: 6px 0 0 0; font-size: 14px; }

    /* ── ORANGE PRIMARY BUTTON ── */
    div.stButton > button {
        background: linear-gradient(135deg, #FF5722, #E64A19) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 14px 24px !important;
        width: 100%;
        box-shadow: 0 4px 14px rgba(255,87,34,0.35) !important;
        transition: transform 0.15s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255,87,34,0.45) !important;
    }

    /* ── DOWNLOAD BUTTON ── */
    div.stDownloadButton > button {
        background: #E8F5E9 !important;
        color: #2E7D32 !important;
        border: 1.5px solid #A5D6A7 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e0e0e0 !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stCaption p {
        color: #1a1a1a !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #1B5E20 !important;
        font-weight: 700;
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 12px; }

    /* ── METRICS ── */
    [data-testid="stMetricValue"] > div {
        color: #2E7D32 !important;
        font-weight: 800 !important;
        font-size: 26px !important;
    }
    [data-testid="stMetricLabel"] p { color: #666 !important; font-size: 13px !important; }
    [data-testid="metric-container"] {
        background: white;
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.07);
        border: 1px solid #f0f0f0;
    }

    /* ── INPUTS ── */
    .stSelectbox > div > div,
    .stDateInput > div > div,
    .stTextInput > div > div {
        border-radius: 10px !important;
        border: 1.5px solid #ddd !important;
        background: #ffffff !important;
        color: #1a1a1a !important;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] *,
    [data-testid="stSelectbox"] span,
    [data-baseweb="select"] span,
    [data-testid="stDateInput"] input,
    [data-baseweb="input"] input {
        color: #1a1a1a !important;
        background: transparent !important;
    }

    /* ── DROPDOWN POPOVER ── */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    ul[data-baseweb="menu"] {
        background: #ffffff !important;
        border: 1.5px solid #e0e0e0 !important;
        border-radius: 14px !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12) !important;
        overflow: hidden !important;
    }
    [data-baseweb="menu"] li,
    [data-baseweb="menu"] [role="option"] {
        background: #ffffff !important;
        color: #1a1a1a !important;
        font-size: 14px !important;
        padding: 10px 16px !important;
        border-radius: 0 !important;
        transition: background 0.15s !important;
    }
    [data-baseweb="menu"] li:hover,
    [data-baseweb="menu"] [role="option"]:hover,
    [data-baseweb="menu"] [aria-selected="true"] {
        background: #E8F5E9 !important;
        color: #1B5E20 !important;
        font-weight: 600 !important;
    }
    [data-baseweb="menu"] [aria-selected="true"] {
        background: #C8E6C9 !important;
        color: #1B5E20 !important;
    }
    [data-baseweb="menu"]::-webkit-scrollbar { width: 6px; }
    [data-baseweb="menu"]::-webkit-scrollbar-thumb {
        background: #A5D6A7;
        border-radius: 6px;
    }

    /* ── ALERTS ── */
    .stAlert { border-radius: 12px !important; }

    /* ── WARNING / SAFETY BOX ── */
    .hm-alert {
        background: #FFF3E0;
        border-left: 4px solid #FF5722;
        border-radius: 0 12px 12px 0;
        padding: 14px 18px;
        color: #BF360C;
        font-size: 14px;
        margin: 8px 0;
    }

    /* ── SECTION HEADERS ── */
    .hm-section-title {
        font-size: 18px;
        font-weight: 700;
        color: #1B5E20;
        margin: 0 0 16px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ── DATAFRAME ── */
    [data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden; }

    /* ── MAP WRAPPER ── */
    .hm-map-wrap {
        border-radius: 14px;
        overflow: hidden;
        border: 2px solid #E8F5E9;
    }

    /* ── EMPTY STATE ── */
    .hm-empty {
        text-align: center;
        padding: 48px 24px;
        color: #888;
    }
    .hm-empty .icon { font-size: 56px; margin-bottom: 16px; }
    .hm-empty h3    { color: #555 !important; font-size: 18px; }
    .hm-empty p     { font-size: 14px; }

    /* ── DIVIDER ── */
    hr { border-color: #e8e8e8 !important; margin: 16px 0 !important; }
    .main h1, .main h2, .main h3 { color: #1B5E20 !important; }

    /* ── SPINNER ── */
    [data-testid="stSpinner"] {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%) !important;
        border-radius: 16px !important;
        padding: 20px 24px !important;
        margin: 12px 0 !important;
        box-shadow: 0 8px 28px rgba(27,94,32,0.25) !important;
        display: flex !important;
        align-items: center !important;
        gap: 16px !important;
        position: relative !important;
        overflow: hidden !important;
    }
    [data-testid="stSpinner"]::before {
        content: "";
        position: absolute;
        top: 0; left: -100%;
        width: 60%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
        animation: hm-shimmer 1.8s infinite;
    }
    @keyframes hm-shimmer {
        0%   { left: -100%; }
        100% { left: 200%; }
    }
    [data-testid="stSpinner"] p,
    [data-testid="stSpinner"] span,
    [data-testid="stSpinner"] div {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        letter-spacing: 0.2px !important;
    }
    [data-testid="stSpinner"] svg {
        stroke: #ffffff !important;
        fill: none !important;
        width: 26px !important;
        height: 26px !important;
    }
    [data-testid="stStatusWidget"],
    [data-testid="stStatusWidget"] * {
        display: none !important;
    }
    [data-testid="stSpinner"]::after {
        content: "";
        position: absolute;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
        width: 10px; height: 10px;
        background: #FF5722;
        border-radius: 50%;
        animation: hm-pulse 1.2s ease-in-out infinite;
    }
    @keyframes hm-pulse {
        0%, 100% { opacity: 1; transform: translateY(-50%) scale(1); }
        50%       { opacity: 0.4; transform: translateY(-50%) scale(0.6); }
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
for _k, _v in {
    'analysis_run':       False,
    'jalur_descriptions': {},
    'current_gunung':     None,
    'current_kebugaran':  None,
    'gpx_data':           (None, None, [], []),
    'weather_info':       (None, False),
    'structured_weather': None,
    'auto_run_gunung':    None,
    'preselect_gunung':   None,
    'gaya_pendakian':     'Tektok (PP dalam 1 hari)',
    'ai_gaya':            {},
    'twitter_sentiment':  {},
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
GPX_FOLDER_PATH    = './data_gpx'
TWITTER_FOLDER     = './data_twitter'
GROQ_API_KEY       = st.secrets.get("GROQ_API_KEY")
OWM_API_KEY        = st.secrets.get("OWM_API_KEY")

st.set_page_config(page_title="HIKE METRIC", page_icon="📈", layout="wide")

# ─────────────────────────────────────────────
#  GUNUNG YANG DITUTUP (status berbahaya)
# ─────────────────────────────────────────────
GUNUNG_DITUTUP = {
    'Semeru': {
        'status':  'Awas (Level IV)',
        'alasan':  'Gunung Semeru berstatus Awas (Level IV) — erupsi aktif dengan luncuran awan panas dan lahar dingin yang berbahaya. Pendakian resmi DITUTUP oleh TNBTS hingga status diturunkan.',
        'sumber':  'PVMBG & TNBTS',
        'warna':   '#B71C1C',
        'bg':      '#FFEBEE',
        'border':  '#EF5350',
        'icon':    '🌋',
    },
    'Merapi': {
        'status':  'Siaga (Level III)',
        'alasan':  'Gunung Merapi berstatus Siaga (Level III) — aktivitas vulkanik tinggi dengan guguran lava dan awan panas. Radius aman ditetapkan hingga 7 km dari puncak. Pendakian wisata DITUTUP oleh BPPTKG.',
        'sumber':  'PVMBG & BPPTKG',
        'warna':   '#E65100',
        'bg':      '#FFF3E0',
        'border':  '#FF8F00',
        'icon':    '⛔',
    },
}

# ─────────────────────────────────────────────
#  KEBUGARAN → KESULITAN MAPPING
# ─────────────────────────────────────────────
KEBUGARAN_TO_KESULITAN = {
    'Rendah': 'Pemula',
    'Sedang': 'Menengah',
    'Tinggi': 'Ahli',
}
KESULITAN_ORDER = ['Pemula', 'Menengah', 'Ahli']
KESULITAN_STYLE = {
    'Pemula':   {'icon': '🟢', 'color': '#2E7D32', 'bg': '#E8F5E9', 'border': '#43A047', 'header': 'linear-gradient(90deg,#2E7D32,#66BB6A)'},
    'Menengah': {'icon': '🟡', 'color': '#F57F17', 'bg': '#FFFDE7', 'border': '#FBC02D', 'header': 'linear-gradient(90deg,#F57F17,#FFCA28)'},
    'Ahli':     {'icon': '🔴', 'color': '#C62828', 'bg': '#FFEBEE', 'border': '#E53935', 'header': 'linear-gradient(90deg,#C62828,#EF5350)'},
}

# ─────────────────────────────────────────────
#  UTIL
# ─────────────────────────────────────────────
def extract_json_from_text(text: str):
    if not text:
        return None
    start = text.find('{')
    end   = text.rfind('}')
    if start == -1 or end == -1 or end <= start:
        return None
    candidate = text[start:end+1]
    candidate = re.sub(r'```json', '', candidate, flags=re.IGNORECASE)
    candidate = re.sub(r'```', '', candidate)
    candidate = re.sub(r',\s*}', '}', candidate)
    candidate = re.sub(r',\s*\]', ']', candidate)
    candidate = ''.join(ch for ch in candidate if ch.isprintable())
    stack = 0
    for ch in candidate:
        if ch == '{': stack += 1
        elif ch == '}': stack -= 1
        if stack < 0:
            return None
    return candidate if stack == 0 else None


# ─────────────────────────────────────────────
#  TWITTER / SENTIMEN
# ─────────────────────────────────────────────

# Kata kunci sentimen Bahasa Indonesia
_POSITIF_KW = [
    'indah', 'bagus', 'keren', 'mantap', 'seru', 'luar biasa', 'recommended',
    'rekomen', 'rekomendasi', 'cantik', 'asik', 'asyik', 'menyenangkan',
    'senang', 'bahagia', 'puas', 'wajib', 'must', 'amazing', 'beautiful',
    'sunrise', 'sunset', 'pemandangan', 'menakjubkan', 'spektakuler',
    'terbaik', 'favorit', 'suka', 'cinta', 'wow', 'kece', 'kece badai',
    'worth', 'worth it', 'berhasil', 'sampai puncak', 'summit', 'puncak',
    'selamat', 'aman', 'lancar', 'bersih', 'terawat', 'rapi',
]
_NEGATIF_KW = [
    'berbahaya', 'bahaya', 'erupsi', 'meletus', 'letusan', 'bencana',
    'tutup', 'ditutup', 'lahar', 'awan panas', 'evakuasi', 'korban',
    'meninggal', 'tewas', 'hilang', 'tersesat', 'macet', 'kotor',
    'sampah', 'rusak', 'jelek', 'buruk', 'kecewa', 'mengecewakan',
    'susah', 'sulit', 'berbatu', 'longsor', 'banjir', 'hujan deras',
    'gelap', 'takut', 'panik', 'tergelincir', 'jatuh', 'gagal',
    'tidak aman', 'waspada', 'siaga', 'awas', 'dilarang', 'bahaya',
]

def _sentimen_keyword(text: str) -> str:
    """Analisis sentimen berbasis keyword. Kembalikan 'Positif', 'Negatif', atau 'Netral'."""
    tl = text.lower()
    pos = sum(1 for kw in _POSITIF_KW if kw in tl)
    neg = sum(1 for kw in _NEGATIF_KW if kw in tl)
    if pos > neg:
        return 'Positif'
    elif neg > pos:
        return 'Negatif'
    return 'Netral'


def _sentimen_badge(sentimen: str) -> tuple:
    """Kembalikan (emoji, warna_teks, warna_bg) untuk badge sentimen."""
    return {
        'Positif': ('😊', '#1B5E20', '#E8F5E9'),
        'Negatif': ('😟', '#B71C1C', '#FFEBEE'),
        'Netral':  ('😐', '#4A4A4A', '#F5F5F5'),
    }.get(sentimen, ('😐', '#4A4A4A', '#F5F5F5'))


@st.cache_data(show_spinner=False, ttl=1800)
def load_all_twitter_data(twitter_folder: str) -> pd.DataFrame:
    """
    Baca semua file gunung*.csv dari folder data_twitter.
    Kembalikan DataFrame gabungan dengan kolom: full_text, created_at, username, favorite_count, retweet_count.
    """
    pattern = os.path.join(twitter_folder, 'gunung*.csv')
    files   = sorted(glob.glob(pattern))
    if not files:
        return pd.DataFrame()
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f, low_memory=False)
            df.columns = [c.strip() for c in df.columns]
            dfs.append(df)
        except Exception:
            pass
    if not dfs:
        return pd.DataFrame()
    combined = pd.concat(dfs, ignore_index=True)
    # Pastikan kolom yang diperlukan ada
    for col in ['full_text', 'created_at', 'username', 'favorite_count', 'retweet_count']:
        if col not in combined.columns:
            combined[col] = ''
    combined['full_text'] = combined['full_text'].fillna('').astype(str)
    # Drop duplikat berdasarkan id_str jika ada
    if 'id_str' in combined.columns:
        combined = combined.drop_duplicates(subset='id_str')
    return combined


# Keyword yang menandakan tweet RELEVAN untuk pendakian
_HIKING_RELEVANCE_KW = [
    # Aktivitas mendaki
    'mendaki', 'pendakian', 'hiking', 'naik gunung', 'turun gunung',
    'summit', 'puncak', 'basecamp', 'base camp', 'camp', 'tenda', 'camping',
    # Jalur & medan
    'jalur', 'trek', 'trekking', 'rute', 'pos ', 'pos1', 'pos2', 'pos3',
    'savana', 'sabana', 'hutan', 'kawah', 'batu', 'tanah', 'tanjakan',
    'turunan', 'medan', 'vegetasi', 'panorama', 'pemandangan',
    # Cuaca di gunung
    'sunrise', 'sunset', 'kabut', 'hujan di gunung', 'angin kencang',
    'suhu dingin', 'embun', 'cuaca',
    # Logistik & perlengkapan
    'carrier', 'ransel', 'sleeping bag', 'matras', 'trekking pole',
    'headlamp', 'gaiter', 'porter', 'logistik', 'perbekalan', 'bekal',
    # Keselamatan & kondisi
    'licin', 'longsor', 'tersesat', 'evakuasi', 'simaksi', 'tiket masuk',
    'registrasi', 'rescue', 'sar',
    # Komunitas pendaki
    'pendaki', 'rombongan', 'tim pendaki', 'solo hiking', 'summit attack',
    'aklimatisasi', 'carry on', 'turun aman', 'sampai puncak', 'berhasil',
]

# Keyword yang menandakan tweet TIDAK RELEVAN (spam, off-topic)
_HIKING_IRRELEVANCE_KW = [
    'promo', 'diskon', 'jual', 'beli', 'dijual', 'follow', 'giveaway',
    'retweet', 'kontes', 'lomba', 'politik', 'pilkada', 'pemilu',
    'artis', 'drakor', 'dramal', 'nonton', 'film', 'musik', 'konser',
    'resep', 'masakan', 'kuliner', 'restoran', 'cafe', 'kafe',
    'fashion', 'outfit', 'ootd',
]


def _hitung_skor_relevansi(text: str) -> int:
    """
    Hitung skor relevansi hiking sebuah tweet.
    Skor positif = konten hiking, skor negatif = off-topic.
    """
    tl = text.lower()
    skor = sum(1 for kw in _HIKING_RELEVANCE_KW if kw in tl)
    skor -= sum(2 for kw in _HIKING_IRRELEVANCE_KW if kw in tl)
    return skor


def filter_tweets_for_gunung(gunung_name: str, all_tweets: pd.DataFrame, max_tweets: int = 20) -> pd.DataFrame:
    """
    Filter tweet yang relevan dengan gunung tertentu DAN relevan dengan konten hiking.
    """
    if all_tweets.empty:
        return pd.DataFrame()

    gunung_lower = gunung_name.lower()
    core_name = re.sub(r'^(gunung|gn|mt\.?\s*|mount\s*)', '', gunung_lower).strip()

    patterns = [core_name]
    if ' ' in core_name:
        patterns.append(core_name.split()[0])

    # Step 1: filter berdasarkan nama gunung
    mask = all_tweets['full_text'].str.lower().str.contains(
        '|'.join(re.escape(p) for p in patterns), na=False
    )
    filtered = all_tweets[mask].copy()

    if filtered.empty:
        return pd.DataFrame()

    # Step 2: hitung skor relevansi hiking per tweet
    filtered['relevansi_skor'] = filtered['full_text'].apply(_hitung_skor_relevansi)

    # Step 3: buang tweet yang tidak relevan (skor < 1)
    filtered = filtered[filtered['relevansi_skor'] >= 1].copy()

    if filtered.empty:
        return pd.DataFrame()

    # Step 4: tambah kolom sentimen
    filtered['sentimen'] = filtered['full_text'].apply(_sentimen_keyword)

    # Step 5: urutkan berdasarkan relevansi + engagement
    for col in ['favorite_count', 'retweet_count']:
        filtered[col] = pd.to_numeric(filtered[col], errors='coerce').fillna(0)

    filtered = filtered.sort_values(
        by=['relevansi_skor', 'favorite_count', 'retweet_count'],
        ascending=False
    ).head(max_tweets)

    return filtered

def compute_sentiment_summary(tweets_df: pd.DataFrame, total_sebelum_filter: int = 0) -> dict:
    """Hitung ringkasan sentimen dari DataFrame tweet yang sudah difilter."""
    if tweets_df.empty:
        return {
            'positif': 0, 'negatif': 0, 'netral': 0,
            'total': 0, 'dominant': 'Netral',
            'disaring': total_sebelum_filter,
        }
    counts = tweets_df['sentimen'].value_counts().to_dict()
    pos = counts.get('Positif', 0)
    neg = counts.get('Negatif', 0)
    net = counts.get('Netral', 0)
    total = pos + neg + net
    if pos >= neg and pos >= net:
        dominant = 'Positif'
    elif neg >= pos and neg >= net:
        dominant = 'Negatif'
    else:
        dominant = 'Netral'
    return {
        'positif': pos, 'negatif': neg, 'netral': net,
        'total': total, 'dominant': dominant,
        'disaring': max(0, total_sebelum_filter - total),
    }

# ─────────────────────────────────────────────
#  AI: FALLBACK ULASAN KOMUNITAS
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_ai_community_reviews(gunung: str, kebugaran: str) -> list:
    """
    Minta AI menghasilkan 2-3 ulasan komunitas realistis jika tidak ada data Twitter.
    Kembalikan list of dict: {nama, bintang, komentar, waktu, emoji, sentimen}
    """
    if not GROQ_API_KEY:
        return []

    prompt = f"""Kamu adalah asisten yang menghasilkan ulasan komunitas pendaki gunung Indonesia yang realistis.

Buatkan 3 ulasan pendaki untuk Gunung {gunung} dengan variasi sentimen (2 positif, 1 netral atau negatif).
Tingkat kebugaran rata-rata pendaki: {kebugaran}.

Setiap ulasan harus mencerminkan pengalaman nyata: kondisi jalur, cuaca, pemandangan, pos, dll.
Gunakan bahasa Indonesia santai/gaul seperti ulasan nyata di media sosial.

Output HANYA JSON murni (tanpa backtick/markdown):
{{
  "ulasan": [
    {{
      "nama": "nama pendaki fiktif realistis",
      "bintang": angka 1-5,
      "komentar": "ulasan 2-3 kalimat",
      "waktu": "X hari/minggu/bulan lalu",
      "emoji": "1 emoji relevan",
      "sentimen": "Positif" atau "Negatif" atau "Netral"
    }}
  ]
}}"""

    raw = call_groq_api(prompt, temperature=0.8)
    try:
        result = json.loads(raw) if raw else None
    except Exception:
        cleaned = extract_json_from_text(raw or '')
        try:
            result = json.loads(cleaned) if cleaned else None
        except Exception:
            result = None

    if result and isinstance(result.get('ulasan'), list):
        return result['ulasan']
    return []


# ─────────────────────────────────────────────
#  RENDER: CATATAN KOMUNITAS DARI TWITTER
# ─────────────────────────────────────────────
def render_komunitas_twitter(gunung_name: str, tweets_df: pd.DataFrame, sentiment_summary: dict, ai_fallback: list):
    has_twitter_data = not tweets_df.empty
    source_label = "📊 Data Twitter/X Nyata" if has_twitter_data else "🤖 Ulasan AI"
    source_color = "#1565C0" if has_twitter_data else "#6A1B9A"
    source_bg    = "#E3F2FD" if has_twitter_data else "#F3E5F5"

    dom = sentiment_summary.get('dominant', 'Netral')
    dom_emoji, dom_fc, dom_bg = _sentimen_badge(dom)
    total_data   = sentiment_summary.get('total', len(ai_fallback))
    total_disaring = sentiment_summary.get('disaring', 0)

    # ── Header banner ──
    st.markdown(f"""
        <div style="background:#1B5E20;border-radius:20px;overflow:hidden;
                    margin-bottom:16px;border:1px solid rgba(0,0,0,0.06);">
            <div style="padding:20px 24px 14px;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;
                            flex-wrap:wrap;gap:12px;margin-bottom:14px;">
                    <div>
                        <div style="font-size:18px;font-weight:700;color:white;">
                            💬 Catatan Komunitas Pendaki
                        </div>
                        <div style="font-size:13px;color:rgba(255,255,255,0.7);margin-top:3px;">
                            Pengalaman nyata dari pendaki <strong style="color:white;">{gunung_name}</strong>
                            &mdash; filter relevansi hiking aktif
                        </div>
                    </div>
                    <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
                        <div style="background:{source_bg};border-radius:8px;
                                    padding:4px 12px;font-size:12px;font-weight:600;
                                    color:{source_color};">{source_label}</div>
                        <div style="background:rgba(255,255,255,0.12);border-radius:12px;
                                    padding:8px 14px;text-align:center;">
                            <div style="font-size:20px;">{dom_emoji}</div>
                            <div style="font-size:10px;color:rgba(255,255,255,0.75);
                                        margin-top:2px;font-weight:600;">Mayoritas {dom}</div>
                        </div>
                    </div>
                </div>
    """, unsafe_allow_html=True)

    # ── Bar sentimen ──
    if has_twitter_data and total_data > 0:
        pos_pct = round(sentiment_summary['positif'] / total_data * 100)
        neg_pct = round(sentiment_summary['negatif'] / total_data * 100)
        net_pct = 100 - pos_pct - neg_pct
        disaring_info = (
            f" &nbsp;|&nbsp; 🔍 {total_disaring} tweet non-hiking disaring"
            if total_disaring > 0 else ""
        )
        st.markdown(f"""
                <div style="background:rgba(0,0,0,0.15);border-radius:10px;padding:12px 16px;">
                    <div style="font-size:11px;color:rgba(255,255,255,0.65);
                                margin-bottom:8px;font-weight:500;">
                        📊 Distribusi dari {total_data} tweet relevan hiking{disaring_info}
                    </div>
                    <div style="display:flex;gap:3px;height:10px;border-radius:20px;overflow:hidden;">
                        <div style="flex:{pos_pct};background:#43A047;border-radius:20px 0 0 20px;min-width:4px;"></div>
                        <div style="flex:{net_pct};background:#9E9E9E;min-width:2px;"></div>
                        <div style="flex:{neg_pct};background:#E53935;border-radius:0 20px 20px 0;min-width:4px;"></div>
                    </div>
                    <div style="display:flex;gap:16px;margin-top:8px;flex-wrap:wrap;">
                        <span style="font-size:11px;color:rgba(255,255,255,0.85);">
                            😊 Positif: <strong>{sentiment_summary['positif']}</strong> ({pos_pct}%)
                        </span>
                        <span style="font-size:11px;color:rgba(255,255,255,0.85);">
                            😐 Netral: <strong>{sentiment_summary['netral']}</strong> ({net_pct}%)
                        </span>
                        <span style="font-size:11px;color:rgba(255,255,255,0.85);">
                            😟 Negatif: <strong>{sentiment_summary['negatif']}</strong> ({neg_pct}%)
                        </span>
                    </div>
                </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # ── Helper: ekstrak keyword yang terdeteksi dari sebuah tweet ──
    def _ekstrak_keyword_terdeteksi(text: str, max_kw: int = 4) -> list:
        tl = text.lower()
        found = [kw.strip() for kw in _HIKING_RELEVANCE_KW if kw.strip() in tl]
        # Deduplikasi & ambil max_kw
        seen = set()
        result = []
        for kw in found:
            if kw not in seen:
                seen.add(kw)
                result.append(kw)
            if len(result) >= max_kw:
                break
        return result

    # ── Render kartu tweet ──
    if has_twitter_data:
        # Grid kartu: 2 kolom jika layar cukup lebar
        cols = st.columns(2)
        show_tweets = tweets_df.head(6)

        for idx, (_, row) in enumerate(show_tweets.iterrows()):
            text      = str(row.get('full_text', '')).strip()
            user      = str(row.get('username', 'Pengguna X')).strip() or 'Pengguna X'
            fav       = int(row.get('favorite_count', 0))
            rt        = int(row.get('retweet_count', 0))
            sentimen  = str(row.get('sentimen', 'Netral'))
            skor_rel  = int(row.get('relevansi_skor', 1))
            created   = str(row.get('created_at', '')).strip()

            s_emoji, s_fc, s_bg = _sentimen_badge(sentimen)

            # Warna garis atas kartu per sentimen
            top_color = {'Positif': '#43A047', 'Negatif': '#E53935'}.get(sentimen, '#9E9E9E')

            try:
                dt = datetime.datetime.strptime(created, '%a %b %d %H:%M:%S +0000 %Y')
                waktu_str = dt.strftime('%d %b %Y')
            except Exception:
                waktu_str = created[:10] if len(created) >= 10 else 'Baru-baru ini'

            # Bersihkan teks
            display_text = re.sub(r'https?://\S+', '', text).strip()
            if len(display_text) > 240:
                display_text = display_text[:237] + '...'

            # Keyword yang terdeteksi
            kw_detected = _ekstrak_keyword_terdeteksi(text)
            kw_html = ''.join([
                f'<span style="background:#F1F8E9;color:#33691E;font-size:10px;'
                f'border-radius:20px;padding:2px 8px;display:inline-block;">{kw}</span>'
                for kw in kw_detected
            ])

            # Indikator relevansi (dot 1–5, max skor ~5)
            rel_level = min(max(skor_rel, 1), 5)
            dots_html = ''.join([
                f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
                f'background:{"#2E7D32" if i < rel_level else "#E0E0E0"};margin-right:3px;"></span>'
                for i in range(5)
            ])

            col = cols[idx % 2]
            with col:
                st.markdown(f"""
                    <div style="background:white;border-radius:14px;overflow:hidden;
                                margin-bottom:12px;border:1px solid #F0F0F0;">
                        <div style="height:3px;background:{top_color};"></div>
                        <div style="padding:14px 16px;">
                            <div style="display:flex;justify-content:space-between;
                                        align-items:flex-start;margin-bottom:10px;">
                                <div style="display:flex;align-items:center;gap:10px;">
                                    <div style="width:36px;height:36px;border-radius:50%;
                                                background:#E3F2FD;display:flex;align-items:center;
                                                justify-content:center;font-size:14px;
                                                color:#1565C0;flex-shrink:0;font-weight:600;">𝕏</div>
                                    <div>
                                        <div style="font-weight:700;font-size:13px;color:#1a1a1a;">
                                            @{user[:22]}
                                        </div>
                                        <div style="font-size:11px;color:#999;">{waktu_str}</div>
                                    </div>
                                </div>
                                <span style="background:{s_bg};color:{s_fc};font-size:11px;
                                             font-weight:700;padding:3px 10px;border-radius:20px;
                                             flex-shrink:0;">{s_emoji} {sentimen}</span>
                            </div>
                            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                                <span style="font-size:10px;color:#777;white-space:nowrap;">
                                    Relevansi hiking
                                </span>
                                <div>{dots_html}</div>
                            </div>
                            <div style="font-size:13px;color:#444;line-height:1.65;
                                        border-top:1px dashed #eee;padding-top:10px;">
                                {display_text}
                            </div>
                            {f'<div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:8px;">{kw_html}</div>' if kw_html else ''}
                            <div style="display:flex;justify-content:space-between;
                                        align-items:center;margin-top:10px;">
                                <div style="display:flex;gap:10px;">
                                    <span style="font-size:11px;color:#aaa;">❤️ {fav}</span>
                                    <span style="font-size:11px;color:#aaa;">🔁 {rt}</span>
                                </div>
                                <span style="font-size:10px;color:#ccc;">Twitter/X</span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        # AI fallback — tampilan tetap sama
        if not ai_fallback:
            st.info("Tidak ada data ulasan komunitas tersedia untuk gunung ini.")
        else:
            cols = st.columns(2)
            for idx, ulasan in enumerate(ai_fallback):
                nama     = ulasan.get('nama', 'Pendaki')
                bintang  = '⭐' * min(max(int(ulasan.get('bintang', 4)), 1), 5)
                komentar = ulasan.get('komentar', '')
                waktu    = ulasan.get('waktu', '1 bulan lalu')
                emoji    = ulasan.get('emoji', '🏔️')
                sentimen = ulasan.get('sentimen', 'Netral')
                s_emoji, s_fc, s_bg = _sentimen_badge(sentimen)
                top_color = {'Positif': '#43A047', 'Negatif': '#E53935'}.get(sentimen, '#9E9E9E')

                col = cols[idx % 2]
                with col:
                    st.markdown(f"""
                        <div style="background:white;border-radius:14px;overflow:hidden;
                                    margin-bottom:12px;border:1px solid #F0F0F0;">
                            <div style="height:3px;background:{top_color};"></div>
                            <div style="padding:14px 16px;">
                                <div style="display:flex;justify-content:space-between;
                                            align-items:flex-start;margin-bottom:10px;">
                                    <div style="display:flex;align-items:center;gap:10px;">
                                        <div style="width:36px;height:36px;border-radius:50%;
                                                    background:#E8F5E9;display:flex;align-items:center;
                                                    justify-content:center;font-size:18px;flex-shrink:0;">
                                            {emoji}
                                        </div>
                                        <div>
                                            <div style="font-weight:700;font-size:13px;color:#1a1a1a;">{nama}</div>
                                            <div style="font-size:11px;color:#999;">{waktu}</div>
                                        </div>
                                    </div>
                                    <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;">
                                        <div style="font-size:12px;">{bintang}</div>
                                        <span style="background:{s_bg};color:{s_fc};font-size:11px;
                                                     font-weight:700;padding:2px 8px;border-radius:20px;">
                                            {s_emoji} {sentimen}
                                        </span>
                                    </div>
                                </div>
                                <div style="font-size:13px;color:#444;line-height:1.65;
                                            border-top:1px dashed #eee;padding-top:10px;">
                                    "{komentar}"
                                </div>
                                <div style="margin-top:8px;">
                                    <span style="font-size:10px;color:#bbb;font-style:italic;">
                                        🤖 Dihasilkan AI — tidak ada data Twitter tersedia
                                    </span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    # ── Divider info filter ──
    if has_twitter_data and total_disaring > 0:
        st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin:8px 0 12px;">
                <div style="flex:1;height:1px;background:#E0E0E0;"></div>
                <span style="font-size:11px;color:#999;white-space:nowrap;">
                    🔍 {total_disaring} tweet tidak relevan hiking disaring otomatis
                </span>
                <div style="flex:1;height:1px;background:#E0E0E0;"></div>
            </div>
        """, unsafe_allow_html=True)

    # ── Footer ──
    footer_note = (
        f"💡 Menampilkan {total_data} tweet relevan hiking dari Gunung {gunung_name}. "
        "Sentimen & relevansi dianalisis otomatis — kondisi jalur aktual dapat berbeda."
        if has_twitter_data else
        "🤖 Ulasan dihasilkan AI karena tidak ada data Twitter tersedia. "
        "Selalu cek info terkini sebelum mendaki."
    )
    st.markdown(f"""
        <div style="background:#F9FBF9;border-radius:10px;padding:10px 16px;
                    border:1px solid #E8F5E9;">
            <span style="font-size:12px;color:#666;">{footer_note}</span>
        </div>
    """, unsafe_allow_html=True)
    
# ─────────────────────────────────────────────
#  RENDER: BANNER GUNUNG DITUTUP
# ─────────────────────────────────────────────
def render_gunung_ditutup_banner(gunung_name: str):
    """Tampilkan banner peringatan untuk gunung yang ditutup karena bahaya aktif."""
    info = GUNUNG_DITUTUP.get(gunung_name)
    if not info:
        return False  # Tidak ditutup

    st.markdown(f"""
        <div style="background:{info['bg']};border:2px solid {info['border']};
                    border-radius:20px;overflow:hidden;margin-bottom:24px;
                    box-shadow:0 8px 32px rgba(0,0,0,0.15);">
            <!-- Header merah/oranye -->
            <div style="background:linear-gradient(135deg,{info['warna']} 0%,{info['border']} 100%);
                        padding:20px 28px;display:flex;align-items:center;gap:16px;">
                <div style="font-size:48px;">{info['icon']}</div>
                <div>
                    <div style="font-size:22px;font-weight:900;color:white;letter-spacing:0.5px;">
                        ⛔ GUNUNG {gunung_name.upper()} DITUTUP
                    </div>
                    <div style="font-size:14px;color:rgba(255,255,255,0.85);margin-top:4px;font-weight:600;">
                        Status Gunung Api: {info['status']}
                    </div>
                </div>
            </div>
            <!-- Body peringatan -->
            <div style="padding:20px 28px;">
                <div style="font-size:15px;color:{info['warna']};line-height:1.8;font-weight:600;margin-bottom:16px;">
                    {info['alasan']}
                </div>
                <div style="display:flex;flex-wrap:wrap;gap:12px;margin-bottom:16px;">
                    <div style="background:white;border:1.5px solid {info['border']};border-radius:12px;
                                padding:12px 18px;display:flex;align-items:center;gap:10px;">
                        <span style="font-size:24px;">🚫</span>
                        <div>
                            <div style="font-weight:700;font-size:13px;color:{info['warna']};">Pendakian Dilarang</div>
                            <div style="font-size:12px;color:#666;">Hingga status diturunkan</div>
                        </div>
                    </div>
                    <div style="background:white;border:1.5px solid {info['border']};border-radius:12px;
                                padding:12px 18px;display:flex;align-items:center;gap:10px;">
                        <span style="font-size:24px;">📡</span>
                        <div>
                            <div style="font-weight:700;font-size:13px;color:{info['warna']};">Pantau Status</div>
                            <div style="font-size:12px;color:#666;">pvmbg.esdm.go.id / BMKG</div>
                        </div>
                    </div>
                    <div style="background:white;border:1.5px solid {info['border']};border-radius:12px;
                                padding:12px 18px;display:flex;align-items:center;gap:10px;">
                        <span style="font-size:24px;">📋</span>
                        <div>
                            <div style="font-weight:700;font-size:13px;color:{info['warna']};">Sumber Resmi</div>
                            <div style="font-size:12px;color:#666;">{info['sumber']}</div>
                        </div>
                    </div>
                </div>
                <div style="background:white;border-radius:12px;padding:14px 18px;
                            border-left:4px solid {info['border']};">
                    <div style="font-size:13px;color:#444;line-height:1.7;">
                        ⚠️ <b>Peringatan Keras:</b> Memasuki kawasan gunung yang berstatus berbahaya dapat 
                        mengancam jiwa. Patuhi larangan resmi dari pemerintah dan otoritas terkait. 
                        Informasi jalur di bawah ini ditampilkan untuk keperluan <b>edukasi dan referensi saja</b>, 
                        BUKAN panduan untuk mendaki saat ini.
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    return True  # Gunung memang ditutup


# ─────────────────────────────────────────────
#  DATASET JALUR PENDAKIAN (JSON)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_jalur_dataset() -> list:
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dataset_41_gunung_semua_jalur.json'),
        os.path.join(os.getcwd(), 'dataset_41_gunung_semua_jalur.json'),
        os.path.join(os.getcwd(), 'pages', 'dataset_41_gunung_semua_jalur.json'),
        'dataset_41_gunung_semua_jalur.json',
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.warning(f"Dataset jalur ditemukan di `{path}` tapi gagal dibaca: {e}")
    st.error("⚠️ File `dataset_41_gunung_semua_jalur.json` tidak ditemukan.")
    return []


def get_gunung_list(data: list) -> list:
    return sorted([g['gunung'] for g in data])


def get_jalur_by_kebugaran(data: list, gunung_name: str, kebugaran: str):
    target_kes = KEBUGARAN_TO_KESULITAN.get(kebugaran, 'Menengah')
    gunung_data = next(
        (g for g in data if g['gunung'].lower() == gunung_name.lower()), None
    )
    if not gunung_data:
        return [], False, f"Gunung **{gunung_name}** tidak ditemukan di dataset."
    matched = [j for j in gunung_data['jalur'] if j['kesulitan'] == target_kes]
    if matched:
        return matched, True, ""
    target_idx = KESULITAN_ORDER.index(target_kes)
    for offset in [1, -1, 2, -2]:
        alt_idx = target_idx + offset
        if 0 <= alt_idx < len(KESULITAN_ORDER):
            alt_kes = KESULITAN_ORDER[alt_idx]
            fallback = [j for j in gunung_data['jalur'] if j['kesulitan'] == alt_kes]
            if fallback:
                arah = "lebih mudah" if alt_idx < target_idx else "lebih menantang"
                msg = (
                    f"💡 Gunung **{gunung_name}** tidak memiliki jalur tingkat **{target_kes}** "
                    f"yang sesuai kebugaran **{kebugaran}**. "
                    f"Menampilkan jalur **{alt_kes}** ({arah}) yang paling mendekati."
                )
                return fallback, False, msg
    return gunung_data['jalur'], False, (
        f"Menampilkan semua {len(gunung_data['jalur'])} jalur yang tersedia "
        f"untuk Gunung **{gunung_name}**."
    )


# ─────────────────────────────────────────────
#  ESTIMASI WAKTU
# ─────────────────────────────────────────────
_MULTIPLIERS = {
    'Rendah': {'naik': 1.9,  'turun': 1.6},
    'Sedang': {'naik': 1.0,  'turun': 1.0},
    'Tinggi': {'naik': 0.75, 'turun': 0.65},
}

def _parse_jam_range(s: str) -> tuple:
    try:
        s = str(s).lower().replace('jam', '').strip()
        if '-' in s:
            parts = [float(p.strip()) for p in s.split('-')]
            return (parts[0], parts[-1])
        v = float(s)
        return (v, v)
    except Exception:
        return (0.0, 0.0)

def _fmt_jam(v: float) -> str:
    return str(int(v)) if v == int(v) else str(v)

def get_estimasi_jalur(jalur: dict, kebugaran: str) -> tuple:
    m   = _MULTIPLIERS.get(kebugaran, _MULTIPLIERS['Sedang'])
    nr  = _parse_jam_range(jalur.get('estimasi_naik',  '0'))
    tr  = _parse_jam_range(jalur.get('estimasi_turun', '0'))
    n_lo = round(nr[0] * m['naik'],  1)
    n_hi = round(nr[1] * m['naik'],  1)
    t_lo = round(tr[0] * m['turun'], 1)
    t_hi = round(tr[1] * m['turun'], 1)
    naik_str  = f"{_fmt_jam(n_lo)}-{_fmt_jam(n_hi)} jam" if n_lo != n_hi else f"{_fmt_jam(n_lo)} jam"
    turun_str = f"{_fmt_jam(t_lo)}-{_fmt_jam(t_hi)} jam" if t_lo != t_hi else f"{_fmt_jam(t_lo)} jam"
    naik_float  = round((nr[0] + nr[1]) / 2 * m['naik'],  1)
    turun_float = round((tr[0] + tr[1]) / 2 * m['turun'], 1)
    return naik_str, turun_str, naik_float, turun_float


# ─────────────────────────────────────────────
#  GPX HELPERS
# ─────────────────────────────────────────────
def _normalize_gpx_name(s: str) -> str:
    s = s.lower()
    s = re.sub(r'\.gpx$', '', s)
    s = re.sub(r'[_\-\.]+', ' ', s)
    s = re.sub(r'\b(gunung|gn|mt|mount)\b', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

@st.cache_data
def scan_gpx_folder(folder_path: str) -> pd.DataFrame:
    rows = []
    try:
        for fname in sorted(os.listdir(folder_path)):
            if fname.lower().endswith('.gpx'):
                normalized = _normalize_gpx_name(fname)
                rows.append({
                    'nama_file':       fname,
                    'nama_normalized': normalized,
                    'gpx_path':        os.path.join(folder_path, fname),
                })
    except FileNotFoundError:
        return pd.DataFrame()
    return pd.DataFrame(rows)

def find_gpx_for_gunung(gunung_name: str, scan_df: pd.DataFrame) -> str | None:
    if scan_df.empty:
        return None
    target = _normalize_gpx_name(gunung_name)
    target_words = target.split()
    mask = scan_df['nama_normalized'] == target
    if mask.any():
        return scan_df[mask].iloc[0]['gpx_path']
    def all_words_match(norm: str) -> bool:
        return all(w in norm for w in target_words)
    mask2 = scan_df['nama_normalized'].apply(all_words_match)
    if mask2.any():
        return scan_df[mask2].iloc[0]['gpx_path']
    if target_words:
        mask3 = scan_df['nama_normalized'].str.contains(re.escape(target_words[0]), na=False)
        if mask3.any():
            return scan_df[mask3].iloc[0]['gpx_path']
    return None

def find_pdf_for_gunung(gunung_name: str, folder_path: str) -> str | None:
    try:
        files = os.listdir(folder_path)
    except FileNotFoundError:
        return None
    target = _normalize_gpx_name(gunung_name)
    target_words = target.split()
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    for f in pdf_files:
        norm = _normalize_gpx_name(f.replace('.pdf', '.gpx'))
        if norm == target:
            return os.path.join(folder_path, f)
    for f in pdf_files:
        norm = _normalize_gpx_name(f.replace('.pdf', '.gpx'))
        if all(w in norm for w in target_words):
            return os.path.join(folder_path, f)
    if target_words:
        for f in pdf_files:
            norm = _normalize_gpx_name(f.replace('.pdf', '.gpx'))
            if target_words[0] in norm:
                return os.path.join(folder_path, f)
    return None

def get_coords_from_gpx(gpx_path: str):
    if not gpx_path or not os.path.exists(gpx_path):
        return None, None, [], []
    try:
        with open(gpx_path, 'r', encoding='utf-8') as fh:
            gpx = gpxpy.parse(fh)
        all_points = []
        for track in gpx.tracks:
            for seg in track.segments:
                pts = [(p.latitude, p.longitude)
                       for p in seg.points
                       if p.latitude is not None and p.longitude is not None]
                if pts:
                    all_points.append(pts)
        waypoints = []
        for wp in (gpx.waypoints or []):
            waypoints.append({'lat': wp.latitude, 'lon': wp.longitude, 'name': wp.name or 'Waypoint'})
        if all_points and all_points[0]:
            lat, lon = all_points[0][0]
        elif waypoints:
            lat, lon = waypoints[0]['lat'], waypoints[0]['lon']
        else:
            return None, None, [], []
        return lat, lon, all_points, waypoints
    except Exception:
        return None, None, [], []

@st.cache_data(show_spinner=False)
def load_gpx_content(gpx_path: str) -> bytes | None:
    if not os.path.exists(gpx_path):
        return None
    try:
        with open(gpx_path, 'rb') as f:
            return f.read()
    except Exception:
        return None


# ─────────────────────────────────────────────
#  WEATHER HELPERS (OWM)
# ─────────────────────────────────────────────
_WEATHER_ICON_MAP = {
    "cerah": "☀️", "clear": "☀️",
    "awan": "⛅", "cloud": "⛅", "berawan": "☁️", "overcast": "☁️",
    "hujan": "🌧️", "rain": "🌧️", "drizzle": "🌦️", "gerimis": "🌦️",
    "badai": "⛈️", "storm": "⛈️", "thunderstorm": "⛈️",
    "kabut": "🌫️", "fog": "🌫️", "mist": "🌫️", "haze": "🌫️",
    "salju": "❄️", "snow": "❄️",
}

def _weather_icon(desc: str) -> str:
    dl = desc.lower()
    for key, icon in _WEATHER_ICON_MAP.items():
        if key in dl:
            return icon
    return "🌡️"

@st.cache_data(ttl=900)
def get_weather_data(lat, lon, date_obj: datetime.date):
    if lat is None or lon is None or not OWM_API_KEY:
        return None, "Data koordinat atau kunci OWM tidak valid."
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric&lang=id&cnt=40"
    )
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
        days_needed = [date_obj + datetime.timedelta(days=i) for i in range(3)]
        day_buckets = {d: [] for d in days_needed}
        for item in data.get('list', []):
            item_date = datetime.datetime.fromtimestamp(item['dt']).date()
            if item_date in day_buckets:
                day_buckets[item_date].append(item)
        if not day_buckets[date_obj]:
            return None, "Tidak ada data prakiraan tersedia untuk tanggal tersebut dari OWM."
        compact_lines = []
        structured = []
        for d in days_needed:
            items = day_buckets[d]
            if not items:
                compact_lines.append(f"{d.strftime('%d %b')}: tidak ada data OWM")
                structured.append({
                    "date": d, "label": d.strftime("%A, %d %b"),
                    "temp_min": "-", "temp_max": "-",
                    "humidity": "-", "wind": "-",
                    "description": "Tidak ada data", "icon": "❓", "hourly": []
                })
                continue
            temps   = [i['main']['temp']    for i in items]
            humids  = [i['main']['humidity'] for i in items]
            descs   = [i['weather'][0]['description'] for i in items]
            wind_sp = [i['wind']['speed']   for i in items]
            icon    = _weather_icon(descs[0])
            compact_lines.append(
                f"{icon} {d.strftime('%A, %d %b')}: "
                f"suhu {min(temps):.0f}–{max(temps):.0f}°C, "
                f"kelembapan {sum(humids)//len(humids)}%, "
                f"angin {max(wind_sp):.1f} m/s, "
                f"kondisi: {descs[0]}"
            )
            hourly = []
            for item in items[:5]:
                t_str = item['dt_txt'].split()[1][:5]
                d_str = item['weather'][0]['description']
                hourly.append({
                    "time": t_str, "temp": round(item['main']['temp']),
                    "desc": d_str, "icon": _weather_icon(d_str),
                    "humidity": item['main']['humidity'], "wind": item['wind']['speed'],
                })
            structured.append({
                "date": d, "label": d.strftime("%A, %d %b"),
                "temp_min": round(min(temps)), "temp_max": round(max(temps)),
                "humidity": round(sum(humids) / len(humids)),
                "wind": round(max(wind_sp), 1),
                "description": descs[0], "icon": icon, "hourly": hourly,
            })
        summary_text = (
            f"Prakiraan cuaca 3 hari mulai {date_obj.strftime('%d %B %Y')}:\n"
            + "\n".join(compact_lines)
        )
        return structured, summary_text
    except Exception as e:
        return None, f"Gagal mengambil data cuaca OWM: {e}"


# ─────────────────────────────────────────────
#  LOGISTIK DATASET
# ─────────────────────────────────────────────
LOGISTIK_CSV_PATH = os.path.join(os.path.dirname(__file__), 'dataset_logistik_pendakian.csv')

KATEGORI_CONFIG = {
    'Umum': {
        'icon': '🧳', 'label': 'Perlengkapan Umum',
        'bg': 'linear-gradient(135deg,#E8F5E9,#F1F8E9)',
        'border': '#43A047', 'badge_bg': '#43A047',
        'chip_bg': '#E8F5E9', 'chip_color': '#1B5E20',
        'header_bg': 'linear-gradient(90deg,#2E7D32,#66BB6A)',
    },
    'Makanan': {
        'icon': '🍱', 'label': 'Makanan & Bekal',
        'bg': 'linear-gradient(135deg,#FFF3E0,#FFF8E1)',
        'border': '#FB8C00', 'badge_bg': '#FB8C00',
        'chip_bg': '#FFF3E0', 'chip_color': '#BF360C',
        'header_bg': 'linear-gradient(90deg,#E65100,#FFA726)',
    },
    'Hidrasi': {
        'icon': '💧', 'label': 'Hidrasi & Minuman',
        'bg': 'linear-gradient(135deg,#E3F2FD,#E8EAF6)',
        'border': '#1E88E5', 'badge_bg': '#1E88E5',
        'chip_bg': '#E3F2FD', 'chip_color': '#0D47A1',
        'header_bg': 'linear-gradient(90deg,#1565C0,#42A5F5)',
    },
}

@st.cache_data(show_spinner=False)
def load_logistik_dataset(csv_path=LOGISTIK_CSV_PATH) -> pd.DataFrame:
    candidates = [
        csv_path,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dataset_logistik_pendakian.csv'),
        os.path.join(os.getcwd(), 'dataset_logistik_pendakian.csv'),
        os.path.join(os.getcwd(), 'pages', 'dataset_logistik_pendakian.csv'),
        'dataset_logistik_pendakian.csv',
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                df.columns = [c.strip() for c in df.columns]
                return df
            except Exception as e:
                st.warning(f"CSV ditemukan di `{path}` tapi gagal dibaca: {e}")
                return pd.DataFrame()
    return pd.DataFrame()

_GAYA_TO_DURASI = {
    'Tektok (PP dalam 1 hari)':  '1 Hari',
    'Bermalam 1 malam':          '2 Hari',
    'Bermalam 2 malam':          '3 Hari',
    'Ekspedisi 3+ malam':        'Argopuro 4 Hari',
}

def estimate_durasi_label(naik_float, turun_float, gunung_name, gaya_pendakian='Tektok (PP dalam 1 hari)') -> str:
    if 'argopuro' in gunung_name.lower():
        return 'Argopuro 4 Hari'
    label = _GAYA_TO_DURASI.get(gaya_pendakian)
    if label:
        return label
    total = naik_float + turun_float
    if total <= 10:   return '1 Hari'
    elif total <= 20: return '2 Hari'
    elif total <= 30: return '3 Hari'
    else:             return 'Argopuro 4 Hari'

def get_logistik_by_durasi(durasi_label: str, df: pd.DataFrame) -> dict:
    if df.empty:
        return {}
    filtered = df[df['Durasi'].str.strip() == durasi_label]
    result = {}
    for kat in ['Umum', 'Makanan', 'Hidrasi']:
        sub = filtered[filtered['Kategori'].str.strip() == kat]
        if not sub.empty:
            result[kat] = sub.to_dict('records')
    return result

def render_logistik_cards(logistik_dict: dict, durasi_label: str):
    if not logistik_dict:
        st.warning("Data perlengkapan tidak tersedia untuk durasi ini.")
        return
    durasi_colors = {
        '1 Hari':          ('#E8F5E9', '#2E7D32', '🌄 Pendakian 1 Hari'),
        '2 Hari':          ('#E3F2FD', '#1565C0', '⛺ Pendakian 2 Hari'),
        '3 Hari':          ('#FFF3E0', '#E65100', '🏕️ Pendakian 3 Hari'),
        'Argopuro 4 Hari': ('#FCE4EC', '#C62828', '🏔️ Argopuro 4 Hari'),
    }
    dbg, dfc, dlabel = durasi_colors.get(durasi_label, ('#F5F5F5', '#555', durasi_label))
    st.markdown(
        f'<div style="background:{dbg};border-radius:12px;padding:10px 18px;'
        f'margin-bottom:18px;display:inline-flex;align-items:center;gap:10px;'
        f'border:1.5px solid {dfc};">'
        f'<span style="font-size:18px;">{dlabel}</span>'
        f'<span style="font-size:12px;color:{dfc};font-weight:700;'
        f'background:white;padding:3px 10px;border-radius:20px;">Dataset Resmi</span>'
        f'</div>',
        unsafe_allow_html=True
    )
    for kat, rows in logistik_dict.items():
        cfg = KATEGORI_CONFIG.get(kat, KATEGORI_CONFIG['Umum'])
        total_items = len(rows)
        chips_html = ""
        for row in rows:
            nama   = str(row.get('Perlengkapan', '-')).replace('<', '&lt;').replace('>', '&gt;')
            jumlah = str(row.get('Jumlah', '')).replace('<', '&lt;').replace('>', '&gt;')
            ket    = str(row.get('Keterangan', '')).replace('<', '&lt;').replace('>', '&gt;')
            chips_html += (
                f'<div style="background:white;border:1.5px solid {cfg["border"]};'
                f'border-radius:12px;padding:10px 14px;margin:5px;'
                f'display:inline-flex;flex-direction:column;'
                f'min-width:140px;max-width:200px;vertical-align:top;'
                f'box-shadow:0 2px 8px rgba(0,0,0,0.06);">'
                f'<div style="font-weight:700;color:#1a1a1a;font-size:13px;'
                f'margin-bottom:4px;">{nama}</div>'
                f'<div style="background:{cfg["chip_bg"]};color:{cfg["chip_color"]};'
                f'font-size:11px;font-weight:700;border-radius:20px;'
                f'padding:2px 8px;display:inline-block;'
                f'margin-bottom:4px;width:fit-content;">&times; {jumlah}</div>'
                f'<div style="font-size:11px;color:#666;line-height:1.4;">{ket}</div>'
                f'</div>'
            )
        full_card = (
            f'<div style="border-radius:16px;overflow:hidden;margin-bottom:18px;'
            f'box-shadow:0 6px 24px rgba(0,0,0,0.10);border:1.5px solid {cfg["border"]};">'
            f'<div style="background:{cfg["header_bg"]};padding:14px 20px;'
            f'display:flex;justify-content:space-between;align-items:center;">'
            f'<div style="color:white;font-weight:800;font-size:16px;">'
            f'{cfg["icon"]} {cfg["label"]}</div>'
            f'<div style="background:rgba(255,255,255,0.25);color:white;'
            f'font-size:12px;font-weight:700;border-radius:20px;padding:4px 12px;">'
            f'{total_items} item</div>'
            f'</div>'
            f'<div style="background:{cfg["bg"]};padding:14px 16px;">'
            f'<div style="display:flex;flex-wrap:wrap;gap:4px;">'
            f'{chips_html}'
            f'</div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(full_card, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  AI HELPERS
# ─────────────────────────────────────────────
def call_groq_api(prompt_text: str, temperature: float = 0.75) -> str | None:
    if not GROQ_API_KEY:
        return None
    url     = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role":    "system",
                "content": (
                    "Kamu adalah pemandu pendakian profesional Indonesia berpengalaman 20 tahun. "
                    "Berikan deskripsi yang akurat, spesifik, dan informatif. "
                    "Respond ONLY in pure JSON without markdown."
                )
            },
            {"role": "user", "content": prompt_text}
        ],
        "response_format": {"type": "json_object"},
        "temperature": temperature,
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=25)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
        else:
            st.error(f"Groq Error ({resp.status_code}): {resp.text[:200]}")
            return None
    except Exception as e:
        st.error(f"Koneksi Groq Gagal: {e}")
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_jalur_descriptions_ai(gunung: str, jalur_names_key: str, kebugaran: str, weather_snippet: str) -> dict:
    if not GROQ_API_KEY:
        return {}
    jalur_names = jalur_names_key.split('|')
    prompt = f"""Kamu adalah pemandu gunung profesional. Deskripsikan setiap jalur pendakian Gunung {gunung} berikut.

Jalur yang perlu dideskripsikan:
{chr(10).join(f'- {n}' for n in jalur_names)}

Tingkat kebugaran pendaki: {kebugaran}
Informasi cuaca: {weather_snippet[:180] if weather_snippet else 'tidak tersedia'}

Untuk SETIAP jalur, tulis deskripsi 3-4 kalimat yang mencakup:
1. Karakter medan (vegetasi, kemiringan, tipe tanah/batuan)
2. Pos-pos atau landmark penting yang dilalui
3. Keindahan atau keunikan khas jalur tersebut
4. Tips atau perhatian khusus untuk pendaki dengan kebugaran {kebugaran}

Output HANYA JSON murni (tanpa backtick/markdown):
{{
  "deskripsi_jalur": {{
    "NamaJalur1": "deskripsi lengkap...",
    "NamaJalur2": "deskripsi lengkap..."
  }}
}}"""
    raw = call_groq_api(prompt, temperature=0.72)
    try:
        result = json.loads(raw) if raw else None
    except Exception:
        cleaned = extract_json_from_text(raw or '')
        try:
            result = json.loads(cleaned) if cleaned else None
        except Exception:
            result = None
    if result and isinstance(result.get('deskripsi_jalur'), dict):
        return result['deskripsi_jalur']
    return {}


@st.cache_data(ttl=3600, show_spinner=False)
def get_gaya_pendakian_ai(gunung, jalur_utama, kebugaran, jarak_km, naik_float, turun_float, kesulitan, weather_snippet) -> dict:
    if not GROQ_API_KEY:
        return {}
    total_jam = round(naik_float + turun_float, 1)
    prompt = f"""Kamu adalah pemandu gunung profesional berpengalaman di Indonesia.
Berikan rekomendasi gaya pendakian untuk pendaki berikut:

Gunung      : {gunung}
Jalur Utama : {jalur_utama}
Jarak       : {jarak_km} km
Estimasi naik  : {naik_float} jam
Estimasi turun : {turun_float} jam
Total perjalanan: {total_jam} jam
Tingkat kesulitan jalur : {kesulitan}
Tingkat kebugaran pendaki: {kebugaran}
Cuaca      : {weather_snippet[:150] if weather_snippet else 'tidak tersedia'}

Tentukan gaya pendakian yang paling tepat dan berikan alasannya.

Pilihan gaya (pilih SATU yang paling sesuai):
- "Tektok (PP dalam 1 hari)"  → total perjalanan dapat diselesaikan aman dalam 1 hari
- "Bermalam 1 malam"          → butuh camp 1 malam agar tidak terlalu terburu-buru
- "Bermalam 2 malam"          → jalur panjang/berat, butuh 2 malam untuk aman dan nyaman
- "Ekspedisi 3+ malam"        → jalur sangat panjang atau perlu aklimatisasi bertahap

Output HANYA JSON murni (tanpa backtick/markdown):
{{
  "gaya": "nama gaya persis dari pilihan di atas",
  "label_durasi": "1 Hari" atau "2 Hari" atau "3 Hari" atau "Argopuro 4 Hari",
  "alasan": "2-3 kalimat penjelasan",
  "tips": ["tip pendek 1", "tip pendek 2", "tip pendek 3"]
}}"""
    raw = call_groq_api(prompt, temperature=0.4)
    try:
        result = json.loads(raw) if raw else None
    except Exception:
        cleaned = extract_json_from_text(raw or '')
        try:
            result = json.loads(cleaned) if cleaned else None
        except Exception:
            result = None
    if result and result.get('gaya') and result.get('label_durasi'):
        return result
    return {}


# ─────────────────────────────────────────────
#  RENDER HELPERS: PETA GPX & PDF
# ─────────────────────────────────────────────
def _render_gpx_map(all_points, waypoints, gpx_path_found):
    st.markdown('<div class="hm-map-wrap">', unsafe_allow_html=True)
    try:
        center = all_points[0][0]
        m = folium.Map(location=center, zoom_start=13, tiles='OpenStreetMap')
        for seg in all_points:
            folium.PolyLine(seg, weight=4, opacity=0.85, color='#FF5722').add_to(m)
        for wp in waypoints:
            folium.Marker(
                [wp['lat'], wp['lon']], popup=wp['name'],
                icon=folium.Icon(color='green', icon='info-sign')
            ).add_to(m)
        folium_static(m, width=620, height=400)
    except Exception as e:
        st.warning(f'Gagal menampilkan peta GPX: {e}')
    st.markdown('</div>', unsafe_allow_html=True)

def _render_pdf_section(pdf_path: str, gunung_name: str):
    if not _PYMUPDF_OK:
        st.warning('Library PyMuPDF tidak tersedia. Jalankan: pip install pymupdf')
        return
    if not pdf_path or not os.path.exists(pdf_path):
        st.warning('File PDF tidak ditemukan.')
        return
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        st.markdown(
            f'<div style="background:#E8F5E9;border-radius:8px;padding:8px 14px;'
            f'font-size:12px;color:#2E7D32;margin-bottom:10px;display:inline-block;">'
            f'📄 <b>Peta PDF</b> — {os.path.basename(pdf_path)} '
            f'({total_pages} halaman)</div>',
            unsafe_allow_html=True
        )
        if total_pages > 1:
            page_num = st.number_input(
                f'Halaman (1–{total_pages})',
                min_value=1, max_value=total_pages, value=1, step=1,
                key=f'pdf_page_{gunung_name}'
            ) - 1
        else:
            page_num = 0
        page      = doc[page_num]
        mat       = fitz.Matrix(2.0, 2.0)
        pix       = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes('png')
        st.image(img_bytes, use_container_width=True,
                 caption=f'Peta {gunung_name} — Hal. {page_num + 1}/{total_pages}')
        doc.close()
        with open(pdf_path, 'rb') as f_pdf:
            pdf_bytes = f_pdf.read()
        st.download_button(
            label='⬇️ Download Peta PDF', data=pdf_bytes,
            file_name=os.path.basename(pdf_path), mime='application/pdf',
            key=f'download_pdf_{gunung_name}'
        )
        st.markdown(
            '<div style="background:#E3F2FD;border-radius:10px;padding:12px 16px;'
            'margin-top:8px;font-size:12px;color:#1565C0;'
            'border-left:3px solid #1E88E5;line-height:1.6;">'
            '📱 <b>Tips:</b> Cetak atau simpan PDF ini sebelum mendaki sebagai '
            'peta cadangan offline.</div>',
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f'Gagal membuka PDF peta: {e}')


# ─────────────────────────────────────────────
#  RENDER: KARTU JALUR
# ─────────────────────────────────────────────
def render_jalur_card(jalur: dict, kebugaran: str, ai_desc: str = '', index: int = 0):
    nama    = jalur.get('nama_jalur', '-')
    jarak   = jalur.get('jarak_km', '-')
    kes     = jalur.get('kesulitan', 'Menengah')
    style   = KESULITAN_STYLE.get(kes, KESULITAN_STYLE['Menengah'])
    naik_str, turun_str, _, _ = get_estimasi_jalur(jalur, kebugaran)
    desc_html = (
        f'<div style="font-size:13px;color:#333;margin-top:10px;line-height:1.65;'
        f'padding-top:10px;border-top:1px dashed #e8e8e8;">{ai_desc}</div>'
        if ai_desc else
        '<div style="font-size:12px;color:#bbb;margin-top:8px;font-style:italic;">'
        '✨ Deskripsi AI tersedia setelah klik Analisis Lengkap</div>'
    )
    st.markdown(f"""
        <div style="background:white;border-radius:16px;padding:18px 20px;
                    margin-bottom:14px;border-left:5px solid {style['border']};
                    box-shadow:0 4px 18px rgba(0,0,0,0.08);">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
                <div style="flex:1;">
                    <div style="font-weight:800;font-size:15px;color:#1a1a1a;margin-bottom:6px;">
                        {style['icon']} Jalur {nama}
                    </div>
                    <span style="font-size:11px;font-weight:700;color:{style['color']};
                                 background:{style['bg']};padding:3px 10px;
                                 border-radius:20px;">{kes}</span>
                </div>
                <div style="text-align:right;font-size:12px;color:#555;
                            background:#f8f8f8;border-radius:10px;
                            padding:8px 12px;flex-shrink:0;line-height:1.7;">
                    <div>📏 <b>{jarak} km</b></div>
                    <div>⬆️ {naik_str}</div>
                    <div>⬇️ {turun_str}</div>
                </div>
            </div>
            {desc_html}
        </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  APPLY THEME & PAGE CONFIG
# ─────────────────────────────────────────────
apply_custom_style()

# ─────────────────────────────────────────────
#  NAVBAR
# ─────────────────────────────────────────────
st.markdown(
    '<div class="hm-navbar">🌄 Hike Metric &nbsp;'
    '<span style="font-size:14px;font-weight:500;opacity:0.8;">— Analisis Pendakian</span>'
    '</div>',
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
#  LOAD DATASET
# ─────────────────────────────────────────────
jalur_data       = load_jalur_dataset()
gunung_list_json = get_gunung_list(jalur_data) if jalur_data else []
scan_df          = scan_gpx_folder(GPX_FOLDER_PATH)
all_tweets_df    = load_all_twitter_data(TWITTER_FOLDER)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────

# Baca query_params sebagai fallback (jika masih ada dari versi lama)
_qp_gunung   = st.query_params.get("gunung", "")
_qp_auto_run = st.query_params.get("auto_run", "") == "1"

# Fallback: jika session_state belum di-set tapi query_params ada, gunakan itu
if _qp_gunung and _qp_auto_run:
    if not st.session_state.get("auto_run_gunung"):
        st.session_state["preselect_gunung"] = _qp_gunung
        st.session_state["auto_run_gunung"]  = _qp_gunung
    st.query_params.clear()

with st.sidebar:
    st.markdown("<h2 style='margin-top:0'>⚙️ Mulai Pendakian</h2>", unsafe_allow_html=True)
    st.markdown("---")

    full_list = gunung_list_json + ['Gunung Lain (tanpa peta)']

    preselect   = st.session_state.get('preselect_gunung', None)
    default_idx = 0
    if preselect and preselect in full_list:
        default_idx = full_list.index(preselect)
        st.markdown(f"""
            <div style="background:#E8F5E9;border-radius:10px;padding:10px 14px;
                        font-size:13px;color:#1B5E20;font-weight:600;margin-bottom:8px;
                        border-left:4px solid #2E7D32;">
                📍 Dipilih dari Peta: <b>{preselect}</b>
            </div>
        """, unsafe_allow_html=True)

    gunung_pilihan = st.selectbox("🏔️ Pilih Gunung", full_list, index=default_idx)

    # Tampilkan badge peringatan di sidebar jika gunung ditutup
    if gunung_pilihan in GUNUNG_DITUTUP:
        info_tutup = GUNUNG_DITUTUP[gunung_pilihan]
        st.markdown(f"""
            <div style="background:{info_tutup['bg']};border:1.5px solid {info_tutup['border']};
                        border-radius:10px;padding:10px 14px;margin:8px 0;
                        font-size:12px;color:{info_tutup['warna']};font-weight:700;">
                {info_tutup['icon']} GUNUNG DITUTUP<br>
                <span style="font-weight:400;">Status: {info_tutup['status']}</span>
            </div>
        """, unsafe_allow_html=True)

    # ── Cek auto-run dari peta SEBELUM apapun ──
    _auto        = st.session_state.get('auto_run_gunung')
    _do_auto_run = bool(_auto and _auto == gunung_pilihan)
    if _do_auto_run:
        # Simpan nama gunung sebelum di-clear untuk dipakai di UI
        _auto_gunung_name = _auto
        st.session_state['auto_run_gunung']  = None
        st.session_state['preselect_gunung'] = None
    else:
        _auto_gunung_name = gunung_pilihan

    # Kebugaran: default Sedang saat auto-run dari peta
    _default_keb = 'Sedang' if _do_auto_run else 'Rendah'
    kebugaran = st.select_slider(
        "💪 Tingkat Kebugaran Fisik",
        options=['Rendah', 'Sedang', 'Tinggi'],
        value=_default_keb,
    )

    keb_desc = {
        'Rendah': ('#FFEBEE', '#C62828', '#EF9A9A', '🔴', 'Jarang olahraga, cepat lelah saat jalan jauh, atau pemula total.'),
        'Sedang': ('#FFFDE7', '#F57F17', '#FFF176', '🟡', 'Rutin olahraga 1–2x seminggu, sanggup jalan kaki 3–5 km tanpa henti.'),
        'Tinggi': ('#E8F5E9', '#1B5E20', '#A5D6A7', '🟢', 'Atletis, rutin olahraga >3x seminggu, sering mendaki atau lari maraton.'),
    }
    bg, fc, bc, ic, txt = keb_desc[kebugaran]
    st.markdown(
        f'<div style="background:{bg};border-radius:10px;padding:10px 14px;'
        f'font-size:13px;color:{fc};border-left:4px solid {bc};">'
        f'{ic} <b>{kebugaran}</b>: {txt}</div>',
        unsafe_allow_html=True
    )

    target_kes = KEBUGARAN_TO_KESULITAN.get(kebugaran, 'Menengah')
    ks = KESULITAN_STYLE[target_kes]
    st.markdown(
        f'<div style="margin-top:8px;font-size:12px;color:#666;">'
        f'Mencari jalur: {ks["icon"]} <b style="color:{ks["color"]};">{target_kes}</b></div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    tanggal_pendakian = st.date_input("📅 Rencana Tanggal Pendakian", datetime.date.today())

    # Reset state hanya jika bukan auto-run DAN gunung/kebugaran berubah
    if not _do_auto_run:
        if (st.session_state['current_gunung'] != gunung_pilihan or
                st.session_state['current_kebugaran'] != kebugaran):
            st.session_state['analysis_run']       = False
            st.session_state['jalur_descriptions'] = {}
            st.session_state['twitter_sentiment']  = {}

    st.markdown("<br>", unsafe_allow_html=True)
    run_button = st.button("⛰️ Analisis Lengkap 🚀")

    # Auto-run aktif → perlakukan seperti tombol diklik
    if _do_auto_run:
        run_button = True
        st.markdown(f"""
            <div style="background:#e8f5e9;border-radius:10px;padding:10px 14px;
                        font-size:13px;color:#1B5E20;font-weight:600;margin-bottom:8px;
                        border-left:4px solid #2E7D32;">
                🚀 Memulai analisis otomatis untuk <b>{_auto_gunung_name}</b>…
            </div>
        """, unsafe_allow_html=True)

    if jalur_data:
        st.markdown("---")
        twitter_count = len(all_tweets_df) if not all_tweets_df.empty else 0
        st.caption(f"📊 {len(jalur_data)} gunung tersedia | 🐦 {twitter_count} tweet dimuat")


# ─────────────────────────────────────────────
#  JALUR SELECTION
# ─────────────────────────────────────────────
jalur_list   = []
is_exact     = False
redirect_msg = ""

if gunung_pilihan != 'Gunung Lain (tanpa peta)' and jalur_data:
    jalur_list, is_exact, redirect_msg = get_jalur_by_kebugaran(
        jalur_data, gunung_pilihan, kebugaran
    )

# ─────────────────────────────────────────────
#  ANALISIS EXECUTION
# ─────────────────────────────────────────────
if run_button:
    st.session_state['preselect_gunung'] = None
    st.session_state['analysis_run']     = False

    if gunung_pilihan == 'Gunung Lain (tanpa peta)' or not jalur_list:
        st.warning("Pilih gunung dari dataset untuk menjalankan analisis lengkap.")
        st.stop()

    days_ahead = (tanggal_pendakian - datetime.date.today()).days
    if days_ahead < 0:
        st.error("Tanggal pendakian di masa lalu.")
        st.stop()

    lat = lon = None
    all_points: list = []
    waypoints:  list = []
    gpx_path_found = find_gpx_for_gunung(gunung_pilihan, scan_df)

    with st.spinner("🗺️  Memproses jalur GPX & prakiraan cuaca..."):
        if gpx_path_found:
            lat, lon, all_points, waypoints = get_coords_from_gpx(gpx_path_found)
        weather_summary     = ""
        is_specific_weather = False
        if lat is not None and OWM_API_KEY and 0 <= days_ahead <= 5:
            weather_data, weather_summary = get_weather_data(lat, lon, tanggal_pendakian)
            if weather_data:
                is_specific_weather = True
                st.session_state['structured_weather'] = weather_data
            else:
                st.session_state['structured_weather'] = None
        else:
            weather_summary = ""
            st.session_state['structured_weather'] = None

    jalur_names_key = '|'.join(j['nama_jalur'] for j in jalur_list)
    weather_snippet = weather_summary[:200] if weather_summary else ""

    with st.spinner("🤖  AI sedang menyusun deskripsi jalur pendakian..."):
        ai_descs = get_jalur_descriptions_ai(
            gunung_pilihan, jalur_names_key, kebugaran, weather_snippet
        )

    jalur_utama_data = jalur_list[0] if jalur_list else {}
    _, _, naik_float_ai, turun_float_ai = get_estimasi_jalur(jalur_utama_data, kebugaran)

    with st.spinner("🏕️  AI menganalisis gaya pendakian terbaik..."):
        ai_gaya = get_gaya_pendakian_ai(
            gunung      = gunung_pilihan,
            jalur_utama = jalur_utama_data.get('nama_jalur', ''),
            kebugaran   = kebugaran,
            jarak_km    = jalur_utama_data.get('jarak_km', 0),
            naik_float  = naik_float_ai,
            turun_float = turun_float_ai,
            kesulitan   = jalur_utama_data.get('kesulitan', 'Menengah'),
            weather_snippet = weather_snippet,
        )

    # ── Analisis Twitter ──
    with st.spinner("📊  Menganalisis sentimen data Twitter..."):
        tweets_filtered = filter_tweets_for_gunung(gunung_pilihan, all_tweets_df, max_tweets=20)
        # Hitung jumlah tweet sebelum filter relevansi untuk info "disaring"
        tweets_nama_saja = filter_tweets_for_gunung.__wrapped__(gunung_pilihan, all_tweets_df, max_tweets=100) \
            if hasattr(filter_tweets_for_gunung, '__wrapped__') else pd.DataFrame()
        total_sebelum = len(tweets_nama_saja) if not tweets_nama_saja.empty else len(tweets_filtered)

        sentiment_summary = compute_sentiment_summary(tweets_filtered, total_sebelum_filter=total_sebelum)

        # Jika tidak ada tweet, minta AI fallback
        ai_community = []
        if tweets_filtered.empty:
            ai_community = get_ai_community_reviews(gunung_pilihan, kebugaran)

    st.session_state.update({
        'analysis_run':       True,
        'jalur_descriptions': ai_descs,
        'ai_gaya':            ai_gaya,
        'current_gunung':     gunung_pilihan,
        'current_kebugaran':  kebugaran,
        'gpx_data':           (lat, lon, all_points, waypoints),
        'weather_info':       (weather_summary, is_specific_weather),
        'twitter_sentiment':  {
            'tweets':    tweets_filtered.to_dict('records') if not tweets_filtered.empty else [],
            'summary':   sentiment_summary,
            'ai_ulasan': ai_community,
        },
    })
    st.rerun()

# ─────────────────────────────────────────────
#  RENDERING HASIL
# ─────────────────────────────────────────────
analysis_ready = (
    st.session_state['analysis_run']
    and st.session_state['current_gunung']    == gunung_pilihan
    and st.session_state['current_kebugaran'] == kebugaran
)

if analysis_ready and jalur_list:
    ai_descs = st.session_state.get('jalur_descriptions', {})
    lat, lon, all_points, waypoints = st.session_state['gpx_data']
    weather_summary, is_specific_weather = st.session_state['weather_info']
    gpx_path_found = find_gpx_for_gunung(gunung_pilihan, scan_df)
    _, _, naik_float, turun_float = get_estimasi_jalur(jalur_list[0], kebugaran)

    # ── Banner Gunung Ditutup (di atas segalanya) ──
    is_ditutup = render_gunung_ditutup_banner(gunung_pilihan)

    if not is_exact and redirect_msg:
        st.info(redirect_msg)

    # ── Header banner ──
    banner_note = (
        "⚠️ Informasi jalur ditampilkan untuk referensi edukasi saja. Pendakian saat ini DILARANG."
        if is_ditutup else
        "Jalur terbaik, peta GPX, cuaca, logistik, dan catatan komunitas tersedia di bawah."
    )
    st.markdown(f"""
        <div class="hm-analysis-banner">
            <h2>{'⚠️' if is_ditutup else '✅'} Hasil Analisis: {gunung_pilihan}</h2>
            <p>{banner_note}</p>
        </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  BARIS 1 — JALUR UTAMA
    # ══════════════════════════════════════════
    jalur_utama   = jalur_list[0]
    jalur_lainnya = jalur_list[1:]

    nama_utama  = jalur_utama.get('nama_jalur', '-')
    jarak_utama = jalur_utama.get('jarak_km', '-')
    kes_utama   = jalur_utama.get('kesulitan', 'Menengah')
    style_utama = KESULITAN_STYLE.get(kes_utama, KESULITAN_STYLE['Menengah'])
    naik_str_u, turun_str_u, _, _ = get_estimasi_jalur(jalur_utama, kebugaran)
    desc_utama  = ai_descs.get(nama_utama, '')

    safety_tips = {
        'Pemula':   [
            ('🥾', 'Gunakan sepatu hiking bersol karet anti-selip'),
            ('💧', 'Bawa minimal 2 liter air per orang'),
            ('🌤️', 'Mulai pendakian pagi hari sebelum pukul 07.00'),
            ('📱', 'Simpan nomor SAR lokal dan beritahu orang terdekat rencana pendakianmu'),
            ('🎒', 'Jangan membawa beban lebih dari 30% berat badan'),
        ],
        'Menengah': [
            ('⛺', 'Siapkan tenda dan sleeping bag untuk antisipasi cuaca buruk'),
            ('🧭', 'Bawa kompas/GPS dan pelajari peta jalur sebelum berangkat'),
            ('🩹', 'Wajib bawa kotak P3K lengkap termasuk obat ketinggian'),
            ('🔦', 'Bawa headlamp + baterai cadangan untuk kondisi darurat malam'),
            ('⚡', 'Hindari puncak saat badai petir — turun sebelum sore hari'),
        ],
        'Ahli':     [
            ('🪢', 'Gunakan tali dan harness untuk jalur teknis berbatu'),
            ('🌡️', 'Waspadai hipotermia — bawa pakaian berlapis dan rain cover'),
            ('🗺️', 'Hafal titik evakuasi darurat di setiap segmen jalur'),
            ('🫀', 'Lakukan aklimatisasi jika ketinggian >3000 mdpl'),
            ('🚨', 'Wajib dalam kelompok min. 3 orang — jangan solo hiking jalur ahli'),
        ],
    }
    tips = safety_tips.get(kes_utama, safety_tips['Menengah'])
    tips_html = "".join([
        f'<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:8px;">'
        f'<span style="font-size:18px;flex-shrink:0;">{ic}</span>'
        f'<span style="font-size:13px;color:#333;line-height:1.5;">{tip}</span>'
        f'</div>'
        for ic, tip in tips
    ])

    st.markdown(f"""
        <div style="background:white;border-radius:20px;overflow:hidden;
                    margin-bottom:22px;box-shadow:0 8px 32px rgba(0,0,0,0.10);
                    border:2px solid {style_utama['border']};">
            <div style="background:{style_utama['header']};padding:18px 24px;
                        display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:11px;font-weight:700;color:rgba(255,255,255,0.75);
                                letter-spacing:1.2px;text-transform:uppercase;margin-bottom:4px;">
                        ⭐ Jalur Paling Direkomendasikan
                    </div>
                    <div style="font-size:20px;font-weight:800;color:white;">
                        🥾 Jalur {nama_utama}
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;justify-content:flex-end;">
                    <div style="background:rgba(255,255,255,0.25);color:white;font-weight:700;
                                font-size:12px;padding:6px 16px;border-radius:20px;">
                        {style_utama['icon']} {kes_utama}
                    </div>
                    <div style="background:rgba(0,0,0,0.18);border-radius:14px;
                                padding:10px 18px;text-align:center;min-width:90px;">
                        <div style="font-size:11px;color:rgba(255,255,255,0.7);
                                    font-weight:600;letter-spacing:0.6px;
                                    text-transform:uppercase;margin-bottom:3px;">📏 Jarak Total</div>
                        <div style="font-size:22px;font-weight:800;color:white;line-height:1.1;">{jarak_utama} km</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.18);border-radius:14px;
                                padding:10px 18px;text-align:center;min-width:110px;">
                        <div style="font-size:11px;color:rgba(255,255,255,0.7);
                                    font-weight:600;letter-spacing:0.6px;
                                    text-transform:uppercase;margin-bottom:3px;">⬆️ Waktu Naik</div>
                        <div style="font-size:22px;font-weight:800;color:white;line-height:1.1;">{naik_str_u}</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.18);border-radius:14px;
                                padding:10px 18px;text-align:center;min-width:110px;">
                        <div style="font-size:11px;color:rgba(255,255,255,0.7);
                                    font-weight:600;letter-spacing:0.6px;
                                    text-transform:uppercase;margin-bottom:3px;">⬇️ Waktu Turun</div>
                        <div style="font-size:22px;font-weight:800;color:white;line-height:1.1;">{turun_str_u}</div>
                    </div>
                </div>
            </div>
            <div style="padding:20px 24px;display:flex;gap:24px;flex-wrap:wrap;">
                <div style="flex:2;min-width:280px;">
                    <div style="font-size:12px;font-weight:700;color:{style_utama['color']};
                                text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px;">
                        📝 Deskripsi Jalur
                    </div>
                    <div style="font-size:14px;color:#333;line-height:1.7;">
                        {desc_utama if desc_utama else '<i style="color:#bbb;">Deskripsi AI tidak tersedia untuk jalur ini.</i>'}
                    </div>
                </div>
                <div style="flex:1.2;min-width:240px;background:{style_utama['bg']};
                            border-radius:14px;padding:16px 18px;">
                    <div style="font-size:12px;font-weight:700;color:{style_utama['color']};
                                text-transform:uppercase;letter-spacing:0.8px;margin-bottom:12px;">
                        🛡️ Tips Keselamatan — Level {kes_utama}
                    </div>
                    {tips_html}
                </div>
            </div>
            <div style="background:#f8fafb;border-top:1px solid #eee;
                        padding:12px 24px;display:flex;align-items:center;gap:8px;">
                <span style="font-size:12px;color:#888;">📊</span>
                <span style="font-size:12px;color:#888;font-style:italic;">
                    Estimasi dari Dataset Resmi — disesuaikan tingkat kebugaran <b>{kebugaran}</b>
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  BARIS 2 — PETA (KIRI) + JALUR LAINNYA (KANAN)
    # ══════════════════════════════════════════
    col_map, col_jalur = st.columns([3, 2])

    with col_map:
        pdf_path_found = find_pdf_for_gunung(gunung_pilihan, GPX_FOLDER_PATH)
        has_gpx = bool(all_points)
        has_pdf = bool(pdf_path_found)

        st.markdown('<div class="hm-card">', unsafe_allow_html=True)

        if has_gpx and has_pdf:
            tab_gpx, tab_pdf = st.tabs(['🗺️ Peta Interaktif (GPX)', '📄 Peta PDF'])
            with tab_gpx:
                _render_gpx_map(all_points, waypoints, gpx_path_found)
            with tab_pdf:
                _render_pdf_section(pdf_path_found, gunung_pilihan)
        elif has_gpx:
            st.markdown('<div class="hm-section-title">🗺️ Peta Jalur GPX</div>', unsafe_allow_html=True)
            _render_gpx_map(all_points, waypoints, gpx_path_found)
        elif has_pdf:
            st.markdown('<div class="hm-section-title">📄 Peta Jalur (PDF)</div>', unsafe_allow_html=True)
            _render_pdf_section(pdf_path_found, gunung_pilihan)
        else:
            st.markdown('<div class="hm-section-title">🗺️ Peta Jalur</div>', unsafe_allow_html=True)
            st.markdown("""
                <div style="background:#f5f5f5;border-radius:10px;padding:32px;
                            text-align:center;color:#999;">
                    <div style="font-size:40px;margin-bottom:10px;">🗺️</div>
                    <div style="font-weight:600;">Peta jalur tidak tersedia</div>
                    <div style="font-size:13px;margin-top:4px;">
                        File GPX atau PDF untuk gunung ini belum tersedia di folder data_gpx
                    </div>
                </div>
            """, unsafe_allow_html=True)

        if gpx_path_found:
            gpx_file_content = load_gpx_content(gpx_path_found)
            if gpx_file_content:
                st.markdown('<br>', unsafe_allow_html=True)
                st.download_button(
                    label='⬇️ Download Jalur GPX',
                    data=gpx_file_content,
                    file_name=os.path.basename(gpx_path_found),
                    mime='application/gpx+xml',
                    key='download_gpx_btn'
                )
                st.markdown("""
                    <div style="background:#FFF8E1;border-radius:10px;padding:14px 18px;
                                margin-top:10px;font-size:13px;color:#E65100;
                                border-left:4px solid #FF8F00;line-height:1.7;">
                        ⚠️ <b>Penting — Cara Menggunakan File GPX Saat Mendaki:</b><br>
                        File GPX ini <b>harus dibuka dengan aplikasi peta eksternal / offline maps</b>,
                        bukan Google Maps. Gunakan aplikasi seperti
                        <b>Gaia GPS</b>, <b>OsmAnd</b>, <b>Maps.me</b>, atau <b>Wikiloc</b>
                        agar jalur dapat diakses <i>tanpa koneksi internet</i> saat berada di gunung.
                    </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_jalur:
        st.markdown('<div class="hm-card">', unsafe_allow_html=True)
        ks_style = KESULITAN_STYLE.get(target_kes, KESULITAN_STYLE['Menengah'])
        match_label = "✅ Sesuai kebugaran" if is_exact else "↪️ Diarahkan ke terdekat"

        if jalur_lainnya:
            st.markdown(f"""
                <div class="hm-section-title">
                    🗂️ Jalur Lainnya
                    <span style="font-size:12px;font-weight:600;color:{ks_style['color']};
                                 background:{ks_style['bg']};padding:3px 10px;
                                 border-radius:20px;">{match_label}</span>
                </div>
            """, unsafe_allow_html=True)
            for i, jalur in enumerate(jalur_lainnya):
                desc = ai_descs.get(jalur['nama_jalur'], '')
                render_jalur_card(jalur, kebugaran, desc, i + 1)
        else:
            st.markdown(f"""
                <div class="hm-section-title">
                    🥾 Jalur Pendakian
                    <span style="font-size:12px;font-weight:600;color:{ks_style['color']};
                                 background:{ks_style['bg']};padding:3px 10px;
                                 border-radius:20px;">{match_label}</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("""
                <div style="text-align:center;padding:32px 16px;color:#aaa;">
                    <div style="font-size:36px;margin-bottom:10px;">🏆</div>
                    <div style="font-size:14px;font-weight:600;color:#666;">
                        Hanya ada 1 jalur tersedia untuk gunung ini
                    </div>
                </div>
            """, unsafe_allow_html=True)

        if not ai_descs:
            st.caption("⚠️ Deskripsi AI tidak berhasil dimuat.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  BARIS 3 — CUACA
    # ══════════════════════════════════════════
    st.markdown('<div class="hm-card">', unsafe_allow_html=True)
    st.markdown('<div class="hm-section-title">🌤️ Prakiraan Cuaca 3 Hari</div>', unsafe_allow_html=True)

    if is_specific_weather:
        st.caption("📡 Sumber: API Cuaca Eksternal (OWM) — 3 hari ke depan")
        structured_weather = st.session_state.get('structured_weather')
        if structured_weather and isinstance(structured_weather, list):
            day_colors = ["#E8F5E9", "#E3F2FD", "#FFF8E1"]
            day_border = ["#2E7D32", "#1565C0", "#F57F17"]
            for idx, day in enumerate(structured_weather):
                bc = day_colors[idx % len(day_colors)]
                bd = day_border[idx % len(day_border)]
                label_badge = "📅 Hari Pendakian" if idx == 0 else f"📆 H+{idx}"
                st.markdown(f"""
                    <div style="background:{bc};border-left:4px solid {bd};
                                border-radius:12px;padding:14px 18px;margin-bottom:10px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <div>
                                <span style="font-size:26px;">{day['icon']}</span>
                                <strong style="font-size:15px;margin-left:8px;">{day['label']}</strong>
                                <span style="font-size:11px;color:#666;margin-left:8px;
                                             background:white;padding:2px 8px;
                                             border-radius:20px;">{label_badge}</span>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-size:18px;font-weight:700;">
                                    {day['temp_min']}°–{day['temp_max']}°C
                                </div>
                                <div style="font-size:12px;color:#555;">
                                    💧 {day['humidity']}% &nbsp;|&nbsp; 💨 {day['wind']} m/s
                                </div>
                            </div>
                        </div>
                        <div style="font-size:13px;color:#444;margin-top:6px;
                                    text-transform:capitalize;">{day['description']}</div>
                        {"".join([
                            f'<span style="font-size:11px;background:white;'
                            f'border-radius:8px;padding:3px 8px;margin:3px 2px 0 0;'
                            f'display:inline-block;color:#333;">'
                            f'{h["icon"]} {h["time"]} {h["temp"]}°C</span>'
                            for h in day.get("hourly", [])
                        ])}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info(weather_summary or "Data cuaca tidak tersedia.")
    else:
        st.caption("⚠️ Cuaca OWM tidak tersedia — gunakan informasi umum musim mendaki.")
        st.info(
            "Pantau prakiraan cuaca lokal menjelang hari H melalui BMKG atau "
            "aplikasi cuaca terpercaya. Hindari mendaki saat musim hujan lebat."
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  BARIS 4 — LOGISTIK
    # ══════════════════════════════════════════
    st.markdown('<div class="hm-card">', unsafe_allow_html=True)
    st.markdown('<div class="hm-section-title">🎒 Perlengkapan & Logistik</div>', unsafe_allow_html=True)

    ai_gaya = st.session_state.get('ai_gaya', {})
    _gaya_style = {
        'Tektok (PP dalam 1 hari)': ('#E3F2FD', '#1565C0', '#BBDEFB', '⚡'),
        'Bermalam 1 malam':         ('#E8F5E9', '#2E7D32', '#C8E6C9', '⛺'),
        'Bermalam 2 malam':         ('#FFF3E0', '#E65100', '#FFE0B2', '🏕️'),
        'Ekspedisi 3+ malam':       ('#FCE4EC', '#C62828', '#FFCDD2', '🏔️'),
    }

    if ai_gaya and ai_gaya.get('gaya'):
        _g  = ai_gaya.get('gaya', 'Tektok (PP dalam 1 hari)')
        _al = ai_gaya.get('alasan', '')
        _tp = ai_gaya.get('tips', [])
        _gs = _gaya_style.get(_g, _gaya_style['Tektok (PP dalam 1 hari)'])
        _tips_html = ''.join([
            f'<span style="display:inline-block;background:white;border:1px solid {_gs[1]}40;'
            f'color:{_gs[1]};font-size:12px;font-weight:600;padding:4px 12px;'
            f'border-radius:20px;margin:3px 4px 3px 0;">'
            f'{_gs[3]} {t}</span>'
            for t in _tp
        ])
        st.markdown(
            f'<div style="background:{_gs[0]};border:1.5px solid {_gs[1]}40;'
            f'border-radius:16px;padding:18px 22px;margin-bottom:20px;">'
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">'
            f'<div style="font-size:32px;">{_gs[3]}</div>'
            f'<div>'
            f'<div style="font-size:11px;font-weight:700;color:{_gs[1]};'
            f'text-transform:uppercase;letter-spacing:0.8px;">🤖 Rekomendasi AI — Gaya Pendakian</div>'
            f'<div style="font-size:18px;font-weight:800;color:#1a1a1a;margin-top:2px;">{_g}</div>'
            f'</div></div>'
            f'<div style="font-size:13px;color:#444;line-height:1.65;margin-bottom:12px;">{_al}</div>'
            f'<div>{_tips_html}</div></div>',
            unsafe_allow_html=True
        )
        _durasi_label = ai_gaya.get('label_durasi', '1 Hari')
    else:
        st.caption('⚠️ Rekomendasi gaya AI tidak tersedia — menggunakan estimasi otomatis.')
        _durasi_label = estimate_durasi_label(naik_float, turun_float, gunung_pilihan)

    _logistik_df   = load_logistik_dataset()
    _logistik_dict = get_logistik_by_durasi(_durasi_label, _logistik_df)

    if _logistik_dict:
        render_logistik_cards(_logistik_dict, _durasi_label)
    else:
        st.warning("Data perlengkapan tidak tersedia. Pastikan file `dataset_logistik_pendakian.csv` ada.")

    st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  BARIS 5 — CATATAN KOMUNITAS (TWITTER + SENTIMEN)
    # ══════════════════════════════════════════
    twitter_data = st.session_state.get('twitter_sentiment', {})
    tweets_records   = twitter_data.get('tweets', [])
    sentiment_summary = twitter_data.get('summary', {'positif': 0, 'negatif': 0, 'netral': 0, 'total': 0, 'dominant': 'Netral'})
    ai_community     = twitter_data.get('ai_ulasan', [])

    # Rekonstruksi DataFrame dari records
    if tweets_records:
        tweets_df_render = pd.DataFrame(tweets_records)
    else:
        tweets_df_render = pd.DataFrame()

    render_komunitas_twitter(
        gunung_name      = gunung_pilihan,
        tweets_df        = tweets_df_render,
        sentiment_summary= sentiment_summary,
        ai_fallback      = ai_community,
    )

else:
    # ══════════════════════════════════════════
    #  EMPTY STATE
    # ══════════════════════════════════════════
    if gunung_pilihan == 'Gunung Lain (tanpa peta)':
        st.markdown(f"""
            <div class="hm-card">
                <div class="hm-empty">
                    <div class="icon">🏔️</div>
                    <h3>Gunung Lain</h3>
                    <p>Dataset jalur tidak tersedia untuk pilihan ini.<br>
                    Pilih salah satu dari <b>{len(gunung_list_json)} gunung</b>
                    dalam dataset untuk melihat jalur yang sesuai.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        _preview_count  = len(jalur_list)
        _gunung_display = gunung_pilihan if gunung_pilihan else "..."

        # Tampilkan mini-preview banner tutup jika gunung berbahaya
        if gunung_pilihan in GUNUNG_DITUTUP:
            info_tutup = GUNUNG_DITUTUP[gunung_pilihan]
            st.markdown(f"""
                <div style="background:{info_tutup['bg']};border:2px solid {info_tutup['border']};
                            border-radius:16px;padding:18px 24px;margin-bottom:20px;
                            display:flex;align-items:center;gap:16px;">
                    <div style="font-size:40px;">{info_tutup['icon']}</div>
                    <div>
                        <div style="font-size:18px;font-weight:800;color:{info_tutup['warna']};">
                            ⛔ GUNUNG {gunung_pilihan.upper()} DITUTUP
                        </div>
                        <div style="font-size:13px;color:#555;margin-top:4px;line-height:1.6;">
                            {info_tutup['alasan']}
                        </div>
                        <div style="font-size:12px;color:{info_tutup['warna']};margin-top:6px;font-weight:600;">
                            Sumber: {info_tutup['sumber']}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="background:white;border-radius:24px;overflow:hidden;
                        box-shadow:0 8px 40px rgba(0,0,0,0.08);
                        border:1px solid rgba(0,0,0,0.05);margin-bottom:20px;">
                <div style="background:linear-gradient(135deg,#1B5E20 0%,#2E7D32 60%,#FF5722 100%);
                            padding:48px 40px;text-align:center;">
                    <div style="font-size:64px;margin-bottom:16px;">⛰️</div>
                    <div style="font-size:26px;font-weight:800;color:white;margin-bottom:8px;">
                        Siap Mendaki {_gunung_display}?
                    </div>
                    <div style="font-size:15px;color:rgba(255,255,255,0.85);max-width:480px;margin:0 auto;">
                        Klik <b>Analisis Lengkap 🚀</b> untuk mendapatkan jalur terbaik,
                        peta GPX, prakiraan cuaca, logistik, dan catatan komunitas pendaki.
                    </div>
                    {f'<div style="margin-top:16px;display:inline-block;background:rgba(255,255,255,0.2);'
                     f'border-radius:20px;padding:6px 18px;font-size:13px;color:white;font-weight:600;">'
                     f'📊 {_preview_count} jalur tersedia untuk gunung ini</div>'
                     if _preview_count > 0 else ''}
                </div>
                <div style="padding:28px 32px;display:flex;flex-wrap:wrap;gap:16px;justify-content:center;">
                    <div style="text-align:center;padding:16px 20px;background:#F1F8E9;
                                border-radius:14px;min-width:140px;">
                        <div style="font-size:28px;margin-bottom:6px;">🥾</div>
                        <div style="font-weight:700;font-size:13px;color:#2E7D32;">Jalur Terbaik</div>
                        <div style="font-size:11px;color:#777;margin-top:2px;">Sesuai kebugaran kamu</div>
                    </div>
                    <div style="text-align:center;padding:16px 20px;background:#FFF3E0;
                                border-radius:14px;min-width:140px;">
                        <div style="font-size:28px;margin-bottom:6px;">🗺️</div>
                        <div style="font-weight:700;font-size:13px;color:#E65100;">Peta GPX</div>
                        <div style="font-size:11px;color:#777;margin-top:2px;">Jalur interaktif + download</div>
                    </div>
                    <div style="text-align:center;padding:16px 20px;background:#E3F2FD;
                                border-radius:14px;min-width:140px;">
                        <div style="font-size:28px;margin-bottom:6px;">🌤️</div>
                        <div style="font-weight:700;font-size:13px;color:#1565C0;">Cuaca 3 Hari</div>
                        <div style="font-size:11px;color:#777;margin-top:2px;">Prakiraan real-time OWM</div>
                    </div>
                    <div style="text-align:center;padding:16px 20px;background:#FCE4EC;
                                border-radius:14px;min-width:140px;">
                        <div style="font-size:28px;margin-bottom:6px;">🛡️</div>
                        <div style="font-weight:700;font-size:13px;color:#C62828;">Tips Keselamatan</div>
                        <div style="font-size:11px;color:#777;margin-top:2px;">Panduan per level pendaki</div>
                    </div>
                    <div style="text-align:center;padding:16px 20px;background:#E8EAF6;
                                border-radius:14px;min-width:140px;">
                        <div style="font-size:28px;margin-bottom:6px;">🐦</div>
                        <div style="font-weight:700;font-size:13px;color:#3949AB;">Sentimen Twitter</div>
                        <div style="font-size:11px;color:#777;margin-top:2px;">Analisis ulasan nyata</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)