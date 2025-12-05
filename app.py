# Sistem Deteksi Resiko Diabetes
# Main Application File

import streamlit as st

# Konfigurasi halaman
st.set_page_config(
    page_title="Deteksi Resiko Diabetes",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Judul aplikasi utama
st.title("🏥 Sistem Deteksi Resiko Diabetes")
st.write("Selamat datang di sistem deteksi resiko diabetes")

# Informasi sidebar
st.sidebar.success("Pilih halaman di atas")
