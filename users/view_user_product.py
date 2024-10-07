from aiogram import Bot
from aiogram.types import CallbackQuery, InputFile, InputMediaPhoto, InputMediaVideo, Message, ContentType
from users.user_keyboard import admin_answer_to_user, admin_to_user_keyboard, categories_user_keyboard, product_user_keyboard, view_product_user_keyboard, cart_user_product, admin_order_keyboard
import database
import config
from aiogram.fsm.context import FSMContext
from users import user_state




# Mahsulotlarni ko'rish tugmasi
async def view_product_user_key_handler(callback: CallbackQuery):
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
                        caption=f"Kategoriya: {category[1]}",  # category[1] - kategoriya nomi
                        reply_markup=categories_user_keyboard([category])
                    )
                except Exception as e:
                    await callback.message.answer(f"Kategoriya: {category[1]}\nRasmni yuklashda xatolik: {e}")
            else:
                await callback.message.answer(
                    text=f"Kategoriya: {category[1]} (Rasm mavjud emas)",
                    reply_markup=categories_user_keyboard([category])
                )
    else:
        await callback.message.answer("Hozirda kategoriyalar mavjud emas.", reply_markup=view_product_user_keyboard)



# Kategoriya tugmasi bosilganda mahsulotlar ko'rsatiladi
async def view_category_user_handler(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[2])
    await callback.message.edit_reply_markup(reply_markup=None)
    
    products = database.get_user_products_by_category(category_id)
    
    if products:
        for product in products:
            messages = []
            
            # Mahsulot haqida ma'lumot
            messages.append(
                f"📦 <b>Mahsulot:</b> {product[1]}\n\n"
                f"📝 <b>Tavsif:</b> {product[3]}\n\n"
                f"💰 <b>Narx:</b> {product[9]} so'm\n"
                f"📦 <b>Skladagi soni :</b> {product[10]} dona\n"
                f"📅 <b>Qo'shilgan sana:</b> {product[11]}"
            )
            media = []  # Rasmlar va videolar uchun ro'yxat
            
            # Rasmlar
            for image_column in range(4, 8):  # Rasmlar ustunlari: image1, image2, image3, image4
                image_url = product[image_column]
                if image_url:
                    media.append(InputMediaPhoto(media=image_url))
            
            # Video
            video_url = product[8]  # video ustuni
            if video_url:
                media.append(InputMediaVideo(media=video_url))
            
            # Agar rasm va video mavjud bo'lsa, ularni bitta xabarda jo'natish
            if media:
                await callback.message.answer_media_group(media=media)
            
            # Mahsulot haqida matnli ma'lumotlarni jo'natish
            await callback.message.answer("\n".join(messages), parse_mode="HTML", reply_markup=product_user_keyboard(product[0]))
    else:
        await callback.message.answer("Bu kategoriya uchun hozircha mahsulotlar mavjud emas.", reply_markup=view_product_user_keyboard)


# Maxsulotlari cart page qo'shish
async def add_to_user_cart_handler(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[3])
    await callback.message.edit_reply_markup(reply_markup=None)
    user_id = callback.from_user.id  # Foydalanuvchi ID sini olish
    
    # Mahsulotni savatchaga qo'shish
    add_cart = database.add_to_user_cart(user_id, product_id)
    print(f"User product cart Maxsulot qo'shildi: {add_cart}")
    await callback.message.answer("Mahsulot savatchaga qo'shildi.", reply_markup=view_product_user_keyboard)


async def view_user_cart_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_reply_markup(reply_markup=None)
    cart_items = database.get_user_cart(user_id)
    
    if cart_items:
        cart_message = "🛒 <b>Sizning savatchangiz:</b>\n\n"
        total_price = 0
        for item in cart_items:
            # O'zgaruvchilarni 5 ta qiymat uchun unpack qilish
            product_name, product_price, quantity, category_name, category_id, users_products_id = item
            total = product_price * quantity
            cart_message += (f"📦 <b>Mahsulot:</b> {product_name}\n"
                            f"💰 <b>Narx:</b> {product_price} x {quantity} = {total}\n\n")
            total_price += total

        cart_message += f"Jami: {total_price}"
        print(f"Savatchadagi maxsulotlar: {cart_message}")
        await callback.message.answer(cart_message, parse_mode="HTML", reply_markup=cart_user_product)
    else:
        await callback.message.answer("Savatchangiz bo'sh.", reply_markup=view_product_user_keyboard)




