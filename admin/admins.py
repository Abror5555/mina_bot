from aiogram import Bot, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext
from admin.admin_states import EditDiller, EditUsers
from database import get_all_dillers, get_all_users, get_diller_info, update_diller_info, delete_diller_table, get_confirmed_user_orders, get_canceled_user_orders, get_confirmed_diller_orders, get_canceled_diller_orders
from admin.admin_keyboard import edit_diller_keyboard, edit_diller_keyboard_user, back_to
from config import ADMIN
from database import get_statistics, get_all_users, get_user_info, update_users_info, delete_user
from . import admin_user_keyboard
import pandas as pd





# Diller tugmasi bosilganda barcha dillerlar ro'yxatini chiqarish
async def show_dillers(message: Message):
    user_id = message.from_user.id
    if user_id == ADMIN:
        dillers = get_all_dillers()  # Barcha dillerlar ma'lumotlar bazasidan olinadi
        if dillers:
            diller_list = "\n".join([f"👤 <b>{diller[1]}</b> (Kompaniya nomi: {diller[2]})" for diller in dillers])
            await message.answer(f"Barcha dillerlar ro'yxati:\n\n{diller_list}", parse_mode="HTML")
        else:
            await message.answer("Dillerlar topilmadi.")


# User tugmasi bosilganda barcha dillerlar ro'yxatini chiqarish
async def show_users(message: Message):
    user_id = message.from_user.id
    if user_id == ADMIN:
        dillers = get_all_users()  # Barcha dillerlar ma'lumotlar bazasidan olinadi
        if dillers:
            diller_list = "\n".join([f"👤 <b>{diller[1]}</b> (Region: {diller[2]})" for diller in dillers])
            await message.answer(f"Barcha userlar ro'yxati:\n\n{diller_list}", parse_mode="HTML")
        else:
            await message.answer("Users topilmadi.")



# Adminlarga xabar yuborish funksiyasi
async def notify_admins(message: str, bot: Bot):
    try:
        await bot.send_message(chat_id=ADMIN, text=message, parse_mode="HTML")
    except Exception as e:
        print(f"Xato yuz berdi: {e}")


########## Diller uchun maxsus funksiyalar #############
async def show_all_dillers(message:Message, state:FSMContext):
    user = message.from_user.id
    if user == ADMIN:
        dillers = get_all_dillers()
        if not dillers:
            await message.answer("Hozircha dillerlar yo'q.")
            return
        
        for diller in dillers:
            user_id, name, company_name = diller
            text = f"Ism: {name}\nKompaniya: {company_name}"
            # Inline tugmalarini yaratamiz
            keyboard = edit_diller_keyboard(user_id)
            await message.answer(text, reply_markup=keyboard)
            await state.set_state(EditDiller.diller_id)
    else: message.answer("Siz admin emassiz")


async def view_diller_malumot(callback_query:CallbackQuery):
    # Callback_data'ni ajratib, diller_id va maydon nomini ajratamiz
    data_parts = callback_query.data.split("_")
    # Diller ID'ni oxirgi qiymatdan olish
    diller_id = int(data_parts[-1])  # Bu yerda integer qiymatni olishga harakat qilamiz
    await callback_query.message.edit_reply_markup(reply_markup=None)
    diller_info = get_diller_info(diller_id)
    if diller_info:
        # Diller haqida ma'lumotlarni ajratib olish
        name, company_name, region, district, latitude, longitude, phone_number, first_name, last_name, diller_limit, added_at = diller_info
        google_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"
        # Ma'lumotlarni foydalanuvchiga chiqarish uchun tayyorlash
        text = (f"👤 <b>Ism:</b> {name}\n"
            f"🏢 <b>Kompaniya:</b> {company_name}\n"
            f"📍 <b>Region:</b> {region}\n"
            f"🏘 <b>Tuman:</b> {district}\n"
            f"🌐 <b>Latitude:</b> {latitude}\n"
            f"🌐 <b>Longitude:</b> {longitude}\n"
            f"📞 <b>Telefon:</b> {phone_number}\n"
            f"👤 <b>First Name:</b> {first_name}\n"
            f"👤 <b>Last Name:</b> {last_name}\n"
            f"💳 <b>Diller limiti:</b> {diller_limit}\n"
            f"📅 <b>Qo'shilgan vaqti:</b> {added_at}\n"
            f"🌍 <b>Foydalanuvchi joylashuvi:</b> <a href='{google_maps_url}'>Google Maps orqali ko'rish</a>")

        keyboard = back_to
        await callback_query.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
                
