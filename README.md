# CRYPTOVAULT – Secure Digital Vault Application

Aplikasi desktop (PySide6) untuk menyimpan dan melindungi pesan serta berkas digital
dengan kombinasi kriptografi klasik dan modern. Proyek akhir mata kuliah Kriptografi.

**Status:** Tahap 1 selesai (kerangka proyek). Belum ada kode fitur.

## Arsitektur
3-Layer: Presentation -> Business Logic -> Data Access -> MySQL / File Storage.
Detail lengkap: `docs/TAHAP1_ARSITEKTUR.md`.

## Persiapan cepat (Windows, PowerShell)
```powershell
python --version          # harus 3.12.x
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env    # lalu isi nilai di .env
```
