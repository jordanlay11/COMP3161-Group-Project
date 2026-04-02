DROP DATABASE IF EXISTS course_mgmt;
CREATE DATABASE course_mgmt;
USE course_mgmt;

-- 1. Base user table
CREATE TABLE userAccount (
    user_id   INT          NOT NULL AUTO_INCREMENT,
    email     VARCHAR(100) NOT NULL UNIQUE,
    password  VARCHAR(255) NOT NULL,
    loggedIn  BOOLEAN      NOT NULL DEFAULT FALSE,
    role      ENUM('admin','lecturer','student') NOT NULL,
    PRIMARY KEY (user_id)
);

-- 2. Admin
CREATE TABLE admin (
    admin_id   INT          NOT NULL AUTO_INCREMENT,
    user_id    INT          NOT NULL UNIQUE,
    adminName  VARCHAR(100) NOT NULL,
    PRIMARY KEY (admin_id),
    FOREIGN KEY (user_id) REFERENCES userAccount(user_id)
);

-- 3. Lecturer
CREATE TABLE lecturer (
    lec_id   INT          NOT NULL AUTO_INCREMENT,
    user_id  INT          NOT NULL UNIQUE,
    lecName  VARCHAR(100) NOT NULL,
    PRIMARY KEY (lec_id),
    FOREIGN KEY (user_id) REFERENCES userAccount(user_id)
);

-- 4. Student
CREATE TABLE student (
    sid      INT          NOT NULL AUTO_INCREMENT,
    user_id  INT          NOT NULL UNIQUE,
    sname    VARCHAR(100) NOT NULL,
    PRIMARY KEY (sid),
    FOREIGN KEY (user_id) REFERENCES userAccount(user_id)
);

-- 5. Course
CREATE TABLE course (
    course_id   INT          NOT NULL AUTO_INCREMENT,
    title       VARCHAR(150) NOT NULL,
    created_by  INT          NOT NULL,
    PRIMARY KEY (course_id),
    FOREIGN KEY (created_by) REFERENCES admin(admin_id)
);

-- 6. Course-Lecturer (one lecturer per course)
CREATE TABLE course_lecturer (
    course_id  INT NOT NULL,
    lec_id     INT NOT NULL,
    PRIMARY KEY (course_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id),
    FOREIGN KEY (lec_id)    REFERENCES lecturer(lec_id)
);

-- 7. Enrolment
CREATE TABLE enrolment (
    enrolment_id  INT      NOT NULL AUTO_INCREMENT,
    sid           INT      NOT NULL,
    course_id     INT      NOT NULL,
    enrolled_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (enrolment_id),
    UNIQUE KEY uq_student_course (sid, course_id),
    FOREIGN KEY (sid)       REFERENCES student(sid),
    FOREIGN KEY (course_id) REFERENCES course(course_id)
);

-- 8. Assignment
CREATE TABLE assignment (
    assignment_id  INT          NOT NULL AUTO_INCREMENT,
    course_id      INT          NOT NULL,
    title          VARCHAR(150) NOT NULL,
    max_grade      DECIMAL(5,2) NOT NULL DEFAULT 100.00,
    PRIMARY KEY (assignment_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id)
);

-- 9. Submission
CREATE TABLE submission (
    submission_id  INT          NOT NULL AUTO_INCREMENT,
    assignment_id  INT          NOT NULL,
    sid            INT          NOT NULL,
    grade          DECIMAL(5,2) DEFAULT NULL,
    submitted_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (submission_id),
    UNIQUE KEY uq_student_assignment (sid, assignment_id),
    FOREIGN KEY (assignment_id) REFERENCES assignment(assignment_id),
    FOREIGN KEY (sid)           REFERENCES student(sid)
);

-- 10. Section
CREATE TABLE section (
    section_id    INT          NOT NULL AUTO_INCREMENT,
    course_id     INT          NOT NULL,
    sectionTitle  VARCHAR(150) NOT NULL,
    PRIMARY KEY (section_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id)
);

