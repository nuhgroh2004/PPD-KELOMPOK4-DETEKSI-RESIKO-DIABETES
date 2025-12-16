# Page 2 - Deteksi Resiko Diabetes

import streamlit as st
import pandas as pd
import joblib

# =============================
# KONFIGURASI HALAMAN
# =============================
st.set_page_config(
    page_title="Page 2 - Deteksi Risiko Diabetes",
    layout="wide"
)

# =============================
# HEADER
# =============================
st.title("Page 2 - Deteksi Risiko Diabetes")
st.write(
    "Halaman ini digunakan untuk memprediksi risiko diabetes berdasarkan data kesehatan pengguna "
    "menggunakan model machine learning yang telah dilatih."
)

# =============================
# INFO DOWNLOAD MODEL
# =============================
st.info(
    "Model belum tersedia?\n\n"
    "Silakan unduh model terlebih dahulu dari Google Colab setelah proses training selesai.\n"
    "Pastikan file model disimpan dengan nama:\n"
    "model/best_model.pkl"
)

# =============================
# LOAD MODEL
# =============================
@st.cache_resource
def load_model():
    return joblib.load("model/best_model.pkl")

try:
    model = load_model()
    model_loaded = True
except:
    model_loaded = False
    st.warning("Model belum ditemukan. Pastikan file model sudah tersedia.")

# =============================
# FUNGSI KONVERSI USIA → AGE GROUP BRFSS
# =============================
def convert_age_to_group(age):
    if age <= 24:
        return 1
    elif age <= 29:
        return 2
    elif age <= 34:
        return 3
    elif age <= 39:
        return 4
    elif age <= 44:
        return 5
    elif age <= 49:
        return 6
    elif age <= 54:
        return 7
    elif age <= 59:
        return 8
    elif age <= 64:
        return 9
    elif age <= 69:
        return 10
    elif age <= 74:
        return 11
    elif age <= 79:
        return 12
    else:
        return 13

# =============================
# MAPPING TEKS → NILAI
# =============================
yes_no_map = {
    "Tidak": 0,
    "Ya": 1
}

# =============================
# FORM INPUT USER
# =============================
st.subheader("Masukkan Data Kesehatan Pengguna")

with st.form("form_prediksi"):
    col1, col2 = st.columns(2)

    with col1:
        bmi = st.number_input("BMI", min_value=10.0, max_value=60.0, value=25.0)
        age_real = st.number_input("Usia (tahun)", min_value=18, max_value=100, value=30)
        high_bp_text = st.selectbox("Tekanan Darah Tinggi", list(yes_no_map.keys()))
        high_chol_text = st.selectbox("Kolesterol Tinggi", list(yes_no_map.keys()))

    with col2:
        smoker_text = st.selectbox("Perokok", list(yes_no_map.keys()))
        phys_activity_text = st.selectbox("Aktivitas Fisik", list(yes_no_map.keys()))
        heart_disease_text = st.selectbox("Riwayat Penyakit Jantung", list(yes_no_map.keys()))

    submit = st.form_submit_button("Prediksi Risiko")

# =============================
# PROSES PREDIKSI
# =============================
if submit and model_loaded:

    age_group = convert_age_to_group(age_real)

    input_data = pd.DataFrame([[
        bmi,
        age_group,
        yes_no_map[high_bp_text],
        yes_no_map[high_chol_text],
        yes_no_map[smoker_text],
        yes_no_map[phys_activity_text],
        yes_no_map[heart_disease_text]
    ]], columns=[
        'BMI',
        'Age',
        'HighBP',
        'HighChol',
        'Smoker',
        'PhysActivity',
        'HeartDiseaseorAttack'
    ])

    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]

    st.subheader("Hasil Prediksi")

    if prediction == 1:
        st.error(f"Risiko diabetes terdeteksi dengan probabilitas {probability:.2%}")
    else:
        st.success(f"Risiko diabetes rendah dengan probabilitas {probability:.2%}")

    # =============================
    # REKOMENDASI
    # =============================
    st.subheader("Rekomendasi")

    if probability < 0.3:
        st.write(
            "- Pertahankan pola hidup sehat.\n"
            "- Lakukan aktivitas fisik secara rutin.\n"
            "- Jaga pola makan seimbang."
        )
    elif probability < 0.6:
        st.write(
            "- Tingkatkan aktivitas fisik.\n"
            "- Kurangi konsumsi makanan tinggi gula dan lemak.\n"
            "- Lakukan pemeriksaan kesehatan secara berkala."
        )
    else:
        st.write(
            "- Disarankan berkonsultasi dengan tenaga medis.\n"
            "- Terapkan pola makan rendah gula dan lemak.\n"
            "- Tingkatkan aktivitas fisik.\n"
            "- Pantau kadar gula darah secara rutin."
        )

# =============================
# CATATAN
# =============================
st.caption(
    "Hasil prediksi bersifat pendukung dan tidak menggantikan diagnosis medis profesional."
)
