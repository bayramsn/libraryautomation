import os
import django
import requests
from io import BytesIO
from django.core.files.base import ContentFile
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')
django.setup()

from library.models import Book, Author, Category
from django.utils import timezone

# Kategori oluştur
classics_category, created = Category.objects.get_or_create(
    name="Dünya Klasikleri",
    defaults={"description": "Dünya edebiyatının en önemli klasik eserleri."}
)

# Kitap bilgileri
classic_books = [
    {
        "title": "Suç ve Ceza",
        "author": {
            "name": "Fyodor Dostoyevski",
            "birth_date": "1821-11-11",
            "biography": "Rus yazar ve düşünür. Psikolojik derinliği olan romanlarıyla tanınır."
        },
        "isbn": "9789750719387",
        "publication_date": "1866-01-01",
        "description": "Raskolnikov adlı yoksul bir öğrencinin işlediği cinayet ve sonrasında yaşadığı psikolojik çöküşü anlatan roman.",
        "page_count": 687,
        "language": "Türkçe",
        "publisher": "İş Bankası Kültür Yayınları",
        "cover_image_url": "https://i.dr.com.tr/cache/600x600-0/originals/0000000064552-1.jpg"
    },
    {
        "title": "Sefiller",
        "author": {
            "name": "Victor Hugo",
            "birth_date": "1802-02-26",
            "biography": "Fransız yazar, şair ve politikacı. Romantik akımın öncülerinden."
        },
        "isbn": "9789750738609",
        "publication_date": "1862-01-01",
        "description": "Jean Valjean'ın hikayesi üzerinden 19. yüzyıl Fransa'sındaki sosyal adaletsizliği anlatan epik roman.",
        "page_count": 1724,
        "language": "Türkçe",
        "publisher": "İş Bankası Kültür Yayınları",
        "cover_image_url": "https://i.dr.com.tr/cache/600x600-0/originals/0001788076001-1.jpg"
    },
    {
        "title": "Anna Karenina",
        "author": {
            "name": "Lev Tolstoy",
            "birth_date": "1828-09-09",
            "biography": "Rus yazar. Gerçekçi edebiyatın en önemli temsilcilerinden biri."
        },
        "isbn": "9789750726477",
        "publication_date": "1877-01-01",
        "description": "Evli bir kadın olan Anna Karenina'nın yasak aşkı ve trajik sonunu anlatan roman.",
        "page_count": 864,
        "language": "Türkçe",
        "publisher": "İş Bankası Kültür Yayınları",
        "cover_image_url": "https://i.dr.com.tr/cache/600x600-0/originals/0000000411546-1.jpg"
    },
    {
        "title": "Madame Bovary",
        "author": {
            "name": "Gustave Flaubert",
            "birth_date": "1821-12-12",
            "biography": "Fransız yazar. Gerçekçi edebiyatın öncülerinden."
        },
        "isbn": "9789750741449",
        "publication_date": "1857-01-01",
        "description": "Taşrada yaşayan bir doktorun karısı olan Emma Bovary'nin romantik hayalleri ve aldatmaları üzerine bir roman.",
        "page_count": 329,
        "language": "Türkçe",
        "publisher": "İş Bankası Kültür Yayınları",
        "cover_image_url": "https://i.dr.com.tr/cache/600x600-0/originals/0001704045001-1.jpg"
    },
    {
        "title": "Don Kişot",
        "author": {
            "name": "Miguel de Cervantes",
            "birth_date": "1547-09-29",
            "biography": "İspanyol yazar. Modern romanın kurucusu olarak kabul edilir."
        },
        "isbn": "9789750726019",
        "publication_date": "1605-01-01",
        "description": "Şövalye romanlarından etkilenerek kendini şövalye sanan bir adamın maceralarını anlatan roman.",
        "page_count": 1077,
        "language": "Türkçe",
        "publisher": "İş Bankası Kültür Yayınları",
        "cover_image_url": "https://i.dr.com.tr/cache/600x600-0/originals/0000000105409-1.jpg"
    },
    {
        "title": "Bülbülü Öldürmek",
        "author": {
            "name": "Harper Lee",
            "birth_date": "1926-04-28",
            "biography": "Amerikalı yazar. Pulitzer ödüllü tek romanıyla tanınır."
        },
        "isbn": "9789750738746",
        "publication_date": "1960-07-11",
        "description": "1930'ların Amerika'sında ırkçılık ve adaletsizliği bir çocuğun gözünden anlatan roman.",
        "page_count": 360,
        "language": "Türkçe",
        "publisher": "İş Bankası Kültür Yayınları",
        "cover_image_url": "https://i.dr.com.tr/cache/600x600-0/originals/0001788075001-1.jpg"
    },
    {
        "title": "Gurur ve Önyargı",
        "author": {
            "name": "Jane Austen",
            "birth_date": "1775-12-16",
            "biography": "İngiliz yazar. Romantik dönem edebiyatının önemli isimlerinden."
        },
        "isbn": "9789750726538",
        "publication_date": "1813-01-28",
        "description": "Elizabeth Bennet ve Bay Darcy arasındaki ilişkiyi konu alan, 19. yüzyıl İngiltere'sinin sosyal yapısını eleştiren roman.",
        "page_count": 424,
        "language": "Türkçe",
        "publisher": "İş Bankası Kültür Yayınları",
        "cover_image_url": "https://i.dr.com.tr/cache/600x600-0/originals/0000000105331-1.jpg"
    },
    {
        "title": "Fareler ve İnsanlar",
        "author": {
            "name": "John Steinbeck",
            "birth_date": "1902-02-27",
            "biography": "Amerikalı yazar. Nobel Edebiyat Ödülü sahibi."
        },
        "isbn": "9789750726101",
        "publication_date": "1937-01-01",
        "description": "Büyük Buhran döneminde Kaliforniya'da çalışan iki göçmen tarım işçisinin dostluğunu anlatan novella.",
        "page_count": 111,
        "language": "Türkçe",
        "publisher": "İş Bankası Kültür Yayınları",
        "cover_image_url": "https://i.dr.com.tr/cache/600x600-0/originals/0000000064031-1.jpg"
    },
    {
        "title": "Dönüşüm",
        "author": {
            "name": "Franz Kafka",
            "birth_date": "1883-07-03",
            "biography": "Çek asıllı Alman yazar. 20. yüzyıl edebiyatının en önemli isimlerinden."
        },
        "isbn": "9789750726132",
        "publication_date": "1915-01-01",
        "description": "Gregor Samsa'nın bir sabah dev bir böceğe dönüşmesiyle başlayan absürt hikaye.",
        "page_count": 74,
        "language": "Türkçe",
        "publisher": "İş Bankası Kültür Yayınları",
        "cover_image_url": "https://i.dr.com.tr/cache/600x600-0/originals/0000000064062-1.jpg"
    },
    {
        "title": "Uğultulu Tepeler",
        "author": {
            "name": "Emily Brontë",
            "birth_date": "1818-07-30",
            "biography": "İngiliz yazar ve şair. Tek romanıyla edebiyat tarihine geçmiştir."
        },
        "isbn": "9789750738685",
        "publication_date": "1847-12-01",
        "description": "Catherine Earnshaw ve Heathcliff arasındaki tutkulu ve yıkıcı aşkı anlatan gotik roman.",
        "page_count": 376,
        "language": "Türkçe",
        "publisher": "İş Bankası Kültür Yayınları",
        "cover_image_url": "https://i.dr.com.tr/cache/600x600-0/originals/0001788074001-1.jpg"
    }
]

