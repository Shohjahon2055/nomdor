import io
import os
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, FSInputFile, BufferedInputFile
from asgiref.sync import sync_to_async
from django.conf import settings
from PIL import Image

from nomdor.models import Category, Product, Order
from nomdor.services import create_order
from .models import CartItem
from .keyboards import (
    main_menu, categories_kb, products_kb, product_kb, cart_kb,
    delivery_kb, phone_kb, location_kb, confirm_kb, fmt,
)

router = Router()


class OrderForm(StatesGroup):
    phone = State()
    location = State()
    confirm = State()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Assalomu alaykum! Nomdor restoraniga xush kelibsiz 🍽",
        reply_markup=main_menu(),
    )


# ---------- MENYU ----------

async def get_categories():
    qs = Category.objects.filter(products__is_available=True).distinct()
    return [c async for c in qs]


@router.message(F.text == "🍽 Menyu")
async def show_menu(message: Message):
    categories = await get_categories()
    if not categories:
        return await message.answer("Hozircha menyu bo'sh.")
    await message.answer("Kategoriyani tanlang:", reply_markup=categories_kb(categories))


@router.callback_query(F.data == "menu")
async def back_to_menu(call: CallbackQuery):
    categories = await get_categories()
    await call.message.delete()
    await call.message.answer("Kategoriyani tanlang:", reply_markup=categories_kb(categories))
    await call.answer()


