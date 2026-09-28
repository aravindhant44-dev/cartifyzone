from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Cart, Order, OrderItem


# FIRST PAGE -> REGISTER OR HOME
def first_page(request):
    if request.user.is_authenticated:
        return redirect('/home/')
    return redirect('/register/')


# HOME
@login_required(login_url='/login/')
def home(request):
    q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()

    products = Product.objects.all().select_related('category')

    if q:
        products = products.filter(name__icontains=q)

    if category_id and category_id.isdigit():
        products = products.filter(category_id=int(category_id))

    categories = Category.objects.all()

    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
        'query': q,
        'selected_category': category_id,
    })


# PRODUCT DETAILS
@login_required(login_url='/login/')
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_details.html', {
        'product': product
    })


# ADD TO CART
@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        return redirect('/home/')

    cart_item, created = Cart.objects.get_or_create(
        product=product,
        user=request.user,
        defaults={'quantity': 1}
    )

    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()

    return redirect('/cart/')


# CART
@login_required(login_url='/login/')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('product')

    total = 0
    for item in cart_items:
        item.line_total = item.product.price * item.quantity
        total += item.line_total

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


# INCREASE QTY
@login_required(login_url='/login/')
def increase_quantity(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id, user=request.user)

    if item.quantity < item.product.stock:
        item.quantity += 1
        item.save()

    return redirect('/cart/')


# DECREASE QTY
@login_required(login_url='/login/')
def decrease_quantity(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id, user=request.user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('/cart/')


# REMOVE ITEM
@login_required(login_url='/login/')
def remove_from_cart(request, cart_id):
    item = get_object_or_404(Cart, id=cart_id, user=request.user)
    item.delete()

    return redirect('/cart/')


# CHECKOUT
@login_required(login_url='/login/')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('product')

    if not cart_items.exists():
        return redirect('/cart/')

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not customer_name or not phone or not address:
            return render(request, 'checkout.html', {
                'error': 'All fields (Name, Phone, Address) are required.'
            })

        # Stock check
        for item in cart_items:
            if item.quantity > item.product.stock:
                return render(request, 'checkout.html', {
                    'error': f"Insufficient stock for {item.product.name}. Available: {item.product.stock}"
                })

        total = sum(item.product.price * item.quantity for item in cart_items)

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                customer_name=customer_name,
                phone=phone,
                address=address,
                total_amount=total
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                # Deduct stock
                item.product.stock -= item.quantity
                item.product.save()

            cart_items.delete()

        return redirect('/success/')

    return render(request, 'checkout.html')


# SUCCESS
@login_required(login_url='/login/')
def success(request):
    return render(request, 'success.html')


# REGISTER
def register(request):
    if request.user.is_authenticated:
        return redirect('/home/')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        email = request.POST.get('email', '').strip()

        if not username or not password:
            return render(request, 'register.html', {
                'error': 'Username and Password are required.'
            })

        if User.objects.filter(username__iexact=username).exists():
            return render(request, 'register.html', {
                'error': 'Username already exists. Please login instead.'
            })

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('/login/')

    return render(request, 'register.html')


# LOGIN
def user_login(request):
    if request.user.is_authenticated:
        return redirect('/home/')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('/home/')

        return render(request, 'login.html', {
            'error': 'Invalid Username or Password'
        })

    return render(request, 'login.html')


# LOGOUT
def user_logout(request):
    logout(request)
    return redirect('/login/')


# PROFILE
@login_required(login_url='/login/')
def profile(request):
    return render(request, 'profile.html')


# ORDERS
@login_required(login_url='/login/')
def orders(request):
    all_orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-id')

    return render(request, 'orders.html', {
        'orders': all_orders
    })


# DELETE / CANCEL ORDER
@login_required(login_url='/login/')
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.delete()

    return redirect('/orders/')