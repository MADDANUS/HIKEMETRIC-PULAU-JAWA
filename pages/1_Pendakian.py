import streamlit as st
import datetime
import pandas as pd
import requests
import os
import json
import gpxpy
import folium
from streamlit_folium import folium_static
from google import genai
import re

# Inisialisasi Session State untuk menyimpan hasil
if 'analysis_run' not in st.session_state:
    st.session_state['analysis_run'] = False
if 'ai_data' not in st.session_state:
    st.session_state['ai_data'] = None
if 'current_gunung' not in st.session_state:
    st.session_state['current_gunung'] = None
if 'gpx_data' not in st.session_state:
    st.session_state['gpx_data'] = (None, None, [], []) # (lat, lon, all_points, waypoints)
if 'weather_info' not in st.session_state:
    st.session_state['weather_info'] = (None, False) # (summary, is_specific)
    
# -----------------------------
# CONFIG
# -----------------------------
GPX_FOLDER_PATH = './data_gpx' 

# Akses secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
OWM_API_KEY = st.secrets.get("OWM_API_KEY")

# Initialize Gemini client lazily
GEMINI_CLIENT = None
if GEMINI_API_KEY:
    try:
        GEMINI_CLIENT = genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        GEMINI_CLIENT = None

st.set_page_config(page_title="HIKE METRIC", page_icon="📈", layout="wide")

# -----------------------------
# UTIL: Safe JSON extraction & repair (Keep these functions)
# -----------------------------
def extract_json_from_text(text: str) -> (str | None):
    # ... (Keep your original extract_json_from_text function here) ...
    if not text:
        return None
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1 or end <= start:
        return None
    candidate = text[start:end+1]
    candidate = re.sub(r'```json', '', candidate, flags=re.IGNORECASE)
    candidate = re.sub(r'```', '', candidate)
    candidate = re.sub(r',\s*}', '}', candidate)
    candidate = re.sub(r',\s*\]', ']', candidate)
    candidate = ''.join(ch for ch in candidate if ch.isprintable())
    stack = 0
    for i, ch in enumerate(candidate):
        if ch == '{': stack += 1
        elif ch == '}': stack -= 1
        if stack < 0:
            return None
    if stack != 0:
        return None
    return candidate
# -----------------------------
# GPX / File helpers
# -----------------------------
@st.cache_data
def scan_gpx_folder(folder_path: str) -> pd.DataFrame:
    rows = []
    try:
        for fname in sorted(os.listdir(folder_path)):
            if fname.lower().endswith('.gpx'):
                clean_name = fname.replace('.gpx', '').replace('Gunung ', '').replace('.', '').strip()
                rows.append({'nama_gunung': clean_name, 'gpx_path': os.path.join(folder_path, fname)})
    except FileNotFoundError:
        return pd.DataFrame()
    return pd.DataFrame(rows)

def get_coords_from_gpx(gpx_path: str, max_distance_meters=10, max_time_gap_seconds=1800):
    if not gpx_path or not os.path.exists(gpx_path):
        return None, None, [], []
    try:
        with open(gpx_path, 'r', encoding='utf-8') as fh:
            gpx = gpxpy.parse(fh)
        all_points = []
        for track in gpx.tracks:
            for seg in track.segments:
                pts = [(p.latitude, p.longitude) for p in seg.points if p.latitude is not None and p.longitude is not None]
                if pts:
                    all_points.append(pts)
        waypoints = []
        for wp in getattr(gpx, 'waypoints', []) or []:
            waypoints.append({'lat': wp.latitude, 'lon': wp.longitude, 'name': wp.name or 'Waypoint'})
        if all_points and len(all_points) > 0 and len(all_points[0]) > 0:
            lat, lon = all_points[0][0]
        elif waypoints:
            lat, lon = waypoints[0]['lat'], waypoints[0]['lon']
        else:
            return None, None, [], []
        return lat, lon, all_points, waypoints
    except Exception as e:
        return None, None, [], []

