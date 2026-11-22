from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(unique=True, allow_unicode=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="تصویر دسته")
    
    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
    def __str__(self): return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام برند")
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    
    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"
    def __str__(self): return self.name

class CarModel(models.Model):
    brand = models.CharField(max_length=50, verbose_name="برند خودرو (مثلاً پژو)")
    model_name = models.CharField(max_length=50, verbose_name="مدل خودرو (مثلاً ۲۰۶)")
    year = models.CharField(max_length=50, verbose_name="سال ساخت", blank=True, null=True)
    
    class Meta:
        verbose_name = "مدل خودرو"
        verbose_name_plural = "مدل‌های خودرو"
    def __str__(self): return f"{self.brand} {self.model_name} ({self.year})"

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام محصول")
    slug = models.SlugField(unique=True, allow_unicode=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    
    oem_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="کد فنی / OEM")
    description = models.TextField(verbose_name="توضیحات")
    
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت اصلی (تومان)")
    discount_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name="قیمت با تخفیف")
    stock = models.IntegerField(default=0, verbose_name="موجودی انبار")
    
    main_image = models.ImageField(upload_to='products/', verbose_name="تصویر اصلی")
    compatible_cars = models.ManyToManyField(CarModel, blank=True, related_name='compatible_products')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self): return self.name
        
    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('processing', 'در حال آماده‌سازی'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل شده'),
        ('canceled', 'لغو شده'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=50, verbose_name="نام")
    last_name = models.CharField(max_length=50, verbose_name="نام خانوادگی")
    phone = models.CharField(max_length=15, verbose_name="شماره تماس")
    address = models.TextField(verbose_name="آدرس دقیق")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    total_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="مبلغ کل")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"
    def __str__(self): return f"Order {self.id} - {self.phone}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self): return f"{self.product.name} x {self.quantity}"