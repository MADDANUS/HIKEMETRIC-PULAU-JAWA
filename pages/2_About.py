import streamlit as st

st.set_page_config(page_title="Tentang Aplikasi", page_icon="💡")

# ─────────────────────────────────────────────
#  SHARED THEME
# ─────────────────────────────────────────────
def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: #eef2f3 !important;
        color: #1a1a1a !important;
    }

    footer{ visibility: hidden; }
    
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

    .hm-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.07);
        border: 1px solid rgba(0,0,0,0.05);
    }

    .hm-card h2, .hm-card h3 { color: #1B5E20 !important; font-weight: 700; margin-top: 0; }

    .hm-hero {
        background: linear-gradient(135deg, #1B5E20 0%, #388E3C 60%, #FF5722 100%);
        border-radius: 20px;
        padding: 36px 32px;
        color: white;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .hm-hero::before {
        content: "💡";
        position: absolute;
        right: 30px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 90px;
        opacity: 0.18;
    }
    .hm-hero h1 { color: white !important; font-size: 30px; font-weight: 800; margin: 0 0 8px 0; }
    .hm-hero p  { color: rgba(255,255,255,0.88); font-size: 15px; margin: 0; }

    .tech-item {
        display: flex;
        align-items: flex-start;
        gap: 16px;
        padding: 18px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    .tech-item:last-child { border-bottom: none; }
    .tech-icon {
        background: #E8F5E9;
        border-radius: 14px;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        flex-shrink: 0;
    }
    .tech-body h4 { margin: 0 0 6px 0; color: #1B5E20; font-size: 16px; font-weight: 700; }
    .tech-body p  { margin: 0; color: #555; font-size: 14px; line-height: 1.55; }

    .hm-pill {
        display: inline-block;
        background: #E8F5E9;
        color: #2E7D32;
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 12px;
        font-weight: 600;
        margin: 4px 4px 4px 0;
        border: 1px solid #C8E6C9;
    }
    .hm-pill-orange {
        background: #FBE9E7;
        color: #BF360C;
        border-color: #FFCCBC;
    }

    .dev-card {
        background: linear-gradient(135deg, #f9f9f9, #ffffff);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        border: 1px solid #e8e8e8;
    }
    .dev-avatar {
        width: 70px; height: 70px;
        background: linear-gradient(135deg, #1B5E20, #388E3C);
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 32px;
        margin: 0 auto 14px auto;
    }

    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e0e0e0 !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stCaption p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #1a1a1a !important; }

    hr { border-color: #e8e8e8 !important; margin: 20px 0 !important; }
    .main h1, .main h2, .main h3 { color: #1B5E20 !important; }
    </style>
    """, unsafe_allow_html=True)


def about_page():
    apply_theme()

    # Navbar
    st.markdown('<div class="hm-navbar">🌄 Hike Metric</div>', unsafe_allow_html=True)

    # Hero
    st.markdown("""
        <div class="hm-hero">
            <h1>💡 Tentang Hike Metric</h1>
            <p>Dibangun dengan teknologi modern untuk memberikan panduan pendakian yang akurat dan real-time.</p>
        </div>
    """, unsafe_allow_html=True)

    # Technology Stack Card
    st.markdown('<div class="hm-card">', unsafe_allow_html=True)
    st.markdown("<h2>🛠️ Teknologi yang Digunakan</h2>", unsafe_allow_html=True)
    st.markdown("""
        <div class="tech-item">
            <div class="tech-icon">🐍</div>
            <div class="tech-body">
                <h4>Streamlit</h4>
                <p>Kerangka kerja Python utama untuk pengembangan antarmuka web yang cepat, interaktif, dan <em>data-driven</em>. Memungkinkan rendering komponen UI secara reaktif tanpa memerlukan JavaScript.</p>
                <span class="hm-pill">Python</span>
                <span class="hm-pill">Web Framework</span>
            </div>
        </div>
        <div class="tech-item">
            <div class="tech-icon">🤖</div>
            <div class="tech-body">
                <h4>GROQ (Llama 3)</h4>
                <p>Model Kecerdasan Buatan generatif yang berfungsi sebagai mesin analisis logistik, estimasi durasi pendakian, dan perangkum sentimen komunitas dari data mentah.</p>
                <span class="hm-pill">AI / LLM</span>
                <span class="hm-pill">JSON Output</span>
                <span class="hm-pill-orange hm-pill">Gratis</span>
            </div>
        </div>
        <div class="tech-item">
            <div class="tech-icon">🌤️</div>
            <div class="tech-body">
                <h4>OpenWeatherMap (OWM)</h4>
                <p>Layanan API cuaca eksternal terintegrasi untuk menyediakan data prakiraan 5-hari yang spesifik dan berbasis koordinat geospasial sesuai lokasi gunung pilihan.</p>
                <span class="hm-pill">REST API</span>
                <span class="hm-pill">Real-Time</span>
                <span class="hm-pill">Geospasial</span>
            </div>
        </div>
        <div class="tech-item">
            <div class="tech-icon">🗺️</div>
            <div class="tech-body">
                <h4>GPX / Folium</h4>
                <p>Kombinasi pustaka untuk pemrosesan data GPS (parsing file GPX) dan rendering visualisasi peta interaktif dengan jalur, waypoint, dan elevasi.</p>
                <span class="hm-pill">GPS Parsing</span>
                <span class="hm-pill">Peta Interaktif</span>
            </div>
        </div>
        <div class="tech-item">
            <div class="tech-icon">📊</div>
            <div class="tech-body">
                <h4>Data Scraper & NLP</h4>
                <p>Mekanisme <em>web scraping</em> dikombinasikan dengan teknik Pemrosesan Bahasa Alami untuk pengumpulan dan penyaringan data kondisi jalur terkini dari sumber komunitas.</p>
                <span class="hm-pill">NLP</span>
                <span class="hm-pill">Web Scraping</span>
                <span class="hm-pill">Community Data</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Stack summary metrics
    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("⛰️", "5+", "Gunung Tersedia"),
        ("🤖", "AI", "Rekomendasi Personal"),
        ("🌤️", "3 Hari", "Prakiraan Cuaca"),
        ("🗺️", "GPX", "Peta Interaktif"),
    ]
    for col, (icon, val, label) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f"""
                <div class="hm-card" style="text-align:center; padding:20px 12px;">
                    <div style="font-size:28px;">{icon}</div>
                    <div style="font-size:22px; font-weight:800; color:#2E7D32; margin:6px 0;">{val}</div>
                    <div style="font-size:12px; color:#777;">{label}</div>
                </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    about_page()