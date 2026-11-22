from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField("نام دسته", max_length=100)
    slug = models.SlugField(unique=True, blank=True, allow_unicode=True)
    description = models.TextField("توضیحات", blank=True)
    image = models.ImageField("تصویر دسته", upload_to="categories/", blank=True)
    is_active = models.BooleanField("فعال", default=True)
    sort_order = models.PositiveIntegerField("ترتیب نمایش", default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField("نام برند", max_length=100, unique=True)
    logo = models.ImageField("لوگو", upload_to="brands/", blank=True)
    website = models.URLField("وب‌سایت", blank=True)

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    make = models.CharField("سازنده", max_length=80)
    model = models.CharField("مدل", max_length=80)
    year_from = models.PositiveSmallIntegerField("از سال", null=True, blank=True)
    year_to = models.PositiveSmallIntegerField("تا سال", null=True, blank=True)
    trim = models.CharField("تیپ/موتور", max_length=100, blank=True)

    class Meta:
        ordering = ["make", "model"]
        verbose_name = "خودرو"
        verbose_name_plural = "خودروهای سازگار"

    def __str__(self):
        return f"{self.make} {self.model} {self.trim}".strip()

class Product(models.Model):
    name = models.CharField("نام محصول", max_length=180)
    slug = models.SlugField(unique=True, blank=True, allow_unicode=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products", verbose_name="دسته")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="برند")
    sku = models.CharField("کد کالا", max_length=80, blank=True, db_index=True)
    technical_code = models.CharField("کد فنی", max_length=100, blank=True, db_index=True)
    description = models.TextField("توضیحات", blank=True)
    specifications = models.JSONField("مشخصات فنی (JSON)", default=dict, blank=True)
    compatible_vehicles = models.ManyToManyField(Vehicle, blank=True, verbose_name="خودروهای سازگار")
    price = models.PositiveBigIntegerField("قیمت (تومان)", null=True, blank=True)
    stock = models.PositiveIntegerField("موجودی", default=0)
    image = models.ImageField("تصویر اصلی", upload_to="products/", blank=True)
    is_active = models.BooleanField("نمایش در فروشگاه", default=True)
    is_featured = models.BooleanField("محصول منتخب", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField("تصویر", upload_to="products/gallery/")
    alt_text = models.CharField("متن جایگزین", max_length=180, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصولات"

class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "جدید"), ("confirmed", "تأیید شده"),
        ("processing", "در حال آماده‌سازی"), ("sent", "ارسال شده"),
        ("delivered", "تحویل شده"), ("cancelled", "لغو شده"),
    ]
    customer_name = models.CharField("نام مشتری", max_length=120)
    phone = models.CharField("شماره تماس", max_length=20)
    province_city = models.CharField("شهر", max_length=100)
    address = models.TextField("نشانی")
    postal_code = models.CharField("کد پستی", max_length=20, blank=True)
    notes = models.TextField("توضیحات", blank=True)
    status = models.CharField("وضعیت", max_length=20, choices=STATUS_CHOICES, default="new")
    total = models.PositiveBigIntegerField("مبلغ کل (تومان)", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"

    def __str__(self):
        return f"سفارش #{self.pk} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=180)
    unit_price = models.PositiveBigIntegerField()
    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name = "قلم سفارش"
        verbose_name_plural = "اقلام سفارش"

class ContactMessage(models.Model):
    name = models.CharField("نام", max_length=100)
    phone = models.CharField("شماره تماس", max_length=20)
    message = models.TextField("پیام")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField("خوانده شده", default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "پیام مشتری"
        verbose_name_plural = "پیام‌های مشتریان"

    def __str__(self):
        return f"{self.name} - {self.phone}"
