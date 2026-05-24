import os

# 1. Tentukan path folder GPX Anda
GPX_FOLDER_PATH = './data_gpx' 

# 2. Daftar kata kunci gunung di Pulau Jawa (Whitelist)
gunung_jawa = [
    "Andong", "Anjasmoro", "Argopuro", "Arjuno", "Bismo", "Burangrang", 
    "Butak", "Ceremai", "Cikuray", "Galunggung", "Gede-Pangrango", 
    "Guntur", "Halimun", "Ijen", "Kelud", "Kembang", 
    "Lawu", "Liman", "Manglayang", "Merapi", "Merbabu", "Papandayan", 
    "Patuha", "Malabar", "Penanggungan", "Prau", "Rakutak", "Salak", 
    "Sanghyang", "Semeru", "Sindoro", "Slamet", "Sumbing", 
    "Tangkuban", "Tapak", "Tegal Panjang", "Telomoyo", "Telong", 
    "Ungaran", "Wayang"
]

def bersihkan_folder_gpx():
    count_deleted = 0
    count_kept = 0
    
    try:
        files = os.listdir(GPX_FOLDER_PATH)
        for fname in files:
            if fname.lower().endswith('.gpx'):
                # Cek apakah nama file mengandung salah satu kata kunci gunung Jawa
                is_jawa = any(gj.lower() in fname.lower() for gj in gunung_jawa)
                
                if not is_jawa:
                    file_path = os.path.join(GPX_FOLDER_PATH, fname)
                    os.remove(file_path) # Menghapus file
                    print(f"Dihapus: {fname}")
                    count_deleted += 1
                else:
                    print(f"Dipertahankan: {fname}")
                    count_kept += 1
                    
        print(f"\nSelesai! {count_deleted} file dihapus, {count_kept} file Jawa dipertahankan.")
        
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    bersihkan_folder_gpx()