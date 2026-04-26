from flask import Blueprint, request, jsonify
from db.db import get_db_connection
from utils.auth import require_auth

thread_api = Blueprint('thread_api', __name__)

#Create thread
@thread_api.route('/api/threads', methods=['POST'])
@require_auth  # any logged-in user can create a thread
def create_thread():
    data        = request.get_json()
    forum_id    = data.get('forum_id')
    threadTitle = data.get('threadTitle')
    threadBody  = data.get('threadBody')

    user_id = request.user['user_id']

    if not all([forum_id, threadTitle, threadBody]):
        return jsonify({"error": "Missing fields"}), 400

    try:
        conn   = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO discussionThread (forum_id, threadTitle, threadBody, createdBy)
        VALUES (%s, %s, %s, %s)
        """, (forum_id, threadTitle, threadBody, user_id))

        conn.commit()

        return jsonify({"message": "Thread created"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#Get thread for forum
@thread_api.route('/api/forums/<int:forum_id>/threads', methods=['GET'])
def get_threads(forum_id):

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT * FROM discussionThread
        WHERE forum_id = %s
        """, (forum_id,))

        threads = cursor.fetchall()

        return jsonify(threads), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

