import sqlite3

connection = sqlite3.connect('not_telegram.db')
cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users(
id INTEGER PRIMARY KEY,
username TEXT NOT NULL,
email TEXT NOT NULL,
age INTEGER,
balance INTEGER NOT NULL
)
''')

cursor.execute('DELETE FROM Users')

for i in range(10):
    cursor.execute(
     'INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)',
     (f'User{i+1}', f'example{i+1}@gmail.com', f'{(i+1)*10}', '1000')
     )

for i in range(10):
    if not (i % 2):
        cursor.execute(
     'UPDATE Users SET balance = 500 WHERE id = ?',
     (i+1,)
     )

for i in range(10):
    if not (i % 3):
        cursor.execute(
     'DELETE FROM Users WHERE id = ?',
     (i+1,)
     )

cursor.execute('SELECT * FROM Users WHERE age != 60 ORDER BY id')
users = cursor.fetchall()

for user in users:
    print(f'Имя: {user[1]} | Почта: {user[2]} | Возраст: {user[3]} | Баланс: {user[4]}')

connection.commit()
connection.close()