-- 11. Item
CREATE TABLE item (
    item_id    INT          NOT NULL AUTO_INCREMENT,
    section_id INT          NOT NULL,
    itemTitle  VARCHAR(150) NOT NULL,
    itemType   ENUM('link','file','slide') NOT NULL,
    url        VARCHAR(500),
    PRIMARY KEY (item_id),
    FOREIGN KEY (section_id) REFERENCES section(section_id)
);

-- 12. Calendar Event
CREATE TABLE calendarEvent (
    event_id   INT          NOT NULL AUTO_INCREMENT,
    course_id  INT          NOT NULL,
    task       VARCHAR(200) NOT NULL,
    dueDate    DATE         NOT NULL,
    status     ENUM('upcoming','completed','cancelled') NOT NULL DEFAULT 'upcoming',
    PRIMARY KEY (event_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id)
);

-- 13. Discussion Forum
CREATE TABLE discussionForum (
    forum_id    INT          NOT NULL AUTO_INCREMENT,
    course_id   INT          NOT NULL,
    forumTitle  VARCHAR(150) NOT NULL,
    createdBy   INT          NOT NULL,
    PRIMARY KEY (forum_id),
    FOREIGN KEY (course_id) REFERENCES course(course_id),
    FOREIGN KEY (createdBy) REFERENCES userAccount(user_id)
);

-- 14. Discussion Thread
CREATE TABLE discussionThread (
    thread_id    INT          NOT NULL AUTO_INCREMENT,
    forum_id     INT          NOT NULL,
    threadTitle  VARCHAR(200) NOT NULL,
    threadBody   TEXT         NOT NULL,
    createdBy    INT          NOT NULL,
    PRIMARY KEY (thread_id),
    FOREIGN KEY (forum_id)  REFERENCES discussionForum(forum_id),
    FOREIGN KEY (createdBy) REFERENCES userAccount(user_id)
);

-- 15. Reply
CREATE TABLE reply (
    reply_id        INT      NOT NULL AUTO_INCREMENT,
    thread_id       INT      NOT NULL,
    parent_reply_id INT      DEFAULT NULL,
    replyBody       TEXT     NOT NULL,
    createdBy       INT      NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (reply_id),
    FOREIGN KEY (thread_id)       REFERENCES discussionThread(thread_id),
    FOREIGN KEY (parent_reply_id) REFERENCES reply(reply_id),
    FOREIGN KEY (createdBy)       REFERENCES userAccount(user_id)
);

-- =============================================================
-- REPORT VIEWS
-- =============================================================

-- 1. Courses with 50 or more students
CREATE VIEW vw_large_courses AS
SELECT c.course_id, c.title, COUNT(e.sid) AS student_count
FROM course c
JOIN enrolment e ON c.course_id = e.course_id
GROUP BY c.course_id, c.title
HAVING COUNT(e.sid) >= 50;

-- 2. Students doing 5 or more courses
CREATE VIEW vw_busy_students AS
SELECT s.sid, s.sname, COUNT(e.course_id) AS course_count
FROM student s
JOIN enrolment e ON s.sid = e.sid
GROUP BY s.sid, s.sname
HAVING COUNT(e.course_id) >= 5;

-- 3. Lecturers teaching 3 or more courses
CREATE VIEW vw_busy_lecturers AS
SELECT l.lec_id, l.lecName, COUNT(cl.course_id) AS course_count
FROM lecturer l
JOIN course_lecturer cl ON l.lec_id = cl.lec_id
GROUP BY l.lec_id, l.lecName
HAVING COUNT(cl.course_id) >= 3;

-- 4. Top 10 most enrolled courses
CREATE VIEW vw_top_enrolled_courses AS
SELECT c.course_id, c.title, COUNT(e.sid) AS student_count
FROM course c
JOIN enrolment e ON c.course_id = e.course_id
GROUP BY c.course_id, c.title
ORDER BY student_count DESC
LIMIT 10;

-- 5. Top 10 students by overall average grade
CREATE VIEW vw_top_students AS
SELECT s.sid, s.sname, ROUND(AVG(sub.grade), 2) AS overall_average
FROM student s
JOIN submission sub ON s.sid = sub.sid
WHERE sub.grade IS NOT NULL
GROUP BY s.sid, s.sname
ORDER BY overall_average DESC
LIMIT 10;