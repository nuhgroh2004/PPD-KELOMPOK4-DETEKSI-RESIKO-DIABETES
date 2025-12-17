# 🩺 Sistem Deteksi Risiko Diabetes

Platform berbasis kecerdasan buatan untuk deteksi dini risiko diabetes mellitus menggunakan **Machine Learning (XGBoost)** dan **Gemini AI** untuk rekomendasi kesehatan.

---

## 📋 Deskripsi Proyek

Aplikasi web interaktif yang membantu mendeteksi potensi risiko diabetes berdasarkan:
- **Data Demografi** (Usia, Jenis Kelamin, Pendidikan, Penghasilan)
- **Riwayat Medis** (Tekanan Darah, Kolesterol, Penyakit Jantung, dll)
- **Gaya Hidup** (Aktivitas Fisik, Kebiasaan Merokok, Pola Makan, Kesehatan Mental)

### ✨ Fitur Utama
- ✅ Prediksi risiko diabetes menggunakan model **XGBoost**
- 🤖 Rekomendasi personal dari **Gemini AI** (diet, olahraga, gaya hidup)
- 📊 Visualisasi data survei kesehatan (BRFSS 2015)
- 💊 Dashboard interaktif dengan UI modern

---

## 🚀 Quick Start

### 1️⃣ Clone Repository
```bash
git clone https://github.com/nuhgroh2004/PPD-KELOMPOK4-DETEKSI-RESIKO-DIABETES.git
cd PPD-KELOMPOK4-DETEKSI-RESIKO-DIABETES-master
```

### 2️⃣ Install Dependencies
```bash
# Buat virtual environment (opsional tapi disarankan)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install semua library
pip install -r requirements.txt
```

### 3️⃣ Setup API Key Gemini AI

#### **Dapatkan API Key:**
1. Kunjungi [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Login dengan akun Google
3. Klik "Create API Key" → Salin key yang dihasilkan

#### **Konfigurasi API Key:**
```bash
# Copy file template environment
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

**Edit file `.env`** dan masukkan API key Anda:
```env
GEMINI_API_KEY=AIzaSyB1234567890abcdefghijklmnopqrstuv
```

> ⚠️ **PENTING:** Jangan commit file `.env` ke repository! File ini sudah ada di `.gitignore`

### 4️⃣ Download Model (Jika Belum Ada)
Pastikan file model ada di root folder:
- `diabetes_xgboost_model.joblib` atau
- `diabetes_xgboost_model.pkl`

### 5️⃣ Run Aplikasi
```bash
streamlit run app.py
```

Aplikasi akan terbuka di browser: **http://localhost:8501**

---

## 📁 Struktur Folder

```
PPD-KELOMPOK4-DETEKSI-RESIKO-DIABETES-master/
│
├── app.py                          # Halaman utama (landing page)
├── requirements.txt                # Daftar library Python
├── .env.example                    # Template file environment
├── .env                            # API Keys (TIDAK DI-COMMIT!)
├── .gitignore                      # File yang diabaikan Git
│
├── pages/
│   ├── 1_Page_1.py                 # Visualisasi Data Survei
│   └── 2_Page_2.py                 # Prediksi Risiko Diabetes
│
├── css/
│   └── app.css                     # Custom styling
│
├── data/
│   └── diabetes_clean.csv          # Dataset BRFSS 2015
│
└── *.joblib / *.pkl                # Model Machine Learning
```

---

## 🛠️ Teknologi yang Digunakan

| Kategori | Library/Tools |
|----------|---------------|
| **Framework Web** | Streamlit |
| **Machine Learning** | XGBoost, Scikit-learn |
| **AI Generatif** | Google Gemini AI |
| **Data Processing** | Pandas, NumPy |
| **Visualisasi** | Matplotlib, Seaborn |
| **Environment** | Python-dotenv |

---

## 📊 Model Machine Learning

### Dataset
- **Sumber:** BRFSS 2015 (Behavioral Risk Factor Surveillance System)
- **Jumlah Data:** 70.692+ responden
- **Features:** 21 variabel kesehatan

### Model
- **Algoritma:** XGBoost Classifier
- **Metrics:** Accuracy ~75%, AUC-ROC ~0.85

---

## 🔐 Keamanan API Key

### ✅ Cara Aman (Sudah Diimplementasikan)
```python
# Menggunakan .env file
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
```

### ❌ JANGAN Lakukan Ini
```python
# Hard-coded key (BAHAYA!)
api_key = "AIzaSyB1234567890abcdefghijklmnopqrstuv"  # ❌
```

### 🛡️ Best Practices
- ✅ Gunakan file `.env` untuk development
- ✅ Simpan secrets di platform deployment (Streamlit Cloud: secrets.toml)
- ✅ Rotate API key secara berkala
- ✅ Set quota limits di Google Cloud Console

---

## 🌐 Deployment

### Streamlit Cloud (Gratis)
1. Push code ke GitHub
2. Buka [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect repository
4. Set secrets di **Settings → Secrets**:
   ```toml
   [secrets]
   GEMINI_API_KEY = "your_api_key_here"
   ```

---

## 📖 Cara Penggunaan

1. **Halaman Utama** → Informasi tentang sistem
2. **Page 1: Visualisasi Data** → Lihat distribusi dataset
3. **Page 2: Prediksi Risiko** → Isi form kesehatan:
   - Data demografi (usia, jenis kelamin, pendidikan)
   - Riwayat medis (tekanan darah, kolesterol, dll)
   - Gaya hidup (olahraga, merokok, pola makan)
4. Klik **"Analisis Risiko Sekarang"**
5. Dapatkan hasil prediksi + rekomendasi AI

---

## 🤝 Kontribusi

Proyek ini dikembangkan oleh **Kelompok 4** untuk mata kuliah Pengolahan dan Pemrograman Data (PPD) Program Studi Teknologi Rekayasa Perangkat Lunak Universitas Gadjah Mada.

### Tim Pengembang
- Anugrah Aidil Fitri
- Dwi Anggara Najwan Sugama
- Nuhgroh Ramadani

---

## ⚠️ Disclaimer

> Aplikasi ini hanya untuk **tujuan edukasi dan skrining awal**. Hasil prediksi TIDAK menggantikan diagnosis medis profesional. Konsultasikan dengan dokter untuk pemeriksaan lanjutan.

---

## 📞 Troubleshooting

### Error: "Module not found"
```bash
pip install -r requirements.txt
```

### Error: "API Key not found"
- Pastikan file `.env` sudah dibuat
- Cek isi file: `GEMINI_API_KEY=your_key_here`
- Restart aplikasi setelah mengubah `.env`

### Error: "Model file not found"
- Download model `.joblib` atau `.pkl` dari repository
- Letakkan di root folder project

### Gemini AI Error 429 (Quota Exceeded)
- Model menggunakan `gemini-2.0-flash-lite` untuk menghemat kuota
- Tunggu 1 menit sebelum request berikutnya
- Cek quota di [Google AI Studio](https://makersuite.google.com/)

---

## 📜 Lisensi

[Tentukan lisensi project, contoh: MIT License]

---

## 🔗 Links

- **Repository:** https://github.com/nuhgroh2004/PPD-KELOMPOK4-DETEKSI-RESIKO-DIABETES
- **Dataset:** [BRFSS 2015](https://www.cdc.gov/brfss/annual_data/annual_2015.html)
- **Gemini AI:** https://ai.google.dev/

---

**⭐ Jangan lupa star repository ini jika bermanfaat!**
