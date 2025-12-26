"""
Django management command to check database connection.
Usage: python manage.py check_db
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    help = 'Check database connection'

    def handle(self, *args, **options):
        try:
            # Get database info
            db_config = settings.DATABASES['default']
            db_name = db_config.get('NAME', 'Unknown')
            db_host = db_config.get('HOST', 'Unknown')
            db_port = db_config.get('PORT', 'Unknown')
            db_user = db_config.get('USER', 'Unknown')
            
            self.stdout.write(self.style.SUCCESS('Database Configuration:'))
            self.stdout.write(f'  Database: {db_name}')
            self.stdout.write(f'  Host: {db_host}')
            self.stdout.write(f'  Port: {db_port}')
            self.stdout.write(f'  User: {db_user}')
            
            # Test connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                self.stdout.write(self.style.SUCCESS(f'\n✓ Database connection successful!'))
                self.stdout.write(f'  PostgreSQL version: {version[0]}')
                
                # Check if tables exist
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
                tables = cursor.fetchall()
                if tables:
                    self.stdout.write(f'\n✓ Found {len(tables)} tables in database')
                    self.stdout.write('  Tables: ' + ', '.join([t[0] for t in tables[:10]]))
                    if len(tables) > 10:
                        self.stdout.write(f'  ... and {len(tables) - 10} more')
                else:
                    self.stdout.write(self.style.WARNING('\n⚠ No tables found. Run migrations first.'))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Database connection failed!'))
            self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))
            return