# -----------------------------
# Weather helper (OWM) with caching
# -----------------------------
@st.cache_data(ttl=900)
def get_weather_data(lat, lon, date_obj: datetime.date):
    if lat is None or lon is None or not OWM_API_KEY:
        return None, "Data koordinat atau kunci OWM tidak valid."
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric&lang=id"
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
        target_list = [item for item in data.get('list', []) if datetime.datetime.fromtimestamp(item['dt']).date() == date_obj]
        if not target_list:
            return None, "Tidak ada data prakiraan tersedia untuk tanggal tersebut dari OWM."
        parts = []
        for item in target_list[:8]:
            time_str = item['dt_txt'].split()[1][:5]
            parts.append(f"Pukul {time_str}: {item['main']['temp']}°C, {item['weather'][0]['description']}")
        summary = f"Prakiraan cuaca (titk awal jalur) pada {date_obj.strftime('%d %B %Y')}: " + " | ".join(parts)
        return target_list, summary
    except Exception as e:
        return None, f"Gagal mengambil data cuaca OWM: {e}"

# -----------------------------
# Gemini calls with caching
# -----------------------------
def call_gemini_for_recommendation(prompt_text: str):
    if not GEMINI_CLIENT:
        return None
    try:
        res = GEMINI_CLIENT.models.generate_content(model='gemini-2.5-flash', contents=prompt_text)
        return getattr(res, 'text', str(res))
    except Exception:
        return None
    
@st.cache_data(ttl=3600)
def get_full_recommendation(gunung, kebugaran, tanggal_pendakian, weather_summary):
    if not GEMINI_CLIENT:
        return None

    if "Prakiraan cuaca spesifik" in weather_summary:
        cuaca_source = "Berdasarkan data cuaca akurat 24 jam ke depan yang disisipkan di atas."
    else:
        cuaca_source = "Berdasarkan pengetahuan umum AI mengenai ketinggian, lokasi, dan musim saat ini."

    prompt = f"""
Bertindak sebagai Asisten Pendakian Gunung AI profesional. Berikan analisis dan rekomendasi lengkap untuk Gunung **{gunung}**.
Tingkat kebugaran pendaki: **{kebugaran}**.
Rencana tanggal: **{tanggal_pendakian.strftime('%d %B %Y')}**.

Data Cuaca: {weather_summary}
{cuaca_source}

Instruksi Khusus untuk Logistik:
1. Hitung total durasi pendakian (Naik + Turun) dari estimasi Anda.
2. Untuk kategori 'Makanan', kolom 'keterangan' HARUS berisi daftar item makanan yang DETAIL dan KUANTITATIF (misal: Beras 0.5 kg, 3 bungkus mie instan) berdasarkan total durasi jam pendakian tersebut. Asumsikan rata-rata kebutuhan 2500 kkal/hari/pendaki.


Jawab hanya dalam format JSON yang valid dan lengkap berikut. Pastikan JSON dapat di-parse:
{{
    "estimasi": {{"jarak_total_km": <float>, "waktu_naik_jam": <float>, "waktu_turun_jam": <float>}},
    "rekomendasi_jalur": [
        {{"nama": <string>, "deskripsi_singkat": <string>, "tingkat_kesulitan": <string>}}
    ],
    "ringkasan_cuaca_ai": <string>,
    "perlengkapan_logistik": [
        {{"item": <string>, "keterangan": <string>, "kategori": <string>}}
    ],
    "tips_keselamatan": [<string>, <string>]
}}
"""
    raw = call_gemini_for_recommendation(prompt)
    if not raw:
        return None
    clean = extract_json_from_text(raw)
    if not clean:
        return None
    try:
        data = json.loads(clean)
        return data
    except json.JSONDecodeError:
        clean2 = re.sub(r',\s*}', '}', clean)
        clean2 = re.sub(r',\s*\]', ']', clean2)
        try:
            return json.loads(clean2)
        except Exception:
            return None

