# from db_tables.db_tables import *
import sqlite3

conn = sqlite3.connect("database/app_database.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(Customers_Order);")
print(cursor.fetchall())

conn.close()

