from faker import Faker
import random

fake = Faker()

output = open("COMP3161_projectdata.sql", "w")

def w(line):
    output.write(line + "\n")

w("USE course_mgmt;")
w("")

# Admin
w("-- Admin")
w("INSERT INTO userAccount (email, password, role) VALUES ('admin@school.com', 'hashedpass', 'admin');")
w("INSERT INTO admin (user_id, adminName) VALUES (1, 'System Admin');")
w("")

# Lecturers (100)
w("-- Lecturers")
for i in range(1, 101):
    name = fake.name().replace("'", "")
    email = fake.unique.email()
    uid = i + 1
    w(f"INSERT INTO userAccount (email, password, role) VALUES ('{email}', 'hashedpass', 'lecturer');")
    w(f"INSERT INTO lecturer (user_id, lecName) VALUES ({uid}, '{name}');")

w("")

# Courses (200)
course_names = [
    "Introduction to Programming", "Data Structures", "Algorithms",
    "Database Systems", "Operating Systems", "Computer Networks",
    "Software Engineering", "Artificial Intelligence", "Machine Learning",
    "Web Development", "Mobile Development", "Computer Graphics",
    "Cybersecurity", "Cloud Computing", "Discrete Mathematics",
    "Linear Algebra", "Calculus", "Statistics", "Physics", "Chemistry"
]

w("-- Courses")
for i in range(1, 201):
    base = course_names[i % len(course_names)]
    title = f"{base} {i}".replace("'", "")
    w(f"INSERT INTO course (title, created_by) VALUES ('{title}', 1);")

w("")

# Course-Lecturer assignments
w("-- Course-Lecturer assignments")
# 25 lecturers teach 4 courses each (courses 1-100)
for course_id in range(1, 101):
    lec_id = (course_id - 1) // 4 + 1
    w(f"INSERT INTO course_lecturer (course_id, lec_id) VALUES ({course_id}, {lec_id});")

# 25 lecturers teach 2 courses each (courses 101-150)
for course_id in range(101, 151):
    lec_id = 25 + (course_id - 101) // 2 + 1
    w(f"INSERT INTO course_lecturer (course_id, lec_id) VALUES ({course_id}, {lec_id});")

# 50 lecturers teach 1 course each (courses 151-200)
for course_id in range(151, 201):
    lec_id = 50 + (course_id - 151) + 1
    w(f"INSERT INTO course_lecturer (course_id, lec_id) VALUES ({course_id}, {lec_id});")

w("")

# Assignments (1 per course)
w("-- Assignments")
for i in range(1, 201):
    w(f"INSERT INTO assignment (course_id, title, max_grade) VALUES ({i}, 'Assignment 1 - Course {i}', 100.00);")

w("")

# Students (100,000)
w("-- Students")
student_enrolments = {}

for i in range(1, 100001):
    name = fake.name().replace("'", "")
    email = fake.unique.email()
    uid = i + 101  # 1 admin + 100 lecturers
    w(f"INSERT INTO userAccount (email, password, role) VALUES ('{email}', 'hashedpass', 'student');")
    w(f"INSERT INTO student (user_id, sname) VALUES ({uid}, '{name}');")

w("")

# Enrolments (3-6 courses per student)
w("-- Enrolments")
for sid in range(1, 100001):
    num_courses = random.randint(3, 6)
    courses = random.sample(range(1, 201), num_courses)
    student_enrolments[sid] = courses
    for course_id in courses:
        w(f"INSERT IGNORE INTO enrolment (sid, course_id) VALUES ({sid}, {course_id});")

w("")

# Submissions
w("-- Submissions")
for sid, courses in student_enrolments.items():
    for course_id in courses:
        grade = round(random.uniform(40, 100), 2)
        w(f"INSERT IGNORE INTO submission (assignment_id, sid, grade) VALUES ({course_id}, {sid}, {grade});")

w("")

output.close()
print("Done! comp3161_data.sql has been generated.")
