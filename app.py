from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from flask_admin import Admin
from flask_admin.base import MenuLink
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
import os
import secrets

# Deleted migrate temporarily
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.sqlite3'
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = secrets.token_hex(16)  # Generates a 32-character random key

bcrypt = Bcrypt(app)

admin = Admin(app, name='Course Management', template_mode='bootstrap3')

def error(message, status=404):
    return jsonify({'Error': message}), status

def success(message, status=200):
    return jsonify({'Success': message}), status

class Registration(db.Model):  # handles relationships between students, courses, and grades
    #### switch back to backref if not using laziness
    __tablename__ = 'registration'
    student = db.relationship('Student', back_populates='registration')
    course = db.relationship('Course', back_populates='registration')
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)
    grade = db.Column(db.Numeric(5, 2), nullable=True, default=100)


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(), unique=True, nullable=False)
    time = db.Column(db.String())
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=True)
    registration = db.relationship('Registration', back_populates='course')
    students = association_proxy('registration', 'student')
    max_students = db.Column(db.Integer, nullable=False)

    def __init__(self, course_name, teacher_id, time, max_students):
        self.course_name = course_name
        self.time = time
        self.max_students = max_students
        teacher = Teacher.query.get(teacher_id)
        if teacher:
            self.teacher = teacher
        else:
            self.teacher = None

    def to_dict(self):
        teachername = "None"
        if self.teacher is not None:
            teachername = self.teacher.legal_name

        return {
            'course_name': self.course_name,
            'time': self.time,
            'teacher_id': self.teacher_id,
            'teacher_name': teachername,
            'num_students': len(self.students),
            'max_students': self.max_students
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    legal_name = db.Column(db.String(), nullable=False)
    role = db.Column(db.String(), nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': role
    }

    # def __init__(self, username, legal_name, password):
    #     self.username = username
    #     self.legal_name = legal_name
    #     self.password = bcrypt.generate_password_hash(password)

    def to_dict(self):
        return {
            'legal_name': self.legal_name
        }


class Student(User):
    __tablename__ = 'student'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    registration = db.relationship('Registration', back_populates='student')
    courses = association_proxy('registration', 'course')
    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }

    def get_grade(self, course_name):
        for registration in self.registration:
            if registration.course.course_name == course_name:
                return registration.grade
        return None

    def to_dict(self):
        return {
            'legal_name': self.legal_name
        }

    def to_dict_grade(self, course_name):
        return {
            self.legal_name: self.get_grade(course_name)
        }


class Teacher(User):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    # one-to-many relationship (one teacher has many courses)
    courses = db.relationship('Course', backref=db.backref('teacher'), lazy=True)
    __mapper_args__ = {
        'polymorphic_identity': 'teacher',
    }

    def to_dict(self):
        return {
            'legal_name': self.legal_name
        }


class Admin(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    def to_dict(self):
        return {
            'legal_name': self.legal_name
        }

class UserModelView(ModelView):
    column_list = ('id', 'username', 'password', 'legal_name', 'role')
    form_columns = ('username', 'password', 'legal_name', 'role')
    def on_model_change(self, form, model, is_created):
        if 'password' in form:
            raw_password = form.password.data
            model.password = bcrypt.generate_password_hash(raw_password).decode('utf-8')

class CourseModelView(ModelView):
    column_list = ('course_name', 'teacher_id', 'time', 'max_students')
    form_columns = ('course_name', 'teacher_id', 'time', 'max_students')

class RegModelView(ModelView):
    column_list = ('student_id', 'course_id', 'grade')

# Admin views to create, read, update, and delete
admin.add_view(UserModelView(User, db.session))
admin.add_view(CourseModelView(Course, db.session))
admin.add_view(RegModelView(Registration, db.session))
admin.add_link(MenuLink(name='Logout', category='', url='/'))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_screen():
    return render_template('login.html')


# Create new user (student, teacher, or admin)
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('create.html')

    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        legal_name = data['legal_name']
        role = data['role']

        if role == 'student':
            if Student.query.filter_by(username=username).first():
                return error("Student already exists", 400)
            student = Student(username=username, password=password, legal_name=legal_name)
            db.session.add(student)
            db.session.commit()
            return jsonify(student.to_dict())
        elif role == 'teacher':
            if Teacher.query.filter_by(username=username).first():
                return error("Teacher already exists", 400)
            teacher = Teacher(username=username, password=password, legal_name=legal_name)
            db.session.add(teacher)
            db.session.commit()
            return jsonify(teacher.to_dict())
        elif role == 'admin':
            if Admin.query.filter_by(username=username).first():
                return error("Admin already exists", 400)
            admin = Admin(username=username, password=password, legal_name=legal_name)
            db.session.add(admin)
            db.session.commit()
            return jsonify(admin.to_dict())
        else:
            return error('Role not found')


# User page routing
@app.route('/<string:username>/<string:password>')
def show_user_page(username, password):
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password.encode('utf-8'), password):
        if user.role == 'admin':
            return redirect('/admin')
        else:
            return render_template(f'{user.role}Template.html', name=user.legal_name)
    return error('Invalid username or password')