async def checkout_user_handler(callback: CallbackQuery, category_id=None):
    user_id = callback.from_user.id
    await callback.message.edit_reply_markup(reply_markup=None)
    cart_items = database.get_user_cart(user_id, category_id)
    
    # Foydalanuvchi haqida ma'lumotni olish
    user_info = database.get_user_info(user_id)
    user_name = user_info[0]
    region = user_info[1]
    district = user_info[2]
    phone_number = user_info[5]
    latitude = user_info[3]  # Foydalanuvchi joylashuvi
    longitude = user_info[4]
   
    # Google Maps uchun URL yaratish
    google_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"
    
    if cart_items:
        # Admin uchun buyurtma haqida xabar yaratamiz
        cart_message = (f"🟢 <b>Yangi xarid</b> foydalanuvchi: <b>{user_name}</b> (ID: {user_id}) dan:\n\n"
                        f"📍 <b>Hudud:</b> {region}\n"
                        f"📍 <b>To'liq manzil:</b> {district}\n"
                        f"📞 <b>Telefon raqami:</b> {phone_number}\n\n")
        total_price = 0
        
        for item in cart_items:
            product_name = item[0]  # Mahsulot nomi
            product_price = item[1]  # Mahsulot narxi
            quantity = item[2]  # Mahsulot miqdori
            category_name = item[3]  # Mahsulot kategoriyasi
            category_id = item[4]  # Kategoriyaning ID si
            total = product_price * quantity
            
            cart_message += (f"🏷 <b>Kategoriya:</b> {category_name}\n"
                             f"🛍 <b>Mahsulot:</b> {product_name}\n"
                             f"💲 <b>Narx:</b> {product_price} x {quantity} = {total}\n\n")
            total_price += total
        
        cart_message += f"💰 <b>Jami narx:</b> {total_price}\n\n"
        cart_message += f"🌍 <b>Foydalanuvchi joylashuvi:</b> <a href='{google_maps_url}'>Google Maps orqali ko'rish</a>"
        
        # Adminga buyurtma haqida xabar jo'natish
        admin_id = config.ADMIN  # Admin ID'ni konfiguratsiyadan olishingiz kerak
        await callback.bot.send_message(
            chat_id=admin_id,
            text=cart_message,
            parse_mode="HTML",
            disable_web_page_preview=False,
            reply_markup=admin_to_user_keyboard(user_id, user_name)
        )

        # Foydalanuvchiga buyurtma yuborilganligi haqida xabar
        await callback.message.answer("Sizning xaridingiz qabul qilindi va adminga yuborildi.")
    else:
        await callback.message.answer("Savatchangiz bo'sh.", reply_markup=view_product_user_keyboard)


# Tasdiqlash tugmasi callback handler

async def confirm_user_order_handler(callback: CallbackQuery, state: FSMContext):
    user_info = callback.data.split("_")
    user_id = user_info[-2]
    user_name = user_info[-1]
    await callback.message.edit_reply_markup(reply_markup=None)
    # Adminga foydalanuvchiga yuborish kerak bo'lgan ma'lumotlarni kiritish imkoniyatini beramiz
    await callback.message.answer("Foydalanuvchiga yuborish uchun ma'lumotlarni kiriting:")
    
    # Ma'lumotlarni saqlaymiz va adminni kiritish jarayoniga o'tkazamiz
    await state.update_data(user_id=user_id, user_name=user_name)
    await state.set_state(user_state.AdminOrderForm.message_to_user)






