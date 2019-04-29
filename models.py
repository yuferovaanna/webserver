class UsersModel:
    """Сущность пользователей"""
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        """Инициализация таблицы"""
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(20) UNIQUE,
                             password_hash VARCHAR(128),
                             email VARCHAR(20),
                             is_admin INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash, email, is_admin=False):
        """Вставка новой записи"""
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash, email, is_admin) 
                          VALUES (?,?,?,?)''',
                       (user_name, password_hash, email, int(is_admin)))
        cursor.close()
        self.connection.commit()

    def exists(self, user_name):
        """Проверка, есть ли пользователь в системе"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ?", [user_name])
        row = cursor.fetchone()
        return (True, row[2], row[0]) if row else (False,)

    def get(self, user_id):
        """Возврат пользователя по id"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id)))
        row = cursor.fetchone()
        return row

    def get_all(self):
        """Запрос всех пользователей"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows


class StoresModel:
    """Сущность магазины"""
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        """Инициализация таблицы"""
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS stores 
                            (store_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             name VARCHAR(20) UNIQUE,
                             address VARCHAR(128)
                        )''')
        cursor.close()
        self.connection.commit()

    def insert(self, name, address):
        """Добавление магазина"""
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO stores 
                          (name, address) 
                          VALUES (?,?)''',
                       (name, address))
        cursor.close()
        self.connection.commit()

    def exists(self, name):
        """Поиск магазина по названию"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM stores WHERE name = ?",
                       name)
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)

    def get(self, store_id):
        """Запрос магазина по id"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM stores WHERE store_id = ?", (str(store_id)))
        row = cursor.fetchone()
        return row

    def get_all(self):
        """Запрос всех магазинов"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM stores")
        rows = cursor.fetchall()
        return rows

    def delete(self, store_id):
        """Удаление магазинов"""
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM stores WHERE store_id = ?''', (str(store_id)))
        cursor.close()
        self.connection.commit()


class FilmsModel:
    """Сущность фильмов"""
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        """Инициализация таблицы"""
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS films 
                            (film_id INTEGER PRIMARY KEY AUTOINCREMENT,
                             name VARCHAR(20),
                             price INTEGER,
                             store INTEGER,
                             file VARCHAR(255)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, name, price, store, file):
        """Добавление фильма"""
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO films 
                          (name, price, store, file) 
                          VALUES (?,?,?,?)''',
                       (name, str(price), str(store), file))
        cursor.close()
        self.connection.commit()

    def exists(self, name):
        """Поиск фильма по модели"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM films WHERE name = ?",
                       name)
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)

    def get(self, film_id):
        """Поиск фильма по id"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM films WHERE film_id = ?", (str(film_id)))
        row = cursor.fetchone()
        return row

    def get_all(self):
        """Запрос всех фильмов"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT name, price, film_id, file FROM films")
        rows = cursor.fetchall()
        return rows

    def delete(self, film_id):
        """Удаление фильма"""
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM films WHERE film_id = ?''', (str(film_id)))
        cursor.close()
        self.connection.commit()

    def get_by_price(self, start_price, end_price):
        """Запрос фильмов по цене"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT name, price, film_id FROM films WHERE price >= ? AND price <= ?", (str(start_price), str(end_price)))
        row = cursor.fetchall()
        return row

    def get_by_store(self, store_id):
        """Запрос фильмов по магазину"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT name, price, film_id FROM films WHERE store = ?", (str(store_id)))
        row = cursor.fetchall()
        return row
