# CRYPTOVAULT – Hasil Tahap 1: Finalisasi Arsitektur

## Aturan 3-Layer
- Presentation (PySide6): hanya UI, memanggil Service. Tanpa SQL dan tanpa algoritma kripto.
- Business Logic: semua algoritma kripto dan aturan bisnis. Tanpa import PySide6.
- Data Access: CRUD dengan parameterized query dan File Storage. Tidak mengenkripsi.
- Alur searah: Presentation -> Business -> Data Access.
- Operasi lambat (Argon2id, file besar, Windows Hello) dijalankan lewat QThread worker di Presentation.

## Alur Autentikasi (Opsi A)
1. Deteksi USB (psutil), baca `dongle_id` dari `cryptovault.key`.
2. Ambil public key dari DB, buat challenge acak 32 byte, dongle menandatangani (Ed25519), verifikasi.
3. Input username + password, verifikasi Argon2id, cek is_active, cek dongle milik user tsb.
4. Windows Hello (UserConsentVerifier).
5. Buat session (user_id, role) lalu masuk Dashboard. Semua langkah dicatat di audit_logs.
Pesan gagal dibuat generik.

## Database (8 tabel spesifikasi + penyesuaian)
users, dongle_registrations, encryption_keys, messages, files, images, blockchain_blocks, audit_logs.
Tambahan/penyesuaian:
- Tabel baru `vault_entries` (entry_id, user_id, key_id, label, ciphertext, nonce, auth_tag, created_at) untuk Database Vault.
- `messages.kdf_salt` untuk menurunkan kunci AES dari kunci input pengguna. Kunci Vigenere tidak disimpan.
- `users.last_login_at`, `users.failed_attempts`; `role` ENUM('admin','user','auditor').
- `files`: original_filename, file_size, chunk_size.
- `blockchain_blocks.created_at` DATETIME(6) dengan format string konsisten; penambahan blok memakai transaksi SELECT ... FOR UPDATE.
- `audit_logs.user_id` boleh NULL (login gagal).

## Key Management (envelope encryption)
MASTER_KEK di `.env` membungkus DEK (AES-256-GCM). DEK terbungkus disimpan di `encryption_keys.wrapped_key`.
DEK dipisah per tujuan.

## Risiko dan Keterbatasan
- USB flashdisk biasa bukan hardware security token; private key bisa disalin. Mitigasi: private key terenkripsi (Argon2id + AES-GCM), challenge acak sekali pakai, dongle bisa dinonaktifkan.
- Windows Hello: bergantung perangkat; API tidak membedakan biometrik dari PIN; aplikasi desktop mungkin butuh HWND interop; mode simulasi harus berlabel jelas.
- Hash-chain: pemegang akses tulis DB bisa menghitung ulang rantai; mitigasi anchor HMAC.
- ChaCha20-Poly1305 tidak streaming di library: file dipecah per chunk (1 MiB) dengan nonce turunan dan penanda chunk terakhir.
- LSB hanya penyembunyian; kerahasiaan dari AES-GCM.

## Roadmap
1 Analisis | 2 Inisialisasi | 3 Database | 4 GUI | 5 Autentikasi | 6 Kriptografi | 7 Steganografi | 8 Blockchain | 9 Integrasi | 10 Testing
