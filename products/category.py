from aiogram import Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from products import product_state
from database import save_category, get_all_categories, delete_category, save_user_product, get_all_user_products, delete_user_product
from database import save_diller_product, get_all_diller_products, delete_diller_product
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from products.product_keyboard import view_category_button, view_user_product_button, user_product_button
from config import ADMIN







async def category_all(message:Message):
    user_id = message.from_user.id
    if user_id == ADMIN: await message.reply("Mavjud Kategoriyalar", reply_markup=view_category_button)
    else: message.answer("Siz admin emassiz")

async def product_all(message:Message):
    user_id = message.from_user.id
    if user_id == ADMIN: await message.reply("Mavjud maxsulotlar", reply_markup=view_user_product_button)
    else: message.answer("Siz admin emassiz")



async def category_all_calback(calback:CallbackQuery):
    user_id = calback.from_user.id
    if user_id == ADMIN: 
        await calback.message.reply("Mavjud Kategoriyalar", reply_markup=view_category_button)
        await calback.message.edit_reply_markup(reply_markup=None)
    else: calback.message.answer("Siz admin emassiz")



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


# Admin uchun kategoriya qo'shish funksiyasi
async def add_category(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await callback_query.message.edit_reply_markup(reply_markup=None)
    if user_id == ADMIN:
        await callback_query.message.answer("Kategoriya nomini kiriting:")
        
        # Kategoriya nomini olish uchun holat
        await state.set_state(product_state.Add_Category.name)
    else: 
        await callback_query.message.answer("Siz admin emassiz")

# Kategoriya nomini olish va rasmni so'rash
async def get_category_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id == ADMIN:
        category_name = message.text
        await state.update_data(category_name=category_name)
        await message.answer("Kategoriya uchun rasmni yuboring:")
        
        # Rasmni olish uchun holat
        await state.set_state(product_state.Add_Category.img)
    else: 
        await state.clear()
        await message.answer("Siz admin emassiz")

# Rasmni olish va kategoriyani saqlash
async def get_category_image(message:Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id == ADMIN:
        data = await state.get_data()
        category_name = data.get("category_name")
        image_file_id = message.photo[-1].file_id  # Eng katta rasm
        await save_category(category_name, image_file_id)  # Bazaga saqlash
        await message.answer_photo(image_file_id)
        await message.answer(f"Kategoriya '{category_name}' saqlandi.", reply_markup= user_product_button)
        await state.clear()
    else:
        await state.clear()
        await message.answer("Siz admin emassiz")



######## KATEGORIYALARNI KO'RISH VA O'CHIRISH ############
async def view_categories(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    await callback_query.message.edit_reply_markup(reply_markup=None)
    if user_id == ADMIN:
        categories = await get_all_categories()

        if categories:
            for category in categories:
                id, name, image = category

                # Inline buttonda kategoriya ID bilan birga delete_category_{id} formatida callback_data yuboriladi
                delete_button = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Kategoriyani o'chirish", callback_data=f"delete_category_{id}")],
                    [InlineKeyboardButton(text="⬅️ Orqaga qaytish", callback_data="category_orqaga_qaytish")]
                ])

                # Kategoriya nomi va rasm bilan javob berish
                await callback_query.message.answer_photo(photo=image, caption=name, reply_markup=delete_button)
        else:
            await callback_query.message.answer("Hozircha kategoriya mavjud emas.")
    else: callback_query.message.answer("Siz admin emassiz")

async def delete_category_handler(callback_query: CallbackQuery):
    # Callback data formatidan ID ni olish (delete_category_{id} formatida bo'ladi)
    category_id = int(callback_query.data.split("_")[2])
    
    # Bazadan kategoriyani o'chirish
    await delete_category(category_id)

    # Muvaffaqiyatli javob qaytarish
    await callback_query.answer("Kategoriya muvaffaqiyatli o'chirildi.")
    await callback_query.message.delete()

###########   AND     #################




