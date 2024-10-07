from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Orqaga qaytish tugmasi
back_to_users = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="⬅️ Orqaga qaytish", callback_data="to_back")
    ]
])



# Admin uchun dillerlarni tahrirlash funksiyasi tugmalari 
def edit_users_keyboard(users_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"users_edit_{users_id}"),
            InlineKeyboardButton(text="🗑️ O'chirish", callback_data=f"delete_users_{users_id}"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ Ma'lumotlarni ko'rish", callback_data=f"view_users_{users_id}")
        ],
        [
            InlineKeyboardButton(text="⬅️ Orqaga qaytish", callback_data="to_back")  # Orqaga qaytish tugmasi
        ]
    ])
    return keyboard

# Foydalanuvchi uchun tahrirlash tugmalari yaratish funksiyasi
def edit_users_keyboard_user(user_id):
    keyboard_builder = InlineKeyboardBuilder()
    
    # Tugmalarni qo'shish (imojilar bilan)
    keyboard_builder.button(text="👤 Ism", callback_data=f"ttt_name_{user_id}")
    keyboard_builder.button(text="🌍 Region", callback_data=f"ttt_region_{user_id}")
    keyboard_builder.button(text="🏢 Tuman", callback_data=f"ttt_district_{user_id}")
    keyboard_builder.button(text="📍 Latitude", callback_data=f"ttt_latitude_{user_id}")
    keyboard_builder.button(text="📍 Longitude", callback_data=f"ttt_longitude_{user_id}")
    keyboard_builder.button(text="📞 Telefon", callback_data=f"ttt_phone_number_{user_id}")

    # Tugmalarni tartibga solish
    keyboard_builder.adjust(2)  # Har bir qatorda 2 ta tugma chiqadi

    # Orqaga qaytish tugmasi
    keyboard_builder.button(text="⬅️ Orqaga qaytish", callback_data="to_back")

    # Klaviaturani yig'ish
    return keyboard_builder.as_markup()
