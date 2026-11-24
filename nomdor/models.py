from django.db import models
from accounts.models import CustomUser

# Create your models here.


class About(models.Model):
    title=models.CharField(max_length=200)
    description=models.TextField()

    def __str__(self):
        return self.title

class Category(models.Model):
    name=models.CharField(max_length=200)


    def __str__(self):
        return self.name

class Product(models.Model):
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name='products')
    name=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    image=models.ImageField(upload_to='Media/',blank=True,null=True)

    is_available=models.BooleanField(default=True)
    likes=models.ManyToManyField(CustomUser,through='like',related_name='liked_posts')

    def __str__(self):
        return self.name

class Like(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} likes {self.product.name}"


class Promotion(models.Model):
    title=models.CharField(max_length=200)
    description=models.TextField()

class Vacancy(models.Model):
    title=models.CharField(max_length=200)
    description=models.TextField()
    salary=models.DecimalField(max_digits=10,decimal_places=2)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title


class Branch(models.Model):
    title=models.CharField(max_length=200)
    adress=models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return self.title


class Contact(models.Model):
    name=models.CharField(max_length=200)
    phone=models.CharField(max_length=200)
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Yangi"
        PREPARING = "preparing", "Tayyorlanmoqda"
        DELIVERING = "delivering", "Yo'lda"
        DONE = "done", "Yakunlandi"
        CANCELED = "canceled", "Bekor qilindi"

    class DeliveryType(models.TextChoices):
        DELIVERY = "delivery", "Yetkazib berish"
        PICKUP = "pickup", "Olib ketish"

    class Source(models.TextChoices):
        SITE = "site", "Sayt"
        BOT = "bot", "Telegram bot"

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    telegram_id = models.BigIntegerField(null=True, blank=True)
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.SITE)
    name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20)
    delivery_type = models.CharField(max_length=10, choices=DeliveryType.choices)
    address = models.CharField(max_length=300, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Buyurtma #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} x{self.quantity}"