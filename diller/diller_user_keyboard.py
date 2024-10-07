from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN


# Foydalanuvchidan telefon raqamni so'rash uchun tugma
start_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]
    ],
    resize_keyboard=True, 
    input_field_placeholder="Pastdagi tugmani bosing.👇", 
    one_time_keyboard=True
)

view_diller_info = ReplyKeyboardMarkup(
    keyboard=[
        [
            
            KeyboardButton(text="Tasdiqlangan buyurtmalar"),
            KeyboardButton(text="Bekor qilingan buyurtmalar")
        ],
        [
            KeyboardButton(text="Diller ma'lumotlari")
        ]
    ],
    resize_keyboard=True,
)

# Joylashuvni so'raydigan tugma
location_request_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Joylashuvni yuborish", request_location=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# MCHJ so'rovi uchun inline tugma
mchj_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data="mchj_ha"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="mchj_yoq"),
        ],
    ]
)

# Joylashuvni so'raydigan inline tugma
location_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📍 Joylashuvni yuboring", callback_data="send_location")],
    ]
)

# Admin bilan bog'lanish tugmasi
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👨‍💼 Admin bilan bog'lanish", url=f"https://t.me/{ADMIN}")]
    ]
)

# Diller ma'lumotlarini boshqarish uchun tugmalar
diller_contact = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💾 Ma'lumotlarni saqlash", callback_data="diller_save_data"),
            InlineKeyboardButton(text="🔄 Ma'lumotlarni yangilash", callback_data="diller_delete_data")
        ],
    ]
)

# Kategoriya tanlash tugmalari
def categories_diller_keyboard(categories):
    buttons = [
        [InlineKeyboardButton(text=f"📂 {category[1]}", callback_data=f"view_ctd_{category[0]}")]
        for category in categories
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Mahsulotlarni ko'rish tugmasi
view_product_diller_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Bizning mahsulotlarimizni ko'rishni xohlaysizmi", callback_data="view_product_diller_key")],
        [InlineKeyboardButton(text="🛒 Savatchani ko'rish", callback_data="view_diller_cart")]
    ]
)

# Mahsulot qo'shish tugmasi
def product_diller_keyboard(product_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Savatchaga qo'shish", callback_data=f"add_diller_cart_{product_id}")]
        ]
    )

# Savatchani ko'rish tugmasi
cart_diller_product_view = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Savatchani ko'rish", callback_data="view_diller_cart")]
    ]
)

# Savatchani sotib olish tugmasi
cart_diller_product = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Buyurtma qilish", callback_data="checkout_diller_cart")]
    ]
)

# Admin buyurtmani tasdiqlash yoki bekor qilish tugmalari
def admin_order_diller_keyboard(user_id, diller_name):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_ord_by_diller_{user_id}_{diller_name}")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"cancel_ord_by_diller_{user_id}_{diller_name}")],
            [InlineKeyboardButton(text="✉️ Dillerga Javob yozish", callback_data=f"admin_reply_to_diller_{user_id}_{diller_name}")]
        ]
    )

# Admin javob berish tugmasi
admin_answer = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Adminga javob yozish", callback_data="admin_answer_to_diller")]
    ]
)

# Admin dillerga javob yozishi uchun tugma
def admin_to_diller_keyboard(user_id, diller_name):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Dillerga javob yozish", callback_data=f"admin_reply_to_diller_{user_id}_{diller_name}")]
        ]
    )

# Dillerga xabar yuborish tugmasi
def send_to_message_diller(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📤 Yuborish", callback_data=f"send_to_diller_{user_id}")]
        ]
    )

# Adminning dillerga javob berish tugmasi
def admin_diller_reply_keyboard(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Dillerga javob berish", callback_data=f"reply_diller_{user_id}")]
        ]
    )

# Dillerning adminga javob berish tugmasi
def diller_reply_keyboard(admin_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Adminga javob berish", callback_data=f"diller_admin_{admin_id}")]
        ]
    )
