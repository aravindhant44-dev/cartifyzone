from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Cart, Order

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required



# FIRST PAGE -> REGISTER
def first_page(request):
    if request.user.is_authenticated:
        return redirect('/home/')
    return redirect('/register/')

# HOME
@login_required(login_url='/login/')
def home(request):

    q = request.GET.get('q')
    category_id = request.GET.get('category')

    products = Product.objects.all()

    if q:
        products = products.filter(name__icontains=q)

    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()

    return render(request, 'home.html', {
        'products': products,
        'categories': categories
    })


# PRODUCT DETAILS
@login_required(login_url='/login/')
def product_detail(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    return render(request, 'product_details.html', {
        'product': product
    })
# DELETE / CANCEL ORDER
@login_required(login_url='/login/')
def delete_order(request, order_id):

    order = Order.objects.get(id=order_id)
    order.delete()

    return redirect('/orders/')

# ADD TO CART
@login_required(login_url='/login/')
def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('/cart/')


# CART
@login_required(login_url='/login/')
def cart(request):

    cart_items = Cart.objects.all()

    total = 0

    for item in cart_items:
        total += item.product.price * item.quantity

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


# INCREASE QTY
@login_required(login_url='/login/')
def increase_quantity(request, cart_id):

    item = get_object_or_404(Cart, id=cart_id)

    item.quantity += 1
    item.save()

    return redirect('/cart/')


# DECREASE QTY
@login_required(login_url='/login/')
def decrease_quantity(request, cart_id):

    item = get_object_or_404(Cart, id=cart_id)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('/cart/')


# REMOVE ITEM
@login_required(login_url='/login/')
def remove_from_cart(request, cart_id):

    item = get_object_or_404(Cart, id=cart_id)
    item.delete()

    return redirect('/cart/')


# CHECKOUT
@login_required(login_url='/login/')
def checkout(request):

    if request.method == 'POST':

        customer_name = request.POST['customer_name']
        phone = request.POST['phone']
        address = request.POST['address']

        cart_items = Cart.objects.all()

        total = 0

        for item in cart_items:
            total += item.product.price * item.quantity

        Order.objects.create(
            customer_name=customer_name,
            phone=phone,
            address=address,
            total_amount=total
        )

        Cart.objects.all().delete()

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

        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            return render(
                request,
                'register.html',
                {
                    'error': 'Username already exists. Please login instead.',
                }
            )

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('/login/')

    return render(request, 'register.html')

# LOGIN
def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)
            return redirect('/home/')

        return render(
            request,
            'login.html',
            {'error': 'Invalid Username or Password'}
        )

    return render(request, 'login.html')


# LOGOUT
def user_logout(request):

    logout(request)
    return redirect('/login/')

from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    return render(request, 'profile.html')


@login_required(login_url='/login/')
def orders(request):
    all_orders = Order.objects.all().order_by('-id')

    return render(request, 'orders.html', {
        'orders': all_orders
    })