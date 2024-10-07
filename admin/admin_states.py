from aiogram.fsm.state import State, StatesGroup

##### Diller state #########
class EditDiller(StatesGroup):
    diller_id = State()
    waiting_for_field = State()
    waiting_for_value = State()

##### User state #########
class EditUsers(StatesGroup):
    user_id = State()
    waiting_for_field = State()
    waiting_for_value = State()

