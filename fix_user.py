import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doczen_api.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

email = "arunbolli99@gmail.com"
password = "DocZen123!"

user = User.objects.filter(email=email).first()

if user:
    user.username = email
    user.set_password(password)
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"✅ User {email} updated successfully! You can now login with password: {password}")
else:
    User.objects.create_superuser(username=email, email=email, password=password)
    print(f"✅ User {email} did not exist, so I created a new SUPERUSER with password: {password}")
