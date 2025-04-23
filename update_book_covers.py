import os
import sys
import django
import requests
import time
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings

# Django ayarlarını yükle
# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')
django.setup()

from library.models import Book

# Kitap kapak fotoğrafları için API
# APIs for book cover images
GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes?q=intitle:{title}&maxResults=1"
OPEN_LIBRARY_API = "https://openlibrary.org/search.json?title={title}&limit=1"

def get_cover_from_google_books(title):
    """
    Google Books API'den kitap kapak fotoğrafını al
    Kitap başlığına göre arama yapar ve varsa kapak fotoğrafı URL'sini döndürür
    
    Get book cover image from Google Books API
    Searches by book title and returns cover image URL if available
    """
    try:
        # Başlığı temizle ve URL için hazırla
        # Clean title and prepare for URL
        search_title = title.replace(' ', '+').replace(':', '')
        
        # Önce tam başlıkla ara
        # First search with exact title
        url = GOOGLE_BOOKS_API.format(title=search_title)
        print(f"  Google Books API sorgusu: {url}")
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'items' in data and len(data['items']) > 0:
            volume_info = data['items'][0].get('volumeInfo', {})
            image_links = volume_info.get('imageLinks', {})
            
            # Yüksek çözünürlüklü kapak fotoğrafını al
            # Get high resolution cover image
            if 'thumbnail' in image_links:
                # Daha büyük boyut için URL'yi değiştir
                # Change URL for larger size
                cover_url = image_links['thumbnail'].replace('zoom=1', 'zoom=2')
                return cover_url
            
        # Tam başlıkla bulunamadıysa, başlığın ilk birkaç kelimesiyle dene
        # If not found with exact title, try with first few words
        if ' ' in title:
            words = title.split(' ')
            if len(words) > 2:
                short_title = ' '.join(words[:2])  # İlk iki kelime / First two words
                return get_cover_from_google_books(short_title)
                
    except Exception as e:
        print(f"  Google Books API hatası: {str(e)}")
    
    return None

def get_cover_from_open_library(title):
    """
    Open Library API'den kitap kapak fotoğrafını al
    Kitap başlığına göre arama yapar ve varsa kapak fotoğrafı URL'sini döndürür
    
    Get book cover image from Open Library API
    Searches by book title and returns cover image URL if available
    """
    try:
        # Başlığı temizle ve URL için hazırla
        # Clean title and prepare for URL
        search_title = title.replace(' ', '+').replace(':', '')
        
        # Önce tam başlıkla ara
        # First search with exact title
        url = OPEN_LIBRARY_API.format(title=search_title)
        print(f"  Open Library API sorgusu: {url}")
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'docs' in data and len(data['docs']) > 0:
            doc = data['docs'][0]
            if 'cover_i' in doc:
                cover_id = doc['cover_i']
                # Büyük boyutlu kapak fotoğrafı URL'si
                # Large size cover image URL
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                return cover_url
                
        # Tam başlıkla bulunamadıysa, başlığın ilk birkaç kelimesiyle dene
        # If not found with exact title, try with first few words
        if ' ' in title:
            words = title.split(' ')
            if len(words) > 2:
                short_title = ' '.join(words[:2])  # İlk iki kelime / First two words
                return get_cover_from_open_library(short_title)
                
    except Exception as e:
        print(f"  Open Library API hatası: {str(e)}")
    
    return None

def download_image(url):
    """
    URL'den resmi indir ve PIL Image nesnesine dönüştür
    Hata durumunda None döndürür
    
    Download image from URL and convert to PIL Image object
    Returns None in case of error
    """
    try:
        # URL'yi temizle ve boşlukları kaldır
        # Clean URL and remove spaces
        url = url.strip()
        
        # Amazon URL'lerini düzelt (+ işaretleri sorun çıkarabilir)
        # Fix Amazon URLs (+ signs can cause problems)
        if 'amazon.com' in url:
            url = url.replace('+', '%2B')
        
        print(f"  İndiriliyor: {url}")
        response = requests.get(url, stream=True, timeout=10)
        
        if response.status_code == 200:
            try:
                img = Image.open(BytesIO(response.content))
                
                # Eğer resim RGB modunda değilse, dönüştür
                # Convert to RGB mode if not already
                if img.mode != 'RGB':
                    print(f"  Resim modu dönüştürülüyor: {img.mode} -> RGB")
                    img = img.convert('RGB')
                
                return img
            except Exception as e:
                print(f"  Resim açma hatası: {str(e)}")
                return None
        else:
            print(f"  HTTP hatası: {response.status_code}")
            return None
    except Exception as e:
        print(f"  Resim indirme hatası: {str(e)}")
        return None

