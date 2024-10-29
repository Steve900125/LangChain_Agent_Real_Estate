from pathlib import Path
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
load_dotenv(ROOT / '.env')
SQL_URL = os.getenv("SQL_URL")

def postgres_test():
    """Test connection to PostgreSQL."""
    try:
        conn = psycopg2.connect(SQL_URL)
        print(conn)
        print(type(conn))
        print("Connected to the PostgreSQL database")
        conn.close()
    except (Exception, psycopg2.Error) as error:
        print(f"Error connecting to PostgreSQL: {error}")

def table_exists(table_name):
    """Check if a table exists in the database."""
    try:
        conn = psycopg2.connect(SQL_URL)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT EXISTS (SELECT FROM pg_tables WHERE tablename=%s);", 
            (table_name.lower(),)
        )
        exists = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return exists
    except (Exception, psycopg2.Error) as error:
        print(f"Error checking if table exists: {error}")
        return False

def create_table():
    """Create UserMessage and AgentMessage tables if they do not exist."""
    try:
        if not table_exists("usermessage"):
            conn = psycopg2.connect(SQL_URL)
            cursor = conn.cursor()

            create_user_table_query = """
                CREATE TABLE IF NOT EXISTS UserMessage (
                    user_id VARCHAR(40),
                    user_message VARCHAR(500),
                    timestamp TIMESTAMP   
                );
            """
            cursor.execute(create_user_table_query)

            conn.commit()
            cursor.close()
            conn.close()
            print("UserMessage table created successfully.")
        else:
            print("UserMessage table already exists.")

        if not table_exists("agentmessage"):
            conn = psycopg2.connect(SQL_URL)
            cursor = conn.cursor()

            create_agent_table_query = """
                CREATE TABLE IF NOT EXISTS AgentMessage (
                    user_id VARCHAR(40),
                    agent_message VARCHAR(500),
                    timestamp TIMESTAMP   
                );
            """
            cursor.execute(create_agent_table_query)

            conn.commit()
            cursor.close()
            conn.close()
            print("AgentMessage table created successfully.")
        else:
            print("AgentMessage table already exists.")
    except (Exception, psycopg2.Error) as error:
        print(f"Error creating tables: {error}")

def show_db_table():
    """Show all tables in the database."""
    try:
        conn = psycopg2.connect(SQL_URL)
        cursor = conn.cursor()
        show_query = "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public';"
        cursor.execute(show_query)
        tables = cursor.fetchall()
        print("Tables in the database:")
        for table in tables:
            print(table[0])
        cursor.close()
        conn.close()
    except (Exception, psycopg2.Error) as error:
        print(f"Error showing tables: {error}")

def insert_test():
    """Insert a test record into the UserMessage table."""
    curr_dt = datetime.now()
    timestamp = int(round(curr_dt.timestamp()))
    try:
        conn = psycopg2.connect(SQL_URL)
        cursor = conn.cursor()

        insert_sql = '''
            INSERT INTO usermessage(user_id, user_message, timestamp)
            VALUES ('useridtest123451', 'Goodbye world', %s)
            RETURNING *;
        '''
        timestamp_dt = datetime.fromtimestamp(timestamp)
        cursor.execute(insert_sql, (timestamp_dt,))
        conn.commit()

        print(cursor.fetchall())
        cursor.close()
        conn.close()
        print("PostgreSQL Inserting Success")
    except (Exception, psycopg2.Error) as error:
        print(f"Error PostgreSQL Inserting Fail: {error}")

def get_user_messages(user_id: str):
    """Retrieve user and agent messages joined by user_id and timestamp."""
    user_target = (user_id,)
    sql_join = '''
        SELECT 
            usermessage.user_message,
            agentmessage.agent_message
        FROM 
            usermessage
        INNER JOIN 
            agentmessage ON usermessage.user_id = %s 
            AND usermessage.user_id = agentmessage.user_id 
            AND usermessage.timestamp = agentmessage.timestamp;
    '''
    try:
        conn = psycopg2.connect(SQL_URL)
        cursor = conn.cursor()
        cursor.execute(sql_join, user_target)
        data_list = cursor.fetchall()
        for user_row in data_list:
            print(user_row[0])
            print(user_row[1])
        cursor.close()
        conn.close()
        print("PostgreSQL Selecting Success")
    except (Exception, psycopg2.Error) as error:
        print(f"Error PostgreSQL Selecting Fail: {error}")

def check_database_exist():
    postgres_test()
    create_table()
    show_db_table()
    insert_test()
    print(FILE.parents[1])

if __name__ == "__main__":
    check_database_exist()