#gpx peta
@st.cache_data(show_spinner=False)
def load_gpx_content(gpx_path: str) -> bytes | None:
    """Membaca konten biner file GPX."""
    if not os.path.exists(gpx_path):
        return None
    try:
        with open(gpx_path, 'rb') as f:
            return f.read()
    except Exception:
        return None
# -----------------------------
# Community notes (Twitter processed CSV)
# -----------------------------
@st.cache_data
def load_processed_twitter(path='processed_twitter_data.csv') -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        return df
    except Exception:
        return pd.DataFrame()


def get_community_notes(gunung_name, processed_df: pd.DataFrame):
    if processed_df.empty:
        return "Tidak ada data media sosial yang diproses untuk analisis."

    relevant = processed_df[processed_df['nama_gunung_ekstraksi'].str.lower() == gunung_name.lower()]
    if relevant.empty:
        return f"Tidak ada catatan terkini untuk {gunung_name}."

    context_text = "\n---\n".join(relevant['clean_text'].head(20).tolist())

    prompt = f"""
Bertindak sebagai Analis Kondisi Jalur. Berdasarkan data komunitas berikut untuk Gunung {gunung_name}, berikan rangkuman yang ringkas (maks 4 poin):
1. Sentimen utama (Positif/Negatif).
2. Peringatan bahaya atau kesulitan jalur.
3. Rekomendasi logistik yang sering disebut.
4. Kondisi terkini (keramaian, cuaca lokal).

Data Twitter Mentah:
---
{context_text}
"""

    raw = call_gemini_for_recommendation(prompt)
    if not raw:
        return f"Gagal menganalisis data Twitter melalui Gemini."
    return raw

# -----------------------------
# UI Layout (Dashboard Page)
# -----------------------------

def dashboard_header():
    st.markdown("<div style='display:flex; align-items:center;'>"
                "<img src='https://img.icons8.com/ios-filled/50/2e86de/mountain.png' width=32/>"
                "<h1 style='margin:0; margin-left:8px'>HIKE METRIC</h1></div>", unsafe_allow_html=True)
    st.markdown("<p style='color:var(--muted);margin-top:6px'>Analisis dan rekomendasi untuk pendakian Anda.</p>", unsafe_allow_html=True)
    
# Sidebar inputs
with st.sidebar:
    st.header("⚙️ Mulai Pendakian")
    scan_df = scan_gpx_folder(GPX_FOLDER_PATH)
    gunung_list = scan_df['nama_gunung'].tolist() if not scan_df.empty else []
    gunung_list.append('Gunung Lain (tanpa peta)')

    gunung_pilihan = st.selectbox("Pilih Gunung", gunung_list)
    kebugaran = st.select_slider("Tingkat Kebugaran Fisik", options=['Rendah', 'Sedang', 'Tinggi'])
    tanggal_pendakian = st.date_input("Rencana Tanggal Pendakian", datetime.date.today())
    
    # Simpan input ke Session State agar bisa dibandingkan saat rendering
    st.session_state['selected_gunung'] = gunung_pilihan
    st.session_state['selected_kebugaran'] = kebugaran
    st.session_state['selected_tanggal'] = tanggal_pendakian
    
    run_button = st.button("⛰️ Analisis dan Rekomendasi 🚀")

# Main Dashboard Content
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
dashboard_header()

