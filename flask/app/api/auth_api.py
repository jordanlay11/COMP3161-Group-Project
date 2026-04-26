import bcrypt        # for hashing passwords securely
import jwt           # for creating and verifying JWT tokens
import datetime     # for setting token expiry times
from flask import Blueprint, request, jsonify, current_app
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
    
    if role not in ('admin', 'lecturer', 'student'):
        return jsonify({"error": "Invalid role"}), 400
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        conn = get_db_connection()
        cursor = conn.cursor()


        # 1. Insert into userAccount
        # saves hashed password to database instead of plaintext
        cursor.execute(
            'INSERT INTO userAccount (email, password, role) VALUES (%s, %s, %s)',
            (email, hashed_password.decode('utf-8'), role)
        )
    
        # gets auto-generated user_id for the new user
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
        #fetched by email since we cant compare passwords in sql anymore (stored value is a hash)
        cursor.execute(
            'SELECT user_id, email, password, role FROM userAccount WHERE email = %s',
            (email,)
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        #verification of password against the stored hash using bcrypt

        password_matches= bcrypt.checkpw(
            password.encode('utf-8'), 
            user['password'].encode('utf-8')
        )
        
        if not password_matches:
            return jsonify({'error': 'Invalid credentials'}), 401

        user_id = user["user_id"]
        role = user["role"]

        # Get name from correct table
        name = None
        if role == 'admin':
            cursor.execute('SELECT adminName FROM admin WHERE user_id = %s', (user_id,))
            name = cursor.fetchone()['adminName']
        elif role == 'lecturer':
            cursor.execute('SELECT lecName FROM lecturer WHERE user_id = %s', (user_id,))
            name = cursor.fetchone()['lecName']
        elif role == 'student':
            cursor.execute('SELECT sname FROM student WHERE user_id = %s', (user_id,))
            name = cursor.fetchone()['sname']

        # build the token payload 
        # anyone who has the token can read this data, but cannot fake or modify it
        # because it's signed with the SECRET_KEY
        token_payload = {
            'user_id': user_id,
            'email':   email,
            'role':    role,
            'name':    name,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # token expires in 24 hours
        }

        # sign and create the token using the app's SECRET_KEY
        token = jwt.encode(
            token_payload,
            current_app.config['SECRET_KEY'],  # loaded from .env
            algorithm='HS256'  # the signing algorithm
        )

        # return the token to the client (must be stored and sent on every future request)
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'user_id': user_id,
                'email':   email,
                'role':    role,
                'name':    name
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# ----------------------------
# LOGOUT
# ----------------------------
@auth_api.route('/api/logout', methods=['POST'])
def logout():
    # the client simply deletes the token on their end
    # after 24 hours the token expires automatically and becomes invalid even if the client doesn't delete it
    return jsonify({'message': 'Logged out. Please delete your token on the client side.'}), 200