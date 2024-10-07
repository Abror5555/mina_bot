from aiogram import Bot
from aiogram.types import CallbackQuery, InputFile, InputMediaVideo, Message, InputMediaPhoto, ContentType
from diller.diller_user_keyboard import admin_answer, admin_to_diller_keyboard, categories_diller_keyboard, product_diller_keyboard, cart_diller_product_view, cart_diller_product, admin_order_diller_keyboard, send_to_message_diller, view_product_diller_keyboard, admin_diller_reply_keyboard, diller_reply_keyboard
import database
import config
from aiogram.fsm.context import FSMContext
from diller import diller_user_state



# Mahsulotlarni ko'rish tugmasi
async def view_product_diller_key_handler(callback: CallbackQuery):
    categories = await database.get_all_categories()
    await callback.message.edit_reply_markup(reply_markup=None)
    if categories:
        for category in categories:
            # Kategoriya rasmi bor yoki yo'qligini tekshirish
            if category[2]:  # category[2] - image URL yoki yo'li
                try:
                    # URL orqali rasmni jo'natish
                    await callback.message.answer_photo(
                        photo=category[2],  # Rasm URL yoki yo'li
                        caption=f"🔢 Kategoriya: {category[1]}",  # category[1] - kategoriya nomi
                        reply_markup=categories_diller_keyboard([category])
                    )
                except Exception as e:
                    await callback.message.answer(f"Kategoriya: {category[1]}\nRasmni yuklashda xatolik: {e}")
            else:
                await callback.message.answer(
                    text=f"Kategoriya: {category[1]} (Rasm mavjud emas)",
                    reply_markup=categories_diller_keyboard([category])
                )
    else:
        await callback.message.answer("Hozirda kategoriyalar mavjud emas.", reply_markup=view_product_diller_keyboard)



# Kategoriya tugmasi bosilganda mahsulotlar ko'rsatilad
async def view_category_diller_handler(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[2])
    await callback.message.edit_reply_markup(reply_markup=None)
    
    products = database.get_diller_products_by_category(category_id)
    
    if products:
        for product in products:
            messages = []
            
            # Mahsulot haqida chiroyli va emoji bilan bezatilgan ma'lumot
            messages.append(
                f"📦 <b>Mahsulot:</b> {product[1]}\n\n"
                f"📝 <b>Tavsif:</b> {product[3]}\n\n"
                f"💰 <b>Optim Narx:</b> {product[9]} so'm\n"
                f"📦 <b>Bir Complect:</b> {product[10]} dona\n"
                f"📅 <b>Qo'shilgan sana:</b> {product[11]}"
            )
            
            media = [] 
            # Rasmlarni qo'shish (4-7 ustunlar)
            for image_column in range(4, 8):
                image_url = product[image_column]
                if image_url:
                    media.append(InputMediaPhoto(media=image_url))
            
            # Video
            video_url = product[8]  
            if video_url:
                media.append(InputMediaVideo(media=video_url))
            
            # Media bor bo'lsa, foydalanuvchiga yuborish
            if media:
                await callback.message.answer_media_group(media=media)
            
            product_id = product[0]  # Mahsulot ID'si
            await callback.message.answer(
                "\n".join(messages), 
                parse_mode="HTML", 
                reply_markup=product_diller_keyboard(product_id)
            )
    else:
        await callback.message.answer("Bu kategoriya uchun hozircha mahsulotlar mavjud emas.", reply_markup=view_product_diller_keyboard)







# Maxsulotlari cart page qo'shish
async def add_to_diller_cart_handler(callback:CallbackQuery):
    # Kiritilgan qiymatni tekshirish
    product_id = int(callback.data.split("_")[3])
    await callback.message.edit_reply_markup(reply_markup=None)
    user_id = callback.from_user.id  # Foydalanuvchi ID sini olish
    
    # Mahsulotni savatchaga qo'shish
    add_cart = database.add_to_diller_cart(user_id=user_id, product_id=product_id)
    print(f"Diller product cart Maxsulot qo'shildi: {add_cart}")
    await callback.message.answer("Mahsulot savatchaga qo'shildi.", reply_markup=view_product_diller_keyboard)


