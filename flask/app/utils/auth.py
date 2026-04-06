from db.db import get_db_connection

def check_logged_in(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT loggedIn FROM userAccount WHERE user_id = %s",
        (user_id,)
    )
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user and user["loggedIn"]


def check_role(user_id, required_role):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT role FROM userAccount WHERE user_id = %s",
        (user_id,)
    )
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user and user["role"] == required_role