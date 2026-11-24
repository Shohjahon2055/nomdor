import requests
from django.conf import settings

STATUS_TEXTS = {
    "preparing": "👨‍🍳 Buyurtmangiz #{id} tayyorlanmoqda",
    "delivering": "🚚 Buyurtmangiz #{id} yo'lda",
    "done": "✅ Buyurtmangiz #{id} yakunlandi. Yoqimli ishtaha! 🍽",
    "canceled": "❌ Buyurtmangiz #{id} bekor qilindi",
}


def send_status(order):
    text = STATUS_TEXTS.get(order.status)
    if not text or not order.telegram_id:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage",
            json={"chat_id": order.telegram_id, "text": text.format(id=order.id)},
            timeout=5,
        )
    except requests.RequestException:
        pass


def send_new_order(order):
    chat_id = getattr(settings, "ADMIN_CHAT_ID", None)
    if not chat_id:
        return
    kind = "🚚 Yetkazib berish" if order.delivery_type == "delivery" else "🏃 Olib ketish"
    total = f"{int(order.total):,}".replace(",", " ")
    lines = [f"🆕 <b>Yangi buyurtma #{order.id}</b> ({order.get_source_display()})\n"]
    for i in order.items.all():
        lines.append(f"{i.name} × {i.quantity}")
    lines.append(f"\n💰 <b>Jami: {total} so'm</b>")
    lines.append(f"\n{kind}\n👤 {order.name}\n📱 {order.phone}")
    if order.address:
        lines.append(f"📍 {order.address}")
    base = f"https://api.telegram.org/bot{settings.BOT_TOKEN}"
    try:
        requests.post(f"{base}/sendMessage", timeout=5, json={
            "chat_id": chat_id, "text": "\n".join(lines), "parse_mode": "HTML"})
        if order.latitude is not None and order.longitude is not None:
            requests.post(f"{base}/sendLocation", timeout=5, json={
                "chat_id": chat_id,
                "latitude": float(order.latitude),
                "longitude": float(order.longitude)})
    except requests.RequestException:
        pass