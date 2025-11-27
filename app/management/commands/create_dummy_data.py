"""
Django management command to create dummy data for FlowMarket
Usage: python manage.py create_dummy_data
"""
from django.core.management.base import BaseCommand
from app.models import Contact, Campaign, Product, CampaignTemplate, ContactList, SentCampaign
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Creates dummy data for testing FlowMarket platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--contacts',
            type=int,
            default=50,
            help='Number of contacts to create (default: 50)'
        )
        parser.add_argument(
            '--products',
            type=int,
            default=30,
            help='Number of products to create (default: 30)'
        )
        parser.add_argument(
            '--campaigns',
            type=int,
            default=20,
            help='Number of campaign templates to create (default: 20)'
        )
        parser.add_argument(
            '--lists',
            type=int,
            default=10,
            help='Number of contact lists to create (default: 10)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing data before creating new data'
        )

    def handle(self, *args, **options):
        contacts_count = options['contacts']
        products_count = options['products']
        campaigns_count = options['campaigns']
        lists_count = options['lists']
        clear_data = options['clear']

        self.stdout.write(self.style.SUCCESS('🚀 Starting dummy data creation...'))

        # Clear existing data if requested
        if clear_data:
            self.stdout.write(self.style.WARNING('⚠️  Clearing all existing data...'))
            SentCampaign.objects.all().delete()
            ContactList.objects.all().delete()
            CampaignTemplate.objects.all().delete()
            Campaign.objects.all().delete()
            Product.objects.all().delete()
            Contact.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ All data cleared'))

        # Create Contacts
        self.stdout.write('📞 Creating contacts...')
        contacts = self.create_contacts(contacts_count)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(contacts)} contacts'))

        # Create Products
        self.stdout.write('📦 Creating products...')
        products = self.create_products(products_count)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(products)} products'))

        # Create Campaign Templates
        self.stdout.write('📝 Creating campaign templates...')
        campaign_templates = self.create_campaign_templates(campaigns_count)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(campaign_templates)} campaign templates'))

        # Create Contact Lists
        self.stdout.write('📋 Creating contact lists...')
        contact_lists = self.create_contact_lists(lists_count, contacts)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(contact_lists)} contact lists'))

        # Create Legacy Campaigns (old Campaign model)
        self.stdout.write('📧 Creating legacy campaigns...')
        legacy_campaigns = self.create_legacy_campaigns(10)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(legacy_campaigns)} legacy campaigns'))

        # Create Sent Campaigns
        self.stdout.write('📨 Creating sent campaign records...')
        sent_campaigns = self.create_sent_campaigns(15, campaign_templates, contact_lists)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(sent_campaigns)} sent campaign records'))

        self.stdout.write(self.style.SUCCESS('\n🎉 Dummy data creation completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'\nSummary:'))
        self.stdout.write(f'  • {len(contacts)} Contacts')
        self.stdout.write(f'  • {len(products)} Products')
        self.stdout.write(f'  • {len(campaign_templates)} Campaign Templates')
        self.stdout.write(f'  • {len(contact_lists)} Contact Lists')
        self.stdout.write(f'  • {len(legacy_campaigns)} Legacy Campaigns')
        self.stdout.write(f'  • {len(sent_campaigns)} Sent Campaigns')

    def create_contacts(self, count):
        """Create dummy contacts with realistic Kenyan phone numbers"""
        first_names = [
            'John', 'Jane', 'David', 'Sarah', 'Michael', 'Mary', 'James', 'Patricia',
            'Robert', 'Jennifer', 'William', 'Linda', 'Richard', 'Elizabeth', 'Joseph',
            'Susan', 'Thomas', 'Jessica', 'Charles', 'Margaret', 'Daniel', 'Dorothy',
            'Matthew', 'Lisa', 'Anthony', 'Nancy', 'Mark', 'Karen', 'Donald', 'Betty',
            'Paul', 'Helen', 'Andrew', 'Sandra', 'Joshua', 'Donna', 'Kenneth', 'Carol',
            'Kevin', 'Ruth', 'Brian', 'Sharon', 'George', 'Michelle', 'Edward', 'Laura',
            'Ronald', 'Deborah', 'Timothy', 'Cynthia'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
            'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
            'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
            'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
            'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen',
            'Hill', 'Flores', 'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera',
            'Campbell', 'Mitchell', 'Carter', 'Roberts'
        ]

        contacts = []
        for i in range(count):
            phone_number = f"+254{random.randint(700000000, 799999999)}"
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            full_name = f"{first_name} {last_name}"
            
            contact = Contact.objects.create(
                phone_number=phone_number,
                name=full_name,
                is_active=random.choice([True, True, True, False])  # 75% active
            )
            contacts.append(contact)
        
        return contacts

    def create_products(self, count):
        """Create dummy products"""
        product_adjectives = [
            'Premium', 'Luxury', 'Budget', 'Professional', 'Deluxe',
            'Classic', 'Modern', 'Vintage', 'Smart', 'Eco-friendly',
            'Elite', 'Advanced', 'Essential', 'Ultimate', 'Superior'
        ]
        
        product_nouns = [
            'Phone', 'Laptop', 'Watch', 'Headphones', 'Camera',
            'Shoes', 'Shirt', 'Dress', 'Sofa', 'Lamp',
            'Ball', 'Racket', 'Novel', 'Perfume', 'Toy',
            'Tablet', 'Speaker', 'Keyboard', 'Mouse', 'Monitor',
            'Bag', 'Wallet', 'Sunglasses', 'Hat', 'Scarf',
            'Jacket', 'Pants', 'Boots', 'Sneakers', 'Sandals',
            'Notebook', 'Pen', 'Charger', 'Cable', 'Case'
        ]

        products = []
        for i in range(count):
            # Add timestamp to make names unique
            name = f"{random.choice(product_adjectives)} {random.choice(product_nouns)} #{random.randint(1000, 9999)}"
            price = round(random.uniform(10, 1000), 2)
            
            descriptions = [
                f"High-quality {name.lower()} perfect for everyday use. Durable and reliable.",
                f"Best-selling {name.lower()} with premium features and modern design.",
                f"Top-rated {name.lower()} loved by customers worldwide. Great value!",
                f"Durable and reliable {name.lower()} backed by warranty and support.",
                f"Affordable {name.lower()} with excellent quality and performance.",
                f"Professional-grade {name.lower()} designed for serious users.",
                f"Stylish {name.lower()} that combines form and function perfectly.",
                f"Innovative {name.lower()} with cutting-edge technology built-in.",
                f"Versatile {name.lower()} suitable for multiple use cases.",
                f"Compact {name.lower()} with powerful features in a small package."
            ]
            
            product = Product.objects.create(
                name=name,
                description=random.choice(descriptions),
                price=price,
                is_active=random.choice([True, True, True, False])  # 75% active
            )
            products.append(product)
        
        return products

    def create_campaign_templates(self, count):
        """Create dummy campaign templates"""
        campaign_types = [
            'Promotional', 'Welcome', 'Reminder', 'Announcement', 'Update',
            'Thank You', 'Seasonal', 'Flash Sale', 'New Arrival', 'Feedback'
        ]
        
        messages = [
            "Hi [Name]! 🎉 Don't miss our exclusive 50% OFF sale this weekend! Shop now at FlowMarket.",
            "Hello [Name]! Welcome to FlowMarket family. Get 20% OFF on your first purchase with code WELCOME20.",
            "Hey [Name]! Your favorite items are back in stock. Limited quantities available. Order now!",
            "Dear [Name], thank you for being our valued customer. Enjoy 30% OFF as our appreciation gift!",
            "[Name], Flash Sale Alert! 🔥 Up to 70% OFF on selected items for the next 24 hours only!",
            "Hi [Name]! New arrivals just in! Check out our latest collection at special launch prices.",
            "Hello [Name]! Your order is ready for pickup. Visit us today and get a free gift!",
            "[Name], we miss you! Come back and enjoy 40% OFF on your next purchase. Code: COMEBACK40",
            "Dear [Name], Holiday Special! 🎄 Save big on all categories. Limited time offer!",
            "Hey [Name]! Rate your recent purchase and get 100 reward points instantly!",
            "[Name], exclusive VIP offer just for you! 60% OFF + Free delivery on orders above $50.",
            "Hi [Name]! Clear your cart now and get an extra 15% OFF. Offer ends tonight!",
            "Hello [Name]! Birthday month special! Enjoy 50% OFF all week long. Happy Birthday! 🎂",
            "[Name], last chance! Sale ends in 6 hours. Grab your favorites before they're gone!",
            "Dear [Name], we've restocked your wishlist items! Shop now before they sell out again.",
        ]

        templates = []
        for i in range(count):
            campaign_type = random.choice(campaign_types)
            message = random.choice(messages)
            
            template = CampaignTemplate.objects.create(
                name=f"{campaign_type} Campaign {i+1}",
                message=message,
                created_by=f"+254{random.randint(700000000, 799999999)}",
                is_active=random.choice([True, True, True, False])  # 75% active
            )
            templates.append(template)
        
        return templates

    def create_contact_lists(self, count, contacts):
        """Create dummy contact lists and assign contacts"""
        list_types = [
            'VIP Customers', 'New Subscribers', 'Inactive Users', 'Premium Members',
            'Test Group A', 'Test Group B', 'Seasonal Shoppers', 'Loyal Customers',
            'First Time Buyers', 'High Spenders', 'Mobile App Users', 'Email Subscribers',
            'Social Media Followers', 'Event Attendees', 'Product Interest Group'
        ]
        
        descriptions = [
            'High value customers with frequent purchases',
            'Recently subscribed contacts for onboarding',
            'Contacts who haven\'t engaged in the last 90 days',
            'Premium tier members with exclusive benefits',
            'Test group for A/B testing campaigns',
            'Secondary test group for comparison',
            'Customers who shop during seasonal sales',
            'Long-term customers with 5+ orders',
            'New customers with 1-2 orders',
            'Customers with high average order value',
            'Users who downloaded our mobile app',
            'Contacts subscribed to email newsletter',
            'Engaged followers from social platforms',
            'People who attended our events',
            'Interested in specific product categories'
        ]

        contact_lists = []
        for i in range(count):
            list_name = list_types[i] if i < len(list_types) else f"Custom List {i+1}"
            description = descriptions[i] if i < len(descriptions) else "Custom contact segment"
            
            contact_list = ContactList.objects.create(
                name=list_name,
                description=description,
                is_active=random.choice([True, True, True, False])  # 75% active
            )
            
            # Add random contacts to the list (10-30 contacts per list)
            num_contacts = random.randint(10, min(30, len(contacts)))
            selected_contacts = random.sample(contacts, num_contacts)
            contact_list.contacts.add(*selected_contacts)
            
            contact_lists.append(contact_list)
        
        return contact_lists

    def create_legacy_campaigns(self, count):
        """Create dummy legacy campaigns (old Campaign model)"""
        messages = [
            "Summer Sale! Get 50% off on all items. Visit our store today!",
            "Flash Sale Alert! Limited time offer on electronics. Don't miss out!",
            "Thank you for being our valued customer. Enjoy 20% off your next purchase!",
            "New arrivals in stock! Check out our latest collection now.",
            "Weekend Special: Buy 2 Get 1 Free on selected items!",
            "Exclusive offer: Free delivery on orders above $30. Shop now!",
            "Clearance Sale! Up to 70% off on last season items. Hurry!",
            "Happy Holidays! Special discounts on gift items. Order today!",
            "Mid-season sale! Save big on fashion and accessories.",
            "Customer Appreciation Day! Extra 30% off everything in store.",
        ]

        campaigns = []
        for i in range(count):
            # Random date in the past 60 days
            days_ago = random.randint(1, 60)
            sent_date = datetime.now() - timedelta(days=days_ago)
            
            recipients_count = random.randint(50, 500)
            
            campaign = Campaign.objects.create(
                message=random.choice(messages),
                recipients_count=recipients_count,
                api_response='{"status": "success", "sent": ' + str(recipients_count) + '}',
                status=random.choice(['success', 'success', 'success', 'failed'])  # 75% success
            )
            # Manually set the sent_at timestamp
            Campaign.objects.filter(id=campaign.id).update(sent_at=sent_date)
            campaigns.append(campaign)
        
        return campaigns

    def create_sent_campaigns(self, count, campaign_templates, contact_lists):
        """Create dummy sent campaign records"""
        if not campaign_templates or not contact_lists:
            return []

        sent_campaigns = []
        for i in range(count):
            template = random.choice(campaign_templates)
            contact_list = random.choice(contact_lists)
            recipients_count = contact_list.contact_count()
            
            # Random date in the past 30 days
            days_ago = random.randint(1, 30)
            sent_date = datetime.now() - timedelta(days=days_ago)
            
            status = random.choice(['success', 'success', 'success', 'failed'])  # 75% success
            
            sent_campaign = SentCampaign.objects.create(
                campaign_template=template,
                contact_list=contact_list,
                message=template.message,
                recipients_count=recipients_count,
                sent_by=f"+254{random.randint(700000000, 799999999)}",
                api_response='{"status": "' + status + '", "sent": ' + str(recipients_count) + '}',
                status=status
            )
            # Manually set the sent_at timestamp
            SentCampaign.objects.filter(id=sent_campaign.id).update(sent_at=sent_date)
            sent_campaigns.append(sent_campaign)
        
        return sent_campaigns
