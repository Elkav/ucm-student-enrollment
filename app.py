# main.py

from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.base import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
import secrets


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite4"
db = SQLAlchemy(app)
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Generates a 32-character random key
migrate = Migrate(app, db)

admin = Admin(app, name='Class Management', template_mode='bootstrap3')

# Course model (previously a db.Table)
class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"), nullable=False)
    # student_id = db.Column(db.Integer, db.ForeignKey("student.id", name="studentID"), nullable=False)
    course_name = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    students_enrolled = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    teacher = db.relationship('Teacher', backref='courses')

# Teacher model
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    legal_name = db.Column(db.String(), nullable=False)
    
    def to_dict(self):
        return {
            "legal_name": self.legal_name,
        }

# Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    legal_name = db.Column(db.String(), nullable=False)
    
    def to_dict(self):
        return {
            "legal_name": self.legal_name,
        }

# AdminUser model
# so far not being used
# this is the admin user we made and not the one that is provided by flask admin
class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    legal_name = db.Column(db.String(), nullable=False)
    
    def to_dict(self):
        return {
            "username": self.username
        }
    
class MyModelView(ModelView):
    column_list = ('course_name', 'teacher_id', 'time', 'students_enrolled', 'grade')
    form_columns = ('course_name', 'teacher_id', 'time', 'students_enrolled', 'grade')

# Admin views to create, read, update, and delete
admin.add_view(ModelView(Student, db.session))
admin.add_view(ModelView(Teacher, db.session))
admin.add_view(MyModelView(Course, db.session))
admin.add_link(MenuLink(name='Logout', category='', url='/'))

@app.route('/')
def index():
    return render_template("index.html")

# Create new user (student, teacher, or admin)
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template("create.html")

    if request.method == 'POST':
        data = request.get_json()
        username = data["username"]
        password = data["password"]
        legal_name = data["legal_name"]
        statue = data["statue"]
        
        if statue == 'student':
            if Student.query.filter_by(username=username).first():
                return "400"
            student = Student(username=username, password=password, legal_name=legal_name)
            db.session.add(student)
            db.session.commit()
            return jsonify(student.to_dict())
        elif statue == 'teacher':
            if Teacher.query.filter_by(username=username).first():
                return "400"
            teacher = Teacher(username=username, password=password, legal_name=legal_name)
            db.session.add(teacher)
            db.session.commit()
            return jsonify(teacher.to_dict())
        elif statue == 'admin':
            if AdminUser.query.filter_by(username=username).first():
                return "400"
            adminUser = AdminUser(username=username, password=password, legal_name=legal_name)
            db.session.add(adminUser)
            db.session.commit()
            return jsonify(adminUser.to_dict())
        else:
            return "404"

# User page routing
@app.route('/<string:username>/<string:password>')
def show_user_page(username, password):
    student = Student.query.filter_by(username=username).first()
    if student and student.password == password:
        return render_template("studentTemplate.html", name=student.legal_name)

    teacher = Teacher.query.filter_by(username=username).first()
    if teacher and teacher.password == password:
        return render_template("teacherTemplate.html", name=teacher.legal_name)

    adminUser = AdminUser.query.filter_by(username=username).first()
    if adminUser and adminUser.password == password:
        # return render_template("adminTemplate.html", name=adminUser.username)
        return redirect('/admin')

    return "404"

@app.route('/student/<string:username>', methods=['GET', 'POST'])
def show_student_courses(username):
    student = Student.query.filter_by(username=username).first()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables
        app.run(debug=True)
        # db.drop_all()  # Remove this line to avoid dropping your database every time
