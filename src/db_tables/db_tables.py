from core_bot.core_bot import *  # Assuming this imports required bot functionality
import sqlite3

# Create SQLite database and tables
conn = sqlite3.connect("database/app_database.db")
cursor = conn.cursor()

# Create Lunch table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Lunch (
    date DATE NOT NULL,
    items TEXT NOT NULL,
    price REAL NOT NULL,
    PRIMARY KEY (date, items)
)
''')

# Create Bakery table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Bakery (
    date DATE NOT NULL,
    items TEXT NOT NULL,
    price REAL NOT NULL,
    PRIMARY KEY (date, items)
)
''')

# Create Customers_Order table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Customers_Order (
    date DATE NOT NULL,
    chat_id INTEGER NOT NULL,
    username INTEGER NOT NULL,
    lunch_item TEXT,
    bakery_item TEXT,
    price_lunch REAL NOT NULL,
    price_bakery REAL NOT NULL,
    price_total REAL NOT NULL,
    is_paid INTEGER DEFAULT 0, -- 0 for unpaid, 1 for paid
    PRIMARY KEY (date, chat_id),
    FOREIGN KEY (lunch_item) REFERENCES Lunch(items),
    FOREIGN KEY (bakery_item) REFERENCES Bakery(items)
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully!")
