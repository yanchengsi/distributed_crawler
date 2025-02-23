from whoosh.index import create_in
from whoosh.fields import Schema, TEXT
import sqlite3

def data_indexing():
    schema = Schema(content=TEXT(stored=True))
    ix = create_in("indexdir", schema)
    writer = ix.writer()
    conn = sqlite3.connect('web_data.db')
    c = conn.cursor()
    c.execute("SELECT content FROM web_pages")
    rows = c.fetchall()
    for row in rows:
        writer.add_document(content=row[0])
    writer.commit()
    conn.close()