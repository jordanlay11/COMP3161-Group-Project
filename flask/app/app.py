import os            #gives us access to environment variables
from flask import Flask
from api.auth_api import auth_api
from api.course_api import course_api
from api.forum_api import forum_api
from api.thread_api import thread_api
from api.reply_api import reply_api
from api.assignment_api import assignment_api
from api.calendar_api import calendar_api
from api.content_api import content_api
from api.report_api import report_api

app = Flask(__name__)

# Load the SECRET_KEY from environment variables (set in .env / docker-compose.yml)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

app.register_blueprint(auth_api)
app.register_blueprint(course_api)
app.register_blueprint(forum_api)
app.register_blueprint(thread_api)
app.register_blueprint(reply_api)
app.register_blueprint(assignment_api)
app.register_blueprint(calendar_api)
app.register_blueprint(content_api)
app.register_blueprint(report_api)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)