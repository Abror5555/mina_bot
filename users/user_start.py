from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from users.user_keyboard import location_keyboard, location_request_button, start_button, user_contact, view_product_user_keyboard, view_user_info
from database import save_contact, is_user, get_user_info
from config import ADMIN
from aiogram.fsm.context import FSMContext
from diller.diller_user_state import DillerState
from users.user_state import UserState
from admin.admins import notify_admins


async def user_callback_handler(callback_query: CallbackQuery, state:FSMContext):
    if callback_query.data == 'mchj_yoq':
        await callback_query.message.answer("Assalomu aleykum.\nIltimos ismingizni kiriting")
        await callback_query.message.edit_reply_markup(reply_markup=None)
        await state.set_state(UserState.name)
    elif callback_query.data == 'mchj_ha':
        await callback_query.message.answer("Iltimos firmangizni nomi kiriting...")
        await callback_query.message.edit_reply_markup(reply_markup=None)
        await state.set_state(DillerState.name)
        

async def user_state_name_answer(message:Message, state:FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer(f"Ismingiz {name}\nQaysi vioyatda istiqomat qilsiz..!")
    await state.set_state(UserState.region)

async def user_region_answer(message:Message, state:FSMContext):
    region = message.text
    await state.update_data(region=region)
    await message.answer(f"Siz istiqomat qiladigan viloyat {region}\nIstiqomat qiladigan hududingizni To'liq kiriting...!")
    await message.answer("Masalan: shaharlar, Tumanlar yoki Mahalla nomi")
    await state.set_state(UserState.district)

async def user_district_answer(message:Message, state:FSMContext):
    district = message.text
    await state.update_data(district=district)
    await message.answer(f"Siz yashaydigan hududingizni Joylashuvini kiriting...")
    await message.answer("pastda turgan tugmanibosing 👇", reply_markup=location_keyboard)
    await state.set_state(UserState.location)

# Joylashuv tugmasi bosilganda handler
async def user_request_location(callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.answer("Iltimos, joylashuvingizni yuboring", reply_markup=location_request_button)
    await callback_query.answer()

async def user_location_handler(message: Message, state: FSMContext):
    user_location = message.location
    latitude = user_location.latitude
    longitude = user_location.longitude

    # Joylashuv ma'lumotlarini saqlash
    await state.update_data(latitude=latitude, longitude=longitude)

    # Google Maps URL ni foydalanuvchiga yuborish
    google_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"

    await message.answer(f"Joylashuvingiz qabul qilindi!\n<b>Kenglik</b>: {latitude}\n<b>Uzunlik</b>: {longitude}\n\n<b>Google Maps'da ko'rish uchun:</b>\n{google_maps_url}", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
    await message.answer("To'liq ro'yxatdan o'tish uchun telefon raqamingizni yuboring", reply_markup=start_button)
    await state.set_state(UserState.phone)


###########  Malumotlarni tekshirish uchun  ###########
async def user_tasdiq_message_answer(message:Message, state:FSMContext):
    contact = message.contact
    await state.update_data(user_id=contact.user_id)
    await state.update_data(phone_number=contact.phone_number)
    await state.update_data(first_name=contact.first_name)
    await state.update_data(last_name=contact.last_name)
    # Holatdagi barcha ma'lumotlarni olish
    data = await state.get_data()

    name = data.get("name")
    region = data.get("region")
    district = data.get("district")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    phone_number=contact.phone_number,
    first_name=contact.first_name,
    last_name=contact.last_name
    google_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"

    if last_name == None: 
        matn = f"""
<b>👤 Ismingiz</b>: {name}
<b>📍 Viloyat</b>: {region}
<b>📍 To'liq manzil</b>: {district}
<b>📍 Joylashuv</b>: <a href='{google_maps_url}'>Google Maps orqali ko'rish</a>
<b>📞 Telefon raqam</b>: {phone_number}
<b>👤 Telegram profil nomi</b>: {first_name}
"""
    else:
        matn = f"""
<b>👤 Ismingiz</b>: {name}
<b>📍 Viloyat</b>: {region}
<b>📍 To'liq manzil</b>: {district}
<b>📍 Joylashuv</b>: <a href='{google_maps_url}'>Google Maps orqali ko'rish</a>
<b>📞 Telefon raqam</b>: {phone_number}
<b>👤 Telegram profil nomi</b>: {first_name} {last_name}
"""
        
    await message.answer(f"ma'lumotlaringiz to'g'ri ekanini tasdiqlang\n{matn}", parse_mode="HTML", reply_markup=user_contact)
    await state.set_state(UserState.save_state)

############## Bazaga saqalsh ################
async def get_user_contact(callback_quary: CallbackQuery, state: FSMContext, bot:Bot):
    # Holatdagi barcha ma'lumotlarni olish
    await callback_quary.message.edit_reply_markup(reply_markup=None)
    data = await state.get_data()

    name = data.get("name")
    region = data.get("region")
    district = data.get("district")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    user_id = data.get("user_id")
    phone_number = data.get("phone_number")
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    # Userning barcha ma'lumotlarini bazaga saqlash
    save_contact(
        user_id=user_id,
        name=name,
        region=region,
        district=district,
        latitude=latitude,
        longitude=longitude,
        phone_number=phone_number,
        first_name=first_name,
        last_name=last_name
    )
    await callback_quary.message.answer("Sizning barcha ma'lumotlaringiz saqlandi.", reply_markup=view_user_info)
    await callback_quary.message.answer("Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!", reply_markup=view_product_user_keyboard)
    message = f"""<b>Yangi foydalanuvchi qo'shildi:</b>\n
<b>📌 Telegram Id:</b> {user_id}\n
<b>👤 Ismi:</b> {name}\n
<b>📞 Telefon Raqami:</b> {phone_number}"""
    await notify_admins(message, bot)
    await state.clear()  # Holatni tozalash


async def show_user_info(message: Message):
    user_id = message.from_user.id
    
    if is_user(user_id):
        user_info = get_user_info(user_id)
        if user_info:
            name, region, district, latitude, longitude, phone_number, first_name, last_name,  added_at = user_info
            google_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"
            if last_name == None:
                await message.answer(
                    f"🛠 <b>Sizning ma'lumotlaringiz:</b>\n\n"
                    f"👤 <b>Ismingiz:</b> {name}\n"
                    f"📍 <b>Region:</b> {region}\n"
                    f"🏘 <b>Tuman:</b> {district}\n"
                    f"📞 <b>Telefon:</b> {phone_number}\n"
                    f"💬 <b>Telegram profil nomi:</b> {first_name}\n"
                    f"📍 <b>Joylashuv:</b> <a href='{google_maps_url}'>Google Maps orqali ko'rish</a>\n"
                    f"📅 <b>Qo'shilgan sana:</b> {added_at}",
                    parse_mode="HTML",
                    reply_markup=view_product_user_keyboard
                )
            else:
                await message.answer(
                    f"🛠 <b>Sizning ma'lumotlaringiz:</b>\n\n"
                    f"👤 <b>Ismingiz:</b> {name}\n"
                    f"📍 <b>Region:</b> {region}\n"
                    f"🏘 <b>Tuman:</b> {district}\n"
                    f"📞 <b>Telefon:</b> {phone_number}\n"
                    f"💬 <b>Telegram profil nomi:</b> {first_name}, {last_name}\n"
                    f"📍 <b>Joylashuv:</b> <a href='{google_maps_url}'>Google Maps orqali ko'rish</a>\n"
                    f"📅 <b>Qo'shilgan sana:</b> {added_at}",
                    parse_mode="HTML",
                    reply_markup=view_product_user_keyboard
                )
        else:
            await message.answer("Sizning foydalanuvchi ma'lumotlaringiz topilmadi.")
    else:
        await message.answer("Siz user emassiz.")




######### To'plangan state-larni o'chirish
async def delete_user_state_answer(callback_quary:CallbackQuery, state:FSMContext):
    this_state = await state.get_state()
    if this_state == "None": await callback_quary.message.answer("Bekor qilish uchun ariza mavjudmas")
    else:
        await state.clear()
        await callback_quary.message.answer("to'plangan malumotlar o'chirildi")
        await callback_quary.message.answer("malumotlarni qayta kiritish uchun /start komandasini bosing...")
        await callback_quary.message.edit_reply_markup(reply_markup=None)