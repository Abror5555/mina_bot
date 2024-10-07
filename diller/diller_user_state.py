from aiogram.fsm.state import State, StatesGroup


############ REGISTER Diller #############
class DillerState(StatesGroup):
    name = State()
    company_name = State()
    region = State()
    district = State()
    location = State()
    phone = State()
    save_state = State()


class DillerOrderState(StatesGroup):
    diller_id = State()
    diller_name = State()
    waiting_for_diller_details = State()
    waiting_for_admin_reply = State()
    waiting_for_diller_reply = State()
    cancel_diller_order = State()
    confirm_diller_order = State()