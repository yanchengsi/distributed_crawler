import sqlite3

def data_storage(data):
    conn = sqlite3.connect('web_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS web_pages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT)''')
    c.execute("INSERT INTO web_pages (content) VALUES (?)", (data,))
    conn.commit()
    conn.close()