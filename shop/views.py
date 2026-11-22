from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import ContactForm, CheckoutForm
from .models import Category, Product, OrderItem

def home(request):
    categories = Category.objects.filter(is_active=True)
    featured = Product.objects.filter(is_active=True, is_featured=True).select_related("brand", "category")[:8]
    latest = Product.objects.filter(is_active=True).select_related("brand", "category")[:8]
    return render(request, "shop/home.html", {"categories": categories, "featured": featured, "latest": latest})

def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("brand", "category")
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "newest")
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(sku__icontains=q) |
            Q(technical_code__icontains=q) | Q(description__icontains=q) |
            Q(brand__name__icontains=q)
        )
    if category.isdigit():
        products = products.filter(category_id=int(category))
    if sort == "price_asc":
        products = products.order_by("price", "-created_at")
    elif sort == "price_desc":
        products = products.order_by("-price", "-created_at")
    elif sort == "name":
        products = products.order_by("name")
    categories = Category.objects.filter(is_active=True)
    return render(request, "shop/product_list.html", {
        "products": products, "categories": categories, "q": q,
        "selected_category": category, "sort": sort,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("brand", "category"), slug=slug, is_active=True)
    return render(request, "shop/product_detail.html", {"product": product})

def _cart_rows(request):
    cart = request.session.get("cart", {})
    ids = [int(k) for k in cart.keys() if str(k).isdigit()]
    products = Product.objects.filter(id__in=ids, is_active=True)
    rows, total = [], 0
    for product in products:
        qty = max(1, int(cart.get(str(product.id), 1)))
        line = (product.price or 0) * qty
        rows.append({"product": product, "quantity": qty, "line_total": line})
        total += line
    return rows, total

def cart_detail(request):
    rows, total = _cart_rows(request)
    return render(request, "shop/cart.html", {"rows": rows, "total": total})

@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = request.session.get("cart", {})
    current = int(cart.get(str(product.id), 0))
    if product.stock <= current:
        messages.error(request, "موجودی کافی نیست.")
    else:
        cart[str(product.id)] = current + 1
        request.session["cart"] = cart
        messages.success(request, "محصول به سبد خرید اضافه شد.")
    return redirect(request.POST.get("next") or "shop:cart")

@require_POST
def cart_update(request, product_id):
    cart = request.session.get("cart", {})
    product = get_object_or_404(Product, id=product_id)
    try:
        qty = int(request.POST.get("quantity", "1"))
    except ValueError:
        qty = 1
    if qty <= 0:
        cart.pop(str(product_id), None)
    elif qty <= product.stock:
        cart[str(product_id)] = qty
    else:
        messages.error(request, "تعداد درخواستی بیشتر از موجودی است.")
    request.session["cart"] = cart
    return redirect("shop:cart")

def checkout(request):
    rows, total = _cart_rows(request)
    if not rows:
        messages.info(request, "سبد خرید شما خالی است.")
        return redirect("shop:product_list")
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Lock rows where supported; re-check stock before creating order.
                locked = {p.id: p for p in Product.objects.select_for_update().filter(id__in=[r["product"].id for r in rows])}
                for row in rows:
                    p = locked.get(row["product"].id)
                    if not p or p.stock < row["quantity"]:
                        messages.error(request, f"موجودی «{row['product'].name}» کافی نیست.")
                        return redirect("shop:cart")
                order = form.save(commit=False)
                order.total = total
                order.save()
                for row in rows:
                    p = locked[row["product"].id]
                    OrderItem.objects.create(order=order, product=p, product_name=p.name,
                                             unit_price=p.price or 0, quantity=row["quantity"])
                    p.stock -= row["quantity"]
                    p.save(update_fields=["stock"])
            request.session["cart"] = {}
            return render(request, "shop/order_success.html", {"order": order})
    else:
        form = CheckoutForm()
    return render(request, "shop/checkout.html", {"form": form, "rows": rows, "total": total})

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "پیام شما ثبت شد. با شما تماس می‌گیریم.")
            return redirect("shop:contact")
    else:
        form = ContactForm()
    return render(request, "shop/contact.html", {"form": form})
