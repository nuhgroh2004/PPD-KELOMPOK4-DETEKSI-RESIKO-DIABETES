import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

# --- IMPORT LIBRARY GOOGLE (SAFEGUARD) ---
try:
    import google.generativeai as genai
    HAS_GENAI_LIB = True
except ImportError:
    HAS_GENAI_LIB = False

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Prediksi Risiko Diabetes",
    page_icon="🩺",
    layout="wide"
)

# --- LOAD CSS EXTERNAL ---
try:
    with open("css/app.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# --- KONFIGURASI API GEMINI (SAFE MODE) ---
api_key = None
try:
    if 'GEMINI_API_KEY' in st.secrets:
        api_key = st.secrets['GEMINI_API_KEY']
except:
    pass

if HAS_GENAI_LIB and api_key:
    genai.configure(api_key=api_key)

# --- FUNGSI LOAD MODEL ---
@st.cache_resource
def load_model():
    try:
        # Prioritaskan file .joblib karena lebih stabil untuk scikit-learn/xgboost
        model = joblib.load('diabetes_xgboost_model.joblib')
        return model
    except FileNotFoundError:
        try:
            # Fallback ke .pkl jika .joblib tidak ada
            import pickle
            model = pickle.load(open('diabetes_xgboost_model.pkl', 'rb'))
            return model
        except FileNotFoundError:
            return None

# --- FUNGSI REKOMENDASI AI ---
def get_gemini_recommendation(user_data, is_high_risk):
    risk_status = "TINGGI (Indikasi Diabetes/Pra-Diabetes)" if is_high_risk else "RENDAH (Sehat)"
    
    prompt = f"""
    Bertindaklah sebagai dokter spesialis penyakit dalam.
    Saya memiliki data gaya hidup pasien sebagai berikut:
    - BMI: {user_data['BMI']}
    - Tekanan Darah Tinggi: {'Ya' if user_data['HighBP']==1 else 'Tidak'}
    - Kolesterol Tinggi: {'Ya' if user_data['HighChol']==1 else 'Tidak'}
    - Perokok: {'Ya' if user_data['Smoker']==1 else 'Tidak'}
    - Aktivitas Fisik: {'Ya' if user_data['PhysActivity']==1 else 'Tidak'}
    - Konsumsi Buah/Sayur: {'Rutin' if user_data['Fruits']==1 and user_data['Veggies']==1 else 'Kurang'}
    - Usia: Kategori {user_data['Age']} (Skala 1-13)
    
    Hasil prediksi risiko diabetes pasien ini adalah: {risk_status}.
    
    Tugas:
    1. Jelaskan faktor risiko utama dari data di atas yang berkontribusi pada hasil prediksi.
    2. Berikan 3 rekomendasi perubahan gaya hidup spesifik (terkait diet dan olahraga).
    3. Berikan saran medis apakah perlu cek lab lanjutan (HbA1c/Gula Darah Puasa).
    4. Gunakan bahasa Indonesia yang empatik namun tegas secara medis.
    """
    
    if not api_key or not HAS_GENAI_LIB:
        return "API Key tidak ditemukan. (Mode Simulasi)"
    
    try:
        # --- PERBAIKAN: MENGGUNAKAN MODEL LITE PREVIEW ---
        # Model ini biasanya lebih longgar kuotanya untuk akun Free Tier
        model_ai = genai.GenerativeModel('gemini-2.0-flash-lite-preview-02-05')
        response = model_ai.generate_content(prompt)
        return response.text
        
    except Exception as e:
        # Jika masih kena limit, kita berikan pesan yang jelas
        if "429" in str(e):
            return """
            ⚠️ **Sedang Sibuk (Traffic Tinggi)**
            
            Server AI sedang sibuk atau kuota gratis sementara habis. 
            Silakan **Tunggu 1 menit** lalu coba tekan tombol Analisis lagi.
            """
        return f"Gagal menghubungi AI: {str(e)}"

# --- UI HALAMAN ---
st.markdown('<p class="sub-header">Kalkulator Risiko Diabetes & Gaya Hidup</p>', unsafe_allow_html=True)
st.caption("Menggunakan model Machine Learning berbasis data gaya hidup & riwayat kesehatan.")

model = load_model()
if not model:
    st.error("⚠️ File model ('diabetes_xgboost_model.joblib' atau '.pkl') tidak ditemukan. Pastikan file sudah diupload ke folder yang sama.")

# Form Input (Disesuaikan dengan feature_config.json)
with st.form("health_form"):
    st.markdown("### 1. Data Fisik & Riwayat Medis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        bmi = st.number_input("BMI (Body Mass Index)", 10.0, 50.0, 25.0, help="Berat (kg) / Tinggi (m)^2")
        gen_hlth = st.selectbox("Kondisi Kesehatan Umum", options=[1,2,3,4,5], format_func=lambda x: {1:"Sangat Baik", 2:"Baik", 3:"Cukup", 4:"Buruk", 5:"Sangat Buruk"}[x])
        age = st.slider("Kategori Usia", 1, 13, 1, help="1: 18-24th ... 13: 80th+")
        
    with col2:
        high_bp = st.selectbox("Riwayat Darah Tinggi?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
        high_chol = st.selectbox("Riwayat Kolesterol Tinggi?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
        chol_check = st.selectbox("Cek Kolesterol 5 thn Terakhir?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
        
    with col3:
        heart_disease = st.selectbox("Penyakit Jantung?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
        stroke = st.selectbox("Riwayat Stroke?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
        diff_walk = st.selectbox("Kesulitan Berjalan?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")

    st.markdown("### 2. Gaya Hidup & Kebiasaan")
    col4, col5, col6 = st.columns(3)
    
    with col4:
        phys_activity = st.selectbox("Olahraga dlm 30 Hari Terakhir?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
        fruits = st.selectbox("Makan Buah Tiap Hari?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
        veggies = st.selectbox("Makan Sayur Tiap Hari?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")

    with col5:
        smoker = st.selectbox("Perokok? (Min. 100 batang seumur hidup)", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
        hvy_alcohol = st.selectbox("Peminum Alkohol Berat?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
        any_healthcare = st.selectbox("Punya Jaminan Kesehatan?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")

    with col6:
        ment_hlth = st.slider("Hari Kesehatan Mental Buruk (30 hari terakhir)", 0, 30, 0)
        phys_hlth = st.slider("Hari Kesehatan Fisik Buruk (30 hari terakhir)", 0, 30, 0)
        sex = st.selectbox("Jenis Kelamin", [0, 1], format_func=lambda x: "Wanita" if x==0 else "Pria") # Asumsi 0:F, 1:M (Cek metadata asli jika terbalik)
    
    # Input tambahan (dummy/default jika tidak terlalu berpengaruh di UI tapi diminta model)
    no_doc_cost = 0 # Default Tidak
    education = 4 # Default SMA/Kuliah
    income = 5 # Default Menengah

    submit_btn = st.form_submit_button("🔍 Analisis Risiko Sekarang", type="primary", use_container_width=True)

# Proses Prediksi
if submit_btn and model:
    # Membuat Dictionary sesuai NAMA KOLOM yang persis diminta feature_config.json
    input_data = {
        'HighBP': [high_bp],
        'HighChol': [high_chol],
        'CholCheck': [chol_check],
        'BMI': [bmi],
        'Smoker': [smoker],
        'Stroke': [stroke],
        'HeartDiseaseorAttack': [heart_disease],
        'PhysActivity': [phys_activity],
        'Fruits': [fruits],
        'Veggies': [veggies],
        'HvyAlcoholConsump': [hvy_alcohol],
        'AnyHealthcare': [any_healthcare],
        'NoDocbcCost': [no_doc_cost], # Hidden input
        'GenHlth': [gen_hlth],
        'MentHlth': [ment_hlth],
        'PhysHlth': [phys_hlth],
        'DiffWalk': [diff_walk],
        'Sex': [sex],
        'Age': [age],
        'Education': [education], # Hidden input
        'Income': [income]        # Hidden input
    }
    
    # Konversi ke DataFrame
    input_df = pd.DataFrame(input_data)
    
    # Pastikan urutan kolom sesuai dengan yang diinginkan model (jika sensitif urutan)
    # Biasanya pipeline sklearn aman dengan nama kolom, tapi jaga-jaga kita urutkan:
    expected_columns = [
        "HighBP", "HighChol", "CholCheck", "BMI", "Smoker", "Stroke", 
        "HeartDiseaseorAttack", "PhysActivity", "Fruits", "Veggies", 
        "HvyAlcoholConsump", "AnyHealthcare", "NoDocbcCost", "GenHlth", 
        "MentHlth", "PhysHlth", "DiffWalk", "Sex", "Age", "Education", "Income"
    ]
    
    # Reorder kolom DataFrame
    input_df = input_df[expected_columns]

    # Prediksi
    try:
        prediction = model.predict(input_df)[0]
        # Jika model support predict_proba
        try:
            probability = model.predict_proba(input_df)[0][1]
        except:
            probability = 0.0

        st.divider()
        col_res1, col_res2 = st.columns([1, 2])
        
        with col_res1:
            st.subheader("Hasil Diagnosis")
            if prediction == 1:
                st.error("### 🚨 POSITIF\nBeresiko Diabetes")
                st.write(f"Tingkat Keyakinan Model: **{probability:.1%}**")
            else:
                st.success("### ✅ NEGATIF\nRisiko Rendah")
                st.write(f"Tingkat Keyakinan Model: **{(1-probability):.1%}**")

        with col_res2:
            st.subheader("💡 Rekomendasi Dokter AI")
            with st.spinner("Menyusun saran kesehatan..."):
                rec_text = get_gemini_recommendation(input_data, prediction == 1)
                st.info(rec_text)
                
    except Exception as e:
        st.error(f"Terjadi kesalahan saat prediksi: {str(e)}")
        st.write("Pastikan format data input sesuai dengan feature_config.json")