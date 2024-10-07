from aiogram import Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from products import product_state
from database import get_all_categories, save_user_product, get_all_user_products, delete_user_product
from database import save_diller_product, get_all_diller_products, delete_diller_product
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from products.product_keyboard import user_product_button,view_user_product_button
from config import ADMIN
from aiogram.types import InputMediaPhoto, InputMediaVideo




######### MAXSULOTLAR QO'SHISH ############

# Admin uchun mahsulotlar qo'shish funksiyasi (kategoriya tanlash va video bilan)
async def user_add_product(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await callback_query.message.edit_reply_markup(reply_markup=None)

    if user_id == ADMIN:
        categories = await get_all_categories()
        if categories:
            buttons = []
            for category in categories:
                id, name, _ = category
                buttons.append([InlineKeyboardButton(text=name, callback_data=f"select_category_{id}")])
            buttons.append([InlineKeyboardButton(text="⬅️ Orqaga qaytish", callback_data="orqaga_qaytish")])
            markup = InlineKeyboardMarkup(inline_keyboard=buttons)
            await callback_query.message.answer("Mahsulot qaysi kategoriya uchun qo'shiladi? Kategoriyani tanlang:", reply_markup=markup)
            await state.set_state(product_state.UserProductState.category)
            await callback_query.message.delete()
        else:
            await callback_query.message.answer("Hozircha hech qanday kategoriya mavjud emas.")
    else:
        await callback_query.message.answer("Siz admin emassiz")


# Kategoriya tanlagandan so'ng mahsulot nomini olish
async def select_category_for_user_product(callback_query: CallbackQuery, state: FSMContext):
    callback_data = callback_query.data

    if callback_data == "orqaga_qaytish":
        # Agar "Orqaga qaytish" tugmasi bosilgan bo'lsa, product_all_callback funksiyasini chaqiramiz
        await product_all_callback(callback_query)
        return

    # Agar Orqaga qaytish bosilmagan bo'lsa, kategoriya jarayoni davom etadi
    category = callback_data.split("_")
    
    try:
        category_id = int(category[-1])  # Oxirgi qismni category_id sifatida oling
    except ValueError:
        await callback_query.message.answer("Xatolik: noto'g'ri category_id olindi.")
        return

    await callback_query.message.edit_reply_markup(reply_markup=None)
    await state.update_data(category_id=category_id)
    await callback_query.message.answer("Mahsulot nomini kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(product_state.UserProductState.name)
    await callback_query.message.delete()

# Orqaga qaytish tugmasi bosilganda
async def product_all_callback(callback:CallbackQuery):
    user_id = callback.from_user.id
    if user_id == ADMIN: 
        await callback.message.reply("Mavjud maxsulotlar", reply_markup=view_user_product_button)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.delete()
    else: 
        callback.answer("Siz admin emassiz") 
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.delete()


# Mahsulot tavsifi olish
async def get_user_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Mahsulot tavsifini kiriting:")
    await state.set_state(product_state.UserProductState.description)

# Mahsulot rasmlarini olish
async def get_user_product_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Mahsulot uchun rasmlarni yuboring (Jami 4 ta rasm bo'lishi kerak):")
    await message.answer("Birinchi rasmni yuboring...:")
    await state.set_state(product_state.UserProductState.image1)

# Birinchi rasmni olish va ikkinchi rasmni so'rash
async def get_product_image1(message: Message, state: FSMContext):
    image1 = message.photo[-1].file_id  # Oxirgi kelgan rasmni olish
    await state.update_data(image1=image1)
    await message.answer("Mahsulotning ikkinchi rasmini yuboring:")
    await state.set_state(product_state.UserProductState.image2)

# Ikkinchi rasmni olish va uchinchi rasmni so'rash
async def get_product_image2(message: Message, state: FSMContext):
    image2 = message.photo[-1].file_id
    await state.update_data(image2=image2)
    await message.answer("Mahsulotning uchinchi rasmini yuboring:")
    await state.set_state(product_state.UserProductState.image3)

# Uchinchi rasmni olish va to'rtinchi rasmni so'rash
async def get_product_image3(message: Message, state: FSMContext):
    image3 = message.photo[-1].file_id
    await state.update_data(image3=image3)
    await message.answer("Mahsulotning to'rtinchi rasmini yuboring:")
    await state.set_state(product_state.UserProductState.image4)

# To'rtinchi rasmni olish va videoni so'rash (majburiy emas)
async def get_product_image4(message: Message, state: FSMContext):
    image4 = message.photo[-1].file_id
    await state.update_data(image4=image4)
    await message.answer("Mahsulot uchun videoni yuboring (majburiy emas, 'skip' deb yozishingiz mumkin):")
    await state.set_state(product_state.UserProductState.video)


# Mahsulot videosini olish
async def get_user_product_video(message: Message, state: FSMContext):
    # Agar foydalanuvchi "skip" deb yozsa, videoni o'tkazib yuborish
    if message.text and message.text.lower() == "skip":
        await state.update_data(video=None)  # Video bo'lmagan holatda None sifatida saqlanadi
        await message.answer("Video yuklanmadi.")
        await message.answer("Maxsulot narxini kiriting")
        await state.set_state(product_state.UserProductState.price)
    elif message.video:
        # Agar video yuborilgan bo'lsa, uni saqlash
        video = message.video.file_id
        await state.update_data(video=video)
        await message.answer("Video muvaffaqiyatli yuklandi.")
        await message.answer("Maxsulot narxini kiriting")
        await state.set_state(product_state.UserProductState.price)
    else:
        # Video yuborilmagan va "skip" ham qilinmagan holatni ogohlantirish
        await message.answer("Iltimos, video yuboring yoki 'skip' deb yozing.")
        


# Maxsulot narxini olish
async def get_user_price_message_answer(message:Message, state:FSMContext):
        price_text = message.text
        try:
            # Narxni float yoki int ga o'girishga urinib ko'ramiz
            price = int(price_text)
            
            if price <= 0:
                await message.answer("Narx 0 dan katta bo'lishi kerak. Iltimos, qaytadan kiriting.")
                return

            # Narx to'g'ri formatda bo'lsa, davom etish
            await message.answer(f"Narx qabul qilindi: {price}")
            await message.answer("Maxsulot sonini kiriting")
            
            # Bu yerda holatni yangilab ketishingiz mumkin
            await state.update_data(price=price)
            await state.set_state(product_state.UserProductState.stock)
        
        except ValueError:
            # Agar xatolik bo'lsa, foydalanuvchiga xabar bering
            await message.answer("Iltimos, narxni to'g'ri formatda kiriting (faqat raqamlar).")


# Maxsulot sonini olish
async def get_user_stock_message_answer(message:Message, state:FSMContext):
        stock_text = message.text
        try:
            # Maxsulot sonini int ga o'girishga urinib ko'ramiz
            stock = int(stock_text)
            
            if stock <= 0:
                await message.answer("Narx 0 dan katta bo'lishi kerak. Iltimos, qaytadan kiriting.")
                return

            # Maxsulot soni to'g'ri formatda bo'lsa, davom etish
            await message.answer(f"Maxsulot soni qabul qilindi: {stock}")
            await message.answer("Mahsulot ma'lumotlari tayyor. Tasdiqlash uchun 'ok' deb yozing.\nMaxsulotlar tasdiqlanishini istamasangiz 'yoq' deb yozing")
            
            # Bu yerda holatni yangilab ketishingiz mumkin
            await state.update_data(stock=stock)
            await state.set_state(product_state.UserProductState.confirm)
        
        except ValueError:
            # Agar xatolik bo'lsa, foydalanuvchiga xabar bering
            await message.answer("Iltimos, Maxsulot sonini to'g'ri formatda kiriting (faqat raqamlar).")


async def confirm_user_product(message: Message, state: FSMContext):
    if message.text.lower() == "ok":
        # State-dan barcha to'plangan ma'lumotlarni olish
        data = await state.get_data()
        category_id = data.get('category_id')
        name = data.get('name')
        description = data.get('description')
        
        # Rasmlar alohida holatlardan olinmoqda
        image1 = data.get('image1')
        image2 = data.get('image2')
        image3 = data.get('image3')
        image4 = data.get('image4')

        # Video (agar mavjud bo'lsa) olish
        video = data.get('video')  # Video None bo'lishi mumkin
        
        # Narx va sklad ma'lumotlarini olish
        price = data.get("price")
        stock = data.get("stock")

        # Mahsulotni saqlash uchun chaqirish
        save_user_product(
            name=name, 
            category_id=category_id, 
            description=description, 
            image1=image1, 
            image2=image2, 
            image3=image3, 
            image4=image4, 
            video=video, 
            price=price, 
            stock=stock
        )

        # Mahsulot muvaffaqiyatli qo'shilganligi haqida javob berish
        await message.answer("Mahsulot muvaffaqiyatli qo'shildi!", reply_markup=user_product_button)
        
        # Holatni tozalash
        await state.clear()
    
    elif message.text.lower() == "yoq":
        # Agar foydalanuvchi ma'lumotlarni bekor qilsa
        await message.answer("Barcha to'plangan ma'lumotlar o'chirildi", reply_markup=user_product_button)
        
        # Holatni tozalash
        await state.clear()





async def view_all_user_products(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    await callback_query.message.edit_reply_markup(reply_markup=None)
    
    # Faqat admin mahsulotlarni ko'ra olishi uchun shart
    if user_id == ADMIN:
        products = get_all_user_products()

        if products:
            for product in products:
                # 12 ustunni to'g'ri ajratib olish
                id, name, category_id, description, image1, image2, image3, image4, video, price, stock, added_at = product
                
                # Rasmlar ro'yxatini yig'ish (bo'sh bo'lmagan rasmlarni olish)
                media = []
                if image1:
                    media.append(InputMediaPhoto(media=image1))
                if image2:
                    media.append(InputMediaPhoto(media=image2))
                if image3:
                    media.append(InputMediaPhoto(media=image3))
                if image4:
                    media.append(InputMediaPhoto(media=image4))
                if video:
                    media.append(InputMediaVideo(media=video))

                # O'chirish tugmasi bilan birga inline tugmalarni qo'shish
                delete_button = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🗑️ Mahsulotni o'chirish", callback_data=f"delete_pd_{id}")],
                    [InlineKeyboardButton(text="⬅️ Orqaga qaytish", callback_data="orqaga_qaytish")]
                ])

                # Agar rasm yoki video bo'lsa, ularni yuborish
                if media:
                    await callback_query.message.answer_media_group(media=media)

                # Matnli ma'lumotlar bilan birga tugmalarni yuborish
                await callback_query.message.answer(
                    f"Kategoriya: {category_id}\nNomi: {name}\nTavsif: {description}\nNarx: {price}\nSklad: {stock}\nQo'shilgan sana: {added_at}",
                    reply_markup=delete_button
                )
        else:
            await callback_query.message.answer("Hozircha hech qanday mahsulot mavjud emas.")
    else:
        await callback_query.message.answer("Siz admin emassiz.")




# Mahsulotni o'chirish funksiyasi
async def delete_user_product_handler(callback_query: CallbackQuery):
    product = callback_query.data.split("_")
    product_id = product[-1]
    product_id = int(product_id)
    # Mahsulotni bazadan o'chirish
    user_delete_product = delete_user_product(product_id)
    print(f"turi {type(product_id)}, {product_id}")
    print(f"O'chirilgan ustun {user_delete_product}")
    callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.delete()
    # Javob qaytarish
    await callback_query.message.answer("Mahsulot muvaffaqiyatli o'chirildi.")
    