# 🖼️ OCR (Optical Character Recognition) Application  
**Python-Based OCR with GUI and CLI Support**

## 📖 Daftar Isi
1. [Deskripsi Proyek](#-deskripsi-proyek)
2. [Fitur Utama](#-fitur-utama)
3. [Teknologi yang Digunakan](#-teknologi-yang-digunakan)
4. [Instalasi dan Setup](#-instalasi-dan-setup)
5. [Cara Menjalankan](#-cara-menjalankan)
6. [Struktur Proyek](#-struktur-proyek)
7. [Penggunaan Aplikasi](#-penggunaan-aplikasi)
8. [Troubleshooting](#-troubleshooting)
9. [Untuk Laporan/Karya Ilmiah](#-untuk-laporankarya-ilmiah)
10. [Lisensi](#-lisensi)

---

## 🎯 Deskripsi Proyek

Aplikasi OCR (Optical Character Recognition) ini dikembangkan menggunakan Python untuk mengonversi teks dalam gambar menjadi teks digital yang dapat diedit. Aplikasi mendukung pemrosesan gambar, ekstraksi teks multi-bahasa, serta tersedia dalam dua mode: **GUI (Graphical User Interface)** dan **CLI (Command Line Interface)**.

### **Tujuan Pengembangan:**
1. Membangun sistem OCR yang dapat mengenali teks bahasa Indonesia dan Inggris
2. Mengimplementasikan preprocessing gambar untuk meningkatkan akurasi OCR
3. Membuat antarmuka pengguna yang mudah digunakan (GUI dan CLI)
4. Mendukung eksekusi di berbagai platform (local, cloud, GitHub Codespaces)

---

## ✨ Fitur Utama

### ✅ **Core Features:**
- **Multi-language OCR**: Mendukung bahasa Indonesia, Inggris, dan lainnya
- **Image Preprocessing**: Grayscale conversion, thresholding, noise removal
- **Dual Interface**: GUI (Tkinter) dan CLI untuk berbagai kebutuhan
- **Batch Processing**: Dapat memproses multiple gambar sekaligus
- **Export Results**: Simpan hasil dalam format TXT, JSON, atau CSV

### ✅ **Platform Support:**
- **Local Desktop**: Jalankan dengan GUI di Windows/Mac/Linux
- **GitHub Codespaces**: Jalankan di browser tanpa instalasi
- **Headless Server**: Dapat berjalan di environment tanpa display

### ✅ **User Experience:**
- Preview gambar sebelum dan sesudah preprocessing
- Statistik akurasi OCR (confidence level)
- History pemrosesan
- Auto-save hasil

---

## 🛠️ Teknologi yang Digunakan

### **Core Technologies:**
| Teknologi | Versi | Fungsi |
|-----------|-------|---------|
| **Python** | 3.7+ | Bahasa pemrograman utama |
| **Tesseract OCR** | 5.0+ | Engine pengenalan teks |
| **PIL (Pillow)** | 10.0+ | Image processing tanpa OpenCV |
| **Tkinter** | 8.6+ | GUI framework (built-in Python) |

### **Dependencies:**
```txt
pytesseract==0.3.10      # Python wrapper untuk Tesseract
Pillow==10.1.0           # Image processing library
numpy==1.26.3            # Array operations (opsional)