async def show_all_dillers_back(callback_quary:CallbackQuery, state:FSMContext):
    user = callback_quary.from_user.id
    await callback_quary.message.edit_reply_markup(reply_markup=None)
    if user == ADMIN:
        dillers = get_all_dillers()
        if not dillers:
            await callback_quary.message.answer("Hozircha dillerlar yo'q.")
            return
        
        for diller in dillers:
            user_id, name, company_name = diller
            text = f"Ism: {name}\nKompaniya: {company_name}"
            # Inline tugmalarini yaratamiz
            keyboard = edit_diller_keyboard(user_id)
            await callback_quary.message.answer(text, reply_markup=keyboard)
            await state.set_state(EditDiller.diller_id)
    else: callback_quary.message.answer("Siz admin emassiz")




# Dillerni tahrirlashni boshlash uchun funksiya
async def edit_diller_info(callback_query: CallbackQuery, state: FSMContext):
    # Callback_data'ni ajratib, diller_id va maydon nomini ajratamiz
    data_parts = callback_query.data.split("_")
    # Maydonni olish (oxirgi qismidan oldingi qismlarni birlashtiramiz)
    field = "_".join(data_parts[1:-1])  # 'company_name', 'diller_limit', etc.
    await callback_query.message.edit_reply_markup(reply_markup=None)
    
    try:
        # Diller ID'ni oxirgi qiymatdan olish
        diller_id = int(data_parts[-1])  # Bu yerda integer qiymatni olishga harakat qilamiz
        # Diller ma'lumotlarini olish
        diller_info = get_diller_info(diller_id)

        if diller_info:
            # Diller haqida ma'lumotlarni ajratib olish
            name, company_name, region, district, latitude, longitude, phone_number, first_name, last_name, diller_limit, added_at = diller_info
            
            # Ma'lumotlarni foydalanuvchiga chiqarish uchun tayyorlash
            text = (f"👤 <b>Ism:</b> {name}\n"
            f"🏢 <b>Kompaniya:</b> {company_name}\n"
            f"📍 <b>Region:</b> {region}\n"
            f"🏘 <b>Tuman:</b> {district}\n"
            f"🌐 <b>Latitude:</b> {latitude}\n"
            f"🌐 <b>Longitude:</b> {longitude}\n"
            f"📞 <b>Telefon:</b> {phone_number}\n"
            f"👤 <b>First Name:</b> {first_name}\n"
            f"👤 <b>Last Name:</b> {last_name}\n"
            f"💳 <b>Diller limiti:</b> {diller_limit}\n"
            f"📅 <b>Qo'shilgan vaqti:</b> {added_at}\n" 
            f"✏️ Tahrir qilmoqchi bo'lgan maydonni tanlang.")

            
            # Inline keyboard yaratiladi
            keyboard = edit_diller_keyboard_user(diller_id)

            # Xabarni chiqarish
            await callback_query.message.answer(text, parse_mode="HTML", reply_markup=keyboard)

        # Diller ID va holatni saqlash
        await state.update_data(diller_id=diller_id)
        await state.set_state(EditDiller.waiting_for_field)

    except ValueError:
        # Agar raqamga aylantirishda xato bo'lsa
        await callback_query.message.answer("Noto'g'ri diller ID yoki ma'lumot.")

async def select_field_to_edit(callback_query: CallbackQuery, state: FSMContext):
    # Callback_data ni "_" bo'yicha ajratib, maydon nomini olish
    data_parts = callback_query.data.split("_")  # Masalan, ['edit', 'company', 'name', '12345']
    
    # Maydonni qayta yig'amiz va oxirgi qismdagi diller_id'ni olib tashlaymiz
    field = "_".join(data_parts[1:-1]) 
    print(field)
    # Dillerning maydon nomini saqlash
    await state.update_data(field=field)
    # Tugmalarni o'chirish
    await callback_query.message.edit_reply_markup(reply_markup=None) 
    await callback_query.message.answer(f"{field.capitalize()} maydoni uchun yangi qiymatni kiriting.")
    await state.set_state(EditDiller.waiting_for_value)

