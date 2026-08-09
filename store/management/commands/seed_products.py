from django.core.management.base import BaseCommand
from store.models import Category, Product


class Command(BaseCommand):
    help = "Seeds initial categories and products idempotently"

    def handle(self, *args, **options):
        self.stdout.write("Starting product seeding...")

        categories_data = ["Electronics", "Fashion", "Books"]
        category_map = {}

        for cat_name in categories_data:
            cat_obj, created = Category.objects.get_or_create(name=cat_name)
            category_map[cat_name] = cat_obj
            if created:
                self.stdout.write(f"Created category: {cat_name}")
            else:
                self.stdout.write(f"Category already exists: {cat_name}")

        products_data = [
            {
                "name": "iPhone 15",
                "category": category_map["Electronics"],
                "price": 79999.00,
                "description": "Latest Apple iPhone with advanced camera system and high performance.",
                "image": "products/apple-iphone.png",
                "stock": 10
            },
            {
                "name": "Samsung Galaxy S24",
                "category": category_map["Electronics"],
                "price": 69999.00,
                "description": "Premium smartphone with Dynamic AMOLED display and AI features.",
                "image": "products/samsung-galaxy-images.png",
                "stock": 15
            },
            {
                "name": "Dell Inspiron 15",
                "category": category_map["Electronics"],
                "price": 54999.00,
                "description": "Powerful laptop for work and entertainment with high resolution screen.",
                "image": "products/dell_laptop.jfif",
                "stock": 10
            },
            {
                "name": "Samsung 43-inch Smart TV",
                "category": category_map["Electronics"],
                "price": 32999.00,
                "description": "Crystal 4K UHD Smart TV with immersive sound and smart connectivity.",
                "image": "products/smart_tv.png",
                "stock": 10
            },
            {
                "name": "Logitech M331 Silent Plus",
                "category": category_map["Electronics"],
                "price": 1499.00,
                "description": "Ergonomic wireless mouse with silent clicking technology.",
                "image": "products/mouse.jfif",
                "stock": 25
            },
            {
                "name": "Men's Formal Shirt",
                "category": category_map["Fashion"],
                "price": 1299.00,
                "description": "Premium cotton formal shirt for professional wear.",
                "image": "products/Shirt-formal.png",
                "stock": 20
            },
            {
                "name": "Men's Formal Pant",
                "category": category_map["Fashion"],
                "price": 1899.00,
                "description": "Tailored fit formal trousers crafted for all-day comfort.",
                "image": "products/formal_phant.png",
                "stock": 15
            },
            {
                "name": "Women's Casual Kurti",
                "category": category_map["Fashion"],
                "price": 999.00,
                "description": "Elegant printed cotton kurti for everyday traditional style.",
                "image": "products/womens_kurti.png",
                "stock": 8
            },
            {
                "name": "Sports Running Shoes",
                "category": category_map["Fashion"],
                "price": 2499.00,
                "description": "Lightweight cushioned running shoes for active fitness routines.",
                "image": "products/shoes.png",
                "stock": 10
            },
            {
                "name": "Python Programming Guide",
                "category": category_map["Books"],
                "price": 599.00,
                "description": "Comprehensive guide to mastering Python fundamentals and modern practices.",
                "image": "products/python_book.jfif",
                "stock": 7
            },
            {
                "name": "Django Web Development",
                "category": category_map["Books"],
                "price": 799.00,
                "description": "Step-by-step book for building full-stack web applications using Django.",
                "image": "products/django_development_book.png",
                "stock": 12
            },
            {
                "name": "Data Structures & Algorithms",
                "category": category_map["Books"],
                "price": 699.00,
                "description": "Fundamental concepts of data structures, algorithms, and problem solving.",
                "image": "products/data_strutures_books.png",
                "stock": 10
            },
            {
                "name": "Artificial Intelligence Basics",
                "category": category_map["Books"],
                "price": 899.00,
                "description": "Introduction to AI, machine learning concepts, and modern applications.",
                "image": "products/artficial_intelligence_book.png",
                "stock": 12
            }
        ]

        seeded_count = 0
        for p_data in products_data:
            product, created = Product.objects.get_or_create(
                name=p_data["name"],
                defaults={
                    "category": p_data["category"],
                    "price": p_data["price"],
                    "description": p_data["description"],
                    "image": p_data["image"],
                    "stock": p_data["stock"]
                }
            )
            if created:
                seeded_count += 1
                self.stdout.write(f"Created product: {product.name}")
            else:
                # Update image or stock if missing
                if not product.image:
                    product.image = p_data["image"]
                    product.save()
                self.stdout.write(f"Product already exists: {product.name}")

        self.stdout.write(self.style.SUCCESS(f"Seeding completed. {seeded_count} new products created."))
