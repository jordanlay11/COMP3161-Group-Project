import os               #gives us access to environment variables
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(     #looks for environment variables, if not found uses default values
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "3161_project_user"),
        password=os.environ.get("DB_PASSWORD", "3161project"),
        database=os.environ.get("DB_NAME", "course_mgmt")
    )

