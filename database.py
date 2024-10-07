import sqlite3
from datetime import datetime
import re

# Jadvalni yaratish funksiyasi
def create_table():
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        name TEXT,
        region TEXT,
        district TEXT,
        latitude REAL,
        longitude REAL,
        phone_number TEXT,
        first_name TEXT,
        last_name TEXT,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dillers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        name TEXT,
        company_name TEXT,
        region TEXT,
        district TEXT,
        latitude REAL,
        longitude REAL,
        phone_number TEXT,
        first_name TEXT,
        last_name TEXT,
        diller_limit REAL DEFAULT 1000000,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        added_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        image TEXT,
        added_at TEXT
    )
    """)

    # Mahsulotlar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category_id INTEGER,
            description TEXT,
            image1 TEXT,
            image2 TEXT,
            image3 TEXT,
            image4 TEXT,
            video TEXT,
            price REAL,
            stock INTEGER,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE 
        )
    """)

    # Dillerlar uchun mahsulotlar jadvali
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diller_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category_id INTEGER,
        description TEXT,
        image1 TEXT,
        image2 TEXT,
        image3 TEXT,
        image4 TEXT,
        video TEXT,
        wholesale_price REAL,
        stock INTEGER,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
    )
    """)


    # User Cart jadvali
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES users_products(id),
        UNIQUE(user_id, product_id)  -- Bir foydalanuvchi har bir mahsulotni faqat bir marta qo'shishi mumkin
    );
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS confirm_user_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        user_name TEXT NOT NULL,
        region TEXT NOT NULL,
        category_name TEXT NOT NULL,
        product_details TEXT NOT NULL,
        admin_comment TEXT NOT NULL,
        canceled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS canceled_user_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        user_name TEXT NOT NULL,
        region TEXT NOT NULL,
        category_name TEXT NOT NULL,
        product_details TEXT NOT NULL,
        admin_comment TEXT NOT NULL,
        canceled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)






    # Diller Cart jadvali
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diller_cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES diller_products(id),
        UNIQUE(user_id, product_id)  -- Bir foydalanuvchi har bir mahsulotni faqat bir marta qo'shishi mumkin
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS confirm_diler_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        user_name TEXT NOT NULL,
        company_name TEXT NOT NULL,
        category_name TEXT NOT NULL,
        product_details TEXT NOT NULL,
        admin_comment TEXT NOT NULL,
        canceled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS canceled_diler_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        user_name TEXT NOT NULL,
        company_name TEXT NOT NULL,
        category_name TEXT NOT NULL,
        product_details TEXT NOT NULL,
        admin_comment TEXT NOT NULL,
        canceled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

                   
    conn.commit()
    conn.close()






############ Admin ID'sini saqlash funksiyasi ############
def save_admin(user_id: int):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO admins (user_id, added_at)
    VALUES (?, ?)
    """, (user_id, added_at))

    conn.commit()
    conn.close()

########## Adminni tekshirish ##########
def is_admin(user_id: int):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
    admin = cursor.fetchone()

    conn.close()
    return admin is not None


# Oddiy foydalanuvchi ma'lumotlarini saqlash funksiyasi
def save_contact(user_id, phone_number, name, first_name, last_name, region, district, latitude, longitude):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT OR REPLACE INTO user (user_id, name, region, district, latitude, longitude, phone_number, first_name, last_name, added_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, name, region, district, latitude, longitude, phone_number, first_name, last_name, added_at))

    conn.commit()
    conn.close()

############## Foydalanuvchini bazada borligini tekshirish #################
def is_user_exist(user_id: int, is_admin=False):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    if is_admin:
        cursor.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
    else:
        cursor.execute("SELECT 1 FROM user WHERE user_id = ?", (user_id,))

    user = cursor.fetchone()
    conn.close()
    return user is not None


