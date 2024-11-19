import sqlite3

connection = sqlite3.connect('products.db')
cursor = connection.cursor()


def initiate_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            image_path TEXT
        )
    ''')


# cursor.execute('INSERT INTO Products (title, description, price, image_path) VALUES (?, ?, ?, ?)',
#                    ('Webber naturals', 'K2+D3', 100, 'files/1.jpg',))
# cursor.execute('INSERT INTO Products (title, description, price, image_path) VALUES (?, ?, ?, ?)',
#                    ('Vitamix', 'C+Zn+Se+D3', 200, 'files/2.jpg',))
# cursor.execute('INSERT INTO Products (title, description, price, image_path) VALUES (?, ?, ?, ?)',
#                    ('One a day', 'Multi', 300, 'files/3.jpg',))
# cursor.execute('INSERT INTO Products (title, description, price, image_path) VALUES (?, ?, ?, ?)',
#                    ('Now', 'Lutein & Zeaxanthin', 400, 'files/4.jpg',))


connection.commit()
# connection.close()


def get_all_products():
    cursor.execute('SELECT id, title, description, price, image_path FROM Products')
    products = cursor.fetchall()
    connection.close()
    return products
