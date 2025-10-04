from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil

class Command(BaseCommand):
    help = 'Copy default menu images to media directory'

    def handle(self, *args, **options):
        # Source directory (in your repository)
        source_dir = os.path.join(settings.BASE_DIR, 'media', 'menu_images')
        
        # Destination directory (actual media directory)
        dest_dir = os.path.join(settings.MEDIA_ROOT, 'menu_images')
        
        # Create destination directory if it doesn't exist
        os.makedirs(dest_dir, exist_ok=True)
        
        if os.path.exists(source_dir):
            # Copy all images from source to destination
            for filename in os.listdir(source_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    source_file = os.path.join(source_dir, filename)
                    dest_file = os.path.join(dest_dir, filename)
                    
                    if not os.path.exists(dest_file):
                        shutil.copy2(source_file, dest_file)
                        self.stdout.write(f'Copied {filename} to media directory')
                    else:
                        self.stdout.write(f'{filename} already exists in media directory')
            
            self.stdout.write(
                self.style.SUCCESS('Default menu images setup completed!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Source directory {source_dir} not found')
            )