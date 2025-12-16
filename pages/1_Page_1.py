import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =============================
# KONFIGURASI HALAMAN
# =============================
st.set_page_config(
    page_title="Visualisasi Survei Diabetes",
    layout="wide"
)

st.title("Visualisasi Data Survei Diabetes")
st.write(
    "Halaman ini menyajikan visualisasi data survei kesehatan (BRFSS 2015) "
    "untuk memahami distribusi dan faktor risiko diabetes sebelum dilakukan deteksi risiko."
)

# =============================
# LOAD DATASET
# =============================
@st.cache_data
def load_data():
    return pd.read_csv("data/diabetes_clean.csv")

df = load_data()

# =============================
# RINGKASAN DATASET
# =============================
st.subheader("Ringkasan Dataset")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Jumlah Responden", df.shape[0])

with col2:
    st.metric("Jumlah Fitur", df.shape[1] - 1)

with col3:
    st.metric("Sumber Data", "BRFSS 2015")

# =============================
# DISTRIBUSI STATUS DIABETES
# =============================
st.subheader("Distribusi Status Diabetes")

fig, ax = plt.subplots()
df['Diabetes'].value_counts().plot(kind='bar', ax=ax)
ax.set_xlabel("Status Diabetes (0 = Tidak, 1 = Ya)")
ax.set_ylabel("Jumlah Responden")
ax.set_title("Distribusi Responden Berdasarkan Status Diabetes")
st.pyplot(fig)

st.caption(
    "Grafik ini menunjukkan perbandingan jumlah responden dengan dan tanpa diabetes, "
    "yang penting untuk memahami keseimbangan data."
)

# =============================
# DISTRIBUSI BMI
# =============================
st.subheader("Distribusi BMI Berdasarkan Status Diabetes")

fig, ax = plt.subplots()
df.boxplot(column='BMI', by='Diabetes', ax=ax)
ax.set_xlabel("Status Diabetes (0 = Tidak, 1 = Ya)")
ax.set_ylabel("BMI")
ax.set_title("Perbandingan BMI pada Responden Diabetes dan Non-Diabetes")
plt.suptitle("")
st.pyplot(fig)

st.caption(
    "Responden dengan diabetes cenderung memiliki nilai BMI yang lebih tinggi, "
    "menunjukkan BMI sebagai salah satu faktor risiko penting."
)

# =============================
# FAKTOR RISIKO UTAMA
# =============================
st.subheader("Faktor Risiko Utama")

risk_factor = st.selectbox(
    "Pilih faktor risiko:",
    ["Tekanan_Darah_Tinggi", "Kolesterol_Tinggi", "Aktivitas_Fisik", "Penyakit_Jantung"]
)

fig, ax = plt.subplots()
pd.crosstab(df[risk_factor], df['Diabetes']).plot(kind='bar', ax=ax)
ax.set_xlabel(risk_factor)
ax.set_ylabel("Jumlah Responden")
ax.set_title(f"Hubungan {risk_factor} dengan Status Diabetes")
st.pyplot(fig)

# =============================
# INSIGHT SINGKAT
# =============================
st.subheader("Insight Awal")
st.write(
    "- Prevalensi diabetes lebih tinggi pada responden dengan kondisi kesehatan tertentu.\n"
    "- BMI yang lebih tinggi menunjukkan korelasi dengan status diabetes.\n"
    "- Faktor risiko ini menjadi dasar dalam pengembangan model deteksi risiko pada halaman berikutnya."
)
