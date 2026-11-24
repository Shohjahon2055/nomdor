from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍽 Menyu")],
            [KeyboardButton(text="🛒 Savat"), KeyboardButton(text="📦 Buyurtmalarim")],
        ],
        resize_keyboard=True,
    )


from aiogram.utils.keyboard import InlineKeyboardBuilder


def categories_kb(categories):
    kb = InlineKeyboardBuilder()
    for c in categories:
        kb.button(text=c.name, callback_data=f"cat:{c.id}")
    kb.adjust(2)
    return kb.as_markup()


def products_kb(products):
    kb = InlineKeyboardBuilder()
    for p in products:
        kb.button(text=f"{p.name} — {fmt(p.price)}", callback_data=f"prod:{p.id}")
    kb.button(text="⬅️ Kategoriyalar", callback_data="menu")
    kb.adjust(1)
    return kb.as_markup()


def product_kb(product):
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Savatga qo'shish", callback_data=f"add:{product.id}")
    kb.button(text="⬅️ Orqaga", callback_data=f"cat:{product.category_id}")
    kb.adjust(1)
    return kb.as_markup()


def cart_kb(items):
    kb = InlineKeyboardBuilder()
    for i in items:
        kb.button(text="➖", callback_data=f"dec:{i.product_id}")
        kb.button(text=f"{i.product.name} × {i.quantity}", callback_data="noop")
        kb.button(text="➕", callback_data=f"inc:{i.product_id}")
    kb.button(text="🗑 Tozalash", callback_data="clear")
    kb.button(text="✅ Buyurtma berish", callback_data="checkout")
    kb.adjust(*([3] * len(items)), 2)
    return kb.as_markup()


def fmt(price):
    return f"{int(price):,}".replace(",", " ") + " so'm"



from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def delivery_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚚 Yetkazib berish", callback_data="dt:delivery")
    kb.button(text="🏃 Olib ketish", callback_data="dt:pickup")
    kb.adjust(1)
    return kb.as_markup()


def phone_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True,
    )


def location_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)]],
        resize_keyboard=True, one_time_keyboard=True,
    )


def confirm_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Tasdiqlash", callback_data="confirm")
    kb.button(text="❌ Bekor qilish", callback_data="cancel")
    kb.adjust(2)
    return kb.as_markup()