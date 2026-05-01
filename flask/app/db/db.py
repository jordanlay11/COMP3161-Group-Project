import os               #gives us access to environment variables
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(     #looks for environment variables, if not found uses default values
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "NewPassword123!"),
        database=os.environ.get("DB_NAME", "course_mgmt")
    )

