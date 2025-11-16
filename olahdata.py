import pandas as pd
import re
import os
import json
import gpxpy 

# --- 1. KONFIGURASI JALUR ---

# Jalur tempat file CSV Twitter Anda berada
TWITTER_FOLDER_PATH = './data_twitter'

# Jalur ke folder GPX Anda (digunakan untuk mendapatkan daftar gunung)
GPX_FOLDER_PATH = './data_gpx' 

# Daftar kata kunci untuk menyaring noise
KEYWORDS = [
    'jalur', 'simaksi', 'pos', 'puncak', 'basecamp', 'tracking', 
    'licin', 'dingin', 'hujan', 'angin', 'badai', 'cuaca', 'surut', 'banjir',
    'erupsi', 'longsor', 'camp', 'alat', 'logistik', 'sampah', 'ramai'
]

# --- 2. FUNGSI PEMBANTU ---

def get_mountain_list_from_gpx_folder(folder_path):
    """Memindai folder GPX dan mengembalikan daftar nama gunung yang sudah dibersihkan."""
    mountain_list = []
    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(".gpx"):
                # Bersihkan: Hapus ekstensi, spasi, dan pastikan huruf kecil untuk perbandingan
                gunung_name = filename.replace('.gpx', '').replace('Gunung ', '').replace('.', '').strip()
                if gunung_name and gunung_name.lower() != 'unknown':
                    mountain_list.append(gunung_name)
        
        print(f"DEBUG: {len(mountain_list)} nama gunung diekstrak dari folder GPX.")
        print(f"DEBUG: Contoh nama GPX: {mountain_list[:5]}")
        
        return list(set(mountain_list))
    except FileNotFoundError:
        print(f"ERROR: Folder GPX tidak ditemukan di {folder_path}. Menggunakan list default.")
        

def clean_tweet_text(text):
    """Membersihkan teks tweet: menghapus URL, mentions, hashtags."""
    if pd.isna(text) or text is None:
        return ""
    
    text = str(text) 
    text = re.sub(r'http\S+|https\S+|t.co/\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text.lower()

def extract_mountain_name(text, mountain_list):
    """Mencari nama gunung yang ada di mountain_list dalam teks."""
    if not text:
        return 'UNKNOWN'
        
    for mountain in mountain_list:
        # Mencari nama gunung di dalam teks yang sudah dibersihkan
        # Contoh: Mencari 'semeru' di teks 'puncak semeru sangat dingin'
        if mountain.lower() in text:
            return mountain 
    return 'UNKNOWN'

# --- 3. LOGIKA UTAMA EKSEKUSI ---

def process_twitter_data():
    
    # A. 1. Mendapatkan Daftar Gunung dari Folder GPX
    GUNUNG_LIST_FOR_EXTRACTION = get_mountain_list_from_gpx_folder(GPX_FOLDER_PATH)
    
    if not GUNUNG_LIST_FOR_EXTRACTION:
        print("ERROR: Tidak ada nama gunung yang dapat diekstrak dari folder GPX. Program berhenti.")
        return

    # A. 2. Persiapan Pattern Regex
    PATTERN_KEYWORDS = r'|'.join(re.escape(k) for k in KEYWORDS)
    
    # B. Menggabungkan Data CSV secara Dinamis
    all_dfs = []
    
    try:
        # Pindai semua file CSV di dalam folder
        file_names = [f for f in os.listdir(TWITTER_FOLDER_PATH) if f.endswith('.csv')]
        
        if not file_names:
            print(f"ERROR: Tidak ada file .csv yang ditemukan di folder {TWITTER_FOLDER_PATH}.")
            return

        for file in file_names:
            full_path = os.path.join(TWITTER_FOLDER_PATH, file)
            try:
                df = pd.read_csv(full_path)
                all_dfs.append(df)
                print(f"-> Memuat {file}: {len(df)} baris.")
            except Exception as e:
                print(f"-> Gagal memuat {file}. Abaikan: {e}")

    except FileNotFoundError:
        print(f"ERROR: Folder {TWITTER_FOLDER_PATH} tidak ditemukan. Program berhenti.")
        return

    if not all_dfs:
        print("Gagal memproses semua file Twitter yang ditemukan. Program berhenti.")
        return

    combined_df = pd.concat(all_dfs, ignore_index=True)
    print(f"\nTotal baris gabungan: {len(combined_df)}")

    # C. Pembersihan Teks
    print("-> Membersihkan teks...")
    if 'full_text' not in combined_df.columns:
        print("ERROR: Kolom 'full_text' tidak ditemukan. Program berhenti.")
        return
        
    combined_df['clean_text'] = combined_df['full_text'].apply(clean_tweet_text)

    # D. Ekstraksi Nama Gunung
    print("-> Mengekstrak nama gunung...")
    combined_df['nama_gunung_ekstraksi'] = combined_df['clean_text'].apply(
        lambda x: extract_mountain_name(x, GUNUNG_LIST_FOR_EXTRACTION)
    )

    # E. Penyaringan Relevansi
    print("-> Menyaring tweet berdasarkan relevansi dan nama gunung...")
    
    # Filter pertama: Teks harus memiliki salah satu kata kunci umum pendakian
    filtered_df = combined_df[combined_df['clean_text'].str.contains(PATTERN_KEYWORDS, na=False, regex=True)]
    
    # Filter kedua: Tweet harus menyebutkan nama gunung yang kita kenal
    final_filtered_df = filtered_df[filtered_df['nama_gunung_ekstraksi'] != 'UNKNOWN']
    
    # --- DEBUGGING AKHIR ---
    unknown_count = len(filtered_df) - len(final_filtered_df)
    print(f"DEBUG: {unknown_count} tweet relevan diabaikan karena nama gunung tidak terdeteksi.")
    print(f"\nTotal baris setelah filter relevansi dan nama gunung: {len(final_filtered_df)}")
    print(f"Data siap dianalisis oleh AI: {len(final_filtered_df)} baris.")

    # F. Penyimpanan Hasil
    OUTPUT_CSV_FILE = 'processed_twitter_data.csv'
    
    final_filtered_df.to_csv(OUTPUT_CSV_FILE, index=False)
    print(f"✅ Data diproses dan disimpan ke {OUTPUT_CSV_FILE}")

    # G. Menyimpan daftar gunung unik yang berhasil diekstrak (untuk integrasi app.py)
    unique_mountains = final_filtered_df['nama_gunung_ekstraksi'].unique().tolist()
    OUTPUT_JSON_FILE = 'unique_twitter_mountains.json'
    with open(OUTPUT_JSON_FILE, 'w') as f:
        json.dump(unique_mountains, f)
    print(f"✅ Daftar gunung unik yang berhasil diekstrak (untuk integrasi app.py) disimpan ke {OUTPUT_JSON_FILE}")


if __name__ == "__main__":
    process_twitter_data()