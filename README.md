# SecureVault
**Rancang Bangun Aplikasi Brankas Digital Berbasis Desktop dengan Integrasi Super Enkripsi, Steganografi, dan Blockchain Sederhana untuk Pengamanan Data.**

Python 3.12 · CustomTkinter · SQLite · Argon2id · Vigenere + AES-256-GCM · Fernet · LSB (Pillow) · Hash chain SHA-256

## 1. Cara Menjalankan (Windows 10/11 + VS Code)
```powershell
cd SecureVault
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
Di VS Code: `Ctrl+Shift+P` → *Python: Select Interpreter* → pilih `venv`.

## 2. Alur Pemakaian
1. **Registrasi**: colok flashdisk, klik *Registrasi Akun Baru*, isi data, pilih drive. File `donggle_key.dat` (kunci privat Ed25519) ditulis ke flashdisk.
2. **Verifikasi Donggle**: challenge-response acak, ditandatangani donggle, diverifikasi dengan kunci publik di database.
3. **Login**: username + password (Argon2id). Donggle harus milik akun tersebut.
4. **Windows Hello**: autentikasi OS (UserConsentVerifier).
5. **Dashboard** dan seluruh fitur.

## 3. Arsitektur Kunci
```
password --Argon2id(+salt)--> KEK --membuka--> wrapped_vmk (DB) --> VMK (hanya di RAM)
VMK --HKDF--> key_text | key_db | key_file | key_stego
```
Tidak ada master key di source code maupun database. Ganti password cukup membungkus ulang VMK.

## 4. Struktur Proyek
```
main.py            titik masuk
core/              config, session, auth_service, donggle, windows_hello, services
crypto/            vigenere, aes_gcm, super_text, fernet_file, kdf, errors
database/          db (skema SQLite), repository (semua query)
steganography/     lsb
blockchain/        block, chain
ui/                app, theme, widgets, pages_auth, shell, page_*.py
tests/             pytest (crypto, stego, blockchain, auth)
data/              database & output (di-ignore Git)
```

## 5. Menjalankan Pengujian
```powershell
pytest -q
```
Mencakup: vektor uji Vigenere, AES-GCM (nonce unik, tamper, kunci salah), Fernet, LSB, hash chain (deteksi perubahan), registrasi/login/donggle palsu, ganti password, dan memastikan database hanya berisi ciphertext.

## 6. Mode Pengembangan (tanpa flashdisk / tanpa Windows Hello)
Hanya untuk latihan/testing, **jangan dipakai saat demo final**:
```powershell
$env:SECUREVAULT_DONGGLE_DIR="C:\fake_usb"   # folder dianggap flashdisk
$env:SECUREVAULT_SKIP_HELLO="1"              # lewati Windows Hello
python main.py
```

## 7. Demo Deteksi Perubahan Blockchain
Ubah satu blok langsung di database, lalu klik *Verifikasi Integritas*:
```powershell
python -c "import sqlite3;c=sqlite3.connect('data/securevault.db');c.execute(\"UPDATE blockchain_records SET data='DIUBAH' WHERE block_index=2\");c.commit()"
```

## 8. Pembagian Tugas
| Anggota | Modul |
|---|---|
| 1 | `core/auth_service.py`, `donggle.py`, `windows_hello.py`, `session.py`, `crypto/kdf.py` |
| 2 | `crypto/`, `database/` |
| 3 | `ui/`, `steganography/`, `blockchain/`, integrasi |

Branch: `main` (stabil) ← `develop` ← `feature/auth`, `feature/crypto`, `feature/gui`. Jangan commit `data/`, `*.db`, `donggle_key.dat`, `venv/`.

## 9. Keterbatasan (untuk laporan)
- **Vigenere** hanya untuk pembelajaran kriptografi klasik, bukan perlindungan utama. Keamanan berasal dari AES-256-GCM.
- **Blockchain** adalah hash chain lokal; tidak ada konsensus/node. Pihak dengan akses penuh DB dapat menghitung ulang seluruh rantai.
- **Fernet** memproses seluruh file di RAM (batas 200 MB di `core/config.py`).
- **Donggle**: kunci privat di flashdisk tidak dienkripsi passphrase (verifikasi dilakukan sebelum login). Siapa pun yang menyalin file kunci *dan* tahu password dapat masuk. Peningkatan: enkripsi kunci donggle dengan PIN terpisah.
- **Windows Hello** adalah gerbang akses, bukan sumber kunci enkripsi.
- Lupa password = data tidak dapat dipulihkan (konsekuensi desain).
- **Steganografi**: gambar RGBA diubah ke RGB (alpha dibuang). Hasil stego harus disimpan/dikirim sebagai PNG tanpa kompresi ulang.