async def view_diller_cart_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_reply_markup(reply_markup=None)
    cart_items = database.get_diller_cart(user_id)
    
    if cart_items:
        # Chiroyli ko'rinishga keltirish uchun HTML markup va emoji ishlatamiz
        cart_message = "🛒 <b>Sizning savatchangiz:</b>\n\n"
        total_price = 0
        
        for item in cart_items:
            # O'zgaruvchilarni unpack qilish (5 ta qiymat)
            product_name, wholesale_price, quantity, stock, category_name, category_id, product_id = item
            total = wholesale_price * quantity
            
            # Har bir qator uchun mos emoji qo'shamiz
            cart_message += (f"📦 <b>Mahsulot:</b> {product_name}\n"
                             f"💰 <b>Optim narx:</b> {wholesale_price} so'm\n"
                             f"📦 <b>1 kamplect soni:</b> {stock} dona\n"
                             f"🔢 <b>Tanlangan maxsulot soni:</b> {quantity} dona\n"
                             f"💵 <b>Hisoblangan narx:</b> {wholesale_price} x {quantity} = {total} so'm\n\n")
            total_price += total

        # Jami qiymatni ko'rsatish
        cart_message += f"💳 <b>Jami:</b> {total_price} so'm"
        print(f"Savatchadagi maxsulotlar: {cart_message}")
        
        # HTML formatini qo'llab foydalanuvchiga yuboramiz
        await callback.message.answer(cart_message, parse_mode="HTML", reply_markup=cart_diller_product)
    else:
        await callback.message.answer("Savatchangiz bo'sh.", reply_markup=view_product_diller_keyboard)



# Diller sotib olish tugmasi bosilganda mahsulot tafsilotlarini so'rash
async def diller_buy_button_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Qancha mahsulot buyurtma qilmoqchisiz.? Ma'lumotlarni yuboring")
    await state.set_state(diller_user_state.DillerOrderState.waiting_for_diller_details)




async def checkout_diller_handler(message: Message, state: FSMContext, bot: Bot):
    diller_info = message.text
    user_id = message.from_user.id

    # Diller savatidagi mahsulotlarni olish
    cart_items = database.get_diller_cart(user_id)
    
    # Foydalanuvchi haqida ma'lumotni olish
    user_info = database.get_diller_info(user_id)
    user_name = user_info[0]
    company_name = user_info[1]
    region = user_info[2]
    district = user_info[3]
    phone_number = user_info[6]
    latitude = user_info[4]
    longitude = user_info[5]

    # Google Maps uchun URL yaratish
    google_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"
    
    if cart_items:
        # Admin uchun buyurtma xabarini tayyorlash
        cart_message = (f"🟢 <b>Dillerdan yangi buyurtma</b> foydalanuvchi: <b>{user_name}</b> (ID: {user_id}) dan:\n\n"
                        f"🏢 <b>Kampaniya nomi:</b> {company_name}\n"
                        f"📍 <b>Hudud:</b> {region}\n"
                        f"📍 <b>To'liq manzil:</b> {district}\n"
                        f"📞 <b>Telefon raqami:</b> {phone_number}\n\n")
        total_price = 0
        
        for item in cart_items:
            product_name = item[0]
            product_price = item[1]
            quantity = item[2]
            category_name = item[4]
            total = product_price * quantity
            
            cart_message += (f"🏷 <b>Kategoriya:</b> {category_name}\n"
                             f"🛍 <b>Mahsulot:</b> {product_name}\n"
                             f"💲 <b>Narx:</b> {product_price} x {quantity} = {total}\n\n")
            total_price += total
        
        cart_message += f"💰 <b>Jami narx:</b> {total_price}\n\n"
        cart_message += f"🌍 <b>Diller joylashuvi:</b> <a href='{google_maps_url}'>Google Maps orqali ko'rish</a>"
        cart_message += f"\n\n📄 <b>Diller xabari:</b> {diller_info}"

       
        # Adminga buyurtma haqida xabar yuborish
        admin_id = config.ADMIN  # Admin ID'ni konfiguratsiyadan olishingiz kerak
        await bot.send_message(
            chat_id=admin_id,
            text=cart_message,
            parse_mode="HTML",
            disable_web_page_preview=False,
            reply_markup=admin_to_diller_keyboard(user_id, user_name)
        )
        await state.clear()
        # Dillerga buyurtma qabul qilinganligini bildirish
        await message.answer("Sizning buyurtmangiz qabul qilindi va adminga yuborildi.", reply_markup=view_product_diller_keyboard)
    else:
        await message.answer("Savatchangiz bo'sh.", reply_markup=view_product_diller_keyboard)


