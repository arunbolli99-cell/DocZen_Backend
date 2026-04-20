from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # This code runs when the app starts
        import os
        # Only run in the main process (not when reloading or when doing collectstatic)
        if os.environ.get('RUN_MAIN') != 'true' and 'GUNICORN_CMD_ARGS' not in os.environ and 'RENDER' in os.environ:
             # On Render, we want to run this once to ensure the account exists in the ephemeral DB
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
                 print(f"✅ Startup: Account {email} is ready.")
             except Exception as e:
                 print(f"❌ Startup: Error creating account: {e}")
