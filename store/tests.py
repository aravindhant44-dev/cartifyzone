from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.management import call_command
from store.models import Category, Product, Cart, Order, OrderItem


class TestModels(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Laptop",
            category=self.category,
            price=50000.00,
            description="High performance laptop",
            stock=10
        )
        self.user = User.objects.create_user(username="testuser", password="password123")

    def test_category_str(self):
        self.assertEqual(str(self.category), "Electronics")

    def test_product_str(self):
        self.assertEqual(str(self.product), "Test Laptop")

    def test_cart_str(self):
        cart_item = Cart.objects.create(user=self.user, product=self.product, quantity=2)
        self.assertEqual(str(cart_item), "Test Laptop (2)")

    def test_order_str(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="John Doe",
            phone="1234567890",
            address="123 Street",
            total_amount=50000.00
        )
        self.assertEqual(str(order), f"Order #{order.pk} - John Doe")

    def test_order_item_str_and_subtotal(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="John Doe",
            phone="1234567890",
            address="123 Street",
            total_amount=50000.00
        )
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=50000.00
        )
        self.assertEqual(str(order_item), "Test Laptop x 2")
        self.assertEqual(order_item.subtotal(), 100000.00)


class TestSeedProductsCommand(TestCase):
    def test_seed_products_idempotent(self):
        call_command('seed_products')
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(Product.objects.count(), 13)

        # Run a second time to ensure idempotency
        call_command('seed_products')
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(Product.objects.count(), 13)


class TestAuthViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="existinguser", password="password123")

    def test_register_success(self):
        response = self.client.post('/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        })
        self.assertRedirects(response, '/login/')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_duplicate_username(self):
        response = self.client.post('/register/', {
            'username': 'existinguser',
            'email': 'duplicate@example.com',
            'password': 'newpassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username already exists')

    def test_user_login_success(self):
        response = self.client.post('/login/', {
            'username': 'existinguser',
            'password': 'password123'
        })
        self.assertRedirects(response, '/home/')

    def test_user_login_invalid(self):
        response = self.client.post('/login/', {
            'username': 'existinguser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid Username or Password')

    def test_user_logout(self):
        self.client.login(username='existinguser', password='password123')
        response = self.client.get('/logout/')
        self.assertRedirects(response, '/login/')


class TestStoreViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.category = Category.objects.create(name="Tech")
        self.product = Product.objects.create(
            name="Smart Gadget",
            category=self.category,
            price=1500.00,
            description="Cool gadget",
            stock=5
        )

    def test_home_requires_login(self):
        response = self.client.get('/home/')
        self.assertRedirects(response, '/login/?next=/home/')

    def test_home_authenticated(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get('/home/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smart Gadget')

    def test_home_category_filter(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(f'/home/?category={self.category.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smart Gadget')

    def test_product_detail_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(f'/product/{self.product.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smart Gadget')

    def test_product_detail_404(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get('/product/99999/')
        self.assertEqual(response.status_code, 404)


class TestCartAndCheckout(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.category = Category.objects.create(name="Gadgets")
        self.product = Product.objects.create(
            name="Wireless Earbuds",
            category=self.category,
            price=2000.00,
            description="Noise canceling earbuds",
            stock=3
        )
        self.client.login(username='testuser', password='password123')

    def test_add_to_cart(self):
        response = self.client.get(f'/add-to-cart/{self.product.id}/')
        self.assertRedirects(response, '/cart/')
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 1)

    def test_cart_quantity_increase_decrease_remove(self):
        # Add to cart
        self.client.get(f'/add-to-cart/{self.product.id}/')
        cart_item = Cart.objects.get(user=self.user, product=self.product)
        self.assertEqual(cart_item.quantity, 1)

        # Increase
        self.client.get(f'/increase/{cart_item.id}/')
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 2)

        # Decrease
        self.client.get(f'/decrease/{cart_item.id}/')
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 1)

        # Remove
        self.client.get(f'/remove/{cart_item.id}/')
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 0)

    def test_checkout_successful(self):
        self.client.get(f'/add-to-cart/{self.product.id}/')
        response = self.client.post('/checkout/', {
            'customer_name': 'Alice Smith',
            'phone': '9876543210',
            'address': '456 Avenue'
        })
        self.assertRedirects(response, '/success/')
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 0)

        # Verify stock deduction
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

    def test_checkout_empty_cart(self):
        response = self.client.get('/checkout/')
        self.assertRedirects(response, '/cart/')

    def test_orders_page_and_delete(self):
        self.client.get(f'/add-to-cart/{self.product.id}/')
        self.client.post('/checkout/', {
            'customer_name': 'Alice Smith',
            'phone': '9876543210',
            'address': '456 Avenue'
        })
        order = Order.objects.get(user=self.user)

        response = self.client.get('/orders/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice Smith')

        # Cancel order
        delete_resp = self.client.get(f'/delete-order/{order.id}/')
        self.assertRedirects(delete_resp, '/orders/')
        self.assertEqual(Order.objects.filter(user=self.user).count(), 0)
