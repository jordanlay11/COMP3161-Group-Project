from flask import Blueprint, request, jsonify
from db.db import get_db_connection
from utils.auth import check_logged_in

reply_api = Blueprint('reply_api', __name__)

#Create reply
@reply_api.route('/api/replies', methods=['POST'])
def create_reply():
    data = request.get_json()

    thread_id = data.get('thread_id')
    replyBody = data.get('replyBody')
    user_id = data.get('user_id')
    parent_reply_id = data.get('parent_reply_id')  # can be None

    if not all([thread_id, replyBody, user_id]):
        return jsonify({"error": "Missing fields"}), 400

    # 🔐 Check logged in
    if not check_logged_in(user_id):
        return jsonify({"error": "User not logged in"}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Optional: validate parent reply exists
        if parent_reply_id:
            cursor.execute(
                "SELECT * FROM reply WHERE reply_id = %s",
                (parent_reply_id,)
            )
            if not cursor.fetchone():
                return jsonify({"error": "Parent reply not found"}), 400

        # Insert reply
        cursor.execute("""
        INSERT INTO reply (thread_id, parent_reply_id, replyBody, createdBy)
        VALUES (%s, %s, %s, %s)
        """, (thread_id, parent_reply_id, replyBody, user_id))

        conn.commit()

        return jsonify({"message": "Reply created"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#Get replies for a thread
@reply_api.route('/api/threads/<int:thread_id>/replies', methods=['GET'])
def get_replies(thread_id):

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT *
        FROM reply
        WHERE thread_id = %s
        ORDER BY created_at ASC
        """, (thread_id,))

        replies = cursor.fetchall()

        return jsonify(replies), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#Delete reply for bonus
@reply_api.route('/api/replies/<int:reply_id>', methods=['DELETE'])
def delete_reply(reply_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    if not check_logged_in(user_id):
        return jsonify({"error": "User not logged in"}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Only creator can delete
        cursor.execute("""
        DELETE FROM reply
        WHERE reply_id = %s AND createdBy = %s
        """, (reply_id, user_id))

        conn.commit()

        return jsonify({"message": "Reply deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()