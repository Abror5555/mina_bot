from aiogram.fsm.state import State, StatesGroup


############ KATEGORY STATE #############
class Add_Category(StatesGroup):
    name = State()
    img = State()


########### USER PRODUCT STATE #############
class UserProductState(StatesGroup):
    category = State()
    name = State()
    description = State()
    image1 = State()      
    image2 = State()      
    image3 = State()      
    image4 = State()  
    video = State()
    price = State()
    stock = State()
    confirm = State()
    search = State()


########### DILLER PRODUCT STATE #############
class DillerProductState(StatesGroup):
    category = State()
    name = State()
    description = State()
    image = State()
    image1 = State()      
    image2 = State()      
    image3 = State()      
    image4 = State()
    video = State()
    wholesale_price = State()
    stock = State()
    confirm = State()
    search = State()