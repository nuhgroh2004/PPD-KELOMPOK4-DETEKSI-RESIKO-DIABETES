import streamlit as st
import pandas as pd
import joblib
import os

# --- IMPORT SAFEGUARD ---
try:
    import google.generativeai as genai
    HAS_GENAI_LIB = True
except ImportError:
    HAS_GENAI_LIB = False

# --- CONFIG PAGE ---
st.set_page_config(page_title="Prediksi Risiko Diabetes", page_icon="🩺", layout="wide")

# --- LOAD CSS ---
try:
    with open("css/app.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# --- API SETUP ---
api_key = None
try:
    if 'GEMINI_API_KEY' in st.secrets:
        api_key = st.secrets['GEMINI_API_KEY']
except:
    pass

if HAS_GENAI_LIB and api_key:
    genai.configure(api_key=api_key)

# --- LOAD MODEL ---
@st.cache_resource
def load_model():
    try:
        return joblib.load('diabetes_xgboost_model.joblib')
    except:
        try:
            import pickle
            return pickle.load(open('diabetes_xgboost_model.pkl', 'rb'))
        except:
            return None

# --- GEMINI FUNCTION (LITE MODEL) ---
def get_gemini_recommendation(user_data, is_high_risk):
    risk_text = "TINGGI (Indikasi Diabetes)" if is_high_risk else "RENDAH (Sehat)"
    
    prompt = f"""
    Bertindaklah sebagai dokter ahli. Data pasien:
    - BMI: {user_data['BMI']}
    - Tensi Tinggi: {'Ya' if user_data['HighBP']==1 else 'Tidak'}
    - Kolesterol: {'Ya' if user_data['HighChol']==1 else 'Tidak'}
    - Perokok: {'Ya' if user_data['Smoker']==1 else 'Tidak'}
    - Aktif Fisik: {'Ya' if user_data['PhysActivity']==1 else 'Tidak'}
    - Usia: Kategori {user_data['Age']}
    
    Risiko Diabetes: {risk_text}.
    
    Berikan:
    1. Penjelasan singkat faktor risiko utama.
    2. 3 Saran diet spesifik.
    3. 2 Saran olahraga yang aman.
    4. Gunakan bahasa Indonesia yang memotivasi.
    """
    
    if not api_key or not HAS_GENAI_LIB:
        return "⚠️ **Mode Simulasi:** API Key tidak terdeteksi. Saran AI tidak dapat dimuat."
        
    try:
        # Menggunakan model LITE/PREVIEW agar hemat kuota
        model = genai.GenerativeModel('gemini-2.0-flash-lite-preview-02-05')
        return model.generate_content(prompt).text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ Server sibuk. Silakan tunggu 1 menit lagi."
        return f"Error AI: {str(e)}"

# --- UI MAIN PAGE ---
st.markdown('<p class="sub-header">Kalkulator Risiko Diabetes & Gaya Hidup</p>', unsafe_allow_html=True)

model = load_model()
if not model:
    st.error("⚠️ File model tidak ditemukan.")

# --- FORMULIR 3 BAGIAN ---
with st.form("health_form"):
    
    # BAGIAN 1: DEMOGRAFI & DATA FISIK
    st.markdown("### 1. Data Demografi & Fisik")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        age = st.slider("Kategori Usia", 1, 13, 5, help="1 (18-24) ... 9 (60-64) ... 13 (80+)")
        sex = st.selectbox("Jenis Kelamin", [0, 1], format_func=lambda x: "Wanita" if x==0 else "Pria")
        bmi = st.number_input("BMI (Body Mass Index)", 10.0, 50.0, 25.0, help="Normal: 18.5-25 | Gemuk: 25-30 | Obesitas: >30")
        
    with c2:
        # PENDIDIKAN: Label Deskriptif
        edu_labels = {
            1: "1 - Tidak Sekolah / TK",
            2: "2 - SD (Elementary)",
            3: "3 - SMP / SMA (Belum Lulus)",
            4: "4 - Lulus SMA / Sederajat",
            5: "5 - Mahasiswa / D3",
            6: "6 - Sarjana (S1/S2/S3)"
        }
        education = st.selectbox("Pendidikan Terakhir", options=[1,2,3,4,5,6], 
                                 format_func=lambda x: edu_labels.get(x))

        # PENGHASILAN: Label Deskriptif
        income_labels = {
            1: "Kelas 1 (< 10 Juta/Thn)",
            2: "Kelas 2 (10-15 Juta/Thn)",
            3: "Kelas 3 (15-20 Juta/Thn)",
            4: "Kelas 4 (20-25 Juta/Thn)",
            5: "Kelas 5 (25-35 Juta/Thn)",
            6: "Kelas 6 (35-50 Juta/Thn)",
            7: "Kelas 7 (50-75 Juta/Thn)",
            8: "Kelas 8 (> 75 Juta/Thn)"
        }
        income = st.selectbox("Tingkat Penghasilan", options=[1,2,3,4,5,6,7,8], 
                              format_func=lambda x: income_labels.get(x))
        
    with c3:
        no_doc_cost = st.selectbox("Kesulitan Biaya Dokter?", [0, 1], format_func=lambda x: "Ya (Pernah)" if x==1 else "Tidak")
        any_healthcare = st.selectbox("Punya Jaminan Kesehatan?", [0, 1], format_func=lambda x: "Ya (BPJS/Asuransi)" if x==1 else "Tidak")

    st.markdown("---")

    # BAGIAN 2: RIWAYAT KESEHATAN
    st.markdown("### 2. Riwayat Medis")
    c4, c5, c6 = st.columns(3)
    with c4:
        high_bp = st.selectbox("Tekanan Darah Tinggi?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
        high_chol = st.selectbox("Kolesterol Tinggi?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
        chol_check = st.selectbox("Cek Kolesterol 5thn Terakhir?", [0, 1], format_func=lambda x: "Sudah Cek" if x==1 else "Belum")
    with c5:
        heart_disease = st.selectbox("Sakit Jantung?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
        stroke = st.selectbox("Pernah Stroke?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
    with c6:
        # KESEHATAN UMUM: Label Deskriptif
        gen_hlth_labels = {
            1: "1 - Sangat Baik (Excellent)",
            2: "2 - Baik Sekali (Very Good)",
            3: "3 - Baik (Good)",
            4: "4 - Cukup/Sedang (Fair)",
            5: "5 - Buruk (Poor)"
        }
        gen_hlth = st.selectbox("Kondisi Kesehatan Umum?", options=[1,2,3,4,5], 
                                format_func=lambda x: gen_hlth_labels.get(x))
        
        diff_walk = st.selectbox("Susah Jalan Kaki?", [0, 1], format_func=lambda x: "Ya (Sulit)" if x==1 else "Tidak")

    st.markdown("---")

    # BAGIAN 3: GAYA HIDUP & KEBIASAAN
    st.markdown("### 3. Gaya Hidup & Mental")
    c7, c8, c9 = st.columns(3)
    with c7:
        phys_activity = st.selectbox("Olahraga Rutin?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
        veggies = st.selectbox("Makan Sayur Tiap Hari?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
        fruits = st.selectbox("Makan Buah Tiap Hari?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
    with c8:
        smoker = st.selectbox("Perokok? (>100 btg seumur hidup)", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
        hvy_alcohol = st.selectbox("Minum Alkohol Berat?", [0, 1], format_func=lambda x: "Ya" if x==1 else "Tidak")
    with c9:
        ment_hlth = st.slider("Hari Mental Buruk (Stress)", 0, 30, 0)
        phys_hlth = st.slider("Hari Fisik Sakit/Cedera", 0, 30, 0)

    submit = st.form_submit_button("🔍 Analisis Risiko Sekarang", type="primary", use_container_width=True)

# --- PROSES INPUT & PREDIKSI ---
if submit and model:
    # Mapping input ke dictionary (SESUAI urutan feature_config.json)
    input_data = {
        'HighBP': [high_bp], 'HighChol': [high_chol], 'CholCheck': [chol_check],
        'BMI': [bmi], 'Smoker': [smoker], 'Stroke': [stroke],
        'HeartDiseaseorAttack': [heart_disease], 'PhysActivity': [phys_activity],
        'Fruits': [fruits], 'Veggies': [veggies], 'HvyAlcoholConsump': [hvy_alcohol],
        'AnyHealthcare': [any_healthcare], 'NoDocbcCost': [no_doc_cost],
        'GenHlth': [gen_hlth], 'MentHlth': [ment_hlth], 'PhysHlth': [phys_hlth],
        'DiffWalk': [diff_walk], 'Sex': [sex], 'Age': [age],
        'Education': [education], 'Income': [income]
    }
    
    df = pd.DataFrame(input_data)
    
    try:
        prediction = model.predict(df)[0]
        # Mengambil probabilitas (angka mentah 0.0 - 1.0)
        proba_diabetes = model.predict_proba(df)[0][1] if hasattr(model, "predict_proba") else 0
        
        st.divider()
        r1, r2 = st.columns([1, 1.5])
        
        with r1:
            if prediction == 1:
                st.error("### 🚨 POSITIF\nBeresiko Diabetes")
                # Jika Positif, Probabilitas pasti tinggi (misal 80%)
                st.metric("Probabilitas Diabetes", f"{proba_diabetes:.1%}")
            else:
                st.success("### ✅ NEGATIF\nRisiko Rendah")
                # Jika Negatif, Probabilitas diabetesnya pasti rendah (misal 1%)
                # Kita biarkan menampilkan angka rendah tersebut (Sesuai request)
                st.metric("Probabilitas Diabetes", f"{proba_diabetes:.1%}")
        
        with r2:
            st.info("🤖 **Analisis Dokter AI:**")
            with st.spinner("Sedang mengetik saran..."):
                saran = get_gemini_recommendation(input_data, prediction==1)
                st.write(saran)
                
    except Exception as e:
        st.error(f"Gagal memproses data: {e}")