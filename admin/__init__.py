from aiogram import Router, Bot, F
from . import admin_states, admins
from aiogram.filters import Command


router_admin = Router()


########### Admin uchun comandalar ############
router_admin.message.register(admins.show_dillers, F.text == "🤝 Diller")
router_admin.message.register(admins.show_users, F.text == "👤 User")
router_admin.message.register(admins.send_statistics, F.text == "📊 Statistika")
router_admin.callback_query.register(admins.download_statistics, F.data.startswith("download_statistics"))


########## Diller uchun maxsus komandalar #############
router_admin.message.register(admins.show_all_dillers, Command("diller_info_edit"))
router_admin.callback_query.register(admins.edit_diller_info, F.data.startswith("diller_edit_"))
router_admin.callback_query.register(admins.select_field_to_edit, F.data.startswith("edit_"))
router_admin.callback_query.register(admins.view_diller_malumot, F.data.startswith("view_diller_"))
router_admin.callback_query.register(admins.show_all_dillers_back, F.data.startswith("back"))
router_admin.message.register(admins.process_new_value, admin_states.EditDiller.waiting_for_value)
router_admin.callback_query.register(admins.delete_diller, F.data.startswith("delete_diller_"))



######### Userlar uchun maxsus komandalar ############3

router_admin.message.register(admins.show_all_users, Command("user_info_edit"))
router_admin.callback_query.register(admins.view_user_malumot, F.data.startswith("view_users_"))
router_admin.callback_query.register(admins.show_all_users_back, F.data.startswith("to_back"))
router_admin.callback_query.register(admins.edit_users_info, F.data.startswith("users_edit_"))
router_admin.callback_query.register(admins.select_field_to_edit_users, F.data.startswith("ttt_"))
router_admin.message.register(admins.process_new_value_users, admin_states.EditUsers.waiting_for_value)
router_admin.callback_query.register(admins.delete_users, F.data.startswith("delete_users_"))