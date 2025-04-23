# Kütüphane Otomasyonu

Bu proje, bir kütüphane için kitap yönetimi, üye yönetimi, ödünç verme ve rezervasyon işlemlerini yönetmek için geliştirilmiş bir web uygulamasıdır.

## Özellikler

- Kitap yönetimi (ekleme, düzenleme, silme)
- Yazar ve kategori yönetimi
- Üye yönetimi
- Kitap ödünç verme ve iade işlemleri
- Kitap rezervasyon sistemi
- Gecikme cezaları
- Arama ve filtreleme özellikleri
- Kullanıcı profil yönetimi

## Teknolojiler

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Veritabanı:** SQLite (Geliştirme), PostgreSQL (Üretim için önerilen)
- **Diğer:** Font Awesome, AJAX

## Kurulum

1. Projeyi klonlayın:
   ```
   git clone https://github.com/kullanici/library_automation.git
   cd library_automation
   ```

2. Sanal ortam oluşturun ve etkinleştirin:
   ```
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Gerekli paketleri yükleyin:
   ```
   pip install -r requirements.txt
   ```

4. Veritabanı migrasyonlarını uygulayın:
   ```
   python manage.py migrate
   ```

5. Süper kullanıcı oluşturun:
   ```
   python manage.py createsuperuser
   ```

6. Geliştirme sunucusunu başlatın:
   ```
   python manage.py runserver
   ```

7. Tarayıcınızda `http://127.0.0.1:8000` adresine gidin.

## Veritabanı Şeması

Proje aşağıdaki ana modelleri içerir:

- **Author:** Yazarlar
- **Category:** Kitap kategorileri
- **Book:** Kitaplar
- **Member:** Kütüphane üyeleri
- **Loan:** Ödünç verme işlemleri
- **Reservation:** Rezervasyon işlemleri
- **Fine:** Gecikme cezaları

## Kullanım

### Admin Paneli

- `/admin` URL'sini kullanarak admin paneline erişebilirsiniz.
- Admin panelinden kitap, yazar, kategori, üye, ödünç verme ve rezervasyon işlemlerini yönetebilirsiniz.

### Kullanıcı Arayüzü

- Ana sayfa: Kitapları ve kategorileri görüntüleyin
- Kitaplar sayfası: Tüm kitapları listeleyin ve arayın
- Kitap detay sayfası: Kitap bilgilerini görüntüleyin, ödünç alın veya rezerve edin
- Profil sayfası: Kişisel bilgilerinizi ve ödünç aldığınız kitapları görüntüleyin

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakın.

## İletişim

Sorularınız veya önerileriniz için [email@example.com](mailto:email@example.com) adresine e-posta gönderebilirsiniz. 