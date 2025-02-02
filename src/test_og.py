import sqlite3

database_location = 'database/app_database.db'
conn = sqlite3.connect("database/app_database.db")
cursor = conn.cursor()

# Corrected SQL query
# table_name = 'Customers_Order'
table_name = 'Customers_Review'
# table_name ="Order_raiting"
# table_name = 'Lunch'
# table_name = 'Bakery'
# cursor.execute(f"SELECT * FROM {table_name} where date BETWEEN DATE('now', '-30 days') AND DATE('now')  ")
cursor.execute(f"""
    SELECT * FROM {table_name} 
    WHERE STRFTIME('%Y-%m-%d', 
                   SUBSTR(date, 7, 4) || '-' || 
                   SUBSTR(date, 4, 2) || '-' || 
                   SUBSTR(date, 1, 2)) 
          BETWEEN DATE('now', '-30 days') AND DATE('now')
""")

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



