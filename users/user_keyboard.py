from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import database


start_button = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)
    ]
],resize_keyboard=True, input_field_placeholder="Pastdagi tugmani bosing.👇", one_time_keyboard=True)



view_user_info = ReplyKeyboardMarkup(
    keyboard=[
        [
            
            KeyboardButton(text="Xarid qilgan maxsulotlar"),
            KeyboardButton(text="Bekor qilingan xaridlar")
        ],
        [
            KeyboardButton(text="ma'lumotlaringiz")
        ]
    ],
    resize_keyboard=True,
)



location_request_button = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📍 Joylashuvni yuborish", request_location=True)
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Joylashuv so'raydigan inline tugma
location_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📍 Joylashuvni yuboring", callback_data="user_send_location")],
    ]
)


user_contact = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💾 Malumotlarni saqlash", callback_data="user_save_data"),
            InlineKeyboardButton(text="🔄 Malumotlarni yangilash", callback_data="user_delete_data")
        ],
    ]
)

view_product_user_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Bizning mahsulotlarimizni ko'rishni xohlaysizmi", callback_data="view_product_user_key")],
        [InlineKeyboardButton(text="🛒 Savatchani ko'rish", callback_data="view_user_cart")]
    ])



def categories_user_keyboard(categories):
    buttons = [
        [InlineKeyboardButton(text=f"📂 {category[1]}", callback_data=f"view_category_{category[0]}")]
        for category in categories
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)




def product_user_keyboard(product_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Savatchaga qo'shish", callback_data=f"add_user_cart_{product_id}")]
        ]
    )

cart_user_product_view = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Savatchani ko'rish", callback_data="view_user_cart")]
    ]
)

cart_user_product = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Sotib olish", callback_data="checkout_user_cart")],
        [InlineKeyboardButton(text="🛍 Bizning mahsulotlarimizni ko'rishni xohlaysizmi", callback_data="view_product_user_key")]
    ]
)

# Admin userga javob yozishi uchun tugma
def admin_to_user_keyboard(user_id, user_name):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Userga javob yozish", callback_data=f"user_reply_to_admin_{user_id}_{user_name}")]
        ]
    )


def admin_order_keyboard(user_id, user_name):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_order_by_user_{user_id}_{user_name}")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"cancel_order_by_user_{user_id}_{user_name}")],
            [InlineKeyboardButton(text="✉️ Userga Javob yozish", callback_data=f"admin_reply_to_user_{user_id}_{user_name}")]
        ]
    )


# Admin javob berish tugmasi
admin_answer_to_user = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Adminga javob yozish", callback_data="admin_answer_to_user")]
    ]
)




