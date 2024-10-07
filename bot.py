import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, BotCommand
from aiogram.filters import Command
from asyncio import run
from config import BOT_TOKEN, ADMIN
from database import create_table
import diller, admin, users, products
import database
from aiogram.fsm.storage.memory import MemoryStorage


dp = Dispatcher(storage=MemoryStorage())

# Router yaratish
router = Router()


# Logging sozlamalari
logging.basicConfig(
    filename='bot_log.txt',  # Loglar saqlanadigan fayl nomi
    level=logging.INFO,      # Log darajasi (INFO darajasida barcha ma'lumotlar yoziladi)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def startup_answer(bot:Bot):
    await bot.send_message(ADMIN, "Bot ishga tushdi ✅")

async def shutdown_answer(bot:Bot):
    await bot.send_message(ADMIN, "Bot ishdan to'xtadi! ❌")

async def help_answer(message:Message):
    user_id = message.from_user.id
    if user_id == ADMIN:
        await message.answer("""
    Assalomu aleykum bot komandalari:
    admin komandalari:
    /start:  Botni ishga tushurish.
    /help:  Yordam.!
    /diller_info_edit: Diller ma'lumotlarini tahrirlash
    /user_info_edit: Foydalanuvchilarni ma'lumotlarini tahrirlash
            """)
    else:
        await message.answer("""
    Assalomu aleykum.!
    
Bot sizga qulay va juda yuqori sifatli maxsulotlarni taklif qildi.
Agar maxsulotlarni ko'rishni istasangiz /start buyrug'ini yuboring.
""")


async def set_commands(message:Message, bot:Bot):
    user_id = message.from_user.id
    
    

async def start():
    dp.startup.register(startup_answer)
    # dp.message.register(start_answer, Command("start"))
    # dp.message.register(get_contact, F.contact)
    dp.include_routers(diller.diller_router)
    dp.include_routers(users.user_router)
    dp.include_routers(admin.router_admin)
    dp.include_routers(products.product_router)

    dp.message.register(help_answer, Command("help"))
    dp.shutdown.register(shutdown_answer)

    bot = Bot(token=BOT_TOKEN)
    await bot.set_my_commands([
        BotCommand(command="/start", description="Botni ishga tushurish"),
        BotCommand(command="/help", description="Yordam!")
    ])
    # Jadvalni yaratish
    create_table()  # Jadval yaratiladi (agar mavjud bo'lmasa)
    logging.info("Bot ishga tushirildi")
    await dp.start_polling(bot, skip_updates=True, polling_timeout=1)

if __name__ == "__main__":
    run(start())