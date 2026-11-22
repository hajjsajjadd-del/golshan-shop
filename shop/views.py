from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Category, CarModel, Order, OrderItem

def home(request):
    categories = Category.objects.filter(parent=None)[:8]
    products = Product.objects.all().order_by('-created_at')[:8]
    return render(request, 'index.html', {'categories': categories, 'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'product_detail.html', {'product': product})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    pid = str(product.id)
    if pid in cart:
        cart[pid]['quantity'] += 1
    else:
        cart[pid] = {'name': product.name, 'price': int(product.final_price), 'quantity': 1}
    
    request.session['cart'] = cart
    messages.success(request, f'{product.name} به سبد خرید اضافه شد.')
    return redirect('cart_view')

def cart_view(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render(request, 'cart.html', {'cart': cart, 'total': total})

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        request.session['cart'] = cart
    return redirect('cart_view')

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('home')
        
    if request.method == 'POST':
        total = sum(item['price'] * item['quantity'] for item in cart.values())
        order = Order.objects.create(
            first_name=request.POST.get('fname'),
            last_name=request.POST.get('lname'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            total_price=total
        )
        for pid, item in cart.items():
            OrderItem.objects.create(
                order=order,
                product_id=pid,
                price=item['price'],
                quantity=item['quantity']
            )
        request.session['cart'] = {} 
        return render(request, 'cart.html', {'success': True, 'order_id': order.id})

    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render(request, 'checkout.html', {'cart': cart, 'total': total})