# Kitapları ekle
for book_data in classic_books:
    # Yazar oluştur veya al
    author_data = book_data.pop('author')
    birth_date = datetime.strptime(author_data['birth_date'], '%Y-%m-%d').date() if author_data.get('birth_date') else None
    
    author, created = Author.objects.get_or_create(
        name=author_data['name'],
        defaults={
            'biography': author_data.get('biography', ''),
            'birth_date': birth_date
        }
    )
    
    # Kitap kapak resmi URL'sini al
    cover_image_url = book_data.pop('cover_image_url', None)
    
    # Kitabı oluştur veya güncelle
    book, created = Book.objects.get_or_create(
        isbn=book_data['isbn'],
        defaults={
            'title': book_data['title'],
            'publication_date': datetime.strptime(book_data['publication_date'], '%Y-%m-%d').date(),
            'description': book_data['description'],
            'page_count': book_data['page_count'],
            'language': book_data['language'],
            'publisher': book_data['publisher'],
            'category': classics_category,
            'available_copies': 3,  # Her kitaptan 3 kopya
            'total_copies': 3
        }
    )
    
    # Yazarı ekle
    book.authors.add(author)
    
    # Kapak resmini indir ve ekle
    if cover_image_url and created:
        try:
            response = requests.get(cover_image_url)
            if response.status_code == 200:
                book.cover_image.save(
                    f"{book.isbn}_cover.jpg",
                    ContentFile(response.content),
                    save=True
                )
                print(f"Kapak resmi eklendi: {book.title}")
            else:
                print(f"Kapak resmi indirilemedi: {book.title}")
        except Exception as e:
            print(f"Hata: {e}")
    
    print(f"Kitap {'oluşturuldu' if created else 'güncellendi'}: {book.title}")

print("Dünya klasikleri kitapları başarıyla eklendi!") 