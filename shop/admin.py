from django.contrib import admin
from .models import Category, Brand, CarModel, Product, Order, OrderItem

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category', 'brand')
    search_fields = ('name', 'oem_code')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone', 'status', 'total_price')
    list_filter = ('status',)

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(CarModel)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)