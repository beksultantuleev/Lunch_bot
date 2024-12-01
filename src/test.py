import sqlite3

conn = sqlite3.connect("database/app_database.db")
cursor = conn.cursor()

# Corrected SQL query
cursor.execute("SELECT * FROM Customers_Order")
# cursor.execute("SELECT * FROM Customers_Review")
# cursor.execute("SELECT * FROM Bakery")
rows = cursor.fetchall()

# Print all rows
for row in rows:
    print(row)

conn.close()