########## Foydalanuvchi oddiy ekanligini tekshirish #############
def is_user(user_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user is not None





########### User ustunidagi barcha ba'lumotlarni olish ##########
def get_user_info(user_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT name, region, district, latitude, longitude, phone_number, first_name, last_name, added_at
    FROM user WHERE user_id = ?
    """, (user_id,))
    
    user_info = cursor.fetchone()
    conn.close()
    print (f"Get all the information in the user column: {user_info}")
    return user_info  # Foydalanuvchi ma'lumotlarini qaytaradi

############### Foydalanuvchi ma'lumotlarini ko'rish ##############
def get_all_users():
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, name, region FROM user")
    users = cursor.fetchall()
    conn.close()
    print(f"View user information: {users}")
    return users



########## user ma'lumotlarini yangilash ###########
def update_users_info(user_id: int, field: str, new_value: str):
    conn = sqlite3.connect("mina_kompaniya.db")  # Ma'lumotlar bazasiga to'g'ri yo'l
    cursor = conn.cursor()

    try:
        # Kiritilgan ID bo'yicha yozuv bor-yo'qligini tekshirish
        cursor.execute(f"SELECT * FROM user WHERE user_id = {user_id}")
        existing_record = cursor.fetchone()
        print(f"Bazadan topilgan user {existing_record}")
        if existing_record:
            # Dinamik SQL so'rovini yaratish
            query = f"UPDATE user SET {field} = '{new_value}' WHERE user_id = {user_id}"
            cursor.execute(query,)
            conn.commit()  # Tranzaksiyani tasdiqlash
            print(f"Successfully updated {field} for user_id {user_id}")
            return True
        else:
            print(f"No record found for users_id {user_id}")
            return False
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()  # Ulanishni yopish



######### Foydalanuvhilar jadvalini o'chiradigan funksiya ################
def delete_user(user_id: int):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    # SQL parametrlar bilan ishlatish
    cursor.execute("DELETE FROM 'user' WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    return cursor.rowcount  # Nechta qator o'chirilganini qaytaradi







######### Save Diller #############3
def save_diller(user_id, name, company_name, region, district, latitude, longitude, phone_number, first_name, last_name, diller_limit=1000000):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    # SQL so'rovi (added_at avtomatik to'ldiriladi)
    cursor.execute("""
    INSERT OR REPLACE INTO dillers (user_id, name, company_name, region, district, latitude, longitude, phone_number, first_name, last_name, diller_limit)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        name,
        company_name,
        region,
        district,
        latitude,
        longitude,
        phone_number,
        first_name,
        last_name,
        diller_limit  # diller_limitni kiritish
    ))

    conn.commit()
    conn.close()


######## Diller mavjudligi tekshirish #################
def is_diller_exist(user_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM dillers WHERE user_id = ?", (user_id,))
    diller = cursor.fetchone()
    conn.close()
    return diller is not None


############# Foydalanuvchi diller ekanligini tekshirish ############3
def is_diller(user_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM dillers WHERE user_id = ?", (user_id,))
    diller = cursor.fetchone()
    conn.close()
    return diller is not None


############### Diller ma'lumotlarini olish ################
def get_all_dillers():
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, name, company_name FROM dillers")
    dillers = cursor.fetchall()
    conn.close()
    print(f"Get diller: {dillers}")
    return dillers

########### Diller ustunidagi barcha ba'lumotlarni olish ##########
def get_diller_info(user_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, company_name, region, district, latitude, longitude, phone_number, first_name, last_name, diller_limit, added_at 
        FROM dillers WHERE user_id = ?
    """, (user_id,))
    
    diller_info = cursor.fetchone()
    print(f"Get all the information in the dealer column: {diller_info}")
    conn.close()

    print(f"Returned diller_info: {diller_info}")
    return diller_info # Dillerning ma'lumotlarini qaytaradi



########## Diller ma'lumotlarini yangilash ###########
def update_diller_info(user_id: int, field: str, new_value: str):
    conn = sqlite3.connect("mina_kompaniya.db")  # Ma'lumotlar bazasiga to'g'ri yo'l
    cursor = conn.cursor()

    try:
        # Kiritilgan ID bo'yicha yozuv bor-yo'qligini tekshirish
        cursor.execute(f"SELECT * FROM dillers WHERE user_id = {user_id}")
        existing_record = cursor.fetchone()
        print(f"Bazadan topilgan user {existing_record}")
        if existing_record:
            # Dinamik SQL so'rovini yaratish
            query = f"UPDATE dillers SET {field} = '{new_value}' WHERE user_id = {user_id}"
            cursor.execute(query,)
            conn.commit()  # Tranzaksiyani tasdiqlash
            print(f"Successfully updated {field} for diller_id {user_id}")
            return True
        else:
            print(f"No record found for diller_id {user_id}")
            return False
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()  # Ulanishni yopish



########### Diller jadvalini o'chiradigan funksiya ##############33
def delete_diller_table(user_id: int):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    cursor.execute(f"DELETE FROM dillers WHERE user_id = {user_id}")
    conn.commit()
    conn.close()

    return cursor.rowcount  # Nechta qator o'chirilganini qaytaradi




########### Kategoriya saqlash ##############
async def save_category(name: str, image: str):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO categories (name, image, added_at)
    VALUES (?, ?, ?)
    """, (name, image, added_at))

    conn.commit()
    conn.close()

# Kategoriyalarni olish
async def get_all_categories():
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, image FROM categories")
    categories = cursor.fetchall()

    conn.close()
    return categories

# Kategoriya o'chirish
async def delete_category(category_id: int):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()

    conn.close()





############ Users Product ############

# save user product
def save_user_product(name: str, category_id: int, description: str, image1: str, image2: str, image3: str, image4: str, video: str, price: float, stock: int):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users_products (name, category_id, description, image1, image2, image3, image4, video, price, stock)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, category_id, description, image1, image2, image3, image4, video, price, stock))
    conn.commit()
    conn.close()