def update_book_cover(book, image):
    """
    Kitap kapak fotoğrafını güncelle
    Eski kapak fotoğrafını siler ve yenisini kaydeder
    
    Update book cover image
    Deletes old cover image and saves new one
    """
    try:
        # Resmi BytesIO nesnesine kaydet
        # Save image to BytesIO object
        output = BytesIO()
        
        try:
            # Resmi JPEG formatında kaydet
            # Save image in JPEG format
            image.save(output, format='JPEG', quality=85)
            output.seek(0)
        except Exception as e:
            print(f"  Resim kaydetme hatası: {str(e)}")
            # PNG formatında deneyebiliriz
            # We can try PNG format
            try:
                output = BytesIO()
                image.save(output, format='PNG')
                output.seek(0)
                print("  JPEG yerine PNG formatında kaydedildi")
            except Exception as e2:
                print(f"  PNG formatında da kaydetme hatası: {str(e2)}")
                return False
        
        # Eski kapak fotoğrafını sil
        # Delete old cover image
        if book.cover_image:
            try:
                old_path = book.cover_image.path if book.cover_image else None
                if old_path and os.path.exists(old_path):
                    os.remove(old_path)
                    print(f"  Eski kapak silindi: {old_path}")
            except Exception as e:
                print(f"  Eski kapak silme hatası (devam ediliyor): {str(e)}")
        
        # Yeni kapak fotoğrafını kaydet
        # Save new cover image
        filename = f"{book.id}_{book.title.replace(' ', '_')[:30]}.jpg"
        book.cover_image.save(filename, ContentFile(output.read()), save=True)
        print(f"  Yeni kapak kaydedildi: {filename}")
        
        return True
    except Exception as e:
        print(f"  Kapak güncelleme hatası: {str(e)}")
        return False

