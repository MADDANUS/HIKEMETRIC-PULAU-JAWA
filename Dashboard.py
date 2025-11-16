import streamlit as st

# HOME PAGE (Navigation Landing)
# -----------------------------

def home_page():
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.title("🏔️ Selamat Datang di Hike Metric")
    st.markdown("---")
    
    st.subheader("Panduan Pendakian")
    st.markdown("""
        Hike Metric dirancang untuk menjadi teman perencanaan pendakian paling terpercaya Anda. Kami percaya bahwa dengan menggabungkan data geografis yang akurat, prakiraan cuaca *real-time*, dan kecerdasan buatan, kami dapat membantu pendaki membuat keputusan yang lebih aman dan terinformasi.
    
        Aplikasi ini dirancang untuk memberikan analisis mendalam menggunakan:
        
        * **Data Jalur (GPX):** Visualisasi rute interaktif.
        * **Prakiraan Cuaca (OWM):** Kondisi cuaca spesifik untuk tanggal pendakian Anda.
        * **Kecerdasan Buatan (Gemini):** Rekomendasi logistik, estimasi waktu, dan tips keselamatan yang dipersonalisasi.
        
    """)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
   
    
if __name__ == "__main__":
    home_page()