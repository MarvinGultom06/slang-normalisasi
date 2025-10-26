import streamlit as st
import app

# --- Import tambahan untuk logo ---
import base64
from PIL import Image
import os
# -----------------------------------

# --- Path ke logo ---
# Path ini relatif dari folder root (SLANG-NORMALISASI-FINAL), bukan dari folder 'pages'
LOGO_PATH = "assets/logo.png" 

# --- PATH BARU UNTUK IKON KONTEN ---
ICON_TEKS_PATH = "assets/logo_pensil.png"
ICON_FILE_PATH = "assets/logo_file.png"
# -----------------------------------


# --- Fungsi untuk encode gambar ---
@st.cache_data # Cache agar tidak dibaca ulang setiap kali
def get_base64_of_bin_file(bin_file):
    try:
        # DIUBAH: Menambahkan os.path.normpath untuk memperbaiki path (penting!)
        with open(os.path.normpath(bin_file), 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None # Kembalikan None jika file tidak ada

# --- Fungsi untuk membuat tag HTML logo HEADER ---
def get_img_with_href(local_img_path):
    img_base64 = get_base64_of_bin_file(local_img_path)
    if img_base64:
        return f'<img src="data:image/png;base64,{img_base64}" style="height: 50px; margin-right: 8px; vertical-align: middle;">'
    return "" # Kembalikan string kosong jika file tidak ditemukan

# ==========================================================
# --- FUNGSI INI DIUBAH ---
# --- Fungsi untuk ikon konten (centered, above text) ---
def get_content_img_html(local_img_path, height=150): # <-- Anda bisa atur tingginya di sini
    img_base64 = get_base64_of_bin_file(local_img_path)
    
    # Deteksi tipe file
    file_ext = os.path.splitext(local_img_path)[1].lower()
    if file_ext == ".png":
        img_type = "png"
    elif file_ext in [".jpg", ".jpeg"]:
        img_type = "jpeg"
    else:
        return "" # Tipe tidak didukung

    if img_base64:
        # Style ini akan menengahkan gambar dan memberinya tinggi tetap
        return f'<div style="text-align: center; height: {height+10}px; display: flex; align-items: center; justify-content: center;">' \
               f'<img src="data:image/{img_type};base64,{img_base64}" style="height: {height}px; vertical-align: middle;">' \
               f'</div>'
    return ""
# -----------------------------------

# --- Muat icon untuk tab browser ---
try:
    # DIUBAH: Menambahkan os.path.normpath
    page_icon = Image.open(os.path.normpath(LOGO_PATH))
except FileNotFoundError:
    page_icon = None

# ==========================================================
# TEMPLATE WAJIB UNTUK SETIAP HALAMAN
# ==========================================================

# 1. KONFIGURASI (HARUS PERTAMA + layout="wide")
st.set_page_config(
    page_title="Bantuan & About",
    page_icon=page_icon, # <-- DIUBAH
    layout="wide"
)

# 2. PANGGIL CSS (LANGSUNG SETELAH CONFIG)
app.local_css("style.css")

# --- Buat HTML logo ---
LOGO_HTML = get_img_with_href(LOGO_PATH) 

# --- BUAT HTML UNTUK IKON KONTEN ---
# DIUBAH: Memanggil fungsi get_content_img_html
ICON_TEKS_HTML = get_content_img_html(ICON_TEKS_PATH)
ICON_FILE_HTML = get_content_img_html(ICON_FILE_PATH)
# -----------------------------------


# 3. INJEKSI HEADER (SETELAH CSS)
st.markdown(f"""
    <header class="app-header">
        <a href="/" target="_self" class="logo">{LOGO_HTML} SlangBuster</a> <nav class="nav-links">
            <a href="/" target="_self">Home</a>
            <a href="/input_kalimat" target="_self">Input Teks</a>
            <a href="/input_file" target="_self">Input File</a>
            <a href="/help&about" target="_self">About & Help</a>
        </nav>
        <div class="header-right"></div>
    </header>
    """, unsafe_allow_html=True)
# ==========================================================

# --- KONTEN HALAMAN (DIROMBAK TOTAL) ---

st.title("Bantuan dan Tentang Aplikasi") # <-- DIUBAH: Spasi di depan dihapus
st.divider()

# --- Bagian 1: Tentang Model ---
st.subheader("Tentang Model")
st.markdown("""
Aplikasi ini menggunakan model **mT5 (Multilingual T5)** yang telah di-fine-tuning
pada dataset slang bahasa Indonesia (gabungan IndoCollex dan Indonesia-Slang).

Metode yang digunakan adalah **Hybrid**, yang menggabungkan:
* **Model mT5:** Sebagai prediktor utama.
* **Validasi Rule-based:** Memastikan hasil prediksi mT5 ada di dalam daftar kata baku.
* **Algoritma Levenshtein Distance:** Sebagai *fallback* jika prediksi model tidak valid, sistem akan mencari kata baku terdekat dari kamus.
""")

st.divider()

# ==========================================================
# --- Bagian 2: Cara Penggunaan (DIUBAH) ---
# ==========================================================
st.subheader("Cara Penggunaan")

col1, col2 = st.columns(2, gap="large")

with col1:
    # DIUBAH: Logo dipisah dan ditaruh di atas
    st.markdown(ICON_TEKS_HTML, unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Modul Input Teks</h4>", unsafe_allow_html=True)
    st.markdown("""
    Modul ini adalah cara tercepat untuk menormalisasi satu atau beberapa kalimat.
    1.  Buka halaman **[Input Teks](/input_kalimat)**.
    2.  Ketik (atau tempel) kalimat slang di boks teks.
    3.  Klik tombol "Normalisasi Kalimat".
    4.  Hasil akan langsung muncul di samping, beserta tabel detail proses normalisasi untuk setiap kata.
    """)

with col2:
    # DIUBAH: Logo dipisah dan ditaruh di atas
    st.markdown(ICON_FILE_HTML, unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Modul Input File</h4>", unsafe_allow_html=True)
    st.markdown("""
    Gunakan modul ini untuk memproses seluruh dokumen sekaligus.
    1.  Buka halaman **[Input File](/input_file)**.
    2.  Unggah file Anda (`.txt`, `.pdf`, `.csv`, atau `.xlsx`).
    3.  **Jika .txt/.pdf:** Proses akan otomatis berjalan. Anda akan melihat perbandingan teks asli dan teks ternormalisasi.
    4.  **Jika .csv/.xlsx:** Anda akan diminta memilih kolom yang berisi teks slang, lalu klik "Mulai Normalisasi Kolom".
    5.  Tombol "Download Hasil" akan muncul agar Anda bisa menyimpan file yang sudah diproses.
    """)

st.divider()

# --- Bagian 3: Pembuat & Pembimbing (Menggunakan Kolom) ---


col3, col4 = st.columns(2, gap="large")

with col3:
    st.markdown("### Pembuat")
    
    try:
        # Nama Anda sekarang ada di 'caption'
        st.image("assets/marvin.jpg", width=200, caption="Marvin Gultom 535220198") 
    except FileNotFoundError:
        st.warning("File foto 'assets/marvin.jpg' tidak ditemukan.")
    

with col4:
    st.markdown("### Dosen Pembimbing")
    
    # Buat 2 kolom baru di dalam col4
    pembimbing1_col, pembimbing2_col = st.columns(2) 

    # --- Foto Dosen 1 di kolom kiri ---
    with pembimbing1_col:
        try:
            # DIUBAH: Ganti 'use_container_width' dengan 'width'
            st.image("assets/dosen1.jpg", caption="Viny Christanti Mawardi, S.Kom., M.Kom.", width=250)
        except FileNotFoundError:
            st.warning("File foto 'assets/dosen1.jpg' tidak ditemukan.")
    
    # --- Foto Dosen 2 di kolom kanan ---
    with pembimbing2_col:
        try:
            # DIUBAH: Ganti 'use_container_width' dengan 'width'
            st.image("assets/dosen2.jpg", caption="Manatap Dolok Lauro, S.Kom., M.M.S.I.", width=250)
        except FileNotFoundError:
            st.warning("File foto 'assets/dosen2.jpg' tidak ditemukan.")

# FOOTER (PALING BAWAH)
st.markdown(f"""
    <footer class="app-footer">
        <div class="logo">{LOGO_HTML} SlangBuster</div> <div class="footer-center-text">Dikembangkan oleh: Marvin Gultom</div>
        <div class="footer-right"></div>
    </footer>
    """, unsafe_allow_html=True)