def main():
    """
    Ana fonksiyon
    Tüm kitapları işler ve kapak fotoğraflarını günceller
    
    Main function
    Processes all books and updates cover images
    """
    # Güncellenecek kitapları seç
    # Select books to update
    books = Book.objects.all()
    print(f"Toplam {len(books)} kitap işlenecek.")
    
    # Klasik kitaplar ve popüler kitaplar için özel kapak fotoğrafları
    # Special cover images for classic and popular books
    special_covers = {
        "A Christmas Carol": "https://images-na.ssl-images-amazon.com/images/I/81YPueTY+kL.jpg",
        "A Study in Scarlet": "https://images-na.ssl-images-amazon.com/images/I/71cGJhVV9QL.jpg",
        "A Tale of Two Cities": "https://images-na.ssl-images-amazon.com/images/I/81kz-JSHGFL.jpg",
        "Adventures of Huckleberry Finn": "https://images-na.ssl-images-amazon.com/images/I/71Xnz-EkOvL.jpg",
        "Alice's Adventures in Wonderland": "https://images-na.ssl-images-amazon.com/images/I/71pmz7HdGpL.jpg",
        "Pride and Prejudice": "https://images-na.ssl-images-amazon.com/images/I/71Q1tPupKjL.jpg",
        "The Great Gatsby": "https://images-na.ssl-images-amazon.com/images/I/71FTb9X6wsL.jpg",
        "Moby Dick": "https://images-na.ssl-images-amazon.com/images/I/71+WUXzpBFL.jpg",
        "War and Peace": "https://images-na.ssl-images-amazon.com/images/I/91tFN+dgGYL.jpg",
        "The Odyssey": "https://images-na.ssl-images-amazon.com/images/I/81YzHKeWq7L.jpg",
        "Don Quixote": "https://images-na.ssl-images-amazon.com/images/I/81-c1oPG2JL.jpg",
        "Frankenstein": "https://images-na.ssl-images-amazon.com/images/I/71CX11qUBOL.jpg",
        "Jane Eyre": "https://images-na.ssl-images-amazon.com/images/I/81Gm0qxuP8L.jpg",
        "Wuthering Heights": "https://images-na.ssl-images-amazon.com/images/I/81Gm0qxuP8L.jpg",
        "The Count of Monte Cristo": "https://images-na.ssl-images-amazon.com/images/I/81Y8QLPFbWL.jpg",
        "Crime and Punishment": "https://images-na.ssl-images-amazon.com/images/I/81XbzJGJnTL.jpg",
        "The Brothers Karamazov": "https://images-na.ssl-images-amazon.com/images/I/81wdB+X6YOL.jpg",
        "Les Misérables": "https://images-na.ssl-images-amazon.com/images/I/81wdB+X6YOL.jpg",
        "The Picture of Dorian Gray": "https://images-na.ssl-images-amazon.com/images/I/71R8pJXJiJL.jpg",
        "Dracula": "https://images-na.ssl-images-amazon.com/images/I/71AFqYQD-2L.jpg",
        "The Adventures of Sherlock Holmes": "https://images-na.ssl-images-amazon.com/images/I/91YS6mrM00L.jpg",
        "Gulliver's Travels": "https://images-na.ssl-images-amazon.com/images/I/71c1ltgBYML.jpg",
        "The Iliad": "https://images-na.ssl-images-amazon.com/images/I/71YoFJSz3LL.jpg",
        "Hamlet": "https://images-na.ssl-images-amazon.com/images/I/71YoFJSz3LL.jpg",
        "Romeo and Juliet": "https://images-na.ssl-images-amazon.com/images/I/71YoFJSz3LL.jpg",
        "Macbeth": "https://images-na.ssl-images-amazon.com/images/I/71YoFJSz3LL.jpg",
        "The Divine Comedy": "https://images-na.ssl-images-amazon.com/images/I/71YoFJSz3LL.jpg",
        "The Canterbury Tales": "https://images-na.ssl-images-amazon.com/images/I/71YoFJSz3LL.jpg",
        "The Prince": "https://images-na.ssl-images-amazon.com/images/I/71YoFJSz3LL.jpg",
        "The Art of War": "https://images-na.ssl-images-amazon.com/images/I/71YoFJSz3LL.jpg",
        "The Republic": "https://images-na.ssl-images-amazon.com/images/I/71YoFJSz3LL.jpg",
        "The Communist Manifesto": "https://images-na.ssl-images-amazon.com/images/I/71YoFJSz3LL.jpg",
        "The Wealth of Nations": "https://images-na.ssl-images-amazon.com/images/I/71YoFJSz3LL.jpg",
        "The Origin of Species": "https://images-na.ssl-images-amazon.com/images/I/71YoFJSz3LL.jpg",
        "The Interpretation of Dreams": "https://images-na.ssl-images-amazon.com/images/I/71YoFJSz3LL.jpg",
        "The Social Contract": "https://images-na.ssl-images-amazon.com/images/I/71YoFJSz3LL.jpg",
        "The Second Sex": "https://images-na.ssl-images-amazon.com/images/I/71YoFJSz3LL.jpg",
        "The Diary of a Young Girl": "https://images-na.ssl-images-amazon.com/images/I/71YoFJSz3LL.jpg",
        "The Hobbit": "https://images-na.ssl-images-amazon.com/images/I/710+HcoP38L.jpg",
        "The Lord of the Rings": "https://images-na.ssl-images-amazon.com/images/I/71jLBXtWJWL.jpg",
        "Harry Potter and the Philosopher's Stone": "https://images-na.ssl-images-amazon.com/images/I/81m1s4wIPML.jpg",
        "Harry Potter and the Chamber of Secrets": "https://images-na.ssl-images-amazon.com/images/I/91OINeHnJGL.jpg",
        "Harry Potter and the Prisoner of Azkaban": "https://images-na.ssl-images-amazon.com/images/I/81lAPl9Fl0L.jpg",
        "Harry Potter and the Goblet of Fire": "https://images-na.ssl-images-amazon.com/images/I/91jlLIQslmL.jpg",
        "Harry Potter and the Order of the Phoenix": "https://images-na.ssl-images-amazon.com/images/I/91TpLHDnuFL.jpg",
        "Harry Potter and the Half-Blood Prince": "https://images-na.ssl-images-amazon.com/images/I/51KV4CSJNGL.jpg",
        "Harry Potter and the Deathly Hallows": "https://images-na.ssl-images-amazon.com/images/I/71sH3vxziLL.jpg",
        "1984": "https://images-na.ssl-images-amazon.com/images/I/71kxa1-0mfL.jpg",
        "Animal Farm": "https://images-na.ssl-images-amazon.com/images/I/71Y+pAhQXVL.jpg",
        "Brave New World": "https://images-na.ssl-images-amazon.com/images/I/81zE42gT3xL.jpg",
        "To Kill a Mockingbird": "https://images-na.ssl-images-amazon.com/images/I/71FxgtFKcQL.jpg",
        "The Catcher in the Rye": "https://images-na.ssl-images-amazon.com/images/I/91HPG31dTwL.jpg",
        "The Grapes of Wrath": "https://images-na.ssl-images-amazon.com/images/I/71S9dGNpR+L.jpg",
        "The Old Man and the Sea": "https://images-na.ssl-images-amazon.com/images/I/713nNkYQHPL.jpg",
        "For Whom the Bell Tolls": "https://images-na.ssl-images-amazon.com/images/I/71Fyf-iKa+L.jpg",
        "The Sun Also Rises": "https://images-na.ssl-images-amazon.com/images/I/81Ib+7+CkUL.jpg",
        "One Hundred Years of Solitude": "https://images-na.ssl-images-amazon.com/images/I/91-6oKYKH0L.jpg",
        "Love in the Time of Cholera": "https://images-na.ssl-images-amazon.com/images/I/81XTkCUKfQL.jpg",
        "The Alchemist": "https://images-na.ssl-images-amazon.com/images/I/71aFt4+OTOL.jpg",
        "The Little Prince": "https://images-na.ssl-images-amazon.com/images/I/71OZY035QKL.jpg",
        "The Stranger": "https://images-na.ssl-images-amazon.com/images/I/71Hgw6LDTlL.jpg",
        "The Plague": "https://images-na.ssl-images-amazon.com/images/I/71Hgw6LDTlL.jpg",
        "The Trial": "https://images-na.ssl-images-amazon.com/images/I/71Hgw6LDTlL.jpg",
        "The Metamorphosis": "https://images-na.ssl-images-amazon.com/images/I/71Hgw6LDTlL.jpg",
        "Ulysses": "https://images-na.ssl-images-amazon.com/images/I/71Hgw6LDTlL.jpg",
        "Lolita": "https://images-na.ssl-images-amazon.com/images/I/71Hgw6LDTlL.jpg",
        "Catch-22": "https://images-na.ssl-images-amazon.com/images/I/71Hgw6LDTlL.jpg",
        "Slaughterhouse-Five": "https://images-na.ssl-images-amazon.com/images/I/71Hgw6LDTlL.jpg",
        "The Hitchhiker's Guide to the Galaxy": "https://images-na.ssl-images-amazon.com/images/I/81XSN3KyJCL.jpg",
        "The Road": "https://images-na.ssl-images-amazon.com/images/I/71IJ1HC2a0L.jpg",
        "No Country for Old Men": "https://images-na.ssl-images-amazon.com/images/I/71IJ1HC2a0L.jpg",
        "Blood Meridian": "https://images-na.ssl-images-amazon.com/images/I/71IJ1HC2a0L.jpg",
        "The Road Less Traveled": "https://images-na.ssl-images-amazon.com/images/I/71IJ1HC2a0L.jpg",
        "The Power of Now": "https://images-na.ssl-images-amazon.com/images/I/714FbKtXS+L.jpg",
        "The 7 Habits of Highly Effective People": "https://images-na.ssl-images-amazon.com/images/I/71oF3c5ReaL.jpg",
        "How to Win Friends and Influence People": "https://images-na.ssl-images-amazon.com/images/I/71oF3c5ReaL.jpg",
        "Think and Grow Rich": "https://images-na.ssl-images-amazon.com/images/I/71oF3c5ReaL.jpg",
        "The 48 Laws of Power": "https://images-na.ssl-images-amazon.com/images/I/71aG+xDKSYL.jpg",
        "The Art of War": "https://images-na.ssl-images-amazon.com/images/I/71aG+xDKSYL.jpg",
        "The Prince": "https://images-na.ssl-images-amazon.com/images/I/71aG+xDKSYL.jpg",
        "The Republic": "https://images-na.ssl-images-amazon.com/images/I/71aG+xDKSYL.jpg",
        "The Communist Manifesto": "https://images-na.ssl-images-amazon.com/images/I/71aG+xDKSYL.jpg",
        "The Wealth of Nations": "https://images-na.ssl-images-amazon.com/images/I/71aG+xDKSYL.jpg",
        "The Origin of Species": "https://images-na.ssl-images-amazon.com/images/I/71aG+xDKSYL.jpg",
        "The Interpretation of Dreams": "https://images-na.ssl-images-amazon.com/images/I/71aG+xDKSYL.jpg",
        "The Social Contract": "https://images-na.ssl-images-amazon.com/images/I/71aG+xDKSYL.jpg",
        "The Second Sex": "https://images-na.ssl-images-amazon.com/images/I/71aG+xDKSYL.jpg",
        "The Diary of a Young Girl": "https://images-na.ssl-images-amazon.com/images/I/71aG+xDKSYL.jpg",
    }
    
    # Türkçe kitaplar için özel kapak fotoğrafları
    # Special cover images for Turkish books
    turkish_covers = {
        "Adalet Dünyası": "https://i.dr.com.tr/cache/600x600-0/originals/0001788076001-1.jpg",
        "Adalet Evi": "https://i.dr.com.tr/cache/600x600-0/originals/0000000647420-1.jpg",
        "Adalet Günleri": "https://i.dr.com.tr/cache/600x600-0/originals/0001911177001-1.jpg",
        "Adalet Hikayesi": "https://i.dr.com.tr/cache/600x600-0/originals/0001911177001-1.jpg",
        "Adalet Kapısı": "https://i.dr.com.tr/cache/600x600-0/originals/0001911177001-1.jpg",
        "Adalet Kitabı": "https://i.dr.com.tr/cache/600x600-0/originals/0001911177001-1.jpg",
        "Adalet Saati": "https://i.dr.com.tr/cache/600x600-0/originals/0001911177001-1.jpg",
        "Adalet Sırrı": "https://i.dr.com.tr/cache/600x600-0/originals/0001911177001-1.jpg",
        "Adalet Yolu": "https://i.dr.com.tr/cache/600x600-0/originals/0001911177001-1.jpg",
        "Adalet Zamanı": "https://i.dr.com.tr/cache/600x600-0/originals/0001911177001-1.jpg",
        "Amerikan Tanrıları": "https://i.dr.com.tr/cache/600x600-0/originals/0001788076001-1.jpg",
        "Androidler Elektrikli Koyun Düşler mi?": "https://i.dr.com.tr/cache/600x600-0/originals/0001788076001-1.jpg",
        "Anlam Hikayesi": "https://i.dr.com.tr/cache/600x600-0/originals/0001788076001-1.jpg",
        "Anlam Kapısı": "https://i.dr.com.tr/cache/600x600-0/originals/0001788076001-1.jpg",
    }
    
    # Tüm özel kapakları birleştir
    # Combine all special covers
    all_covers = {**special_covers, **turkish_covers}
    
    updated_count = 0
    skipped_count = 0
    
    # Sadece belirli kitapları işlemek için
    # To process only specific books
    # books = Book.objects.filter(id__in=[12, 26, 18, 13, 10])
    
    for book in books:
        print(f"İşleniyor: {book.id}. {book.title}")
        
        try:
            # Özel kapak fotoğrafı var mı kontrol et
            # Check if there is a special cover image
            if book.title in all_covers:
                cover_url = all_covers[book.title]
                print(f"  Özel kapak bulundu: {cover_url}")
                
                # Kapak fotoğrafını indir
                # Download cover image
                image = download_image(cover_url)
                if image:
                    # Kapak fotoğrafını güncelle
                    # Update cover image
                    if update_book_cover(book, image):
                        updated_count += 1
                        print(f"  Kapak güncellendi: {book.title}")
                    else:
                        skipped_count += 1
                        print(f"  Kapak güncellenemedi: {book.title}")
                else:
                    skipped_count += 1
                    print(f"  Kapak indirilemedi: {book.title}")
            else:
                # Google Books API'den kapak fotoğrafını al
                # Get cover image from Google Books API
                cover_url = get_cover_from_google_books(book.title)
                
                # Google Books API'den kapak bulunamadıysa Open Library API'yi dene
                # Try Open Library API if cover not found from Google Books API
                if not cover_url:
                    cover_url = get_cover_from_open_library(book.title)
                
                if cover_url:
                    print(f"  API'den kapak bulundu: {cover_url}")
                    
                    # Kapak fotoğrafını indir
                    # Download cover image
                    image = download_image(cover_url)
                    if image:
                        # Kapak fotoğrafını güncelle
                        # Update cover image
                        if update_book_cover(book, image):
                            updated_count += 1
                            print(f"  Kapak güncellendi: {book.title}")
                        else:
                            skipped_count += 1
                            print(f"  Kapak güncellenemedi: {book.title}")
                    else:
                        skipped_count += 1
                        print(f"  Kapak indirilemedi: {book.title}")
                else:
                    skipped_count += 1
                    print(f"  Kapak bulunamadı: {book.title}")
        except Exception as e:
            skipped_count += 1
            print(f"  Kitap işleme hatası: {str(e)}")
            continue
            
        # API limitlerini aşmamak için bekle
        # Wait to avoid exceeding API limits
        time.sleep(1)
    
    print(f"\nToplam {updated_count} kitap kapağı güncellendi, {skipped_count} kitap atlandı.")
    print(f"İşlem tamamlandı. Toplam {len(books)} kitap işlendi.")

if __name__ == "__main__":
    main() 