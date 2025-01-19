import sqlite3

conn = sqlite3.connect("database/app_database.db")
cursor = conn.cursor()

# Corrected SQL query
table_name = 'Customers_Order'
# table_name = 'Lunch'
# table_name = 'Bakery'
cursor.execute(f"SELECT * FROM {table_name}")
# cursor.execute("SELECT * FROM Customers_Review")
# cursor.execute("SELECT * FROM Bakery")
rows = cursor.fetchall()

# Print all rows
for row in rows:
    print(row)

conn.close()


# with sqlite3.connect('database/app_database.db') as conn:
#     cursor = conn.cursor()

#     # Fetch the price of the item from the Menu table
#     cursor.execute(
#         "SELECT items FROM Lunch WHERE items_id = ?", ('lunch0',))
#     item_name = cursor.fetchone()[0]
#     print(item_name)



