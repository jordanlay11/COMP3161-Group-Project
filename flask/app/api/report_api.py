from flask import Blueprint, jsonify
from db.db import get_db_connection

report_api = Blueprint('report_api', __name__)

#Large course
@report_api.route('/api/reports/large-courses')
def large_courses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM vw_large_courses")
    return jsonify(cursor.fetchall())

#Busy student
@report_api.route('/api/reports/busy-students')
def busy_students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM vw_busy_students")
    return jsonify(cursor.fetchall())

#busy lecturer
@report_api.route('/api/reports/busy-lecturers')
def busy_lecturers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM vw_busy_lecturers")
    return jsonify(cursor.fetchall())

#top enrolled courses
@report_api.route('/api/reports/top-courses')
def top_courses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM vw_top_enrolled_courses")
    return jsonify(cursor.fetchall())

#top students
@report_api.route('/api/reports/top-students')
def top_students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM vw_top_students")
    return jsonify(cursor.fetchall())