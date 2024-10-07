from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN
from aiogram.utils.keyboard import InlineKeyboardBuilder



# Diller uchun inline tugmalar yaratish funksiyasi
def edit_diller_keyboard(diller_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"diller_edit_{diller_id}"),
            InlineKeyboardButton(text="🗑️ O'chirish", callback_data=f"delete_diller_{diller_id}"),
        ],
        [
            InlineKeyboardButton(text="ℹ️ Ma'lumotlarni ko'rish", callback_data=f"view_diller_{diller_id}")
        ]
    ])
    return keyboard


back_to = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="⬅️ Orqaga qaytish", callback_data="back")
    ]
])











# Diller uchun inline tugmalar yaratish funksiyasi
def edit_diller_keyboard_user(diller_id):
    keyboard_builder = InlineKeyboardBuilder()
    
    # Tugmalarni qo'shish
    keyboard_builder.button(text="👤 Ism", callback_data=f"edit_name_{diller_id}")
    keyboard_builder.button(text="🏢 Kompaniya", callback_data=f"edit_company_name_{diller_id}")
    keyboard_builder.button(text="🌍 Region", callback_data=f"edit_region_{diller_id}")
    keyboard_builder.button(text="🏢 Tuman", callback_data=f"edit_district_{diller_id}")
    keyboard_builder.button(text="📍 Latitude", callback_data=f"edit_latitude_{diller_id}")
    keyboard_builder.button(text="📍 Longitude", callback_data=f"edit_longitude_{diller_id}")
    keyboard_builder.button(text="📞 Telefon", callback_data=f"edit_phone_number_{diller_id}")
    keyboard_builder.button(text="💳 Diller_limiti", callback_data=f"edit_diller_limit_{diller_id}")
    keyboard_builder.adjust(1)  # 1 ta tugma har bir qatorda bo'ladi
    # Tugmalarni tartibga solish
    keyboard_builder.adjust(2)  # Har bir qatorda 2 ta tugma chiqadi

    # Orqaga qaytish tugmasi
    keyboard_builder.button(text="⬅️ Orqaga qaytish", callback_data="to_back")

    # Klaviaturani yig'ish
    return keyboard_builder.as_markup()


    