@app.route('/courses')
def show_courses():
    courses = Course.query.all()
    return jsonify([course.to_dict() for course in courses]), 200


# ----------------- STUDENT FUNCTIONALITIES ----------------- #

# Show all courses that the student is registered in
@app.route('/student/<string:username>')
def show_courses_registered(username):
    student = Student.query.filter_by(username=username).first()
    if student:
        courses = student.courses
        return jsonify([{**course.to_dict(), "grade": student.get_grade(course.course_name)} for course in courses]), 200
    else:
        return error('Student not found')


# Add course
@app.route('/student/<string:username>/<string:course_name>', methods=['POST'])
def register_course(username, course_name):
    student = Student.query.filter_by(username=username).first()
    if student:
        course = Course.query.filter_by(course_name=course_name).first()
        if course:
            if course in student.courses:
                return error('Course already registered')
            else:
                reg = Registration(student=student, course=course)
                db.session.add(reg)
                db.session.commit()
            return success('Course registered successfully')
        else:
            return error('Course not found')
    else:
        return error('Student not found')


# Drop course
@app.route('/student/<string:username>/<string:course_name>', methods=['DELETE'])
def drop_course(username, course_name):
    student = Student.query.filter_by(username=username).first()
    if student:
        course = Course.query.filter_by(course_name=course_name).first()
        if course:
            registration = Registration.query.filter_by(student_id=student.id, course_id=course.id).first()
            if registration:
                db.session.delete(registration)
                db.session.commit()
                return success('Course dropped successfully')
            else:
                return error('Registration not found')
        else:
            return error('Course not found')
    else:
        return error('Student not found')


# ----------------- TEACHER FUNCTIONALITIES ----------------- #

# Show all courses that a teacher teaches
@app.route('/teacher/<string:username>')
def show_courses_taught(username):
    teacher = Teacher.query.filter_by(username=username).first()
    if teacher:
        courses = teacher.courses
        return jsonify([course.to_dict() for course in courses]), 200
    else:
        return error('Teacher not found')


# Show all students and their grades in a specific course
@app.route('/teacher/<string:username>/<string:course_name>')
def show_students_in_course(username, course_name):
    teacher = Teacher.query.filter_by(username=username).first()
    if teacher:
        course = Course.query.filter_by(course_name=course_name, teacher_id=teacher.id).first()
        if course:
            return jsonify([student.to_dict_grade(course_name) for student in course.students]), 200
        else:
            return error('Course not found')
    else:
        return error('Teacher not found')


# Change grade of student
@app.route('/teacher/<string:username>/<string:course_name>/<string:student_name>/<int:grade>', methods=['PUT'])
def change_student_grade(username, course_name, student_name, grade):
    teacher = Teacher.query.filter_by(username=username).first()
    if teacher:
        student = Student.query.filter_by(legal_name=student_name).first()
        if student:
            course = Course.query.filter_by(course_name=course_name, teacher_id=teacher.id).first()
            if course:
                registration = Registration.query.filter_by(student_id=student.id, course_id=course.id).first()
                if registration:
                    registration.grade = grade
                    db.session.commit()
                    return success('Student grade successfully updated')
                else:
                    return error('Registration not found')
            else:
                return error('Course not found')
        else:
            return error('Student not found')
    else:
        return error('Teacher not found')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables
        app.run(debug=True)
        # db.drop_all()  # Remove this line to avoid dropping your database every time
