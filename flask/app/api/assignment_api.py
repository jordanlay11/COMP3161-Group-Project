from flask import Blueprint, request, jsonify
from db.db import get_db_connection
from utils.auth import check_logged_in, check_role

assignment_api = Blueprint('assignment_api', __name__)

#Create assignment(lecturer)
@assignment_api.route('/api/assignments', methods=['POST'])
def create_assignment():
    data = request.get_json()

    course_id = data.get('course_id')
    title = data.get('title')
    max_grade = data.get('max_grade', 100)
    user_id = data.get('user_id')

    if not all([course_id, title, user_id]):
        return jsonify({"error": "Missing fields"}), 400

    # 🔐 Auth checks
    if not check_logged_in(user_id):
        return jsonify({"error": "User not logged in"}), 401

    if not check_role(user_id, "lecturer"):
        return jsonify({"error": "Only lecturers can create assignments"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO assignment (course_id, title, max_grade)
        VALUES (%s, %s, %s)
        """, (course_id, title, max_grade))

        conn.commit()

        return jsonify({"message": "Assignment created"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#Get assignments for course
@assignment_api.route('/api/courses/<int:course_id>/assignments', methods=['GET'])
def get_assignments(course_id):

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT * FROM assignment
        WHERE course_id = %s
        """, (course_id,))

        assignments = cursor.fetchall()

        return jsonify(assignments), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#Grade submission(Lecturer only)
@assignment_api.route('/api/grade', methods=['POST'])
def grade_submission():
    data = request.get_json()

    assignment_id = data.get('assignment_id')
    sid = data.get('sid')
    grade = data.get('grade')
    user_id = data.get('user_id')

    if not all([assignment_id, sid, grade, user_id]):
        return jsonify({"error": "Missing fields"}), 400

    # 🔐 Auth checks
    if not check_logged_in(user_id):
        return jsonify({"error": "User not logged in"}), 401

    if not check_role(user_id, "lecturer"):
        return jsonify({"error": "Only lecturers can grade"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE submission
        SET grade = %s
        WHERE assignment_id = %s AND sid = %s
        """, (grade, assignment_id, sid))

        conn.commit()

        return jsonify({"message": "Grade updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#Submit assignment(student only)
@assignment_api.route('/api/submissions', methods=['POST'])
def submit_assignment():
    data = request.get_json()

    assignment_id = data.get('assignment_id')
    sid = data.get('sid')
    user_id = data.get('user_id')

    if not all([assignment_id, sid, user_id]):
        return jsonify({"error": "Missing fields"}), 400

    # 🔐 Auth checks
    if not check_logged_in(user_id):
        return jsonify({"error": "User not logged in"}), 401

    if not check_role(user_id, "student"):
        return jsonify({"error": "Only students can submit"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO submission (assignment_id, sid)
        VALUES (%s, %s)
        """, (assignment_id, sid))

        conn.commit()

        return jsonify({"message": "Submission successful"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#Get student grades
@assignment_api.route('/api/student/<int:sid>/grades', methods=['GET'])
def get_student_grades(sid):

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT a.title, s.grade
        FROM submission s
        JOIN assignment a ON s.assignment_id = a.assignment_id
        WHERE s.sid = %s
        """, (sid,))

        grades = cursor.fetchall()

        return jsonify(grades), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()