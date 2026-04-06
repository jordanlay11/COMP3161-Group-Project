from flask import Blueprint, request, jsonify
from db.db import get_db_connection

auth_api = Blueprint('auth_api', __name__)

# ----------------------------
# REGISTER
# ----------------------------
@auth_api.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')
    role = data.get('role')  # admin / lecturer / student
    name = data.get('name')

    if not all([email, password, role, name]):
        return jsonify({"error": "Missing fields"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Insert into userAccount
        user_query = """
        INSERT INTO userAccount (email, password, role)
        VALUES (%s, %s, %s)
        """
        cursor.execute(user_query, (email, password, role))

        user_id = cursor.lastrowid

        # 2. Insert into role-specific table
        if role == "admin":
            cursor.execute(
                "INSERT INTO admin (user_id, adminName) VALUES (%s, %s)",
                (user_id, name)
            )

        elif role == "lecturer":
            cursor.execute(
                "INSERT INTO lecturer (user_id, lecName) VALUES (%s, %s)",
                (user_id, name)
            )

        elif role == "student":
            cursor.execute(
                "INSERT INTO student (user_id, sname) VALUES (%s, %s)",
                (user_id, name)
            )

        else:
            return jsonify({"error": "Invalid role"}), 400

        conn.commit()

        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ----------------------------
# LOGIN
# ----------------------------
@auth_api.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({"error": "Missing email or password"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get user
        query = """
        SELECT user_id, email, role, loggedIn
        FROM userAccount
        WHERE email = %s AND password = %s
        """
        cursor.execute(query, (email, password))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Check if already logged in
        if user["loggedIn"]:
            return jsonify({"error": "User already logged in"}), 400

        user_id = user["user_id"]
        role = user["role"]

        # Get name from correct table
        name = None

        if role == "admin":
            cursor.execute("SELECT adminName FROM admin WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            name = result["adminName"]

        elif role == "lecturer":
            cursor.execute("SELECT lecName FROM lecturer WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            name = result["lecName"]

        elif role == "student":
            cursor.execute("SELECT sname FROM student WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            name = result["sname"]

        # Update loggedIn status
        cursor.execute(
            "UPDATE userAccount SET loggedIn = TRUE WHERE user_id = %s",
            (user_id,)
        )
        conn.commit()

        return jsonify({
            "message": "Login successful",
            "user": {
                "user_id": user_id,
                "email": email,
                "role": role,
                "name": name
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ----------------------------
# LOGOUT
# ----------------------------
@auth_api.route('/api/logout', methods=['POST'])
def logout():
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check current status
        cursor.execute("SELECT loggedIn FROM userAccount WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        if not result or not result[0]:
            return jsonify({"error": "User is not logged in"}), 400

        cursor.execute(
            "UPDATE userAccount SET loggedIn = FALSE WHERE user_id = %s",
            (user_id,)
        )
        conn.commit()

        return jsonify({"message": "Logged out successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()