# Admin tomonidan yuborilgan ma'lumotni olish
async def process_admin_message_to_user(message: Message, state: FSMContext, bot:Bot):    
    # Admin tomonidan yuborilgan ma'lumotni saqlaymiz
    data = await state.get_data()
    user_id = data.get("user_id")
    
    # Adminga yuborish
    if message.content_type == ContentType.TEXT:
        admin_reply = message.text
        # Dillerga adminning javobini yuborish
        await bot.send_message(
            chat_id=user_id,
            text=f"📩 <b>Admin sizga javob berdi:</b>\n\n{admin_reply}",
            parse_mode="HTML"
        )

    elif message.content_type == ContentType.PHOTO:
        # Rasmlarni yuborish
        photo = message.photo[-1].file_id  # Eng yuqori sifatli rasmni tanlash
        caption = message.caption or "Rasm"
        await bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=f"📩 <b>Admin sizga rasm yubordi:</b>\n{caption}",
            parse_mode="HTML"
        )

    elif message.content_type == ContentType.VIDEO:
        # Videoni yuborish
        video = message.video.file_id
        caption = message.caption or "Video"
        await bot.send_video(
            chat_id=user_id,
            video=video,
            caption=f"📩 <b>Admin sizga video yubordi:</b>\n{caption}",
            parse_mode="HTML"
        )

    elif message.content_type == ContentType.DOCUMENT:
        # Faylni yuborish
        document = message.document.file_id
        caption = message.caption or "Fayl"
        await bot.send_document(
            chat_id=user_id,
            document=document,
            caption=f"📩 <b>Admin sizga fayl yubordi:</b>\n{caption}",
            parse_mode="HTML"
        )
    await bot.send_message(user_id, "Adminga yana javob yuborishingiz mumkin.", reply_markup=admin_answer_to_user)
    await message.answer("Foydalanuvchiga muvafaqiyatli yuborildi.")
    # Yuboriladigan ma'lumotni holatga saqlaymiz
    await state.clear()


