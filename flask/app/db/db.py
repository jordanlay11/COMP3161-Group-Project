import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",            # IMPORTANT: use 'db' for Docker
        user="3161_project_user",
        password="3161project",
        database="course_mgmt"
    )

