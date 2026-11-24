from django.db import transaction
from .models import Order, OrderItem


@transaction.atomic
def create_order(*, items, phone, delivery_type, source, name="", address="",
                 latitude=None, longitude=None, user=None, telegram_id=None):
    """items: [(product, quantity), ...]"""
    order = Order.objects.create(
        user=user, telegram_id=telegram_id, source=source, name=name,
        phone=phone, delivery_type=delivery_type, address=address,
        latitude=latitude, longitude=longitude,
    )
    total = 0
    for product, qty in items:
        OrderItem.objects.create(
            order=order, product=product, name=product.name,
            price=product.price, quantity=qty,
        )
        total += product.price * qty
    order.total = total
    order.save(update_fields=["total"])
    return order