def resolve_image_path(image_field):
    if not image_field:
        return None

    name = (getattr(image_field, "name", "") or "").lstrip("/\\")
    if not name:
        return None

    base = os.path.basename(name)
    base_lower = base.lower()

    candidates = [
        os.path.join(str(settings.MEDIA_ROOT), name),
        os.path.join("/app/media", name),
        os.path.join("/app/products", base),
        os.path.join("/app/products", name),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path

    for search_dir in ("/app/products", "/app/media"):
        if not os.path.isdir(search_dir):
            continue
        for root, _, files in os.walk(search_dir):
            for f in files:
                if f.lower() == base_lower:
                    return os.path.join(root, f)

    return None

def make_photo_input(img_path: str):
    if img_path.lower().endswith(".webp"):
        with Image.open(img_path) as im:
            rgb = im.convert("RGB")
            buf = io.BytesIO()
            rgb.save(buf, format="JPEG", quality=90)
            buf.seek(0)
            filename = os.path.splitext(os.path.basename(img_path))[0] + ".jpg"
            return BufferedInputFile(buf.read(), filename=filename)
    return FSInputFile(img_path)


@router.callback_query(F.data.startswith("cat:"))
async def show_category(call: CallbackQuery):
    cat_id = int(call.data.split(":")[1])
    products = [p async for p in Product.objects.filter(category_id=cat_id, is_available=True)]
    await call.message.delete()
    await call.message.answer("Taomni tanlang:", reply_markup=products_kb(products))
    await call.answer()


@router.callback_query(F.data.startswith("prod:"))
async def show_product(call: CallbackQuery):
    pid = int(call.data.split(":")[1])
    product = await Product.objects.filter(id=pid).afirst()
    if not product:
        return await call.answer("Mahsulot topilmadi", show_alert=True)

    text = f"<b>{product.name}</b>\n\n{product.description}\n\n💰 {fmt(product.price)}"
    kb = product_kb(product)
    img_path = resolve_image_path(product.image)

    photo_sent = False
    if img_path:
        try:
            photo_file = make_photo_input(img_path)
            await call.message.answer_photo(
                photo=photo_file,
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
            photo_sent = True
        except Exception as e:
            print(f"[show_product] answer_photo xato ({img_path}): {e!r}")

    if not photo_sent:
        await call.message.answer(text, parse_mode="HTML", reply_markup=kb)

    try:
        await call.message.delete()
    except Exception:
        pass

    await call.answer()


# ---------- SAVAT ----------

async def get_cart(uid):
    qs = CartItem.objects.filter(telegram_id=uid).select_related("product").order_by("id")
    return [i async for i in qs]


def cart_text(items):
    lines = ["🛒 <b>Savatingiz:</b>\n"]
    total = 0
    for i in items:
        sub = i.product.price * i.quantity
        total += sub
        lines.append(f"{i.product.name} × {i.quantity} = {fmt(sub)}")
    lines.append(f"\n<b>Jami: {fmt(total)}</b>")
    return "\n".join(lines)


@router.callback_query(F.data.startswith("add:"))
async def add_to_cart(call: CallbackQuery):
    pid = int(call.data.split(":")[1])
    product = await Product.objects.filter(id=pid, is_available=True).afirst()
    if not product:
        return await call.answer("Bu taom hozir mavjud emas", show_alert=True)
    item, created = await CartItem.objects.aget_or_create(
        telegram_id=call.from_user.id, product=product, defaults={"quantity": 1}
    )
    if not created:
        item.quantity += 1
        await item.asave()
    await call.answer(f"✅ {product.name} savatga qo'shildi")


@router.message(F.text == "🛒 Savat")
async def show_cart(message: Message):
    items = await get_cart(message.from_user.id)
    if not items:
        return await message.answer("Savatingiz bo'sh 🛒")
    await message.answer(cart_text(items), parse_mode="HTML", reply_markup=cart_kb(items))


async def refresh_cart(call: CallbackQuery):
    items = await get_cart(call.from_user.id)
    if not items:
        await call.message.edit_text("Savatingiz bo'sh 🛒")
    else:
        await call.message.edit_text(
            cart_text(items), parse_mode="HTML", reply_markup=cart_kb(items)
        )


@router.callback_query(F.data.startswith("inc:"))
async def inc(call: CallbackQuery):
    pid = int(call.data.split(":")[1])
    item = await CartItem.objects.filter(telegram_id=call.from_user.id, product_id=pid).afirst()
    if item:
        item.quantity += 1
        await item.asave()
    await refresh_cart(call)
    await call.answer()


@router.callback_query(F.data.startswith("dec:"))
async def dec(call: CallbackQuery):
    pid = int(call.data.split(":")[1])
    item = await CartItem.objects.filter(telegram_id=call.from_user.id, product_id=pid).afirst()
    if item:
        item.quantity -= 1
        if item.quantity <= 0:
            await item.adelete()
        else:
            await item.asave()
    await refresh_cart(call)
    await call.answer()


@router.callback_query(F.data == "clear")
async def clear(call: CallbackQuery):
    await CartItem.objects.filter(telegram_id=call.from_user.id).adelete()
    await call.message.edit_text("Savat tozalandi 🗑")
    await call.answer()


@router.callback_query(F.data == "noop")
async def noop(call: CallbackQuery):
    await call.answer()


# ---------- BUYURTMA BERISH ----------

@router.callback_query(F.data == "checkout")
async def checkout(call: CallbackQuery):
    items = await get_cart(call.from_user.id)
    if not items:
        return await call.answer("Savat bo'sh", show_alert=True)
    await call.message.answer("Qanday olasiz?", reply_markup=delivery_kb())
    await call.answer()


@router.callback_query(F.data.startswith("dt:"))
async def choose_delivery(call: CallbackQuery, state: FSMContext):
    await state.update_data(delivery_type=call.data.split(":")[1])
    await state.set_state(OrderForm.phone)
    await call.message.answer("Telefon raqamingizni yuboring:", reply_markup=phone_kb())
    await call.answer()


@router.message(OrderForm.phone, F.contact)
async def got_phone(message: Message, state: FSMContext):
    await state.update_data(
        phone=message.contact.phone_number, name=message.from_user.full_name
    )
    data = await state.get_data()
    if data["delivery_type"] == "delivery":
        await state.set_state(OrderForm.location)
        await message.answer(
            "Yetkazib berish manzilini yuboring (lokatsiya tugmasi yoki matn bilan yozing):",
            reply_markup=location_kb(),
        )
    else:
        await show_confirm(message, state)


@router.message(OrderForm.phone)
async def phone_text(message: Message):
    await message.answer(
        "Iltimos, pastdagi tugma orqali raqamni yuboring 👇", reply_markup=phone_kb()
    )


@router.message(OrderForm.location, F.location)
async def got_location(message: Message, state: FSMContext):
    await state.update_data(
        lat=message.location.latitude, lon=message.location.longitude, address="Lokatsiya"
    )
    await show_confirm(message, state)


@router.message(OrderForm.location, F.text)
async def got_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text, lat=None, lon=None)
    await show_confirm(message, state)


async def show_confirm(message: Message, state: FSMContext):
    data = await state.get_data()
    items = await get_cart(message.from_user.id)
    kind = "🚚 Yetkazib berish" if data["delivery_type"] == "delivery" else "🏃 Olib ketish"
    text = cart_text(items) + f"\n\n{kind}\n📱 {data['phone']}"
    if data.get("address"):
        text += f"\n📍 {data['address']}"
    await state.set_state(OrderForm.confirm)
    await message.answer("Ma'lumotlar qabul qilindi", reply_markup=main_menu())
    await message.answer(text, parse_mode="HTML", reply_markup=confirm_kb())


@router.callback_query(OrderForm.confirm, F.data == "confirm")
async def confirm_order(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    items = await get_cart(call.from_user.id)
    if not items:
        await state.clear()
        return await call.answer("Savat bo'sh", show_alert=True)

    order = await sync_to_async(create_order)(
        items=[(i.product, i.quantity) for i in items],
        phone=data["phone"], name=data.get("name", ""),
        delivery_type=data["delivery_type"], source=Order.Source.BOT,
        address=data.get("address", ""),
        latitude=data.get("lat"), longitude=data.get("lon"),
        telegram_id=call.from_user.id,
    )
    await CartItem.objects.filter(telegram_id=call.from_user.id).adelete()
    await state.clear()

    lines = [f"✅ <b>Buyurtma #{order.id} qabul qilindi!</b>\n"]
    for i in items:
        lines.append(f"{i.product.name} × {i.quantity} = {fmt(i.product.price * i.quantity)}")
    lines.append(f"\n<b>Jami: {fmt(order.total)}</b>")
    kind = "🚚 Yetkazib berish" if order.delivery_type == "delivery" else "🏃 Olib ketish"
    lines.append(f"\n{kind}\n📱 {order.phone}")
    if order.address:
        lines.append(f"📍 {order.address}")
    lines.append("\nTez orada siz bilan bog'lanamiz. Rahmat! 🍽")
    await call.message.edit_text("\n".join(lines), parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data == "cancel")
async def cancel_order(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("Buyurtma bekor qilindi.")
    await call.answer()


# ---------- BUYURTMALARIM ----------

STATUS_LABELS = {
    "new": "🆕 Yangi",
    "preparing": "👨‍🍳 Tayyorlanmoqda",
    "delivering": "🚚 Yo'lda",
    "done": "✅ Yakunlandi",
    "canceled": "❌ Bekor qilindi",
}


async def get_orders(uid):
    qs = (
        Order.objects.filter(telegram_id=uid)
        .prefetch_related("items")
        .order_by("-created_at")[:5]
    )
    return [o async for o in qs]


@router.message(F.text == "📦 Buyurtmalarim")
async def my_orders(message: Message):
    orders = await get_orders(message.from_user.id)
    if not orders:
        return await message.answer("Sizda hali buyurtmalar yo'q 📦")

    for o in orders:
        lines = [
            f"📦 <b>Buyurtma #{o.id}</b>",
            f"{STATUS_LABELS.get(o.status, o.status)}",
            f"🕒 {o.created_at:%d.%m.%Y %H:%M}\n",
        ]
        for i in o.items.all():
            lines.append(f"{i.name} × {i.quantity}")
        lines.append(f"\n<b>Jami: {fmt(o.total)}</b>")
        await message.answer("\n".join(lines), parse_mode="HTML")