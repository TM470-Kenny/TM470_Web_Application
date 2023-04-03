import sqlite3

connection = sqlite3.connect('sales_tracker.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO products (device, data, contract, price, revenue) VALUES (?, ?, ?, ?, ?)",
            ('iPhone 13', 10, 24, 56.99, 319)
            )

cur.execute("INSERT INTO sales (username, new, upgrade, device, data, contract, price) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ('KennyH', True, False, 'iPhone 13', 10, 24, 56.99)
            )

cur.execute("INSERT INTO sales (username, new, upgrade, device, data, contract, price) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ('KennyH', True, False, 'iPhone 11', 1, 24, 29.99)
            )

connection.commit()
connection.close()