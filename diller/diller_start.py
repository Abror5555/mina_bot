from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, BotCommand
from diller.diller_user_keyboard import view_diller_info, start_button, mchj_keyboard, location_keyboard, location_request_button, diller_contact, view_product_diller_keyboard
from products.product_keyboard import user_product_button
from database import save_contact, is_user_exist, save_admin, save_diller, is_diller_exist, is_diller, get_diller_info
from config import ADMIN
from aiogram.fsm.context import FSMContext
from diller.diller_user_state import DillerState
from users import user_state, user_keyboard
from admin.admins import notify_admins
import database


# /start komandasi uchun handler
async def start_answer(message: Message, bot: Bot):
    user_id = message.from_user.id

    # Agar foydalanuvchi admin bo'lsa
    if user_id == ADMIN:  # Admin ID sini oddiy butun son bilan solishtiramiz
        if is_user_exist(user_id, is_admin=True):
            await message.answer("Assalomu aleykum", reply_markup=user_product_button)
        else:
            # Admin ID'sini bazaga saqlash
            save_admin(user_id)
            await message.answer("Sizning telegram ID raqamingiz admin sifatida saqlandi.", reply_markup=user_product_button)
    else:
        # Oddiy foydalanuvchi uchun
        if is_user_exist(user_id):
            await message.answer(f"Assalomu Aleykum", reply_markup=user_keyboard.view_user_info)
            await message.answer(f"Maxsulotlarni ko'rish uchun pastdagi tugmani bosing 👇", reply_markup=user_keyboard.view_product_user_keyboard)
        

        elif is_diller_exist(user_id):
            await message.answer("Assalomu Aleykum", reply_markup=view_diller_info)
            await message.answer(f"Maxsulotlarni ko'rish uchun pastdagi tugmani bosing 👇", reply_markup=view_product_diller_keyboard)
        else:
            await bot.send_message(message.from_user.id, "Assalomu aleykum\nSizda Yuridik shaxsmisiz", reply_markup=mchj_keyboard)

    




async def mchj_callback_handler(callback_query: CallbackQuery, state:FSMContext):
    if callback_query.data == 'mchj_ha':
        await callback_query.message.answer("Assalomu aleykum.\nIltimos ismingizni kiriting")
        await state.set_state(DillerState.name)
        await callback_query.message.edit_reply_markup(reply_markup=None)
    elif callback_query.data == 'mchj_yoq':
        await callback_query.message.answer("Assalomu aleykum.\nIltimos ismingizni kiriting")
        await state.set_state(user_state.UserState.name)
        await callback_query.message.edit_reply_markup(reply_markup=None)