async def process_new_value(message: Message, state: FSMContext):
    new_value = message.text

    # Diller ID va maydon nomini olamiz
    data = await state.get_data()
    user_id = int(data.get("diller_id"))
    field = data.get("field")
    print(f"ID turi: {type(user_id)}, ID qiymati: {user_id},  Ustun nomi: {field},  Value: {new_value}")
    # Ma'lumotlar bazasida yangilash
    success = update_diller_info(user_id, field, new_value)

    if success:
        await message.answer(f"{field} muvaffaqiyatli yangilandi.")
    else:
        await message.answer(f"Diller ID {user_id} bo'yicha yozuv topilmadi.")

    # State tozalash
    await state.clear()



######## Dillerlarni o'chiradigan funksiya ##########
async def delete_diller(callback_query: CallbackQuery):
    # callback_data dan user_id ni olish
    user_id = int(callback_query.data.split("_")[2])
    print(type(user_id))

    # delete_diller funksiyasini chaqiramiz va o'chirilgan qatorlar sonini olamiz
    deleted_rows = delete_diller_table(user_id)

    if deleted_rows > 0:
        await callback_query.message.answer("Diller muvaffaqiyatli o'chirildi.")
        await callback_query.message.edit_reply_markup(reply_markup=None)
    else:
        await callback_query.message.answer("Diller topilmadi yoki allaqachon o'chirilgan.")
        await callback_query.message.edit_reply_markup(reply_markup=None)
########### END DILLER ##############


########### USER UCHUN MAXSUS FUNKSIYALAR ##########

async def show_all_users(message:Message, state:FSMContext):
    user = message.from_user.id
    if user == ADMIN:
        users = get_all_users()
        if not users:
            await message.answer("Hozircha users yo'q.")
            return
        
        for user in users:
            user_id, name, region = user
            text = f"Ism: {name}\nHudud: {region}"
            # Inline tugmalarini yaratamiz
            keyboard = admin_user_keyboard.edit_users_keyboard(user_id)
            await message.answer(text, reply_markup=keyboard)
            await state.set_state(EditUsers.user_id)
    else: message.answer("Siz admin emassiz")

# User ma'lumotlarini ko'rish
async def view_user_malumot(callback_query:CallbackQuery):
    # Callback_data'ni ajratib, diller_id va maydon nomini ajratamiz
    data_parts = callback_query.data.split("_")
    # Diller ID'ni oxirgi qiymatdan olish
    user_id = int(data_parts[-1])  # Bu yerda integer qiymatni olishga harakat qilamiz
    await callback_query.message.edit_reply_markup(reply_markup=None)
    users_info = get_user_info(user_id)
    if users_info:
        # Diller haqida ma'lumotlarni ajratib olish
        name, region, district, latitude, longitude, phone_number, first_name, last_name, added_at = users_info
        google_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"
        # Ma'lumotlarni foydalanuvchiga chiqarish uchun tayyorlash
        text = (f"👤 <b>Ism:</b> {name}\n"
                f"📍 <b>Region:</b> {region}\n"
                f"🏘 <b>Tuman:</b> {district}\n"
                f"🌐 <b>Latitude:</b> {latitude}\n"
                f"🌐 <b>Longitude:</b> {longitude}\n"
                f"📞 <b>Telefon:</b> {phone_number}\n"
                f"👤 <b>First Name:</b> {first_name}\n"
                f"👤 <b>Last Name:</b> {last_name}\n"
                f"📅 <b>Qo'shilgan vaqti:</b> {added_at}\n"
                f"🌍 <b>Foydalanuvchi joylashuvi:</b> <a href='{google_maps_url}'>Google Maps orqali ko'rish</a>")

        keyboard = admin_user_keyboard.back_to_users
        await callback_query.message.answer(text, parse_mode="HTML", reply_markup=keyboard)

async def show_all_users_back(callback_quary:CallbackQuery, state:FSMContext):
    user = callback_quary.from_user.id
    await callback_quary.message.edit_reply_markup(reply_markup=None)
    if user == ADMIN:
        users = get_all_users()
        if not users:
            await callback_quary.message.answer("Hozircha users yo'q.")
            return
        
        for user in users:
            user_id, name, region = user
            text = f"Ism: {name}\nHudud: {region}"
            # Inline tugmalarini yaratamiz
            keyboard = admin_user_keyboard.edit_users_keyboard(user_id)
            await callback_quary.message.answer(text, reply_markup=keyboard)
            await state.set_state(EditUsers.user_id)
    else: callback_quary.message.answer("Siz admin emassiz")