# --- BLOK EKSEKUSI ANALISIS (Jika tombol ditekan) ---
if run_button:
    # 1. Reset hasil analisis lama
    st.session_state['analysis_run'] = False
    
    # 2. Ambil Input
    gunung = st.session_state['selected_gunung']
    kebugaran = st.session_state['selected_kebugaran']
    tanggal = st.session_state['selected_tanggal']
    
    # Inisialisasi variabel lokal untuk analisis
    lat = lon = None
    all_points = []
    waypoints = []
    weather_summary = ""
    is_specific_weather = False
    
    st.subheader(f"Menganalisis: {gunung}")
    
    with st.spinner("Mengumpulkan data jalur dan cuaca..."):
        # 1. GPX Processing
        row = scan_df[scan_df['nama_gunung'] == gunung]
        if not row.empty:
            gpx_path = row['gpx_path'].iloc[0]
            lat, lon, all_points, waypoints = get_coords_from_gpx(gpx_path)
        
        # 2. Weather Check
        days_ahead = (tanggal - datetime.date.today()).days
        if days_ahead < 0:
             st.error("Tanggal pendakian di masa lalu. Harap pilih hari ini atau tanggal setelahnya.")
             st.stop()
        
        if lat is not None and lon is not None and OWM_API_KEY and days_ahead <= 5 and days_ahead >= 0:
            weather_data, weather_summary = get_weather_data(lat, lon, tanggal)
            if weather_data:
                is_specific_weather = True
            else:
                weather_summary = f"Gagal mendapatkan prakiraan cuaca spesifik dari OWM." 
        else:
            weather_summary = f"Prakiraan cuaca akan berdasarkan pengetahuan umum AI."

    # 3. Call Gemini Recommendation
    ai_data = None
    if GEMINI_CLIENT and days_ahead >= 0:
        with st.spinner("Menganalisis data dan membuat rekomendasi..."):
            ai_data = get_full_recommendation(gunung, kebugaran, tanggal, weather_summary)
    elif days_ahead >= 0:
        st.error("Gemini tidak terkonfigurasi (API Key hilang). Hasil AI tidak tersedia.")

    # 4. Simpan semua hasil ke Session State
    st.session_state['analysis_run'] = True
    st.session_state['ai_data'] = ai_data
    st.session_state['current_gunung'] = gunung
    st.session_state['gpx_data'] = (lat, lon, all_points, waypoints)
    st.session_state['weather_info'] = (weather_summary, is_specific_weather)
    
    # 5. Rerun untuk memaksa Streamlit menggambar ulang dengan data baru
    st.rerun()

# --- BLOK RENDERING HASIL (Menggunakan Session State) ---

# Tentukan apakah hasil analisis harus ditampilkan
should_render = (st.session_state['analysis_run'] and 
                (st.session_state['current_gunung'] == gunung_pilihan)) # Bandingkan gunung saat ini dengan gunung yang dianalisis

