from django.contrib import admin
from .models import Category, Brand, Vehicle, Product, ProductImage, Order, OrderItem, ContactMessage

admin.site.site_header = "مرکز مدیریت گلشن"
admin.site.site_title = "مدیریت گلشن"
admin.site.index_title = "مدیریت فروشگاه لوازم برق خودرو"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    search_fields = ("name",)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("make", "model", "trim", "year_from", "year_to")
    search_fields = ("make", "model", "trim")

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "technical_code", "price", "stock", "is_active", "is_featured")
    list_filter = ("category", "brand", "is_active", "is_featured")
    search_fields = ("name", "sku", "technical_code", "description")
    list_editable = ("price", "stock", "is_active", "is_featured")
    filter_horizontal = ("compatible_vehicles",)
    inlines = [ProductImageInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "unit_price", "quantity")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "phone", "total", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("customer_name", "phone")
    list_editable = ("status",)
    inlines = [OrderItemInline]

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "is_read", "created_at")
    list_filter = ("is_read",)
    search_fields = ("name", "phone", "message")
