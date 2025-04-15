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
    # student_id is changed to be nullable
    # student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    course_name = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    #add a max students
    students_enrolled = db.Column(db.Integer, nullable=False)
    # grade is changed to be nullable
    grade = db.Column(db.Integer, nullable=True, default=0)
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
    column_list = ('course_name', 'teacher_id', 'time', 'students_enrolled')
    form_columns = ('course_name', 'teacher_id', 'time', 'students_enrolled')

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

# All functionalities of Student
@app.route('/student/<string:username>')
def show_all_courses_registered(username):
    student = Student.query.filter_by(username=username).first()
    if student:
        courses = Course.query.filter_by(student_id=student.id).all()
        course_dict = {}
        for course in courses:
            course_dict[course.course_name] = course.time
        return jsonify(course_dict), 200
    else :
        return jsonify({"error": "Student not found"}), 400

@app.route('/student/<string:username>/<string:course_name>', methods=['POST'])
def register_course(username, course_name):
    student = Student.query.filter_by(username=username).first()
    if student:
        course = Course.query.filter_by(course_name=course_name).first()
        if course:
            if course.student_id is None:
                course.student_id = student.id
                db.session.commit()
            else:
                new_instance = Course(
                    teacher_id=course.teacher_id,
                    student_id=student.id,
                    course_name=course_name,
                    time=course.time,
                    students_enrolled=course.students_enrolled,
                )
                db.session.add(new_instance)
                db.session.commit()
            return jsonify({'success': 'change made'}), 200
        else:
            return jsonify({"error": "Course not found"}), 404
    else:
        return jsonify({"error": "Student not found"}), 404


@app.route('/teacher/<string:username>/<string:course_name>', methods=['DELETE'])
def drop_course(username, course_name):
    student = Student.query.filter_by(username=username).first()
    if student:
        course = Course.query.filter_by(course_name=course_name, student_id=student.id).first()
        if course:
            db.session.delete(course)
            db.session.commit()
            return jsonify({'success': 'course drops successfully'}), 200
        else:
            return jsonify({"error": "Course not found"}), 404
    else:
        return jsonify({"error": "Student not found"}), 404

# All functionalities of Teacher
@app.route('/teacher/<string:username>')
def show_all_courses_taught(username):
    teacher = Teacher.query.filter_by(username=username).first()
    if teacher:
        courses_taught = Course.query.filter_by(teacher_id=teacher.id).all()
        if len(courses_taught) > 0:
            course_dict = {}
            for course in courses_taught:
                course_dict[course.course_name] = [course.time, course.students_enrolled]
            return jsonify(course_dict), 200
        else:
            return jsonify({"error": "Teacher did not teach any course"}), 404
    else:
        return jsonify({"error": "Teacher not found"}), 404

@app.route('/teacher/<string:username>/<string:course_name>')
def show_all_students_in_one_course(username, course_name):
    teacher = Teacher.query.filter_by(username=username).first()
    if teacher:
        particular_course = Course.query.filter_by(course_name=course_name, teacher_id=teacher.id).all()
        if len(particular_course) > 0:
            student_dict = {}
            for one_stance in particular_course:
                if one_stance.student_id is not None:
                    student_name = Student.query.filter_by(id=one_stance.student_id).first().legal_name
                    student_dict[student_name] = one_stance.grade
            return jsonify(student_dict), 200
        else:
            return jsonify({"error": "Teacher did not teach this course"}), 404
    else:
        return jsonify({"error": "Teacher not found"}), 404

@app.route('/teacher/<string:username>/<string:course_name>/<string:student_name>/<int:grade>', methods=['POST'])
def change_student_grade(username, course_name, student_name, grade):
    teacher = Teacher.query.filter_by(username=username).first()
    if teacher:
        student_id = Student.query.filter_by(legal_name=student_name).first().id
        student_in_course = Course.query.filter_by(
            course_name=course_name,
            teacher_id=teacher.id,
            student_id=student_id
        ).first()
        if student_in_course:
            student_in_course.grade = grade
            db.session.commit()
            return jsonify({'success': 'student grade updates successfully'}), 200
        else:
            return jsonify({"error": "Student not found"}), 404
    else:
        return jsonify({"error": "Teacher not found"}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables
        app.run(debug=True)
        # db.drop_all()  # Remove this line to avoid dropping your database every time