# Tasdiqlash tugmasi callback handler
async def confirm_diller_order_handler(callback: CallbackQuery, state: FSMContext):
    diller_info = callback.data.split("_")
    # Tekshirish: diller_info uzunligini tekshiramiz va `None` yoki noto'g'ri qiymatlarni oldini olamiz
    if len(diller_info) >= 3 and diller_info[-2].isdigit():
        user_id = int(diller_info[-2])
    else:
        print("Xatolik: user_id noto'g'ri yoki None")
        await callback.message.answer("Xatolik: user ma'lumotlari noto'g'ri.")
        return  # Ushbu joyda jarayonni to'xtatish

    diller_name = diller_info[-1]
    await callback.message.edit_reply_markup(reply_markup=None)
    # Adminga foydalanuvchiga yuborish kerak bo'lgan ma'lumotlarni kiritish imkoniyatini beramiz
    await callback.message.answer("Dillerga javob yozing.")
    
    # Ma'lumotlarni saqlaymiz va adminni kiritish jarayoniga o'tkazamiz
    await state.update_data(diller_id=user_id)
    await state.update_data(diller_name=diller_name)
    await state.set_state(diller_user_state.DillerOrderState.waiting_for_admin_reply)



# Admin javobini qabul qilish va dillerga yuborish
async def diller_handle_admin_reply(message: Message, state: FSMContext, bot: Bot):
    # Diller ID'sini olish (oldindan saqlangan bo'lishi kerak)
    data = await state.get_data()
    diller_id = data.get("diller_id")
    # Adminga yuborish
    if message.content_type == ContentType.TEXT:
        admin_reply = message.text
        # Dillerga adminning javobini yuborish
        await bot.send_message(
            chat_id=diller_id,
            text=f"📩 <b>Admin sizga javob berdi:</b>\n\n{admin_reply}",
            parse_mode="HTML"
        )

    elif message.content_type == ContentType.PHOTO:
        # Rasmlarni yuborish
        photo = message.photo[-1].file_id  # Eng yuqori sifatli rasmni tanlash
        caption = message.caption or "Rasm"
        await bot.send_photo(
            chat_id=diller_id,
            photo=photo,
            caption=f"📩 <b>Admin sizga rasm yubordi:</b>\n{caption}",
            parse_mode="HTML"
        )

    elif message.content_type == ContentType.VIDEO:
        # Videoni yuborish
        video = message.video.file_id
        caption = message.caption or "Video"
        await bot.send_video(
            chat_id=diller_id,
            video=video,
            caption=f"📩 <b>Admin sizga video yubordi:</b>\n{caption}",
            parse_mode="HTML"
        )

    elif message.content_type == ContentType.DOCUMENT:
        # Faylni yuborish
        document = message.document.file_id
        caption = message.caption or "Fayl"
        await bot.send_document(
            chat_id=diller_id,
            document=document,
            caption=f"📩 <b>Admin sizga fayl yubordi:</b>\n{caption}",
            parse_mode="HTML"
        )
    
    await bot.send_message(diller_id, "Adminga yana javob yuborishingiz mumkin.", reply_markup=admin_answer)
    await state.clear()
    # Adminga javob yuborilganligini bildirish
    await message.answer("Javobingiz dillerga yuborildi.")
    




