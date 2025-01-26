from core_bot.core_bot import *  # Assuming this imports required bot functionality
import sqlite3

# Create SQLite database and tables
conn = sqlite3.connect(database_location)
cursor = conn.cursor()

# Create Lunch table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Lunch (
    date DATE NOT NULL,
    items_id TEXT NOT NULL,
    items TEXT NOT NULL,
    price REAL NOT NULL,
    PRIMARY KEY (date, items_id, items)
)
''')

# Create Bakery table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Bakery (
    date DATE NOT NULL,
    items_id TEXT NOT NULL,
    items TEXT NOT NULL,
    price REAL NOT NULL,
    PRIMARY KEY (date, items_id, items)
)
''')

# Create Customers_Order table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Customers_Order (
    date DATE NOT NULL,
    chat_id INTEGER NOT NULL,
    username TEXT,
    ordered_item_id TEXT NOT NULL,
    ordered_item TEXT NOT NULL,
    additional_info TEXT,
    ordered_quantity INTEGER DEFAULT 0,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    is_paid INTEGER DEFAULT 0, -- 0 for unpaid, 1 for paid
    payment_type TEXT,
    screenshot BLOB,
    PRIMARY KEY (date, chat_id, ordered_item),
    FOREIGN KEY (ordered_item) REFERENCES Menu(items) -- Assuming a unified Menu table for lunch and bakery items
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Order_raiting (
    date DATE NOT NULL,
    chat_id INTEGER NOT NULL,
    username TEXT,
    ordered_item_id TEXT NOT NULL,
    ordered_item TEXT NOT NULL,
    raiting_score REAL,
    PRIMARY KEY (date, chat_id, ordered_item)
)
''')

# Create Customers_Review table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Customers_Review (
    date DATE NOT NULL,
    chat_id INTEGER NOT NULL,
    username TEXT,
    review TEXT,
    PRIMARY KEY (date, chat_id)
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully!")
