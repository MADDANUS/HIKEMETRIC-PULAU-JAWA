import streamlit as st

# ─────────────────────────────────────────────
#  SHARED THEME  (paste this block into every page)
# ─────────────────────────────────────────────
def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── GLOBAL ── */
    html, body, .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: #eef2f3 !important;
        color: #1a1a1a !important;
    }

    /* ── HIDE default streamlit header/footer decoration ── */
    #MainMenu, footer, header { visibility: hidden; }
    /* Sidebar navigasi halaman (menu Dashboard, Pendakian, About) */
    [data-testid="stSidebarNav"] a span,
    [data-testid="stSidebarNav"] span,
    [data-testid="stSidebarNavItems"] span {
        color: #1a1a1a !important;
    }

    /* Item yang sedang aktif/dipilih */
    [data-testid="stSidebarNav"] a[aria-current="page"] span {
        color: #1B5E20 !important;
        font-weight: 700 !important;
    }
    
    /* ── CUSTOM TOP NAVBAR ── */
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
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.07);
        border: 1px solid rgba(0,0,0,0.05);
    }

    /* ── SECTION TITLE ── */
    .hm-card h2, .hm-card h3 {
        color: #1B5E20 !important;
        font-weight: 700;
        margin-top: 0;
    }

    /* ── BADGE / PILL ── */
    .hm-badge {
        display: inline-block;
        background: #E8F5E9;
        color: #2E7D32;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 13px;
        font-weight: 600;
        margin: 4px 4px 4px 0;
    }

    /* ── FEATURE ITEM ── */
    .hm-feature {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        padding: 16px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    .hm-feature:last-child { border-bottom: none; }
    .hm-feature-icon {
        background: #E8F5E9;
        border-radius: 12px;
        width: 46px;
        height: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        flex-shrink: 0;
    }
    .hm-feature-text h4 { margin: 0 0 4px 0; color: #1B5E20; font-size: 15px; }
    .hm-feature-text p  { margin: 0; color: #555; font-size: 14px; line-height: 1.5; }

    /* ── HERO BANNER ── */
    .hm-hero {
        background: linear-gradient(135deg, #1B5E20 0%, #388E3C 60%, #FF5722 100%);
        border-radius: 20px;
        padding: 40px 36px;
        color: white;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .hm-hero::before {
        content: "🏔️";
        position: absolute;
        right: 30px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 90px;
        opacity: 0.18;
    }
    .hm-hero h1 { color: white !important; font-size: 32px; font-weight: 800; margin: 0 0 10px 0; }
    .hm-hero p  { color: rgba(255,255,255,0.88); font-size: 16px; line-height: 1.6; margin: 0; }

    /* ── ORANGE BUTTON ── */
    div.stButton > button {
        background: linear-gradient(135deg, #FF5722, #E64A19) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 12px 24px !important;
        width: 100%;
        box-shadow: 0 4px 14px rgba(255,87,34,0.35) !important;
        transition: transform 0.15s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(255,87,34,0.45) !important;
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e0e0e0 !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stCaption p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #1a1a1a !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 16px;
    }

    /* ── METRICS ── */
    [data-testid="stMetricValue"] > div { color: #2E7D32 !important; font-weight: 800 !important; font-size: 28px !important; }
    [data-testid="stMetricLabel"] p     { color: #666 !important; font-size: 13px !important; }
    [data-testid="metric-container"] {
        background: white;
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    }

    /* ── INPUTS ── */
    .stSelectbox > div > div,
    .stDateInput > div > div,
    .stTextInput > div > div {
        border-radius: 10px !important;
        border: 1.5px solid #ddd !important;
    }
    .stSelectbox > div > div:focus-within,
    .stDateInput > div > div:focus-within {
        border-color: #2E7D32 !important;
        box-shadow: 0 0 0 3px rgba(46,125,50,0.12) !important;
    }

    /* ── ALERTS / INFO ── */
    .stAlert {
        border-radius: 12px !important;
    }

    /* ── DIVIDER ── */
    hr { border-color: #e8e8e8 !important; margin: 20px 0 !important; }

    /* ── DATAFRAME ── */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden;
    }

    /* ── HEADINGS inside main content ── */
    .main h1, .main h2, .main h3 { color: #1B5E20 !important; }
    </style>
    """, unsafe_allow_html=True)


def home_page():
    apply_theme()

    # Navbar
    st.markdown("""
        <div class="hm-navbar">
            🌄 Hike Metric
        </div>
    """, unsafe_allow_html=True)

    # Hero Banner
    st.markdown("""
        <div class="hm-hero">
            <h1>Selamat Datang di Hike Metric</h1>
            <p>Platform perencanaan pendakian cerdas yang menggabungkan data geografis,<br>
            prakiraan cuaca real-time, dan kecerdasan buatan untuk pendakian yang lebih aman.</p>
        </div>
    """, unsafe_allow_html=True)

    # Feature Cards
    st.markdown('<div class="hm-card">', unsafe_allow_html=True)
    st.markdown("<h2>📋 Panduan Penggunaan</h2>", unsafe_allow_html=True)
    st.markdown("""
        <div class="hm-feature">
            <div class="hm-feature-icon">🗺️</div>
            <div class="hm-feature-text">
                <h4>Data Jalur (GPX)</h4>
                <p>Visualisasi rute interaktif berbasis data GPS nyata. Lihat setiap pos, ketinggian, dan jarak jalur pendakian pilihan Anda.</p>
            </div>
        </div>
        <div class="hm-feature">
            <div class="hm-feature-icon">🌤️</div>
            <div class="hm-feature-text">
                <h4>Prakiraan Cuaca Real-Time (OWM)</h4>
                <p>Kondisi cuaca spesifik berdasarkan koordinat gunung dan tanggal pendakian Anda, langsung dari OpenWeatherMap.</p>
            </div>
        </div>
        <div class="hm-feature">
            <div class="hm-feature-icon">🤖</div>
            <div class="hm-feature-text">
                <h4>Rekomendasi AI (GROQ)</h4>
                <p>Estimasi waktu, daftar logistik personal, tips keselamatan, dan analisis komunitas yang dipersonalisasi sesuai kebugaran Anda.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Quick stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
            <div class="hm-card" style="text-align:center; padding: 24px 16px;">
                <div style="font-size:36px; margin-bottom:8px;">⛰️</div>
                <div style="font-size:28px; font-weight:800; color:#2E7D32;">GPX Ready</div>
                <div style="font-size:13px; color:#777; margin-top:4px;">Data Jalur Terintegrasi</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="hm-card" style="text-align:center; padding: 24px 16px;">
                <div style="font-size:36px; margin-bottom:8px;">🌦️</div>
                <div style="font-size:28px; font-weight:800; color:#2E7D32;">5-Hari</div>
                <div style="font-size:13px; color:#777; margin-top:4px;">Prakiraan Cuaca Akurat</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="hm-card" style="text-align:center; padding: 24px 16px;">
                <div style="font-size:36px; margin-bottom:8px;">🤖</div>
                <div style="font-size:28px; font-weight:800; color:#2E7D32;">AI-Powered</div>
                <div style="font-size:13px; color:#777; margin-top:4px;">Rekomendasi Personal</div>
            </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    home_page()