async def diller_state_name_answer(message:Message, state:FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer(f"Ismingiz: {name}\nIltimos firmangizni nomi kiriting...")
    await state.set_state(DillerState.company_name)

async def diller_company_name_answer(message:Message, state:FSMContext):
    company_name = message.text
    await state.update_data(company_name=company_name)
    await message.answer(f"Siz kiritgan firmangiz nomi {company_name}\nQaysi vioyatda istiqomat qilsiz..!")
    await state.set_state(DillerState.region)

async def diller_region_answer(message:Message, state:FSMContext):
    region = message.text
    await state.update_data(region=region)
    await message.answer(f"Siz istiqomat qiladigan viloyat {region}\nIstiqomat qiladigan hududingizni To'liq kiriting...")
    await message.answer("Masalan: shaharlar, Tumanlar yoki Mahalla nomi")
    await state.set_state(DillerState.district)

async def diller_district_answer(message:Message, state:FSMContext):
    district = message.text
    await state.update_data(district=district)
    await message.answer(f"Siz yashaydigan hududingizni Joylashuvini kiriting...")
    await message.answer("pastda turgan tugmanibosing 👇", reply_markup=location_keyboard)
    await state.set_state(DillerState.location)

# Joylashuv tugmasi bosilganda handler
async def request_location(callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.answer("Iltimos, joylashuvingizni yuboring", reply_markup=location_request_button)
    await callback_query.answer()

async def location_handler(message: Message, state: FSMContext):
    user_location = message.location
    latitude = user_location.latitude
    longitude = user_location.longitude

    # Joylashuv ma'lumotlarini saqlash
    await state.update_data(latitude=latitude, longitude=longitude)

    # Google Maps URL ni foydalanuvchiga yuborish
    google_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"

    await message.answer(f"Joylashuvingiz qabul qilindi!\n<b>Kenglik</b>: {latitude}\n<b>Uzunlik</b>: {longitude}\n\n<b>Google Maps'da ko'rish uchun:</b>\n{google_maps_url}", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
    await message.answer("To'liq ro'yxatdan o'tish uchun telefon raqamingizni yuboring", reply_markup=start_button)
    await state.set_state(DillerState.phone)


###########  Ma'lumotlarni tekshirish uchun  ###########
async def tasdiq_message_answer(message: Message, state: FSMContext):
    contact = message.contact
    await state.update_data(user_id=contact.user_id)
    await state.update_data(phone_number=contact.phone_number)
    await state.update_data(first_name=contact.first_name)
    await state.update_data(last_name=contact.last_name)
    
    # Holatdagi barcha ma'lumotlarni olish
    data = await state.get_data()

    name = data.get("name")
    company_name = data.get("company_name")
    region = data.get("region")
    district = data.get("district")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    phone_number = contact.phone_number
    first_name = contact.first_name
    last_name = contact.last_name
    
    # Google Maps uchun havola
    google_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"

    # Foydalanuvchining familiyasi mavjudligini tekshiramiz va tegishli matnni tuzamiz
    if last_name is None:
        matn = f"""
<b>👤 Ismingiz</b>: {name}
<b>🏢 Firma nomi</b>: {company_name}
<b>📍 Viloyat</b>: {region}
<b>📍 To'liq manzil</b>: {district}
<b>📍 Joylashuv</b>: <a href='{google_maps_url}'>Google Maps orqali ko'rish</a>
<b>📞 Telefon raqam</b>: {phone_number}
<b>👤 Telegram profil nomi</b>: {first_name}
"""
    else:
        matn = f"""
<b>👤 Ismingiz</b>: {name}
<b>🏢 Firma nomi</b>: {company_name}
<b>📍 Viloyat</b>: {region}
<b>📍 To'liq manzil</b>: {district}
<b>📍 Joylashuv</b>: <a href='{google_maps_url}'>Google Maps orqali ko'rish</a>
<b>📞 Telefon raqam</b>: {phone_number}
<b>👤 Telegram profil nomi</b>: {first_name} {last_name}
"""

    # Ma'lumotlarni tasdiqlash uchun foydalanuvchiga yuborish

    await message.answer(f"Ma'lumotlaringiz to'g'ri ekanini tasdiqlang:\n{matn}", parse_mode="HTML", reply_markup=diller_contact)
    
    # Keyingi holatga o'tish
    await state.set_state(DillerState.save_state)



############## Bazaga saqalsh ################
async def get_diller_contact(callback_quary: CallbackQuery, state: FSMContext, bot:Bot):
    await callback_quary.message.edit_reply_markup(reply_markup=None)
    # Holatdagi barcha ma'lumotlarni olish
    data = await state.get_data()

    name = data.get("name")
    company_name = data.get("company_name")
    region = data.get("region")
    district = data.get("district")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    user_id = data.get("user_id")
    phone_number = data.get("phone_number")
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    # Dillerning barcha ma'lumotlarini bazaga saqlash
    save_diller(
        user_id=user_id,
        name=name,
        company_name=company_name,
        region=region,
        district=district,
        latitude=latitude,
        longitude=longitude,
        phone_number=phone_number,
        first_name=first_name,
        last_name=last_name
    )
    await callback_quary.message.answer("Sizning barcha ma'lumotlaringiz saqlandi.", reply_markup=view_diller_info)
    await callback_quary.message.answer("Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!", reply_markup=view_product_diller_keyboard)
    message = f"""<b>Botga yangi diller qo'shildi:</b>\n
<b>📌 Telegram Id:</b> {user_id}\n
<b>👤 Ismi:</b> {name}\n
<b>🏢 Kompaniya nomi:</b> {company_name}\n
<b>📞 Telefon Raqami:</b> {phone_number}"""
    await bot.send_message(chat_id=ADMIN, text=message, parse_mode="HTML")
    await state.clear()  # Holatni tozalash


async def show_diller_info(message: Message):
    user_id = message.from_user.id
    
    if is_diller(user_id):
        diller_info = get_diller_info(user_id)
        if diller_info:
            # Ma'lumotlarni unpack qilish
            name, company_name, region, district, latitude, longitude, phone_number, first_name, last_name, diller_limit, added_at = diller_info
            google_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"
            
            # Foydalanuvchining familiyasi mavjudligini tekshirish
            if last_name is None:
                await message.answer(
                    f"🛠 <b>Sizning ma'lumotlaringiz:</b>\n\n"
                    f"👤 <b>Ismingiz:</b> {name}\n"
                    f"🏢 <b>Firma nomi:</b> {company_name}\n"
                    f"📍 <b>Region:</b> {region}\n"
                    f"🏘 <b>Tuman:</b> {district}\n"
                    f"📞 <b>Telefon:</b> {phone_number}\n"
                    f"💬 <b>Telegram profil nomi:</b> {first_name}\n"
                    f"📍 <b>Joylashuv:</b> <a href='{google_maps_url}'>Google Maps orqali ko'rish</a>\n"
                    f"💳 <b>Siz uchun ajratilgan limit:</b> {diller_limit}\n"
                    f"📅 <b>Qo'shilgan sana:</b> {added_at}",
                    parse_mode="HTML",
                    reply_markup=view_product_diller_keyboard
                )
            else:
                await message.answer(
                    f"🛠 <b>Sizning ma'lumotlaringiz:</b>\n\n"
                    f"👤 <b>Ismingiz:</b> {name}\n"
                    f"🏢 <b>Firma nomi:</b> {company_name}\n"
                    f"📍 <b>Region:</b> {region}\n"
                    f"🏘 <b>Tuman:</b> {district}\n"
                    f"📞 <b>Telefon:</b> {phone_number}\n"
                    f"💬 <b>Telegram profil nomi:</b> {first_name}, {last_name}\n"
                    f"📍 <b>Joylashuv:</b> <a href='{google_maps_url}'>Google Maps orqali ko'rish</a>\n"
                    f"💳 <b>Siz uchun ajratilgan limit:</b> {diller_limit}\n"
                    f"📅 <b>Qo'shilgan sana:</b> {added_at}",
                    parse_mode="HTML",
                    reply_markup=view_product_diller_keyboard
                )

        else:
            await message.answer("Sizning diller ma'lumotlaringiz topilmadi.")
    else:
        await message.answer("Siz diller emassiz.")





######### To'plangan state-larni o'chirish
async def delete_state_answer(callback_quary:CallbackQuery, state:FSMContext):
    this_state = await state.get_state()
    await callback_quary.message.edit_reply_markup(reply_markup=None)
    if this_state == "None": await callback_quary.message.answer("Bekor qilish uchun ariza mavjudmas")
    else:
        await state.clear()
        await callback_quary.message.answer("to'plangan malumotlar o'chirildi")
        await callback_quary.message.answer("malumotlarni qayta kiritish uchun /start komandasini bosing...")




