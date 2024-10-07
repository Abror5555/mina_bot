from aiogram import Router, F, types
from aiogram.filters import Command, CommandStart
from . import user_start, user_state, view_user_product


user_router = Router()

# Callback query uchun handler
user_router.callback_query.register(user_start.user_callback_handler, F.data.startswith("mchj_yoq"))


################# Diller nomi uchun handler #################
user_router.message.register(user_start.user_state_name_answer, user_state.UserState.name)

################ Viloyat uchun handler ################
user_router.message.register(user_start.user_region_answer, user_state.UserState.region)

################## Tuman uchun handler ##################
user_router.message.register(user_start.user_district_answer, user_state.UserState.district)

################### Joylashuv qabul qiladigan handler ##################
user_router.callback_query.register(user_start.user_request_location, F.data.startswith("user_send_location"))
user_router.message.register(user_start.user_location_handler, user_state.UserState.location, F.location)

################### Contact uchun handler ##############
user_router.message.register(user_start.user_tasdiq_message_answer, user_state.UserState.phone)

####### To'plangan ma'lumotlarni saqlash yoki o'chirish ###################
user_router.callback_query.register(user_start.get_user_contact, F.data.startswith("user_save_data"))
user_router.callback_query.register(user_start.delete_user_state_answer, F.data.startswith("user_delete_data"))

############### Ma'lumotlarni tekshirish ############
user_router.message.register(user_start.show_user_info, F.text == "ma'lumotlaringiz")





################ Maxsulotlarni foydalanuvchiga chiqaradigan qismi ##################

user_router.callback_query.register(view_user_product.view_product_user_key_handler, F.data.startswith("view_product_user_key"))
user_router.callback_query.register(view_user_product.view_category_user_handler, F.data.startswith("view_category_"))



################## Maxsulotlarni cart qismiga qo'shish #####################

user_router.callback_query.register(view_user_product.view_user_cart_handler, F.data.startswith("view_user_cart"))
user_router.callback_query.register(view_user_product.add_to_user_cart_handler, F.data.startswith("add_user_cart_"))
user_router.callback_query.register(view_user_product.checkout_user_handler, F.data.startswith("checkout_user_cart"))


################# Admin bilan muloqot ###############
user_router.callback_query.register(view_user_product.confirm_user_order_handler, F.data.startswith("user_reply_to_admin_"))
user_router.callback_query.register(view_user_product.confirm_user_order_handler, F.data.startswith("admin_reply_to_user_"))
user_router.message.register(view_user_product.process_admin_message_to_user, user_state.AdminOrderForm.message_to_user, F.content_type.in_({types.ContentType.TEXT, types.ContentType.PHOTO, types.ContentType.VIDEO, types.ContentType.DOCUMENT}))
user_router.callback_query.register(view_user_product.user_reply_to_admin, F.data.startswith("admin_answer_to_user"))
user_router.message.register(view_user_product.handle_user_reply_admin, user_state.AdminOrderForm.waiting_for_diller_reply, F.content_type.in_({types.ContentType.TEXT, types.ContentType.PHOTO, types.ContentType.VIDEO, types.ContentType.DOCUMENT}))


#################### Xaridni qabul qilish ###############
user_router.callback_query.register(view_user_product.confirm_send_to_user_handler, F.data.startswith("confirm_order_by_user_"))
user_router.message.register(view_user_product.view_confirm_orders_handler_by_user, F.text == "Xarid qilgan maxsulotlar")


################### Xaridni bekor qilish ###########
user_router.callback_query.register(view_user_product.cancel_user_order_handler, F.data.startswith("cancel_order_by_user_"))
user_router.message.register(view_user_product.cancel_send_to_user_handler, user_state.AdminOrderForm.cancel)
user_router.message.register(view_user_product.view_canceled_orders_handler_by_user, F.text == "Bekor qilingan xaridlar")



################### Adminga user maxsulotlar haqida malumotlarni yuborish ###############
user_router.message.register(view_user_product.view_order_user_reply_product, Command("view_confirm_order_by_admin"))
user_router.message.register(view_user_product.view_cancel_order_user_reply_product, Command("view_cancel_order_by_admin"))