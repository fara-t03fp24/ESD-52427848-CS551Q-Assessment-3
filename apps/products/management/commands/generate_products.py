import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Product, Category, Shop
from apps.users.models import User
from decimal import Decimal

class Command(BaseCommand):
    help = 'Generate sample 3D printing products'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of products to generate')

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        
        # Ensure we have some categories
        categories = [
            "Miniatures", "Household", "Toys", "Gadgets", "Art", 
            "Tools", "Educational", "Architectural", "Fashion", 
            "Medical", "Robotics", "Electronics"
        ]
        
        category_objects = []
        for cat_name in categories:
            cat, created = Category.objects.get_or_create(
                name=cat_name,
                slug=slugify(cat_name)
            )
            category_objects.append(cat)

        # Get or create a test shop and user if none exist
        if not User.objects.filter(is_superuser=True).exists():
            user = User.objects.create_superuser(
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
        else:
            user = User.objects.filter(is_superuser=True).first()

        if not Shop.objects.exists():
            shop = Shop.objects.create(use open data records of 2000-7000 items for your ‘products’ and display them
                name='sample-shop',
                owner=user,
                description='A sample 3D printing shop',
                slug='sample-shop'
            )
        else:
            shop = Shop.objects.first()

        # Product name components for generating realistic names
        adjectives = ['Custom', 'Modular', 'Articulated', 'Flexible', 'Mechanical', 'Smart', 'Innovative', 'Practical',
                     'Compact', 'Portable', 'Foldable', 'Adjustable', 'Universal', 'Advanced', 'Professional', 'Premium']
        objects = ['Dragon', 'Phone Stand', 'Planter', 'Gear Set', 'Container', 'Bracket', 'Sculpture', 'Case',
                  'Organizer', 'Holder', 'Mount', 'Box', 'Toy', 'Model', 'Tool', 'Frame', 'Display', 'Storage']
        features = ['with Moving Parts', 'Multi-Color', 'Snap-Fit', 'Hinged', 'Magnetic', 'Stackable',
                   'with LED Mount', 'Quick Release', 'Adjustable Height', 'Space Saving', 'Multi-Purpose',
                   'Easy Print', 'Low Poly', 'High Detail', 'Modular Design', 'Weather Resistant']

        created_count = 0
        attempts = 0
        max_attempts = count * 2  # Allow some extra attempts for duplicates

        while created_count < count and attempts < max_attempts:
            attempts += 1
            
            # Add a unique identifier to ensure unique names
            name = f"{random.choice(adjectives)} {random.choice(objects)} {random.choice(features)} {created_count + 1}"
            slug = slugify(name)

            try:
                product = Product.objects.create(
                    category=random.choice(category_objects),
                    shop=shop,
                    name=name,
                    slug=slug,
                    description=f"A high-quality 3D printable {name.lower()} perfect for {random.choice(['beginners', 'enthusiasts', 'professionals'])}. "
                              f"Features include {random.choice(['smooth surfaces', 'detailed textures', 'precise fits', 'optimized supports'])}.",
                    price=Decimal(random.uniform(5.99, 199.99)).quantize(Decimal('0.01')),
                    stock=random.randint(0, 100),
                    print_time_hours=random.randint(1, 48),
                    material_type=random.choice(['pla', 'abs', 'petg', 'tpu', 'resin']),
                    difficulty_level=random.choice(['easy', 'medium', 'hard']),
                    weight_grams=random.randint(10, 1000),
                    dimensions=f"{random.randint(10, 300)}x{random.randint(10, 300)}x{random.randint(10, 300)}",
                    is_active=random.choice([True, True, True, False]),  # 75% chance of being active
                    seller=user
                )
                created_count += 1
                
                if created_count % 100 == 0:
                    self.stdout.write(f"Created {created_count} products...")
                    
            except Exception as e:
                self.stdout.write(f"Error creating product: {str(e)}")
                continue

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} sample products'))