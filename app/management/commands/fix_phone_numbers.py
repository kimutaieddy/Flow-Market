"""
Django management command to fix phone numbers in the database
Adds +254 prefix to phone numbers that are missing it
Usage: python manage.py fix_phone_numbers
"""
from django.core.management.base import BaseCommand
from app.models import Contact


class Command(BaseCommand):
    help = 'Fixes phone numbers by adding +254 prefix if missing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 Starting phone number fix...'))

        contacts = Contact.objects.all()
        fixed_count = 0
        already_correct = 0
        error_count = 0

        for contact in contacts:
            phone = contact.phone_number.strip()
            
            # Check if phone number needs fixing
            if phone.startswith('+254'):
                already_correct += 1
                continue
            
            # Remove leading zeros if present
            if phone.startswith('0'):
                phone = phone[1:]
            
            # Remove +254 without leading plus if present
            if phone.startswith('254'):
                phone = phone[3:]
            
            # Add +254 prefix
            new_phone = f"+254{phone}"
            
            try:
                contact.phone_number = new_phone
                contact.save()
                fixed_count += 1
                self.stdout.write(f"  Fixed: {contact.name} - {phone} → {new_phone}")
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"  Error fixing {contact.name}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Phone number fix completed!'))
        self.stdout.write(f'  • Fixed: {fixed_count} contacts')
        self.stdout.write(f'  • Already correct: {already_correct} contacts')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'  • Errors: {error_count} contacts'))
