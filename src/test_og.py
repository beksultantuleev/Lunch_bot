import sqlite3

database_location = 'database/app_database.db'
conn = sqlite3.connect("database/app_database.db")
cursor = conn.cursor()

# Corrected SQL query
# table_name = 'Customers_Order'
# table_name ="Order_raiting"
table_name = 'Lunch'
# table_name = 'Bakery'
cursor.execute(f"SELECT * FROM {table_name}")
# cursor.execute("SELECT * FROM Customers_Review")
# cursor.execute("SELECT * FROM Bakery")
rows = cursor.fetchall()

# Print all rows
for row in rows:
    print(row)

conn.close()


# with sqlite3.connect(database_location) as conn:
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM Order_raiting;")  # Clears all rows
#     conn.commit()  # ✅ Commit before running VACUUM

# # Run VACUUM separately outside the transaction
# with sqlite3.connect(database_location) as conn:
#     conn.execute("VACUUM;")  # Reclaims storage space

# print("Table Order_raiting truncated successfully.")



