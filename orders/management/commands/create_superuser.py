"""
Django management command to create a superuser non-interactively.
Usage: python manage.py create_superuser --username admin --email admin@example.com --password yourpassword
Or set environment variables: DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser non-interactively'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Superuser username')
        parser.add_argument('--email', type=str, help='Superuser email')
        parser.add_argument('--password', type=str, help='Superuser password')
        parser.add_argument('--noinput', action='store_true', help='Use environment variables only')

    def handle(self, *args, **options):
        # Get credentials from arguments or environment variables
        username = options.get('username') or os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = options.get('email') or os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
        password = options.get('password') or os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not username:
            self.stdout.write(self.style.WARNING('Skipping superuser creation: Username not provided. Set DJANGO_SUPERUSER_USERNAME environment variable.'))
            return

        if not password:
            self.stdout.write(self.style.WARNING('Skipping superuser creation: Password not provided. Set DJANGO_SUPERUSER_PASSWORD environment variable.'))
            return

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists. Skipping creation.'))
            return

        # Create superuser
        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser "{username}"'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating superuser: {str(e)}'))

