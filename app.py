import streamlit as st

# Konfigurasi halaman
st.set_page_config(
    page_title="Sistem Deteksi Resiko Diabetes",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load external CSS from css/app.css
with open("css/app.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown('<p class="sub-header">Platform berbasis kecerdasan buatan untuk deteksi dini resiko diabetes mellitus</p>', unsafe_allow_html=True)

# Hero Section
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### Tentang Sistem

    Sistem Deteksi Resiko Diabetes adalah aplikasi berbasis machine learning yang dirancang untuk membantu 
    mendeteksi potensi resiko diabetes mellitus pada individu. Dengan menggunakan algoritma prediksi canggih, 
    sistem ini menganalisis berbagai parameter kesehatan untuk memberikan estimasi resiko yang akurat.

    #### Mengapa Deteksi Dini Penting?

    Diabetes mellitus merupakan salah satu penyakit kronis yang mempengaruhi jutaan orang di seluruh dunia. 
    Deteksi dini memungkinkan:

    - Intervensi medis lebih cepat dan efektif
    - Pencegahan komplikasi jangka panjang
    - Peningkatan kualitas hidup pasien
    - Pengelolaan kesehatan yang lebih baik
    """)

with col2:
    st.markdown("""
    <div class="stats-box">
        <h2>463 Juta</h2>
        <p>Penderita diabetes di dunia (IDF 2019)</p>
        <hr style="border-color: rgba(255,255,255,0.3);">
        <h2>50%</h2>
        <p>Tidak menyadari kondisi mereka</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Fitur Utama Section
st.markdown("### Fitur Utama Sistem")

# Custom HTML for feature cards in a flex row
st.markdown("""
<div class="feature-row">
    <div class="feature-card">
        <p class="feature-title">Analisis Komprehensif</p>
        <p class="feature-desc">
        Evaluasi menyeluruh berdasarkan parameter medis seperti kadar glukosa, 
        tekanan darah, BMI, dan riwayat keluarga untuk memberikan hasil yang akurat.
        </p>
    </div>
    <div class="feature-card">
        <p class="feature-title">Prediksi Akurat</p>
        <p class="feature-desc">
        Menggunakan algoritma machine learning yang telah dilatih dengan 
        dataset medis untuk menghasilkan prediksi yang reliable dan terpercaya.
        </p>
    </div>
    <div class="feature-card">
        <p class="feature-title">Hasil Instan</p>
        <p class="feature-desc">
        Dapatkan hasil analisis resiko dalam hitungan detik dengan 
        rekomendasi tindak lanjut yang jelas dan mudah dipahami.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Cara Kerja Section
st.markdown("### Cara Kerja Sistem")

step_col1, step_col2, step_col3, step_col4 = st.columns(4)

with step_col1:
    st.markdown("""
    **1. Input Data**

    Masukkan parameter kesehatan Anda melalui form yang telah disediakan.
    """)

with step_col2:
    st.markdown("""
    **2. Analisis Data**

    Sistem akan memproses data menggunakan model machine learning.
    """)

with step_col3:
    st.markdown("""
    **3. Prediksi Resiko**

    Algoritma menghasilkan estimasi tingkat resiko diabetes Anda.
    """)

with step_col4:
    st.markdown("""
    **4. Rekomendasi**

    Terima rekomendasi dan saran tindak lanjut yang sesuai.
    """)

st.markdown("---")

# Disclaimer Section
st.markdown("### Penting untuk Diperhatikan")

st.warning("""
**Disclaimer Medis:**

Sistem ini adalah alat bantu skrining awal dan BUKAN pengganti diagnosis medis profesional. 
Hasil prediksi dari sistem ini harus dikonsultasikan dengan tenaga medis yang berkualifikasi. 
Selalu konsultasikan kondisi kesehatan Anda dengan dokter untuk diagnosis dan penanganan yang tepat.
""")

# Footer Section
st.markdown("---")

footer_col1, footer_col2 = st.columns([3, 1])

with footer_col1:
    st.markdown("""
    ### Mulai Deteksi Resiko Anda

    Gunakan menu navigasi di sidebar untuk memulai proses deteksi atau melihat informasi lebih lanjut 
    tentang diabetes dan pencegahannya.
    """)

with footer_col2:
    st.info("**Navigasi:**\n\nGunakan menu di sidebar untuk mengakses fitur sistem")

# Sidebar Information
st.sidebar.title("Navigasi Sistem")
st.sidebar.info("""
**Pilih Menu:**
- Beranda (halaman ini)
- Prediksi Resiko
- Informasi Diabetes
- Tentang Sistem
""")

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Kontak & Support:**

Untuk pertanyaan dan dukungan teknis, 
hubungi administrator sistem.
""")