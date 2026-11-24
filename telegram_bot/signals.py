from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from nomdor.models import Order
from .notify import send_status


@receiver(pre_save, sender=Order)
def remember_old_status(sender, instance, **kwargs):
    if instance.pk:
        old = Order.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
        instance._old_status = old
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def notify_status_change(sender, instance, created, **kwargs):
    if created:
        return
    if instance._old_status != instance.status:
        send_status(instance)