# Diller yana javob berishi uchun callback
async def diller_reply_to_admin(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Adminga javobingizni yozing.")
    await state.set_state(diller_user_state.DillerOrderState.waiting_for_diller_reply)





# Dillerning javobini qabul qilish va adminga yuborish (media ham qo'llab-quvvatlanadi)
async def handle_diller_reply_admin(message: Message, state: FSMContext, bot: Bot):
    diller_id = message.from_user.id
    user_info = database.get_diller_info(diller_id)
    diller_name = user_info[0]  # Diller ismi
    
    # Admin ID ni olish (config fayldan)
    admin_id = config.ADMIN

    # Adminga yuborish
    if message.content_type == ContentType.TEXT:
        diller_reply = message.text
        # Matnli javobni yuborish
        await bot.send_message(
            chat_id=admin_id,
            text=f"📩 <b>Dillerdan yangi xabar:</b>\n\n<b>{diller_name}:\n\n</b> sizga javob berdi:\n{diller_reply}",
            parse_mode="HTML"
        )
    elif message.content_type == ContentType.PHOTO:
        # Rasmlarni yuborish
        photo = message.photo[-1].file_id  # Eng yuqori sifatli rasmni tanlash
        caption = message.caption or "Rasm"
        await bot.send_photo(
            chat_id=admin_id,
            photo=photo,
            caption=f"📩 <b>Dillerdan yangi rasm:</b>\n\n<b>{diller_name}:\n\n</b> sizga rasm yubordi:\n{caption}",
            parse_mode="HTML"
        )
    elif message.content_type == ContentType.VIDEO:
        # Videoni yuborish
        video = message.video.file_id
        caption = message.caption or "Video"
        await bot.send_video(
            chat_id=admin_id,
            video=video,
            caption=f"📩 <b>Dillerdan yangi video:</b>\n\n<b>{diller_name}\n\n</b> sizga video yubordi:\n{caption}",
            parse_mode="HTML"
        )
    elif message.content_type == ContentType.DOCUMENT:
        # Faylni yuborish
        document = message.document.file_id
        caption = message.caption or "Fayl"
        await bot.send_document(
            chat_id=admin_id,
            document=document,
            caption=f"📩 <b>Dillerdan yangi fayl:</b>\n\n<b>{diller_name}\n\n</b> sizga fayl yubordi:\n{caption}",
            parse_mode="HTML"
        )

    # Adminga qayta javob berish imkoniyati haqida xabar yuborish
    await bot.send_message(
        chat_id=admin_id,
        text="Dillerga yana javob yuborishingiz mumkin.",
        reply_markup=admin_order_diller_keyboard(diller_id, diller_name)
    )

    # Dillerga javob yuborilganini bildiruvchi xabar
    await message.answer("Javobingiz adminga yuborildi.")

    # Holatni tozalash
    await state.clear()






########################## DILLER BUYURTMALINI TASDIQLASH FUNKSIYALRI ##################
# Tasdiqlash tugmasi callback handler
async def confirm_send_to_diller_handler(callback: CallbackQuery, bot: Bot):
    user_info = callback.data.split("_")
    user_id = user_info[-2]
    diler_name = user_info[-1]
    # Holatdan diller ma'lumotlarini olish
    user_id = int(user_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    # Diller haqida ma'lumotlarni olish
    diller_info = database.get_diller_info(user_id)
    company_name = diller_info[1]  # Firma nomi (company_name)
    admin_comment = "Sizning buyurtmalaringiz tasdiqlandi"


    
    confirm_items = database.get_diller_cart(user_id)

    if confirm_items:
        # Kategoriya nomlarini va mahsulotlarni birlashtiramiz
        product_details = ""
        category_names = set()  # Kategoriya nomlarini saqlash uchun to'plam

        for item in confirm_items:
            product_name = item[0]
            wholesale_price = item[1]
            quantity = item[2]
            stock = item[3]
            category_name = item[4]
            category_id = item[5]
            product_id = item[6]

            # Mahsulot tafsilotlarini birlashtirish
            product_details += (f"🛍 <b>Mahsulot:</b> {product_name}\n"
                                f"💲 <b>Optim narx:</b> {wholesale_price}\n"
                                f"📦 <b>Miqdor:</b> {quantity}\n"
                                f"🗂 <b>1 komplekda:</b> {stock} dona\n"
                                f"🏷 <b>Kategoriya:</b> {category_name}\n"
                                f"-------------------------\n")
            # Kategoriya nomlarini yig'ish
            category_names.add(category_name)

            # Mahsulotni savatdan o'chirish
            delete_cart_page_by_diller = database.delete_from_diller_cart_to_confirm(user_id, product_id)

        # Ma'lumotlar bazasiga bekor qilingan buyurtmani saqlash
        confirm_order_product = database.save_diller_confirm_order(user_id, diler_name, company_name, ", ".join(category_names), product_details, admin_comment)
        print(f"Tasdiqlangan Buyurtmalr: {confirm_order_product}")
        # Foydalanuvchiga yuboriladigan xabar
        message_reply = (f"📩 <b>Sizning buyurmangiz qabul qilindi qildi:</b>\n\n"
                         f"👤 <b>To'liq ma'lumot uchun admin bilan bog'lanish:</b> <a href='https://t.me/{config.USERNAME}'><b>Admin bilan bog'lanish:</b></a>\n\n"
                        #  f"<b>Tafsilotlar:</b>\n\n{admin_comment}\n\n"
                         f"📦 <b>Tasdiqlangan mahsulotlar:</b>\n\n{product_details}")
        
        # Foydalanuvchiga yuborish
        await bot.send_message(chat_id=user_id, text=message_reply, parse_mode="HTML", reply_markup=view_product_diller_keyboard)
        
        # Adminga yuborilganligi haqida xabar berish
        await callback.message.answer("Dillerga xabar muvaffaqiyatli yuborildi.")
    else:
        await callback.message.answer("Savatchada mahsulot topilmadi.")




# Tasdiqlangan buyurtmalarni ko'rish
async def view_confirm_orders_handler_by_dillers(message: Message):
    user_id = message.from_user.id

    if database.is_diller(user_id):
        confirm_orders = database.get_confirm_orders_by_dillers(user_id)

        if not confirm_orders:
            await message.answer("Tasdiqdan o'tgan buyurtmalar hozircha mavjudmas",  reply_markup=view_product_diller_keyboard)
        else:
            for order in confirm_orders:
                user_id, user_name, company_name, category_name, product_details, admin_comment, canceled_at = order

                # Bekor qilingan buyurtmalar haqida ma'lumot
                order_details = (f"📋 <b>Tasdiqlangan buyurtma</b>:\n"
                                f"👤 <b>Diller:</b> {user_name} (ID: {user_id})\n"
                                f"🏢 <b>Firma nomi:</b> {company_name}\n"
                                f"🏷 <b>Kategoriya:</b> {category_name}\n"
                                f"📅 <b>Tasdiqlangan vaqt:</b> {canceled_at}\n\n"
                                f"📦 <b>Mahsulot tafsilotlari:</b>\n{product_details}\n"
                                f"📝 <b>Admin izohi:</b>\n{admin_comment}")

                await message.answer(order_details, parse_mode="HTML", reply_markup=view_product_diller_keyboard)
    else: message.answer("Siz diller emassiz")




############ DILLER BUYURTMALARINI BEKOR QILADIGAN FUNKSIYALAR ##############
# Bekor qilish tugmasi callback handler
async def cancel_diller_order_handler(callback: CallbackQuery, state:FSMContext):
    user_info = callback.data.split("_")
    
    user_id = user_info[-2]
    diler_name = user_info[-1]
    await callback.message.edit_reply_markup(reply_markup=None)
   
    await callback.message.answer("Dillerga nima sababdan buyurtmani bekor qilganingiz haqida qisqacha xabar qoldiring:")
    
    # Ma'lumotlarni saqlaymiz va adminni kiritish jarayoniga o'tkazamiz
    await state.update_data(user_id=user_id, diler_name=diler_name)
    await state.set_state(diller_user_state.DillerOrderState.cancel_diller_order)



# Bekor qilish tugmasi callback handler
async def cancel_send_to_diller_handler(message: Message, state: FSMContext, bot: Bot):
    # Holatdan diller ma'lumotlarini olish
    user_info = await state.get_data()
    user_id = user_info.get("user_id")
    diler_name = user_info.get("diler_name")
    user_id = int(user_id)
    # Diller haqida ma'lumotlarni olish
    diller_info = database.get_diller_info(user_id)
    company_name = diller_info[1]  # Firma nomi (company_name)

    # Admin tomonidan kiritilgan tafsilotlarni olish
    admin_comment = message.text

    # Bekor qilingan mahsulot haqida ma'lumot olish
    # Barcha savatchadagi mahsulotlarni olib kelamiz
    canceled_items = database.get_diller_cart(user_id)

    if canceled_items:
        # Kategoriya nomlarini va mahsulotlarni birlashtiramiz
        product_details = ""
        category_names = set()  # Kategoriya nomlarini saqlash uchun to'plam

        for item in canceled_items:
            product_name = item[0]
            wholesale_price = item[1]
            quantity = item[2]
            stock = item[3]
            category_name = item[4]
            category_id = item[5]
            product_id = item[6]

            # Mahsulot tafsilotlarini birlashtirish
            product_details += (f"🛍 <b>Mahsulot:</b> {product_name}\n"
                                f"💲 <b>Optim narx:</b> {wholesale_price}\n"
                                f"📦 <b>Miqdor:</b> {quantity}\n"
                                f"🗂 <b>1 komplekda:</b> {stock} dona\n"
                                f"🏷 <b>Kategoriya:</b> {category_name}\n"
                                f"-------------------------\n")
            # Kategoriya nomlarini yig'ish
            category_names.add(category_name)

            # Mahsulotni savatdan o'chirish
            delete_cart_page_by_diller = database.delete_from_diller_cart_to_cancel(user_id, product_id)

        # Ma'lumotlar bazasiga bekor qilingan buyurtmani saqlash
        cancel_order_product = database.save_diller_canceled_order(user_id, diler_name, company_name, ", ".join(category_names), product_details, admin_comment)
        print(f"Bekor qilinga maxsulotlar: {cancel_order_product}")
        # Foydalanuvchiga yuboriladigan xabar
        message_reply = (f"📩 <b>Admin Buyurtmani bekor qildi:</b>\n\n"
                         f"👤 <b>To'liq ma'lumot uchun admin bilan bog'lanish:</b> <a href='https://t.me/{config.USERNAME}'><b>Admin bilan bog'lanish:</b></a>\n\n"
                         f"<b>Tafsilotlar:</b>\n\n{admin_comment}\n\n"
                         f"📦 <b>Bekor qilingan mahsulotlar:</b>\n\n{product_details}")
        
        # Foydalanuvchiga yuborish
        await bot.send_message(chat_id=user_id, text=message_reply, parse_mode="HTML", reply_markup=view_product_diller_keyboard)
        
        # Adminga yuborilganligi haqida xabar berish
        await message.answer("Dillerga xabar muvaffaqiyatli yuborildi.")
    else:
        await message.answer("Savatchada mahsulot topilmadi.")

    # Holatni tozalash
    await state.clear()


# Bekor qilingan maxsulotlarni olish
async def view_canceled_orders_handler_by_dillers(message: Message):
    user_id = message.from_user.id

    if database.is_diller(user_id):
        canceled_orders = database.get_canceled_orders_by_dillers(user_id)
        if not canceled_orders:
            await message.answer("Bekor qilingan buyurtmalar hozircha mavjud emas.", reply_markup=view_product_diller_keyboard)
        else:
            for order in canceled_orders:
                user_id, user_name, company_name, category_name, product_details, admin_comment, canceled_at = order

                # Bekor qilingan buyurtmalar haqida ma'lumot
                order_details = (f"📋 <b>Bekor qilingan buyurtma</b>:\n"
                                f"👤 <b>Diller:</b> {user_name} (ID: {user_id})\n"
                                f"🏢 <b>Firma nomi:</b> {company_name}\n"
                                f"🏷 <b>Kategoriya:</b> {category_name}\n"
                                f"📅 <b>Bekor qilingan vaqt:</b> {canceled_at}\n\n"
                                f"📦 <b>Mahsulot tafsilotlari:</b>\n{product_details}\n"
                                f"📝 <b>Admin izohi:</b>\n{admin_comment}")

                await message.answer(order_details, parse_mode="HTML", reply_markup=view_product_diller_keyboard)
    else: message.answer("Siz diler emassiz")
