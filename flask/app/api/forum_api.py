from flask import Blueprint, request, jsonify
from db.db import get_db_connection
from utils.auth import require_auth

forum_api = Blueprint('forum_api', __name__)

#Create forum
@forum_api.route('/api/forums', methods=['POST'])
@require_auth  # any logged-in user can create a forum
def create_forum():
    data       = request.get_json()
    course_id  = data.get('course_id')
    forumTitle = data.get('forumTitle')

    # user_id comes from the verified token now
    user_id = request.user['user_id']

    if not all([course_id, forumTitle]):
        return jsonify({"error": "Missing fields"}), 400

    try:
        conn   = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO discussionForum (course_id, forumTitle, createdBy)
        VALUES (%s, %s, %s)
        """, (course_id, forumTitle, user_id))

        conn.commit()

        return jsonify({"message": "Forum created"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#Get forum for course
@forum_api.route('/api/courses/<int:course_id>/forums', methods=['GET'])
def get_forums(course_id):

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT * FROM discussionForum
        WHERE course_id = %s
        """, (course_id,))

        forums = cursor.fetchall()

        return jsonify(forums), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()