from flask import Blueprint, request, jsonify
from db.db import get_db_connection
from utils.auth import require_auth, require_role

calendar_api = Blueprint('calendar_api', __name__)

#Create event(lecturer)
@calendar_api.route('/api/calendar', methods=['POST'])
@require_auth
@require_role('lecturer')  # only lecturers can create calendar events
def create_event():
    data      = request.get_json()
    course_id = data.get('course_id')
    task      = data.get('task')
    dueDate   = data.get('dueDate')

    # user_id comes from the verified token now
    user_id = request.user['user_id']

    if not all([course_id, task, dueDate]):
        return jsonify({"error": "Missing fields"}), 400

    try:
        conn   = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO calendarEvent (course_id, task, dueDate)
        VALUES (%s, %s, %s)
        """, (course_id, task, dueDate))

        conn.commit()

        return jsonify({"message": "Event created"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#Get events for course
@calendar_api.route('/api/courses/<int:course_id>/calendar', methods=['GET'])
def get_course_events(course_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT * FROM calendarEvent
        WHERE course_id = %s
        """, (course_id,))

        return jsonify(cursor.fetchall()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

#Get events for student by date
@calendar_api.route('/api/student/<int:sid>/calendar', methods=['GET'])
def get_student_events(sid):
    date = request.args.get('date')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT ce.*
        FROM calendarEvent ce
        JOIN enrolment e ON ce.course_id = e.course_id
        WHERE e.sid = %s AND ce.dueDate = %s
        """, (sid, date))

        return jsonify(cursor.fetchall()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()