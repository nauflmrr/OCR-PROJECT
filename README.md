📚 TUTORIAL PENGGUNAAN OCR APPLICATION
-----
⚡ Instalasi Cepat (5 Menit)
Step 1: Install Python
1. Download dari python.org
2. WAJIB: Centang "Add Python to PATH"
3. Verifikasi: python --version (harus muncul versi)

Step 2: Install Tesseract OCR
# Download dari: https://github.com/UB-Mannheim/tesseract/wiki
# Jalankan installer, pilih "Indonesian" language

Step 3: Download Aplikasi
# Pilih salah satu:
# 1. Clone dari GitHub
git clone https://github.com/username/OCR-Project.git

# 2. Download ZIP
#    - Buka GitHub repository
#    - Klik "Code" → "Download ZIP"
#    - Extract file

Step 4: Install Dependencies
# Masuk ke folder aplikasi
cd OCR-Project

# Install package Python
pip install -r requirements.txt
# Atau:
pip install pytesseract Pillow
-----
🖥️ Cara Menjalankan GUI Mode
Langkah 1: Buka Aplikasi
python main.py

Langkah 2: Tampilan GUI
┌─────────────────────────────────────┐
│        OCR APPLICATION             │
├─────────────────────────────────────┤
│ [📁 Open Image]  [🔄 Preprocess]   │
│ [🔍 Extract Text] [💾 Save]       │
│                                     │
│  ┌─────────────┐ ┌─────────────┐   │
│  │  Original   │ │ Processed   │   │
│  │   Image     │ │   Image     │   │
│  └─────────────┘ └─────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │      Hasil Teks OCR         │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘

Langkah 3: Step-by-Step Penggunaan GUI
1. Buka Gambar:
> Klik tombol "Open Image"
> Pilih file gambar (JPG, PNG, BMP, TIFF)
> Gambar akan muncul di kotak "Original Image"

2. Preprocess (Opsional):
> Klik "Preprocess Image" untuk meningkatkan kualitas
> Hasil preprocessing muncul di "Processed Image"
> Kapan perlu preprocessing? Jika gambar buram/low quality

3. Pilih Bahasa:
> Pilih dari dropdown: Indonesian atau English
> Default: Indonesian

4. Ekstrak Teks:
> Klik "Extract Text"
> Tunggu 1-5 detik
> Hasil muncul di textbox bawah

5. Simpan Hasil:
> Klik "Save"
> Pilih nama file (contoh: hasil_ocr.txt)
> Teks tersimpan!

-----
⌨️ Cara Menggunakan CLI Mode
1. Mode Interaktif (Menu)
python main.py --cli

Output:
🔍 OCR APPLICATION - TEXT MODE
📱 MAIN MENU:
1. Process single image
2. Create and process sample image
3. Test OCR engine
4. Check Tesseract installation
5. Exit

Select option (1-5):

2. Process Gambar Tunggal
# Format dasar
python cli_app.py gambar.jpg --language indonesian

# Contoh lengkap
python cli_app.py invoice.jpg --language ind --preprocess --output hasil.txt

# Opsi:
#   --language ind/eng      : Pilih bahasa
#   --preprocess            : Preprocessing gambar
#   --output nama_file      : Simpan ke file
#   --verbose               : Tampilkan detail
-----
🖼️ Pemrosesan Gambar Tunggal
Format Gambar yang Didukung:
✅ JPG/JPEG (.jpg, .jpeg)

✅ PNG (.png)

✅ BMP (.bmp)

✅ TIFF (.tiff)

❌ PDF (harus convert ke gambar dulu)
