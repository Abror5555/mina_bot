from aiogram.fsm.state import State, StatesGroup


##### User state #########
class UserDiller(StatesGroup):
    diller_id = State()
    waiting_for_field = State()
    waiting_for_value = State()

############ REGISTER Diller #############
class UserState(StatesGroup):
    name = State()
    region = State()
    district = State()
    location = State()
    phone = State()
    save_state = State()


class AdminOrderForm(StatesGroup):
    message_to_user = State()
    waiting_for_diller_reply = State()
    cancel = State()