from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton



user_product_button = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📂 Kategoriyalar"),
            KeyboardButton(text="🛍️ Maxsulotlar"),
        ],
        [   
            KeyboardButton(text="🤝 Diller"),
            KeyboardButton(text="👤 User"),
            KeyboardButton(text="📊 Statistika"),
        ]
    ], resize_keyboard=True
)


# View Category Button
view_category_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Kategoriya qo'shish", callback_data="add_category"),
            InlineKeyboardButton(text="📋 Kategoriyalarni ko'rish", callback_data="view_category"),
        ],
    ]
)

# View User Product Button
view_user_product_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🛒 Foydalanuvchi uchun Maxsulot qo'shish", callback_data="add_product"),
            InlineKeyboardButton(text="🏪 Diller uchun maxsulot qo'shish", callback_data="add_diller_product"),
        ],
        [
            InlineKeyboardButton(text="👥 Foydalanuvchi maxsulotlarni ko'rish", callback_data="view_product"),
            InlineKeyboardButton(text="📦 Dilller maxsulotlarni ko'rish", callback_data="diller_view_product"),
        ],
    ]
)