import pyodbc

def create_db():
    conn_str = "Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=master;Trusted_Connection=yes;"
    try:
        # We need autocommit=True to create a database
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        
        # Check if DB exists
        cursor.execute("SELECT name FROM sys.databases WHERE name = 'DocZenDB'")
        if cursor.fetchone():
            print("Database 'DocZenDB' already exists.")
        else:
            print("Creating database 'DocZenDB'...")
            cursor.execute("CREATE DATABASE DocZenDB")
            print("SUCCESS: Database 'DocZenDB' created.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"FAILED to create database: {str(e)}")

if __name__ == "__main__":
    create_db()