# Saqlangan user ma'lumotlarini olish
def get_all_user_products():
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users_products")
    products = cursor.fetchall()
    conn.close()
    return products


# Foydalanuvchi mahsulotlarini olish
def get_user_products_by_category(category_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users_products WHERE category_id = ?", (category_id,))
    products = cursor.fetchall()
    conn.close()
    return products


# Saqlangan user ma'lumotlarini o'chirish
def delete_user_product(product_id: int):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users_products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount


################ END User Prduct ############



########### User Cart Page ###################

def add_to_user_cart(user_id, product_id, quantity=1):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Mahsulotning tegishli category_id sini olish
        cursor.execute("SELECT category_id FROM users_products WHERE id = ?", (product_id,))
        category_id = cursor.fetchone()[0]  # Mahsulotning category_id sini olamiz
        
        # Savatchaga mahsulotni qo'shish yoki miqdorini yangilash
        cursor.execute("""
            INSERT INTO user_cart (user_id, product_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = quantity + ?
        """, (user_id, product_id, quantity, quantity))
        conn.commit()
        
        print(f"Maxsulot category_id: {category_id}")
        
    except Exception as e:
        print(f"Xatolik: {e}")
    finally:
        conn.close()


def get_user_cart(user_id, category_id=None):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    if category_id:
        # Faqat tanlangan kategoriya mahsulotlarini olib kelish
        cursor.execute("""
            SELECT users_products.name, users_products.price, user_cart.quantity, categories.name, categories.id, users_products.id
            FROM user_cart
            JOIN users_products ON user_cart.product_id = users_products.id
            JOIN categories ON users_products.category_id = categories.id
            WHERE user_cart.user_id = ? AND users_products.category_id = ?
        """, (user_id, category_id))
    else:
        # Barcha mahsulotlarni olib kelish
        cursor.execute("""
            SELECT users_products.name, users_products.price, user_cart.quantity, categories.name, categories.id, users_products.id
            FROM user_cart
            JOIN users_products ON user_cart.product_id = users_products.id
            JOIN categories ON users_products.category_id = categories.id
            WHERE user_cart.user_id = ?
        """, (user_id,))

    items = cursor.fetchall()
    conn.close()
    return items


def clear_user_cart(user_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


################## END USER CART PAGE ##################


################# DELETE CART PAGE BY USER #############
def delete_from_user_cart_to_confirm(user_id, product_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Savatchadan mahsulotni o'chirish
        cursor.execute("""
            DELETE FROM user_cart
            WHERE user_id = ? AND product_id = ?
        """, (user_id, product_id))
        conn.commit()
        print(f"User ID: {user_id} uchun Product ID: {product_id} savatchadan o'chirildi.\nTasdiqlash sahifasiga qo'shildi.")
    except Exception as e:
        print(f"Xatolik: {e}")
    finally:
        conn.close()


# Bekor qilish sahifasi uchun  delete
def delete_from_user_cart_to_cancel(user_id, product_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Savatchadan mahsulotni o'chirish
        cursor.execute("""
            DELETE FROM user_cart
            WHERE user_id = ? AND product_id = ?
        """, (user_id, product_id))
        conn.commit()
        print(f"User ID: {user_id} uchun Product ID: {product_id} savatchadan o'chirildi.\nBekor qilish sahifasiga qo'shildi.")
    except Exception as e:
        print(f"Xatolik: {e}")
    finally:
        conn.close()
############### END DELETE CART PAGE #################3




####################### CONFIRM USER PRODUCT ##############
def save_user_confirm_order(user_id, user_name, region, category_name, product_details, admin_comment):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Bekor qilingan buyurtma tafsilotlarini saqlash
        cursor.execute("""
            INSERT INTO confirm_user_orders (user_id, user_name, region, category_name, product_details, admin_comment)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, user_name, region, category_name, product_details, admin_comment))
        conn.commit()
        print("Xarid qilingan buyurtma bazaga muvaffaqiyatli saqlandi.")
    except Exception as e:
        print(f"Xatolik: {e}")
    finally:
        conn.close()


def get_confirm_orders_by_user(user_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Faqat berilgan user_id ga tegishli bekor qilingan buyurtmalarni olish
        cursor.execute("""
            SELECT user_id, user_name, region, category_name, product_details, admin_comment, canceled_at
            FROM confirm_user_orders
            WHERE user_id = ?
        """, (user_id,))
        canceled_orders = cursor.fetchall()
        return canceled_orders

    except Exception as e:
        print(f"Xatolik: {e}")
        return []

    finally:
        conn.close()




def get_confirm_orders_by_user_reply_admin():
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Bekor qilingan buyurtmalarni olish
        cursor.execute("""
            SELECT user_id, user_name, region, category_name, product_details, admin_comment, canceled_at
            FROM confirm_user_orders
        """)
        canceled_orders = cursor.fetchall()
        return canceled_orders

    except Exception as e:
        print(f"Xatolik: {e}")
        return []

    finally:
        conn.close()

####################### END CONFIRM USER PRODUCT ##############







################### CANCEL USER PRODUCT ##############
def save_user_canceled_order(user_id, user_name, region, category_name, product_details, admin_comment):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Bekor qilingan buyurtma tafsilotlarini saqlash
        cursor.execute("""
            INSERT INTO canceled_user_orders (user_id, user_name, region, category_name, product_details, admin_comment)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, user_name, region, category_name, product_details, admin_comment))
        conn.commit()
        print("Bekor qilingan buyurtma bazaga muvaffaqiyatli saqlandi.")
    except Exception as e:
        print(f"Xatolik: {e}")
    finally:
        conn.close()


def get_canceled_orders_by_users(user_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Faqat berilgan user_id ga tegishli bekor qilingan buyurtmalarni olish
        cursor.execute("""
            SELECT user_id, user_name, region, category_name, product_details, admin_comment, canceled_at
            FROM canceled_user_orders
            WHERE user_id = ?
        """, (user_id,))
        canceled_orders = cursor.fetchall()
        return canceled_orders

    except Exception as e:
        print(f"Xatolik: {e}")
        return []

    finally:
        conn.close()




def get_canceled_orders_by_users_reply_admin():
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Bekor qilingan buyurtmalarni olish
        cursor.execute("""
            SELECT user_id, user_name, region, category_name, product_details, admin_comment, canceled_at
            FROM canceled_user_orders
        """)
        canceled_orders = cursor.fetchall()
        return canceled_orders

    except Exception as e:
        print(f"Xatolik: {e}")
        return []

    finally:
        conn.close()


################### END CANCEL USER PRODUCT ##################





















############## Diller Product  ###############

# save product diller
def save_diller_product(name: str, category_id: int, description: str, image1: str, image2: str, image3: str, image4: str, video: str, wholesale_price: float, stock: int):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO diller_products (name, category_id, description, image1, image2, image3, image4, video, wholesale_price, stock)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, category_id, description, image1, image2, image3, image4, video, wholesale_price, stock))
    conn.commit()
    conn.close()


# Saqlangan diller maxshulotlarini olish
def get_all_diller_products():
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM diller_products")
    products = cursor.fetchall()
    conn.close()
    return products

# Foydalanuvchi mahsulotlarini olish
def get_diller_products_by_category(category_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM diller_products WHERE category_id = ?", (category_id,))
    products = cursor.fetchall()
    conn.close()
    return products


# Diller maxsulotlarini o'chirish
def delete_diller_product(product_id: int):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM diller_products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount

############# END Diller product ############






########### Diller Cart Page ###################

def add_to_diller_cart(user_id, product_id, quantity=1):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Mahsulotning tegishli category_id sini olish
        cursor.execute("SELECT category_id FROM diller_products WHERE id = ?", (product_id,))
        category_id = cursor.fetchone()[0]  # Mahsulotning category_id sini olamiz
        
        # Savatchaga mahsulotni qo'shish yoki miqdorini yangilash
        cursor.execute("""
            INSERT INTO diller_cart (user_id, product_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = quantity + ?
        """, (user_id, product_id, quantity, quantity))
        conn.commit()
        
        print(f"Maxsulot category_id: {category_id}")
        
    except Exception as e:
        print(f"Xatolik: {e}")
    finally:
        conn.close()


def add_or_update_diller_cart(user_id, product_id, quantity):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Savatchada ushbu mahsulot bor-yo'qligini tekshirish
        cursor.execute("SELECT quantity FROM diller_cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
        existing_quantity = cursor.fetchone()

        if existing_quantity:
            # Agar mahsulot savatchada mavjud bo'lsa, yangi miqdorni qo'shamiz
            new_quantity = existing_quantity[0] + quantity
            cursor.execute("UPDATE diller_cart SET quantity = ? WHERE user_id = ? AND product_id = ?", (new_quantity, user_id, product_id))
            print(f"Mahsulot yangilandi: Yangi miqdor {new_quantity}")
        else:
            # Agar mahsulot savatchada yo'q bo'lsa, yangi mahsulotni qo'shamiz
            cursor.execute("INSERT INTO diller_cart (user_id, product_id, quantity) VALUES (?, ?, ?)", (user_id, product_id, quantity))
            print(f"Mahsulot savatchaga qo'shildi: {quantity} dona")
        
        conn.commit()

    except Exception as e:
        print(f"Xatolik: {e}")
    finally:
        conn.close()



def get_diller_cart(user_id, category_id=None):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    if category_id:
        # Faqat tanlangan kategoriya mahsulotlarini olib kelish
        cursor.execute("""
            SELECT diller_products.name, diller_products.wholesale_price, diller_cart.quantity, diller_products.stock, categories.name, categories.id, diller_products.id
            FROM diller_cart
            JOIN diller_products ON diller_cart.product_id = diller_products.id
            JOIN categories ON diller_products.category_id = categories.id
            WHERE diller_cart.user_id = ? AND diller_products.category_id = ?
        """, (user_id, category_id))
    else:
        # Barcha mahsulotlarni olib kelish
        cursor.execute("""
            SELECT diller_products.name, diller_products.wholesale_price, diller_cart.quantity, diller_products.stock, categories.name, categories.id, diller_products.id
            FROM diller_cart
            JOIN diller_products ON diller_cart.product_id = diller_products.id
            JOIN categories ON diller_products.category_id = categories.id
            WHERE diller_cart.user_id = ?
        """, (user_id,))

    items = cursor.fetchall()
    conn.close()
    return items


def clear_diller_cart(user_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def update_diller_limit(user_id, quantity):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Diller limitini yangilash
        cursor.execute("""
            UPDATE dillers 
            SET diller_limit = diller_limit - ?
            WHERE user_id = ?
        """, (quantity, user_id))
        conn.commit()
        
    except Exception as e:
        print(f"Xatolik: {e}")
    finally:
        conn.close()


################### END DILLER CART PAGE ###############




################# DELETE CART PAGE BY DILLER #############
def delete_from_diller_cart_to_confirm(user_id, product_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Savatchadan mahsulotni o'chirish
        cursor.execute("""
            DELETE FROM diller_cart
            WHERE user_id = ? AND product_id = ?
        """, (user_id, product_id))
        conn.commit()
        print(f"User ID: {user_id} uchun Product ID: {product_id} savatchadan o'chirildi.\nTasdiqlash sahifasiga qo'shildi.")
    except Exception as e:
        print(f"Xatolik: {e}")
    finally:
        conn.close()


# Bekor qilish sahifasi uchun  delete
def delete_from_diller_cart_to_cancel(user_id, product_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Savatchadan mahsulotni o'chirish
        cursor.execute("""
            DELETE FROM diller_cart
            WHERE user_id = ? AND product_id = ?
        """, (user_id, product_id))
        conn.commit()
        print(f"User ID: {user_id} uchun Product ID: {product_id} savatchadan o'chirildi.\nBekor qilish sahifasiga qo'shildi.")
    except Exception as e:
        print(f"Xatolik: {e}")
    finally:
        conn.close()
############### END DELETE CART PAGE #################3




####################### CONFIRM DILLER PRODUCT ##############
def save_diller_confirm_order(user_id, user_name, company_name, category_name, product_details, admin_comment):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Bekor qilingan buyurtma tafsilotlarini saqlash
        cursor.execute("""
            INSERT INTO confirm_diler_orders (user_id, user_name, company_name, category_name, product_details, admin_comment)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, user_name, company_name, category_name, product_details, admin_comment))
        conn.commit()
        print("Bekor qilingan buyurtma bazaga muvaffaqiyatli saqlandi.")
    except Exception as e:
        print(f"Xatolik: {e}")
    finally:
        conn.close()


def get_confirm_orders_by_dillers(user_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Faqat berilgan user_id ga tegishli bekor qilingan buyurtmalarni olish
        cursor.execute("""
            SELECT user_id, user_name, company_name, category_name, product_details, admin_comment, canceled_at
            FROM confirm_diler_orders
            WHERE user_id = ?
        """, (user_id,))
        canceled_orders = cursor.fetchall()
        return canceled_orders

    except Exception as e:
        print(f"Xatolik: {e}")
        return []

    finally:
        conn.close()




def get_confirm_orders_by_dillers_reply_admin():
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Bekor qilingan buyurtmalarni olish
        cursor.execute("""
            SELECT user_id, user_name, company_name, category_name, product_details, admin_comment, canceled_at
            FROM confirm_diler_orders
        """)
        canceled_orders = cursor.fetchall()
        return canceled_orders

    except Exception as e:
        print(f"Xatolik: {e}")
        return []

    finally:
        conn.close()

####################### END CONFIRM DILLER PRODUCT ##############







################### CANCEL DILLER PRODUCT ##############
def save_diller_canceled_order(user_id, user_name, company_name, category_name, product_details, admin_comment):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Bekor qilingan buyurtma tafsilotlarini saqlash
        cursor.execute("""
            INSERT INTO canceled_diler_orders (user_id, user_name, company_name, category_name, product_details, admin_comment)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, user_name, company_name, category_name, product_details, admin_comment))
        conn.commit()
        print("Bekor qilingan buyurtma bazaga muvaffaqiyatli saqlandi.")
    except Exception as e:
        print(f"Xatolik: {e}")
    finally:
        conn.close()


def get_canceled_orders_by_dillers(user_id):
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Faqat berilgan user_id ga tegishli bekor qilingan buyurtmalarni olish
        cursor.execute("""
            SELECT user_id, user_name, company_name, category_name, product_details, admin_comment, canceled_at
            FROM canceled_diler_orders
            WHERE user_id = ?
        """, (user_id,))
        canceled_orders = cursor.fetchall()
        return canceled_orders

    except Exception as e:
        print(f"Xatolik: {e}")
        return []

    finally:
        conn.close()




def get_canceled_orders_by_dillers_reply_admin():
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    try:
        # Bekor qilingan buyurtmalarni olish
        cursor.execute("""
            SELECT user_id, user_name, company_name, category_name, product_details, admin_comment, canceled_at
            FROM canceled_diler_orders
        """)
        canceled_orders = cursor.fetchall()
        return canceled_orders

    except Exception as e:
        print(f"Xatolik: {e}")
        return []

    finally:
        conn.close()








################ STATISTIKA ##################
def get_statistics():
    conn = sqlite3.connect("mina_kompaniya.db")
    cursor = conn.cursor()

    # Statistika olish uchun so'rovlar
    cursor.execute("SELECT COUNT(*) FROM user;")
    user_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM dillers;")
    diller_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM categories;")
    category_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users_products;")
    user_product_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM diller_products;")
    diller_product_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM confirm_user_orders;")
    user_confirmed_orders_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM canceled_user_orders;")
    user_canceled_orders_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM confirm_diler_orders;")
    diller_confirmed_orders_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM canceled_diler_orders;")
    diller_canceled_orders_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM user_cart;")
    user_cart_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM diller_cart;")
    diller_cart_count = cursor.fetchone()[0]

    conn.close()

    # Statistika ma'lumotlarini lug'at ko'rinishida qaytarish
    stats = {
        "Foydalanuvchilar soni": user_count,
        "Dillerlar soni": diller_count,
        "Foydalanuvchilar uchun mavjud kategoriyalar soni": category_count,
        "Foydalanuvchilar uchun mavjud mahsulotlar soni": user_product_count,
        "Dillerlar uchun mavjud mahsulotlar soni": diller_product_count,
        "Foydalanuvchilar tasdiqlangan buyurtmalar soni": user_confirmed_orders_count,
        "Foydalanuvchilar bekor qilingan buyurtmalar soni": user_canceled_orders_count,
        "Dillerlar tasdiqlangan buyurtmalar soni": diller_confirmed_orders_count,
        "Dillerlar bekor qilingan buyurtmalar soni": diller_canceled_orders_count,
        "Foydalanuvchilar savatchasidagi mahsulotlar soni": user_cart_count,
        "Dillerlar savatchasidagi mahsulotlar soni": diller_cart_count
    }

    return stats







DB_PATH = "mina_kompaniya.db"

# HTML teglarini olib tashlaydigan funksiya
def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    clean_text = re.sub(cleanr, '', raw_html)
    return clean_text

# Foydalanuvchilarning tasdiqlangan buyurtmalarini olish
def get_confirmed_user_orders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM confirm_user_orders;")
    columns = [description[0] for description in cursor.description]
    data = cursor.fetchall()
    
    # Agar product_details ustuni mavjud bo'lsa, uni tozalash
    product_details_index = columns.index("product_details") if "product_details" in columns else None
    if product_details_index is not None:
        data = [
            tuple(
                clean_html(value) if i == product_details_index else value
                for i, value in enumerate(row)
            )
            for row in data
        ]

    conn.close()
    return data, columns

# Foydalanuvchilarning bekor qilingan buyurtmalarini olish
def get_canceled_user_orders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM canceled_user_orders;")
    columns = [description[0] for description in cursor.description]
    data = cursor.fetchall()
    
    # Agar product_details ustuni mavjud bo'lsa, uni tozalash
    product_details_index = columns.index("product_details") if "product_details" in columns else None
    if product_details_index is not None:
        data = [
            tuple(
                clean_html(value) if i == product_details_index else value
                for i, value in enumerate(row)
            )
            for row in data
        ]

    conn.close()
    return data, columns

# Dillerlarning tasdiqlangan buyurtmalarini olish
def get_confirmed_diller_orders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM confirm_diler_orders;")
    columns = [description[0] for description in cursor.description]
    data = cursor.fetchall()
    
    # Agar product_details ustuni mavjud bo'lsa, uni tozalash
    product_details_index = columns.index("product_details") if "product_details" in columns else None
    if product_details_index is not None:
        data = [
            tuple(
                clean_html(value) if i == product_details_index else value
                for i, value in enumerate(row)
            )
            for row in data
        ]

    conn.close()
    return data, columns

# Dillerlarning bekor qilingan buyurtmalarini olish
def get_canceled_diller_orders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM canceled_diler_orders;")
    columns = [description[0] for description in cursor.description]
    data = cursor.fetchall()
    
    # Agar product_details ustuni mavjud bo'lsa, uni tozalash
    product_details_index = columns.index("product_details") if "product_details" in columns else None
    if product_details_index is not None:
        data = [
            tuple(
                clean_html(value) if i == product_details_index else value
                for i, value in enumerate(row)
            )
            for row in data
        ]

    conn.close()
    return data, columns
################# END STATISTIKA #################