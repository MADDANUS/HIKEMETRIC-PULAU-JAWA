import streamlit as st


st.set_page_config(page_title="Tentang Aplikasi", page_icon="💡")

def about_page():
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.title("💡 Tentang Hike Metric")
    st.markdown("---")

    st.subheader("Teknologi yang Digunakan")
    st.markdown("""
        Aplikasi ini dibangun di atas tumpuan teknologi modern yang canggih untuk memastikan panduan pendakian yang akurat dan *real-time*:

        * **Streamlit:** Digunakan sebagai kerangka kerja (framework) Python utama untuk pengembangan antarmuka web yang cepat, interaktif, dan *data-driven*.
        * **Google Gemini (via `google-genai`):** Model Kecerdasan Buatan generatif yang berfungsi sebagai mesin analisis logistik, estimasi durasi, dan perangkum sentimen komunitas dari data mentah.
        * **OpenWeatherMap (OWM):** Layanan API cuaca eksternal yang terintegrasi untuk menyediakan data prakiraan 5-hari yang spesifik dan berbasis koordinat (geospasial).
        * **GPX/Folium:** Kombinasi pustaka yang digunakan untuk pemrosesan data GPS (parsing file GPX) dan rendering visualisasi peta interaktif.
        * **Data Scraper & NLP:** Mekanisme *web scraping* yang dikombinasikan dengan teknik Pemrosesan Bahasa Alami (NLP) untuk pengumpulan dan penyaringan data kondisi jalur terkini dari sumber komunitas (sebelumnya disebut X).
    """)
    
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    about_page()