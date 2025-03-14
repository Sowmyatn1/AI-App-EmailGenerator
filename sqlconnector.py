import mysql.connector
import os
from dotenv import load_dotenv

""" This is a stand alone code . which was used to test the database connection. we are using mysql.connector to connect to mysql data base
to run this code interminal first run
1. cd /Users/kirankumarkp/Documents/Asowmya/GenAIEmailGenerator/EmailGeneratorAPP 
2. python sqlconnector.py"""

# Load environment variables from .env file
load_dotenv()

# MySQL Connection Details are loaded from .env file 
db_config = {
    "host":os.getenv("DB_host"),
    "user":os.getenv("DB_user"),
    "password": os.getenv("DB_password"),
    "database": os.getenv("DB_database")
}


def connect_to_db():
    try:
        conn=mysql.connector.connect(**db_config)
        print("connected to db")
        return conn
    except mysql.connector.Error as err:
        print(f"Error :{err}")
        return None


if __name__ == "__main__":
    conn=connect_to_db()
    if conn:
        # test the connection by running below query
        
        print("✅ Connection successful! Fetching top customers...\n")
        query = """
        SELECT customer_name, email, total_spent 
        FROM customer
        ORDER BY total_spent DESC 
        LIMIT 5;
        """
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        results=cursor.fetchall()
        conn.close()
        print(results)


    else:
        print("failed")
