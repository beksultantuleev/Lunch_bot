import sqlite3
import datetime


database_location = 'database/app_database.db'
conn = sqlite3.connect("database/app_database.db")
cursor = conn.cursor()

date_mask = "%d-%m-%Y"
current_date = datetime.datetime.now().strftime(date_mask)
past_30_days = (datetime.datetime.now() -
                datetime.timedelta(days=30)).strftime(date_mask)

with sqlite3.connect(database_location) as conn:
    cursor = conn.cursor()

    # Fetch the top 20 highest-rated lunch items in the last 30 days
    cursor.execute("""
        SELECT ordered_item, 
            COUNT(*) AS total_ratings, 
            ROUND(AVG(raiting_score), 2) AS avg_rating
        FROM Order_raiting
        where date BETWEEN DATE('now', '-30 days') AND DATE('now') 
        GROUP BY ordered_item
        ORDER BY avg_rating DESC, total_ratings DESC
        limit 20
       ;
    """,)
#     cursor.execute("""
#         SELECT * FROM Order_raiting 
# WHERE date = DATE('now');

#     """,)

    rows = cursor.fetchall()
    print(rows)