# User yana javob berishi uchun callback
async def user_reply_to_admin(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Adminga javobingizni yozing.")
    await state.set_state(user_state.AdminOrderForm.waiting_for_diller_reply)


# Userni javobini qabul qilish va adminga yuborish
async def handle_user_reply_admin(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    user_info = database.get_user_info(user_id)
    user_name = user_info[0]
    # Admin ID ni olish (config fayldan)
    admin_id = config.ADMIN

    # Adminga yuborish
    if message.content_type == ContentType.TEXT:
        user_reply = message.text
        # Matnli javobni yuborish
        await bot.send_message(
            chat_id=admin_id,
            text=f"📩 <b>Foydalanuvchidan yangi xabar:</b>\n\n<b>{user_name}:\n\n</b> sizga javob berdi:\n{user_reply}",
            parse_mode="HTML"
        )
    elif message.content_type == ContentType.PHOTO:
        # Rasmlarni yuborish
        photo = message.photo[-1].file_id  # Eng yuqori sifatli rasmni tanlash
        caption = message.caption or "Rasm"
        await bot.send_photo(
            chat_id=admin_id,
            photo=photo,
            caption=f"📩 <b>Foydalanuvchidan yangi rasm:</b>\n\n<b>{user_name}:\n\n</b> sizga rasm yubordi:\n{caption}",
            parse_mode="HTML"
        )
    elif message.content_type == ContentType.VIDEO:
        # Videoni yuborish
        video = message.video.file_id
        caption = message.caption or "Video"
        await bot.send_video(
            chat_id=admin_id,
            video=video,
            caption=f"📩 <b>Foydalanuvchidan yangi video:</b>\n\n<b>{user_name}\n\n</b> sizga video yubordi:\n{caption}",
            parse_mode="HTML"
        )
    elif message.content_type == ContentType.DOCUMENT:
        # Faylni yuborish
        document = message.document.file_id
        caption = message.caption or "Fayl"
        await bot.send_document(
            chat_id=admin_id,
            document=document,
            caption=f"📩 <b>Foydalanuvchidan yangi fayl:</b>\n\n<b>{user_name}\n\n</b> sizga fayl yubordi:\n{caption}",
            parse_mode="HTML"
        )



    await bot.send_message(
        chat_id=admin_id, 
        text="Userga yana javob yuborishingiz mumkin.", 
        reply_markup=admin_order_keyboard(user_id, user_name)
    )
    await state.clear()
    # Dillerga javob yuborilganini bildiruvchi xabar
    await message.answer("Javobingiz adminga yuborildi.")





########################## FOYDALANUVCHI BUYURTMALINI TASDIQLASH FUNKSIYALRI ##################
# Tasdiqlash tugmasi callback handler
async def confirm_send_to_user_handler(callback: CallbackQuery, bot: Bot):
    user_info = callback.data.split("_")
    user_id = user_info[-2]
    user_name = user_info[-1]
    # Holatdan diller ma'lumotlarini olish
    user_id = int(user_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    # Diller haqida ma'lumotlarni olish
    diller_info = database.get_user_info(user_id)
    region = diller_info[1]  # Yashash joyi
    admin_comment = "Sizning xaridingiz tasdiqlandi"


    
    confirm_items = database.get_user_cart(user_id)

    if confirm_items:
        # Kategoriya nomlarini va mahsulotlarni birlashtiramiz
        product_details = ""
        category_names = set()  # Kategoriya nomlarini saqlash uchun to'plam

        for item in confirm_items:
            product_name = item[0]
            price = item[1]
            quantity = item[2]
            category_name = item[3]
            product_id = item[5]

            # Mahsulot tafsilotlarini birlashtirish
            product_details += (f"🛍 <b>Mahsulot:</b> {product_name}\n"
                                f"💲 <b>narxi:</b> {price}\n"
                                f"📦 <b>Miqdori:</b> {quantity}\n"
                                f"🏷 <b>Kategoriya:</b> {category_name}\n"
                                f"-------------------------\n")
            # Kategoriya nomlarini yig'ish
            category_names.add(category_name)

            # Mahsulotni savatdan o'chirish
            delete_cart_page_by_diller = database.delete_from_user_cart_to_confirm(user_id, product_id)

        # Ma'lumotlar bazasiga tasdiqlangan buyurtmani saqlash
        confirm_order_product = database.save_user_confirm_order(user_id, user_name, region, ", ".join(category_names), product_details, admin_comment)
        print(f"Tasdiqlangan Buyurtmalr: {confirm_order_product}")
        # Foydalanuvchiga yuboriladigan xabar
        message_reply = (f"📩 <b>Sizning buyurmangiz qabul qilindi qildi:</b>\n\n"
                         f"👤 <b>To'liq ma'lumot uchun admin bilan bog'lanish:</b> <a href='https://t.me/{config.USERNAME}'><b>Admin bilan bog'lanish:</b></a>\n\n"
                        #  f"<b>Tafsilotlar:</b>\n\n{admin_comment}\n\n"
                         f"📦 <b>Tasdiqlangan mahsulotlar:</b>\n\n{product_details}")
        
        # Foydalanuvchiga yuborish
        await bot.send_message(chat_id=user_id, text=message_reply, parse_mode="HTML", reply_markup=view_product_user_keyboard)
        
        # Adminga yuborilganligi haqida xabar berish
        await callback.message.answer("Foydalanuvchiga xabar muvaffaqiyatli yuborildi.")
    else:
        await callback.message.answer("Savatchada mahsulot topilmadi.")




# Tasdiqlangan buyurtmalarni ko'rish
async def view_confirm_orders_handler_by_user(message: Message):
    user_id = message.from_user.id

    if database.is_user(user_id):
        confirm_orders = database.get_confirm_orders_by_user(user_id)

        if not confirm_orders:
            await message.answer("Tasdiqdan o'tgan buyurtmalar hozircha mavjudmas", reply_markup=view_product_user_keyboard)
        else:
            for order in confirm_orders:
                user_id, user_name, region, category_name, product_details, admin_comment, canceled_at = order

                # Bekor qilingan buyurtmalar haqida ma'lumot
                order_details = (f"📋 <b>Tasdiqlangan buyurtma</b>:\n"
                                f"👤 <b>Diller:</b> {user_name} (ID: {user_id})\n"
                                f"🏢 <b>Viloyat:</b> {region}\n"
                                f"🏷 <b>Kategoriya:</b> {category_name}\n"
                                f"📅 <b>Tasdiqlangan vaqt:</b> {canceled_at}\n\n"
                                f"📦 <b>Mahsulot tafsilotlari:</b>\n{product_details}\n"
                                f"📝 <b>Admin izohi:</b>\n{admin_comment}")

                await message.answer(order_details, parse_mode="HTML", reply_markup=view_product_user_keyboard)
    else: message.answer("Siz user emassiz")









# Bekor qilish tugmasi callback handler
async def cancel_user_order_handler(callback: CallbackQuery, state:FSMContext):
    user_info = callback.data.split("_")
    
    user_id = user_info[-2]
    user_name = user_info[-1]
    await callback.message.edit_reply_markup(reply_markup=None)
   
    await callback.message.answer("Foydalanuvchiga Nima uchun buyurtmani bekor qilganingiz haqida qisqacha xabar qoldiring:")
    
    # Ma'lumotlarni saqlaymiz va adminni kiritish jarayoniga o'tkazamiz
    await state.update_data(user_id=user_id, user_name=user_name)
    await state.set_state(user_state.AdminOrderForm.cancel)



# Yuborish tugmasi bosilganda foydalanuvchiga ma'lumot yuboriladi
async def cancel_send_to_user_handler(message:Message, state:FSMContext, bot:Bot):
    # Holatdan diller ma'lumotlarini olish
    user_info = await state.get_data()
    user_id = user_info.get("user_id")
    user_name = user_info.get("user_name")
    user_id = int(user_id)
    # Diller haqida ma'lumotlarni olish
    diller_info = database.get_user_info(user_id)
    region = diller_info[1]  # Yashash joyi

    # Admin tomonidan kiritilgan tafsilotlarni olish
    admin_comment = message.text

    # Bekor qilingan mahsulot haqida ma'lumot olish
    # Barcha savatchadagi mahsulotlarni olib kelamiz
    canceled_items = database.get_user_cart(user_id)

    if canceled_items:
        # Kategoriya nomlarini va mahsulotlarni birlashtiramiz
        product_details = ""
        category_names = set()  # Kategoriya nomlarini saqlash uchun to'plam

        for item in canceled_items:
            product_name = item[0]
            price = item[1]
            quantity = item[2]
            category_name = item[3]
            product_id = item[5]

            # Mahsulot tafsilotlarini birlashtirish
            product_details += (f"🛍 <b>Mahsulot:</b> {product_name}\n"
                                f"💲 <b>narxi:</b> {price}\n"
                                f"📦 <b>Miqdor:</b> {quantity}\n"
                                f"🏷 <b>Kategoriya:</b> {category_name}\n"
                                f"-------------------------\n")
            # Kategoriya nomlarini yig'ish
            category_names.add(category_name)

            # Mahsulotni savatdan o'chirish
            delete_cart_page_by_diller = database.delete_from_user_cart_to_cancel(user_id, product_id)

        # Ma'lumotlar bazasiga bekor qilingan buyurtmani saqlash
        cancel_order_product = database.save_user_canceled_order(user_id, user_name, region, ", ".join(category_names), product_details, admin_comment)
        print(f"Bekor qilinga maxsulotlar: {cancel_order_product}")
        # Foydalanuvchiga yuboriladigan xabar
        message_reply = (f"📩 <b>Admin Buyurtmani bekor qildi:</b>\n\n"
                         f"👤 <b>To'liq ma'lumot uchun admin bilan bog'lanish:</b> <a href='https://t.me/{config.USERNAME}'><b>Admin bilan bog'lanish:</b></a>\n\n"
                         f"<b>Tafsilotlar:</b>\n\n{admin_comment}\n\n"
                         f"📦 <b>Bekor qilingan mahsulotlar:</b>\n\n{product_details}")
        
        # Foydalanuvchiga yuborish
        await bot.send_message(chat_id=user_id, text=message_reply, parse_mode="HTML", reply_markup=view_product_user_keyboard)
        
        # Adminga yuborilganligi haqida xabar berish
        await message.answer("Userga xabar muvaffaqiyatli yuborildi.")
    else:
        await message.answer("Savatchada mahsulot topilmadi.")

    # Holatni tozalash
    await state.clear()



# Bekor qilingan maxsulotlarni olish
async def view_canceled_orders_handler_by_user(message: Message):
    user_id = message.from_user.id

    if database.is_user(user_id):
        canceled_orders = database.get_canceled_orders_by_users(user_id)
        if not canceled_orders:
            await message.answer("Bekor qilingan buyurtmalar hozircha mavjud emas.", reply_markup=view_product_user_keyboard)
        else:
            for order in canceled_orders:
                user_id, user_name, region, category_name, product_details, admin_comment, canceled_at = order

                # Bekor qilingan buyurtmalar haqida ma'lumot
                order_details = (f"📋 <b>Bekor qilingan buyurtma</b>:\n\n"
                                f"👤 <b>Foydalanuvchi:</b> {user_name} (ID: {user_id})\n"
                                f"🏢 <b>region:</b> {region}\n"
                                f"🏷 <b>Kategoriya:</b> {category_name}\n"
                                f"📅 <b>Bekor qilingan vaqt:</b> {canceled_at}\n\n"
                                f"📦 <b>Mahsulot tafsilotlari:</b>\n{product_details}\n"
                                f"📝 <b>Admin izohi:</b>\n{admin_comment}")

                await message.answer(order_details, parse_mode="HTML", reply_markup=view_product_user_keyboard)
    else: message.answer("Siz user emassiz")




# Admin Uchun orderlarni ko'rsatish
async def view_order_user_reply_product(message:Message, bot:Bot):
    user_id = message.from_user.id
    if user_id == config.ADMIN:
        view_order_user_admin = database.get_confirm_orders_by_user_reply_admin()
        if not view_order_user_admin:
            await message.answer("Hech qaysi foydalanuvchida orderlar yo'q")
        else:
            for order in view_order_user_admin:
                user_id, user_name, region, category_name, product_details, admin_comment, canceled_at = order
                order_details = (f"📋 <b>Qabul qilingan buyurtma</b>:\n\n"
                                f"👤 <b>Foydalanuvchi:</b> {user_name} (ID: {user_id})\n"
                                f"🏢 <b>region:</b> {region}\n"
                                f"🏷 <b>Kategoriya:</b> {category_name}\n"
                                f"📅 <b>Qabul qilingan vaqt:</b> {canceled_at}\n\n"
                                f"📦 <b>Mahsulot tafsilotlari:</b>\n{product_details}\n"
                                f"📝 <b>Admin izohi:</b>\n{admin_comment}")
                await bot.send_message(
                    chat_id=config.ADMIN,
                    text=order_details,
                    parse_mode="HTML"
                )
    else: message.answer("Siz admin emassiz")




# Admin Uchun bekor qilingan ma'xsulotlarni ko'rsatish
async def view_cancel_order_user_reply_product(message:Message, bot:Bot):
    user_id = message.from_user.id
    if user_id == config.ADMIN:
        view_order_user_admin = database.get_canceled_orders_by_users_reply_admin()
        if not view_order_user_admin:
            await message.answer("Hech qaysi foydalanuvchilarda bekor qilingan orderlar yo'q")
        else:
            for order in view_order_user_admin:
                user_id, user_name, region, category_name, product_details, admin_comment, canceled_at = order
                order_details = (f"📋 <b>Bekor qilingan buyurtma</b>:\n\n"
                                f"👤 <b>Foydalanuvchi:</b> {user_name} (ID: {user_id})\n"
                                f"🏢 <b>region:</b> {region}\n"
                                f"🏷 <b>Kategoriya:</b> {category_name}\n"
                                f"📅 <b>Bekor qilingan vaqt:</b> {canceled_at}\n\n"
                                f"📦 <b>Mahsulot tafsilotlari:</b>\n{product_details}\n"
                                f"📝 <b>Admin izohi:</b>\n{admin_comment}")
                await bot.send_message(
                    chat_id=config.ADMIN,
                    text=order_details,
                    parse_mode="HTML"
                )
    else: message.answer("Siz admin emassiz")