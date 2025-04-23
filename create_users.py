import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')
django.setup()

from django.contrib.auth.models import User
from library.models import Member
from django.utils import timezone

# Admin kullanıcısı oluştur
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='Admin123!',
        first_name='Admin',
        last_name='User'
    )
    print(f"Admin kullanıcısı oluşturuldu: {admin_user.username}")
else:
    print("Admin kullanıcısı zaten var.")

# Normal kullanıcı oluştur
if not User.objects.filter(username='user').exists():
    normal_user = User.objects.create_user(
        username='user',
        email='user@example.com',
        password='User123!',
        first_name='Normal',
        last_name='User'
    )
    
    # Üye kaydı oluştur
    Member.objects.create(
        user=normal_user,
        phone_number='5551234567',
        address='Örnek Adres, İstanbul',
        membership_date=timezone.now().date()
    )
    
    print(f"Normal kullanıcı oluşturuldu: {normal_user.username}")
else:
    print("Normal kullanıcı zaten var.")

print("\nKullanıcı Bilgileri:")
print("Admin - Kullanıcı adı: admin, Şifre: Admin123!")
print("Kullanıcı - Kullanıcı adı: user, Şifre: User123!") 