# Users tahrirlashni boshlash uchun funksiya
async def edit_users_info(callback_query: CallbackQuery, state: FSMContext):
    # Callback_data'ni ajratib, diller_id va maydon nomini ajratamiz
    data_parts = callback_query.data.split("_")
    # Maydonni olish (oxirgi qismidan oldingi qismlarni birlashtiramiz)
    field = "_".join(data_parts[1:-1])  # 'company_name', 'diller_limit', etc.
    await callback_query.message.edit_reply_markup(reply_markup=None)
    
    try:
        # Diller ID'ni oxirgi qiymatdan olish
        users_id = int(data_parts[-1])  # Bu yerda integer qiymatni olishga harakat qilamiz
        # Diller ma'lumotlarini olish
        users_info = get_user_info(users_id)

        if users_info:
            # Diller haqida ma'lumotlarni ajratib olish
            name, region, district, latitude, longitude, phone_number, first_name, last_name,  added_at = users_info
            
            # Ma'lumotlarni foydalanuvchiga chiqarish uchun tayyorlash
            text = (f"👤 <b>Ism:</b> {name}\n"
                f"📍 <b>Region:</b> {region}\n"
                f"🏘 <b>Tuman:</b> {district}\n"
                f"🌐 <b>Latitude:</b> {latitude}\n"
                f"🌐 <b>Longitude:</b> {longitude}\n"
                f"📞 <b>Telefon:</b> {phone_number}\n"
                f"💬 <b>Telegram nomi:</b> {first_name}\n"
                f"💬 <b>Telegram ikkinchi nomi:</b> {last_name}\n"
                f"📅 <b>Qo'shilgan vaqti:</b> {added_at}\n"
                f"✏️ Tahrir qilmoqchi bo'lgan maydonni tanlang.")

            
            # Inline keyboard yaratiladi
            keyboard = admin_user_keyboard.edit_users_keyboard_user(users_id)

            # Xabarni chiqarish
            await callback_query.message.answer(text, parse_mode="HTML", reply_markup=keyboard)

        # Diller ID va holatni saqlash
        await state.update_data(users_id=users_id)
        await state.set_state(EditUsers.waiting_for_field)

    except ValueError:
        # Agar raqamga aylantirishda xato bo'lsa
        await callback_query.message.answer("Noto'g'ri users ID yoki ma'lumot.")


async def select_field_to_edit_users(callback_query: CallbackQuery, state: FSMContext):
    # Callback_data ni "_" bo'yicha ajratib, maydon nomini olish
    data_parts = callback_query.data.split("_")  # Masalan, ['edit', 'company', 'name', '12345']
    
    # Maydonni qayta yig'amiz va oxirgi qismdagi diller_id'ni olib tashlaymiz
    field = "_".join(data_parts[1:-1]) 
    print(field)
    # Dillerning maydon nomini saqlash
    await state.update_data(field=field)
    # Tugmalarni o'chirish
    await callback_query.message.edit_reply_markup(reply_markup=None) 
    await callback_query.message.answer(f"{field.capitalize()} maydoni uchun yangi qiymatni kiriting.")
    await state.set_state(EditUsers.waiting_for_value)


async def process_new_value_users(message: Message, state: FSMContext):
    new_value = message.text

    # Diller ID va maydon nomini olamiz
    data = await state.get_data()
    user_id = int(data.get("users_id"))
    field = data.get("field")
    print(f"ID turi: {type(user_id)}, ID qiymati: {user_id},  Ustun nomi: {field},  Value: {new_value}")
    # Ma'lumotlar bazasida yangilash
    success = update_users_info(user_id, field, new_value)

    if success:
        await message.answer(f"{field} muvaffaqiyatli yangilandi.")
    else:
        await message.answer(f"Users ID {user_id} bo'yicha yozuv topilmadi.")

    # State tozalash
    await state.clear()



######## Dillerlarni o'chiradigan funksiya ##########
async def delete_users(callback_query: CallbackQuery):
    # callback_data dan user_id ni olish
    user_ddddd = (callback_query.data.split("_"))
    user_id = int(user_ddddd[-1])
    print(type(user_id),  user_id)

    # delete_diller funksiyasini chaqiramiz va o'chirilgan qatorlar sonini olamiz
    deleted_rows = delete_user(user_id)

    if deleted_rows > 0:
        await callback_query.message.answer("User muvaffaqiyatli o'chirildi.")
        await callback_query.message.edit_reply_markup(reply_markup=None)
    else:
        await callback_query.message.answer("User topilmadi yoki allaqachon o'chirilgan.")
        await callback_query.message.edit_reply_markup(reply_markup=None)







