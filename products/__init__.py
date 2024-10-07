from aiogram import Router, Bot, F
from . import category, product_state, product_user, product_diller
from aiogram.filters import Command


product_router = Router()





########## Kategoriyalar ###########
product_router.message.register(category.category_all, F.text == "📂 Kategoriyalar")
product_router.message.register(category.product_all, F.text == "🛍️ Maxsulotlar")
product_router.callback_query.register(category.category_all_calback, F.data.startswith("category_orqaga_qaytish"))
product_router.callback_query.register(category.product_all_callback, F.data.startswith("orqaga_qaytish"))
product_router.callback_query.register(category.add_category, F.data.startswith("add_category"))
product_router.message.register(category.get_category_name, product_state.Add_Category.name)
product_router.message.register(category.get_category_image, product_state.Add_Category.img)
product_router.callback_query.register(category.view_categories, F.data.startswith("view_category"))
product_router.callback_query.register(category.delete_category_handler, F.data.startswith("delete_category"))

############ Foydalanuvchi Maxsulotlari ############
product_router.callback_query.register(product_user.user_add_product, F.data.startswith("add_product"))
product_router.callback_query.register(product_user.select_category_for_user_product, product_state.UserProductState.category)
product_router.message.register(product_user.get_user_product_name, product_state.UserProductState.name)
product_router.message.register(product_user.get_user_product_description, product_state.UserProductState.description)
product_router.message.register(product_user.get_product_image1, product_state.UserProductState.image1)
product_router.message.register(product_user.get_product_image2, product_state.UserProductState.image2)
product_router.message.register(product_user.get_product_image3, product_state.UserProductState.image3)
product_router.message.register(product_user.get_product_image4, product_state.UserProductState.image4)
product_router.message.register(product_user.get_user_product_video, product_state.UserProductState.video)
product_router.message.register(product_user.get_user_price_message_answer, product_state.UserProductState.price)
product_router.message.register(product_user.get_user_stock_message_answer, product_state.UserProductState.stock)
product_router.message.register(product_user.confirm_user_product, product_state.UserProductState.confirm)
product_router.callback_query.register(product_user.delete_user_product_handler, F.data.startswith("delete_pd_"))
product_router.callback_query.register(product_user.view_all_user_products, F.data.startswith("view_product"))




############ Diller Maxsulotlari ############
product_router.callback_query.register(product_diller.diller_add_product, F.data.startswith("add_diller_product"))
product_router.callback_query.register(product_diller.select_category_for_diller_product, product_state.DillerProductState.category)
product_router.message.register(product_diller.get_diller_product_name, product_state.DillerProductState.name)
product_router.message.register(product_diller.get_diller_product_description, product_state.DillerProductState.description)
product_router.message.register(product_diller.get_diller_product_image1, product_state.DillerProductState.image1)
product_router.message.register(product_diller.get_diller_product_image2, product_state.DillerProductState.image2)
product_router.message.register(product_diller.get_diller_product_image3, product_state.DillerProductState.image3)
product_router.message.register(product_diller.get_diller_product_image4, product_state.DillerProductState.image4)
product_router.message.register(product_diller.get_diller_product_video, product_state.DillerProductState.video)
product_router.message.register(product_diller.get_diller_price_message_answer, product_state.DillerProductState.wholesale_price)
product_router.message.register(product_diller.get_diller_stock_message_answer, product_state.DillerProductState.stock)
product_router.message.register(product_diller.confirm_diller_product, product_state.DillerProductState.confirm)
product_router.callback_query.register(product_diller.delete_diller_product_handler, F.data.startswith("delete_pd_"))
product_router.callback_query.register(product_diller.view_all_diller_products, F.data.startswith("diller_view_product"))