if should_render:
    # 1. Ambil data dari Session State
    ai_data = st.session_state['ai_data']
    lat, lon, all_points, waypoints = st.session_state['gpx_data']
    weather_summary, is_specific_weather = st.session_state['weather_info']
    
    if ai_data:
        st.subheader(f"Hasil Analisis: {gunung_pilihan}")
        st.markdown("---")
        
        # Metrics Row
        col1, col2, col3 = st.columns(3)
        estimasi = ai_data.get('estimasi', {})
        col1.metric("Jarak Total", f"{estimasi.get('jarak_total_km', '-') } km", delta_color='off')
        col2.metric("Waktu Naik", f"{estimasi.get('waktu_naik_jam', '-') } jam", delta_color='off')
        col3.metric("Waktu Turun", f"{estimasi.get('waktu_turun_jam', '-') } jam", delta_color='off')

        st.markdown("---")
        left, right = st.columns([2,1])

        # Left Column: Map, Weather, Logistics, Community
        with left:
            st.subheader("🗺️ Peta Jalur")
            
            # Cek apakah GPX Path tersedia
            gpx_file_path = None
            gpx_file_content = None
            
            row = scan_df[scan_df['nama_gunung'] == gunung_pilihan]
            if not row.empty:
                gpx_file_path = row['gpx_path'].iloc[0]
                gpx_file_content = load_gpx_content(gpx_file_path)
            
            st.markdown("<div class='map-card'>", unsafe_allow_html=True)
            if all_points:
                try:
                    center = all_points[0][0]
                    m = folium.Map(location=center, zoom_start=13, tiles="OpenStreetMap")
                    for seg in all_points:
                        folium.PolyLine(seg, weight=4, opacity=0.8, color='#2e86de').add_to(m)
                    for wp in waypoints:
                        folium.Marker([wp['lat'], wp['lon']], popup=wp['name'], icon=folium.Icon(color='red', icon='info-sign')).add_to(m)
                    folium_static(m, width=700, height=420)
                except Exception:
                    st.warning("Gagal menampilkan peta. Data GPX mungkin korup.")
            else:
                st.warning("Peta jalur tidak tersedia untuk pilihan ini.")
            st.markdown("</div>", unsafe_allow_html=True)

            # --- DOWNLOAD BUTTON ---
            if gpx_file_content:
                st.download_button(
                    label="⬇️ Download Jalur GPX",
                    data=gpx_file_content,
                    file_name=os.path.basename(gpx_file_path),
                    mime="application/gpx+xml",
                    key='download_gpx_button'
                )

            st.markdown("---")
            st.subheader("📌 Ringkasan Cuaca")
            if is_specific_weather:
                st.caption("Sumber: API Cuaca Eksternal (OWM)")
                st.info(weather_summary)
            else:
                st.caption("Sumber: Gemini AI (fallback)")
                st.info(ai_data.get('ringkasan_cuaca_ai', 'Ringkasan cuaca AI tidak tersedia.'))

            # --- Perlengkapan & Logistik ---
            st.markdown("---")
            st.subheader("🎒 Perlengkapan & Logistik")

            kit = pd.DataFrame(ai_data.get('perlengkapan_logistik', []))

            if not kit.empty:
                kit.columns = ['Item', 'Keterangan', 'Kategori']
                KEYWORDS_MAKANAN = ['makanan', 'bekal', 'hidrasi', 'logistik makanan', 'minuman']
                is_makanan = kit['Kategori'].str.lower().str.contains('|'.join(KEYWORDS_MAKANAN), na=False)
                makanan_df = kit[is_makanan] 
                perlengkapan_umum_df = kit[~is_makanan]

                st.markdown("##### Perlengkapan Umum (Pakaian, Navigasi, dll.)")
                if not perlengkapan_umum_df.empty:
                    st.dataframe(
                        perlengkapan_umum_df[['Item', 'Keterangan']],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Item": st.column_config.Column("Item", width="small"),
                            "Keterangan": st.column_config.Column("Keterangan", width="large"),
                        }
                    )
                st.markdown("##### Makanan & Hidrasi")
                if not makanan_df.empty:
                    st.dataframe(
                        makanan_df[['Item', 'Keterangan']],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Item": st.column_config.Column("Item", width="small"),
                            "Keterangan": st.column_config.Column("Keterangan (Sesuai Durasi)", width="large"),
                        }
                    )
            else:
                st.warning("Data perlengkapan tidak tersedia dari AI.")
            
            st.markdown("---")
            st.subheader("🗣️ Catatan Komunitas")
            twitter_df = load_processed_twitter()
            if not twitter_df.empty and GEMINI_CLIENT:
                with st.spinner("Menganalisis catatan komunitas..."):
                    notes = get_community_notes(gunung_pilihan, twitter_df)
                st.info(notes)
            elif twitter_df.empty:
                st.warning("Data Komunitas tidak tersedia. Fitur catatan komunitas dinonaktifkan.")
            else:
                st.error("Gemini tidak tersedia untuk analisis komunitas.")

        # Right Column: Recommendations, Safety
        with right:
            st.subheader("🥾 Rekomendasi Jalur & Kesulitan")
            for r in ai_data.get('rekomendasi_jalur', []):
                st.markdown(f"**{r.get('nama')}** — _{r.get('tingkat_kesulitan')}_")
                st.caption(r.get('deskripsi_singkat'))

            st.markdown("---")
            st.subheader("⚠️ Tips Keselamatan")
            for tip in ai_data.get('tips_keselamatan', []):
                st.markdown(f"- {tip}")

    else:
        st.error("AI tidak dapat menghasilkan rekomendasi pada saat ini.")
else:
    # Tampilkan panduan jika belum ada analisis yang dijalankan
    st.info("Pilih Gunung, tingkat kebugaran, dan tanggal di sidebar, lalu klik 'Analisis dan Rekomendasi' untuk melihat hasil.")

st.markdown("</div>", unsafe_allow_html=True)