################### STATISTIKA ###################
async def send_statistics(message: Message):
    user_id = message.from_user.id
    
    if user_id != ADMIN:
        await message.answer("Ushbu buyruq faqat adminlar uchun mavjud.")
        return

    # Statistika ma'lumotlarini olish
    stats_1 = get_statistics()
    if stats_1:
        stats_text_1 = "\n".join([f"{key}: {value}" for key, value in stats_1.items()])
    else:
    # Statistika ma'lumotlarini matn shaklida yaratish
        stats_text_1 = "Bazadan hech qanday ma'lumot topilmadi."



    # Foydalanuvchilar va dillerlarning tasdiqlangan va bekor qilingan buyurtmalari ma'lumotlarini olish
    confirmed_user_orders_data, confirmed_user_orders_columns = get_confirmed_user_orders()
    canceled_user_orders_data, canceled_user_orders_columns = get_canceled_user_orders()
    confirmed_diller_orders_data, confirmed_diller_orders_columns = get_confirmed_diller_orders()
    canceled_diller_orders_data, canceled_diller_orders_columns = get_canceled_diller_orders()

    # Ma'lumotlar mavjudligini tekshirish va statistik matnni yaratish
    if not confirmed_user_orders_data and not canceled_user_orders_data and not confirmed_diller_orders_data and not canceled_diller_orders_data:
        stats_text = "Bazadan hech qanday ma'lumot topilmadi."
    else:
        stats_text = (
            f"<b>Foydalanuvchilar Tasdiqlangan Buyurtmalari:</b> {len(confirmed_user_orders_data)}\n"
            f"<b>Foydalanuvchilar Bekor Qilingan Buyurtmalari:</b> {len(canceled_user_orders_data)}\n"
            f"<b>Dillerlar Tasdiqlangan Buyurtmalari:</b> {len(confirmed_diller_orders_data)}\n"
            f"<b>Dillerlar Bekor Qilingan Buyurtmalari:</b> {len(canceled_diller_orders_data)}\n"
        )

    # Excel fayl yaratish
    if confirmed_user_orders_data or canceled_user_orders_data or confirmed_diller_orders_data or canceled_diller_orders_data:
        confirmed_user_orders_df = pd.DataFrame(confirmed_user_orders_data, columns=confirmed_user_orders_columns)
        canceled_user_orders_df = pd.DataFrame(canceled_user_orders_data, columns=canceled_user_orders_columns)
        confirmed_diller_orders_df = pd.DataFrame(confirmed_diller_orders_data, columns=confirmed_diller_orders_columns)
        canceled_diller_orders_df = pd.DataFrame(canceled_diller_orders_data, columns=canceled_diller_orders_columns)

        excel_path = "tasdiqlangan_va_bekor_qilingan_yakuniy.xlsx"
        with pd.ExcelWriter(excel_path) as writer:
            if not confirmed_user_orders_df.empty:
                confirmed_user_orders_df.to_excel(writer, sheet_name="Tasdiqlangan User Buyurt.", index=False)
            if not canceled_user_orders_df.empty:
                canceled_user_orders_df.to_excel(writer, sheet_name="Bekor qilingan User Buyurt.", index=False)
            if not confirmed_diller_orders_df.empty:
                confirmed_diller_orders_df.to_excel(writer, sheet_name="Tasdiqlangan Diller Buyurt.", index=False)
            if not canceled_diller_orders_df.empty:
                canceled_diller_orders_df.to_excel(writer, sheet_name="Bekor qilingan Diller Buyurt.", index=False)

        # Yuklab olish tugmasini yaratish
        download_button = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📊 Statistikani yuklab olish (XLSX)", callback_data="download_statistics")]
            ]
        )
    else:
        download_button = None

    # Statistika ma'lumotlarini adminga jo'natish
    await message.answer(f"<b>Statistika ma'lumotlari:</b>\n\n{stats_text_1}", parse_mode="HTML")
    await message.answer(stats_text, reply_markup=download_button, parse_mode="HTML" if download_button else None)

# Statistika faylini yuklab olish uchun callback handler
async def download_statistics(callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    if callback_query.from_user.id != ADMIN:
        await callback_query.answer("Siz admin emassiz!", show_alert=True)
        return

    # Statistika ma'lumotlari faylini yuklash
    file = FSInputFile("tasdiqlangan_va_bekor_qilingan_yakuniy.xlsx", filename="Statistika.xlsx")
    await callback_query.message.answer_document(file)
    await callback_query.answer()