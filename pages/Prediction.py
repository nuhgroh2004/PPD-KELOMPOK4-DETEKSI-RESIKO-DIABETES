import streamlit as st
import pandas as pd
import joblib
import os
from dotenv import load_dotenv

# Load environment variables (force reload untuk update API key)
load_dotenv(override=True)

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
# Prioritas: Environment Variable > Streamlit Secrets
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
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
    # Dapatkan path root project (parent directory dari pages/)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Path file model
    model_joblib = os.path.join(root_dir, 'diabetes_xgboost_model.joblib')
    model_pkl = os.path.join(root_dir, 'diabetes_xgboost_model.pkl')
    
    try:
        if os.path.exists(model_joblib):
            return joblib.load(model_joblib)
    except Exception as e:
        st.warning(f"Gagal load .joblib: {e}")
    
    try:
        if os.path.exists(model_pkl):
            import pickle
            return pickle.load(open(model_pkl, 'rb'))
    except Exception as e:
        st.warning(f"Gagal load .pkl: {e}")
    
    return None

# --- GEMINI FUNCTION (LITE MODEL) ---
def get_gemini_recommendation(user_data, is_high_risk):
    risk_text = "TINGGI (Indikasi Diabetes)" if is_high_risk else "RENDAH (Sehat)"
    
    prompt = f"""
    Analisis kesehatan singkat:
    - BMI: {user_data['BMI']}
    - Tensi Tinggi: {'Ya' if user_data['HighBP']==1 else 'Tidak'}
    - Kolesterol: {'Ya' if user_data['HighChol']==1 else 'Tidak'}
    - Perokok: {'Ya' if user_data['Smoker']==1 else 'Tidak'}
    - Aktif Fisik: {'Ya' if user_data['PhysActivity']==1 else 'Tidak'}
    - Usia: Kategori {user_data['Age']}
    
    Risiko Diabetes: {risk_text}.
    
    Berikan saran SINGKAT (maksimal 400 kata):
    1. Faktor risiko utama (1 kalimat)
    2. 3 Saran diet
    3. 2 Saran olahraga
    Gunakan bahasa Indonesia, format poin-poin.
    """
    
    if not api_key or not HAS_GENAI_LIB:
        return "⚠️ **Mode Simulasi:** API Key tidak terdeteksi. Saran AI tidak dapat dimuat."
    
    try:
        # Menggunakan Gemini 2.0 Flash Lite (ringan, hemat kuota, cepat)
        model = genai.GenerativeModel('models/gemini-2.5-flash-lite')
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,
                'top_p': 0.9,
                'max_output_tokens': 600,
            }
        )
        return response.text
    except Exception as e:
        error_msg = str(e).lower()
        if "429" in error_msg or "quota" in error_msg or "resource exhausted" in error_msg:
            return "⚠️ **Kuota API habis.** Tunggu beberapa menit atau generate API key baru di [Google AI Studio](https://aistudio.google.com/apikey)"
        elif "api" in error_msg and "key" in error_msg or "invalid" in error_msg:
            return "⚠️ **API Key tidak valid.** Buat key baru di https://aistudio.google.com/apikey dan update file `.env`"
        elif "403" in error_msg or "permission" in error_msg:
            return "⚠️ **API tidak diizinkan.** Pastikan API key dibuat untuk Gemini API."
        else:
            return f"⚠️ **Error AI:** {str(e)[:200]}\n\nCoba restart Streamlit atau cek koneksi internet."

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
        # USIA: Dropdown dengan kategori jelas
        age_labels = {
            1: "1 - Usia 18-24 tahun", 2: "2 - Usia 25-29 tahun", 3: "3 - Usia 30-34 tahun",
            4: "4 - Usia 35-39 tahun", 5: "5 - Usia 40-44 tahun", 6: "6 - Usia 45-49 tahun",
            7: "7 - Usia 50-54 tahun", 8: "8 - Usia 55-59 tahun", 9: "9 - Usia 60-64 tahun",
            10: "10 - Usia 65-69 tahun", 11: "11 - Usia 70-74 tahun",
            12: "12 - Usia 75-79 tahun", 13: "13 - Usia 80+ tahun"
        }
        age = st.selectbox("Kategori Usia", options=list(age_labels.keys()), 
                          format_func=lambda x: age_labels.get(x), index=4)
        sex = st.selectbox("Jenis Kelamin", [0, 1], format_func=lambda x: "Wanita" if x==0 else "Pria")
        bmi = st.number_input("BMI (Body Mass Index)", 10.0, 50.0, 25.0, help="Berat(kg) / Tinggi(m)². Normal: 18.5-24.9")
        
    with c2:
        # PENDIDIKAN: Sesuai dataset BRFSS
        edu_labels = {
            1: "1 - Tidak pernah sekolah / TK",
            2: "2 - SD (Kelas 1-8)",
            3: "3 - SMP/SMA (Kelas 9-11, belum lulus)",
            4: "4 - Lulus SMA/sederajat",
            5: "5 - Perguruan Tinggi 1-3 tahun (D1/D2/D3)",
            6: "6 - Sarjana S1 atau lebih tinggi"
        }
        education = st.selectbox("Tingkat Pendidikan", options=[1,2,3,4,5,6], 
                                 format_func=lambda x: edu_labels.get(x), index=3)

        # PENGHASILAN: Dalam USD (dataset BRFSS dari US)
        income_labels = {
            1: "1 - Kurang dari $10,000/tahun",
            2: "2 - $10,000 - $15,000/tahun",
            3: "3 - $15,000 - $20,000/tahun",
            4: "4 - $20,000 - $25,000/tahun",
            5: "5 - $25,000 - $35,000/tahun",
            6: "6 - $35,000 - $50,000/tahun",
            7: "7 - $50,000 - $75,000/tahun",
            8: "8 - $75,000 atau lebih/tahun"
        }
        income = st.selectbox("Tingkat Penghasilan (USD)", options=[1,2,3,4,5,6,7,8], 
                              format_func=lambda x: income_labels.get(x), index=4)
        
    with c3:
        any_healthcare = st.selectbox("Memiliki Asuransi Kesehatan?", [0, 1], 
                                     format_func=lambda x: "Ya" if x==1 else "Tidak",
                                     help="Termasuk asuransi swasta, HMO, dll")
        no_doc_cost = st.selectbox("Pernah Tidak ke Dokter karena Biaya? (12 bulan terakhir)", [0, 1], 
                                  format_func=lambda x: "Ya, pernah" if x==1 else "Tidak pernah")

    st.markdown("---")

    # BAGIAN 2: RIWAYAT KESEHATAN
    st.markdown("### 2. Riwayat Medis")
    c4, c5, c6 = st.columns(3)
    with c4:
        high_bp = st.selectbox("Tekanan Darah Tinggi (Hipertensi)?", [0, 1], 
                              format_func=lambda x: "Ya" if x==1 else "Tidak")
        high_chol = st.selectbox("Kolesterol Tinggi?", [0, 1], 
                                format_func=lambda x: "Ya" if x==1 else "Tidak")
        chol_check = st.selectbox("Pernah Cek Kolesterol (5 tahun terakhir)?", [0, 1], 
                                 format_func=lambda x: "Ya, sudah cek" if x==1 else "Belum/Tidak")
    with c5:
        heart_disease = st.selectbox("Penyakit Jantung Koroner / Serangan Jantung?", [0, 1], 
                                    format_func=lambda x: "Ya, pernah" if x==1 else "Tidak",
                                    help="CHD atau MI")
        stroke = st.selectbox("Pernah Mengalami Stroke?", [0, 1], 
                             format_func=lambda x: "Ya, pernah" if x==1 else "Tidak pernah")
    with c6:
        # KESEHATAN UMUM: Skala 1-5
        gen_hlth_labels = {
            1: "1 - Sangat Baik (Excellent)",
            2: "2 - Baik Sekali (Very Good)",
            3: "3 - Baik (Good)",
            4: "4 - Cukup (Fair)",
            5: "5 - Buruk (Poor)"
        }
        gen_hlth = st.selectbox("Kondisi Kesehatan Umum Anda?", options=[1,2,3,4,5], 
                                format_func=lambda x: gen_hlth_labels.get(x), index=2)
    st.markdown("---")

    # BAGIAN 3: GAYA HIDUP & KONDISI LAINNYA
    st.markdown("### 3. Gaya Hidup & Kondisi Lainnya")
    c7, c8, c9 = st.columns(3)
    with c7:
        phys_activity = st.selectbox("Aktivitas Fisik (30 hari terakhir, di luar pekerjaan)?", [0, 1], 
                                    format_func=lambda x: "Ya, aktif" if x==1 else "Tidak")
        veggies = st.selectbox("Konsumsi Sayur (≥1 kali/hari)?", [0, 1], 
                              format_func=lambda x: "Ya" if x==1 else "Tidak")
        fruits = st.selectbox("Konsumsi Buah (≥1 kali/hari)?", [0, 1], 
                             format_func=lambda x: "Ya" if x==1 else "Tidak")
    with c8:
        smoker = st.selectbox("Perokok? (≥100 batang seumur hidup)", [0, 1], 
                             format_func=lambda x: "Ya" if x==1 else "Tidak",
                             help="5 bungkus = 100 batang rokok")
        hvy_alcohol = st.selectbox("Konsumsi Alkohol Berat?", [0, 1], 
                                  format_func=lambda x: "Ya" if x==1 else "Tidak",
                                  help="Pria: >14 gelas/minggu | Wanita: >7 gelas/minggu")
        diff_walk = st.selectbox("Kesulitan Serius Berjalan / Menaiki Tangga?", [0, 1],
                                format_func=lambda x: "Ya" if x==1 else "Tidak")
    with c9:
        ment_hlth = st.slider("Berapa hari kesehatan mental buruk? (30 hari terakhir)", 0, 30, 0,
                             help="Termasuk stress, depresi, masalah emosional")
        phys_hlth = st.slider("Berapa hari kesehatan fisik buruk? (30 hari terakhir)", 0, 30, 0,
                             help="Termasuk sakit fisik dan cedera")

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