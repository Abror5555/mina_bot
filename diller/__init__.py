from aiogram import Router, F, types
from aiogram.filters import Command, CommandStart
from . import diller_start, diller_user_state, view_diller_product
# from aiogram.types import ContentType

diller_router = Router()


######## /start komandasi uchun handler ###############
diller_router.message.register(diller_start.start_answer, CommandStart())

# Callback query uchun handler
diller_router.callback_query.register(diller_start.mchj_callback_handler, F.data.startswith("mchj_ha"))

################# Diller nomi uchun handler #################
diller_router.message.register(diller_start.diller_state_name_answer, diller_user_state.DillerState.name)

############### Firma nomini qabul qiluvchi handler #########
diller_router.message.register(diller_start.diller_company_name_answer, diller_user_state.DillerState.company_name)

################ Viloyat uchun handler ################
diller_router.message.register(diller_start.diller_region_answer, diller_user_state.DillerState.region)

################## Tuman uchun handler ##################
diller_router.message.register(diller_start.diller_district_answer, diller_user_state.DillerState.district)

################### Joylashuv qabul qiladigan handler ##################
diller_router.callback_query.register(diller_start.request_location, F.data.startswith("send_location"))
diller_router.message.register(diller_start.location_handler, diller_user_state.DillerState.location, F.location)

################### Contact uchun handler ##############
diller_router.message.register(diller_start.tasdiq_message_answer, diller_user_state.DillerState.phone)

####### To'plangan ma'lumotlarni saqlash yoki o'chirish ###################
diller_router.callback_query.register(diller_start.get_diller_contact, F.data.startswith("diller_save_data"))
diller_router.callback_query.register(diller_start.delete_state_answer, F.data.startswith("diller_delete_data"))


diller_router.message.register(diller_start.show_diller_info, F.text == "Diller ma'lumotlari")




############## Diller foydalanuvchi maxsulotlarini ko'rish ############
diller_router.callback_query.register(view_diller_product.view_product_diller_key_handler, F.data.startswith("view_product_diller_key"))
diller_router.callback_query.register(view_diller_product.view_diller_cart_handler, F.data.startswith("view_diller_cart"))
diller_router.callback_query.register(view_diller_product.view_category_diller_handler, F.data.startswith("view_ctd_"))
diller_router.callback_query.register(view_diller_product.add_to_diller_cart_handler, F.data.startswith("add_diller_cart_"))
# diller_router.callback_query.register(vew_diller_product.ask_for_quantity, F.data.startswith("add_diller_cart_"))
# diller_router.message.register(vew_diller_product.add_to_diller_cart_handler, diller_user_state.DillerOrderState.waiting_for_quantity)
diller_router.callback_query.register(view_diller_product.diller_buy_button_handler, F.data.startswith("checkout_diller_cart"))
diller_router.message.register(view_diller_product.checkout_diller_handler, diller_user_state.DillerOrderState.waiting_for_diller_details)
diller_router.callback_query.register(view_diller_product.confirm_diller_order_handler, F.data.startswith("admin_reply_to_diller_"))
diller_router.message.register(view_diller_product.handle_diller_reply_admin, diller_user_state.DillerOrderState.waiting_for_diller_reply, F.content_type.in_({types.ContentType.TEXT, types.ContentType.PHOTO, types.ContentType.VIDEO, types.ContentType.DOCUMENT}))
diller_router.callback_query.register(view_diller_product.diller_reply_to_admin, F.data.startswith("admin_answer_to_diller"))
diller_router.message.register(view_diller_product.diller_handle_admin_reply, diller_user_state.DillerOrderState.waiting_for_admin_reply, F.content_type.in_({types.ContentType.TEXT, types.ContentType.PHOTO, types.ContentType.VIDEO, types.ContentType.DOCUMENT}))


############### BUYURTMANI QABUL QILSIH ###############
diller_router.callback_query.register(view_diller_product.confirm_send_to_diller_handler, F.data.startswith("confirm_ord_by_diller_"))
# diller_router.message.register(view_diller_product.confirm_send_to_diller_handler, diller_user_state.DillerOrderState.confirm_diller_order)
diller_router.message.register(view_diller_product.view_confirm_orders_handler_by_dillers, F.text == "Tasdiqlangan buyurtmalar")


################## Buyurtmani bekor qilish #####################
diller_router.callback_query.register(view_diller_product.cancel_diller_order_handler, F.data.startswith("cancel_ord_by_diller"))
diller_router.message.register(view_diller_product.cancel_send_to_diller_handler, diller_user_state.DillerOrderState.cancel_diller_order)
diller_router.message.register(view_diller_product.view_canceled_orders_handler_by_dillers, F.text == "Bekor qilingan buyurtmalar")

