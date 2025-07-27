import mysql.connector

#connection info

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="@Elric2004",
        database="grocery_portal"
    )

# Test if connected to MySQL

if __name__ == "__main__":
    try:
        conn = get_connection()
        print("Connected to MySQL!")
        conn.close()
    except Exception as e:
        print("Connection failed:", e)
