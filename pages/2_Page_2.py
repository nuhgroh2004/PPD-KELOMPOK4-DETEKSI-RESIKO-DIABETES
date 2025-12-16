# Page 2 - Deteksi Resiko Diabetes

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os

# --- IMPORT SAFEGUARD ---
# Kita bungkus import ini supaya app tidak crash jika library belum diinstall
try:
    import google.generativeai as genai
    HAS_GENAI_LIB = True
except ImportError:
    HAS_GENAI_LIB = False

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Prediksi & Rekomendasi",
    page_icon="🩺",
    layout="wide"
)

# --- LOAD CSS EXTERNAL ---
try:
    with open("css/app.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# --- KONFIGURASI API (SAFE MODE) ---
api_key = None

# Coba ambil dari secrets, tapi jangan crash kalau file tidak ada
try:
    if 'GEMINI_API_KEY' in st.secrets:
        api_key = st.secrets['GEMINI_API_KEY']
except:
    pass

# Jika library ada dan key ada, baru configure
if HAS_GENAI_LIB and api_key:
    genai.configure(api_key=api_key)

# --- FUNGSI UTILS ---
def load_model():
    try:
        model = pickle.load(open('model_diabetes.sav', 'rb'))
        return model
    except FileNotFoundError:
        return None

def get_gemini_recommendation(user_data, is_high_risk):
    """
    Jika API Key ada -> Panggil Gemini.
    Jika API Key TIDAK ada -> Return teks dummy untuk cek visual (UI).
    """
    
    # --- MODE SIMULASI VISUAL (Jika API Key / Library tidak ada) ---
    if not api_key or not HAS_GENAI_LIB:
        risk_status = "Tinggi" if is_high_risk else "Rendah"
        return f"""
        ### 🧪 Mode Simulasi Visual (API Gemini Off)
        
        Karena API Key belum dipasang, berikut adalah **contoh tampilan** rekomendasi AI:
        
        **Analisis Singkat:**
        * Pasien memiliki risiko **{risk_status}**. Hal ini dipengaruhi oleh tingginya kadar Glukosa ({user_data['Glucose']}) dan BMI ({user_data['BMI']}).
        
        **Rekomendasi Pola Makan:**
        1.  Kurangi konsumsi karbohidrat sederhana (nasi putih, roti putih).
        2.  Perbanyak serat dari sayuran hijau dan buah-buahan.
        3.  Hindari minuman manis kemasan.
        
        **Saran Aktivitas:**
        * Jalan cepat minimal 30 menit sehari, 5 kali seminggu.
        
        > *Catatan: Ini hanya teks contoh untuk mengecek layout UI.*
        """

    # --- MODE ASLI (JIKA API KEY ADA) ---
    risk_text = "TINGGI (Positif Diabetes)" if is_high_risk else "RENDAH (Negatif Diabetes)"
    prompt = f"""
    Bertindaklah sebagai dokter. Analisis data pasien:
    Usia: {user_data['Age']}, BMI: {user_data['BMI']}, Glukosa: {user_data['Glucose']}.
    Risiko: {risk_text}.
    Berikan 3 saran makan dan olahraga dalam Bahasa Indonesia format Markdown bullet points.
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error API: {str(e)}"

# --- UI HALAMAN ---

st.markdown('<p class="sub-header">Analisis Risiko & Rekomendasi Kesehatan AI</p>', unsafe_allow_html=True)

# Notifikasi jika berjalan di mode visual
if not api_key:
    st.warning("⚠️ **Mode Pratinjau Visual:** API Key Gemini tidak terdeteksi. Sistem akan menampilkan teks simulasi (dummy) pada hasil rekomendasi.")

col_form, col_result = st.columns([1, 2], gap="large")

with col_form:
    st.info("📋 **Data Kesehatan Pasien**")
    with st.form("input_form"):
        # Input fields
        pregnancies = st.number_input("Jumlah Kehamilan", 0, 20, 0)
        glucose = st.number_input("Glukosa (mg/dL)", 0, 500, 150) # Default dibuat tinggi biar langsung kelihatan merah pas tes
        blood_pressure = st.number_input("Tekanan Darah (mm Hg)", 0, 200, 85)
        skin_thickness = st.number_input("Ketebalan Kulit (mm)", 0, 100, 20)
        insulin = st.number_input("Insulin (mu U/ml)", 0, 900, 79)
        bmi = st.number_input("BMI", 0.0, 70.0, 32.0, format="%.1f") # Default tinggi
        dpf = st.number_input("Diabetes Pedigree Function", 0.0, 3.0, 0.471, format="%.3f")
        age = st.number_input("Usia (Tahun)", 0, 120, 45)
        
        submit = st.form_submit_button("🔍 Analisis Risiko (Cek Visual)", type="primary", use_container_width=True)

with col_result:
    if submit:
        # Load Model (atau fallback ke dummy logic)
        model = load_model()
        
        # Logic Dummy untuk simulasi jika model tidak ada
        # Kita set 'True' jika Glukosa > 140 agar bisa lihat tampilan "Bahaya"
        if model:
            input_data = np.array([[pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, age]])
            prediction_result = model.predict(input_data)[0]
        else:
            # Fallback logic
            prediction_result = 1 if glucose > 140 else 0
        
        user_dict = {'Age': age, 'BMI': bmi, 'Glucose': glucose, 'BloodPressure': blood_pressure}

        # TAMPILAN HASIL DIAGNOSIS
        st.subheader("Hasil Diagnosis AI")
        
        if prediction_result == 1:
            st.error(f"""
            ### 🚨 Risiko Terdeteksi: TINGGI
            Pasien memiliki probabilitas tinggi mengidap diabetes.
            **Saran:** Segera konsultasikan ke dokter.
            """)
        else:
            st.success(f"""
            ### ✅ Risiko Terdeteksi: RENDAH
            Kondisi pasien relatif aman.
            **Saran:** Pertahankan gaya hidup sehat.
            """)
            
        st.markdown("---")
        
        # TAMPILAN REKOMENDASI (MOCKUP / ASLI)
        st.subheader("💡 Rekomendasi Personal")
        
        # Panggil fungsi (akan return teks dummy jika key kosong)
        with st.spinner("Menyusun rekomendasi..."):
            recommendation = get_gemini_recommendation(user_dict, prediction_result == 1)
            
            st.markdown(f"""
            <div style="background-color: #f8f9fa; border-left: 5px solid {'#ff4b4b' if prediction_result == 1 else '#28a745'}; padding: 20px; border-radius: 5px; color: #333;">
                {recommendation}
            </div>
            """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="text-align: center; padding: 50px; color: #666; background-color: #f0f2f6; border-radius: 10px;">
            <h3>👋 Area Tampilan Hasil</h3>
            <p>Klik tombol <b>Analisis Risiko</b> di sebelah kiri untuk melihat simulasi tampilan hasil.</p>
        </div>
        """, unsafe_allow_html=True)