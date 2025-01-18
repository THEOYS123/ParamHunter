# *Pemberitahuan Penting Mengenai Filter❗*

- **Filter `-af` (Admin Finder):**  
  Filter ini masih dalam tahap pengembangan dan perbaikan, sehingga kurang efektif untuk digunakan. Tim pengembang sedang berusaha meningkatkan akurasi dan efisiensinya.  

- **Filter `-pr` (Parameter Rentan):**  
  Filter ini juga belum sepenuhnya efisien untuk digunakan dan saat ini sedang dalam proses perbaikan agar dapat memberikan hasil yang lebih optimal.  

Terima kasih atas pengertiannya! Saya RenXploit akan terus memberikan pembaruan untuk meningkatkan kinerja script ini.

# Terminal Hacking

```bash
$ git clone https://github.com/THEOYS123/ParamHunter.git
$ cd ParamHunter
$ python3 start.py

# ParamHunter 🚀  
**ParamHunter** adalah script crawler berbasis Python yang dirancang untuk membantu menganalisis dan memindai website dengan fitur lengkap seperti pencarian halaman admin, parameter rentan, serta filter random otomatis. Tool ini sangat berguna untuk keperluan **pentesting legal**.  
```
---

![Hacker Terminal Background](https://www.wallpaperbetter.com/wallpaper/784/914/979/green-matrix-code-wallpaper-1080x1920.jpg)

## ✨ **Fitur Utama**  
1. **Crawling URL Otomatis** 🔍  
   - Memindai semua link internal dalam website target.  
   - Mendukung filter berdasarkan ekstensi file (contoh: `.php`, `.json`, `.html`).  

2. **Filter Random** 🎲  
   - Menambahkan filter random otomatis untuk mencari file tersembunyi.  
   - Contoh: `/X2dRpY.xml`, `/5hj3tQ.jsp`.  

3. **Admin Finder** 🛡️  
   - Mencari halaman admin dengan path umum seperti:  
     `/admin`, `/wp-admin`, `/cpanel`, `/administrator`.  

4. **Pencarian Parameter Rentan** ⚠️  
   - Mendeteksi parameter yang sering menjadi celah keamanan seperti:  
     `?id=`, `?page=`, `?search=`.  

5. **Hasil Terkelompok** 📊  
   - Hasil crawling akan dikelompokkan berdasarkan filter, sehingga lebih rapi dan mudah dibaca.  

6. **Random User-Agent & Anti-Block** 🌀  
   - Menggunakan `User-Agent` acak untuk menghindari deteksi server.  
   - Mendukung retry otomatis jika terkena **403 Forbidden**.  

7. **Handling Ctrl+C** 🛑  
   - Jika proses dihentikan paksa, script tetap menampilkan hasil yang sudah ditemukan.  

---

## 🛠️ **Instalasi & Persiapan**  
1. Clone repository ini:  
   ```bash
   pip install argparse requests beautifulsoup4 rich
   pip install python
   pkg update
   pkg upgrade
   pkg update && pkg upgrade
   git clone https://github.com/THEOYS123/ParamHunter.git
   cd ParamHunter
   python param.py -h
   
2. Pastikan Python 3.x terinstal di perangkat kamu.
3. udah lah langsung aja pake script nya nih udah di jelasin juga cara install nya jadi jangan bingung anjer jangan pada nanya cara pake nya nih udah gw jelasin cokkkkkkk



---

## 🛠️ **update script**  
1. Update repository ini:
```
   git pull
   cd ParamHunter
   python param.py -h
```

---
⚙️ Cara Penggunaan

1. Basic Crawling
Crawling semua link di website dengan filter tertentu:

python param.py https://example.com -f .php .html .json

2. Filter Random Otomatis
Menggunakan filter random tanpa memasukkan filter manual:

python param.py https://example.com -random

3. Admin Finder
Mencari halaman admin dalam website:

python param.py https://example.com -af

4. Pencarian Parameter Rentan
Mendeteksi parameter rentan seperti ?id=:

python param.py https://example.com -pr

5. Kombinasi Fitur
Menggabungkan admin finder, parameter rentan, dan filter random:

python param.py https://example.com -random -af -pr


# *📸screenshot 📸*

<p align="center">
  <a href="https://f.top4top.io/p_3305ofiqh7.jpg">
    <img src="https://f.top4top.io/p_3305ofiqh7.jpg" width="300"/>
  </a>
</p>


---

📌 Catatan Penting

Gunakan script ini hanya untuk keperluan legal! 🚫

Pastikan kamu memiliki izin untuk menguji website target.

Semua aktivitas yang dilakukan menggunakan script ini adalah tanggung jawab pengguna sepenuhnya.



---

💬 Kontribusi

Kamu punya ide atau ingin berkontribusi? Jangan ragu untuk membuat pull request atau laporkan masalah melalui Issues.


---

✍️ Penulis

Script ini dibuat dengan semangat oleh REN-XPLOIT.

[Klik disini untuk mengunjungi whatsapp saya](https://wa.me/62895365187210)
