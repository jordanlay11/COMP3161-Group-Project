from flask import Blueprint, request, jsonify
from db.db import get_db_connection
from utils.auth import check_logged_in, check_role

course_api = Blueprint('course_api', __name__)

#Create course for admin
@course_api.route('/api/courses', methods=['POST'])
def create_course():
    data = request.get_json()

    title = data.get('title')
    user_id = data.get('user_id')   # IMPORTANT: pass user_id now
    admin_id = data.get('admin_id')
    lec_id = data.get('lec_id')

    if not all([title, user_id, admin_id, lec_id]):
        return jsonify({"error": "Missing fields"}), 400

    #Check logged in
    if not check_logged_in(user_id):
        return jsonify({"error": "User not logged in"}), 401

    #Check admin role
    if not check_role(user_id, "admin"):
        return jsonify({"error": "Only admins can create courses"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO course (title, created_by) VALUES (%s, %s)",
            (title, admin_id)
        )

        course_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO course_lecturer (course_id, lec_id) VALUES (%s, %s)",
            (course_id, lec_id)
        )

        conn.commit()

        return jsonify({"message": "Course created", "course_id": course_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#Enroll student
@course_api.route('/api/enroll', methods=['POST'])
def enroll_student():
    data = request.get_json()

    sid = data.get('sid')
    course_id = data.get('course_id')

    if not all([sid, course_id]):
        return jsonify({"error": "Missing fields"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check student exists
        cursor.execute("SELECT * FROM student WHERE sid = %s", (sid,))
        if not cursor.fetchone():
            return jsonify({"error": "Invalid student"}), 400

        # Enroll
        cursor.execute(
            "INSERT INTO enrolment (sid, course_id) VALUES (%s, %s)",
            (sid, course_id)
        )

        conn.commit()

        return jsonify({"message": "Student enrolled"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#Get courses for student
@course_api.route('/api/student/<int:sid>/courses', methods=['GET'])
def get_student_courses(sid):

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT c.course_id, c.title
        FROM course c
        JOIN enrolment e ON c.course_id = e.course_id
        WHERE e.sid = %s
        """, (sid,))

        courses = cursor.fetchall()

        return jsonify(courses), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#Get courses for lecturer
@course_api.route('/api/lecturer/<int:lec_id>/courses', methods=['GET'])
def get_lecturer_courses(lec_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT c.course_id, c.title
        FROM course c
        JOIN course_lecturer cl ON c.course_id = cl.course_id
        WHERE cl.lec_id = %s
        """, (lec_id,))

        return jsonify(cursor.fetchall()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

#Get all courses
@course_api.route('/api/courses', methods=['GET'])
def get_courses():

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM course")
        courses = cursor.fetchall()

        return jsonify(courses), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#Get members of a course
@course_api.route('/api/courses/<int:course_id>/members', methods=['GET'])
def get_course_members(course_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Students
        cursor.execute("""
        SELECT s.sid, s.sname
        FROM enrolment e
        JOIN student s ON e.sid = s.sid
        WHERE e.course_id = %s
        """, (course_id,))
        students = cursor.fetchall()

        # Lecturer
        cursor.execute("""
        SELECT l.lec_id, l.lecName
        FROM course_lecturer cl
        JOIN lecturer l ON cl.lec_id = l.lec_id
        WHERE cl.course_id = %s
        """, (course_id,))
        lecturer = cursor.fetchone()

        return jsonify({
            "lecturer": lecturer,
            "students": students
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

    
