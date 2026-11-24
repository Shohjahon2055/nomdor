from django.contrib import admin
from .models import Category, Product

admin.site.register(Category)
admin.site.register(Product)

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "source", "delivery_type", "total", "status", "created_at")
    list_filter = ("status", "source", "delivery_type")
    list_editable = ("status",)
    search_fields = ("name", "phone", "telegram_id")
    inlines = [OrderItemInline]

