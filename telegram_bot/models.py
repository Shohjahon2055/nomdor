from django.db import models
from nomdor.models import Product


class CartItem(models.Model):
    telegram_id = models.BigIntegerField(db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("telegram_id", "product")

    def __str__(self):
        return f"{self.telegram_id}: {self.product.name} x{self.quantity}"