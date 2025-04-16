from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from flask_admin import Admin
from flask_admin.base import MenuLink, expose
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.exceptions import Forbidden
from wtforms.fields import SelectField
import secrets

# Deleted migrate temporarily
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = secrets.token_hex(16)  #generates a 32-character random key
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_screen'

def error(message, status=404):
    return jsonify({'error': message}), status

def success(message, status=200):
    return jsonify({'success': message}), status

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
        print("Fetched teacher:", teacher)
        if teacher:
            self.teacher = teacher
        else:
            self.teacher = None

    def to_dict(self):
        teacher_name = "None"
        if self.teacher is not None:
            teacher_name = self.teacher.legal_name

        return {
            'course_name': self.course_name,
            'time': self.time,
            'teacher_id': self.teacher_id,
            'teacher_name': teacher_name,
            'num_students': len(self.students),
            'max_students': self.max_students
        }


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    legal_name = db.Column(db.String(), nullable=False)
    role = db.Column(db.String(), nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': role
    }

    def to_dict(self):
        return {
            'legal_name': self.legal_name
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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


class Administrator(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    def to_dict(self):
        return {
            'legal_name': self.legal_name
        }


class AdminIndex(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        raise Forbidden()

    @expose('/')
    def index(self):
        return self.render('adminTemplate.html', name=current_user.legal_name)

admin = Admin(app, name='Course Management', template_mode='bootstrap3', index_view=AdminIndex())

class UserModelView(ModelView):
    column_list = ('id', 'username', 'password', 'legal_name', 'role')
    form_columns = ('username', 'password', 'legal_name', 'role')

    form_overrides = {
        'role': SelectField
    }

    form_args = {
        'role': {
            'choices': [
                ('student', 'Student'),
                ('teacher', 'Teacher'),
                ('admin', 'Admin')
            ]
        }
    }

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.password = bcrypt.generate_password_hash(model.password).decode('utf-8')

class CourseModelView(ModelView):
    column_list = ('id', 'course_name', 'teacher_id', 'time', 'max_students')
    form_columns = ('course_name', 'teacher_id', 'time', 'max_students')

    def validate_form(self, form):
        if hasattr(form, 'teacher_id') and form.teacher_id.data:
            teacher = User.query.filter_by(id=form.teacher_id.data, role='teacher').first()
            if not teacher:
                form.teacher_id.errors = ['Invalid teacher ID. Please select a valid teacher.']
                return False
        return super().validate_form(form)

class RegModelView(ModelView):
    column_list = ('student_id', 'course_id', 'grade')
    form_columns = ('student_id', 'course_id', 'grade')

    def validate_form(self, form):
        if hasattr(form, 'student_id') and form.student_id.data:
            student = User.query.filter_by(id=form.student_id.data, role='student').first()
            if not student:
                form.student_id.errors = ['Invalid student ID. Please select a valid student.']
                return False
        if hasattr(form, 'course_id') and form.course_id.data:
            course = Course.query.filter_by(id=form.course_id.data).first()
            if not course:
                form.course_id.errors = ['Invalid course ID. Please select a valid course.']
                return False

        return super().validate_form(form)

# Admin views to create, read, update, and delete
admin.add_view(UserModelView(User, db.session))
admin.add_view(CourseModelView(Course, db.session))
admin.add_view(RegModelView(Registration, db.session))
admin.add_link(MenuLink(name='Logout', category='', url='/logout'))


@app.route('/')
def index():
    return render_template('index.html')

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
            if Administrator.query.filter_by(username=username).first():
                return error("Admin already exists", 400)
            admin = Administrator(username=username, password=password, legal_name=legal_name)
            db.session.add(admin)
            db.session.commit()
            return jsonify(admin.to_dict())
        else:
            return error('Role not found')


# Login (User page routing)
@app.route('/login', methods=['GET', 'POST'])
def login_screen():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password.encode('utf-8'), password):
            login_user(user)
            if user.role == 'admin':
                return redirect('/admin')
            return render_template(f'{user.role}Template.html', name=user.legal_name)

        return error('Invalid username or password', 404)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')

@app.route('/courses')
@login_required
def show_courses():
    courses = Course.query.all()
    return jsonify([course.to_dict() for course in courses]), 200


# ----------------- STUDENT FUNCTIONALITIES ----------------- #

@app.route('/student')
@login_required
def show_courses_registered():
    student = Student.query.get(current_user.id)
    if student:
        courses = student.courses
        return jsonify([{**course.to_dict(), "grade": student.get_grade(course.course_name)} for course in courses]), 200
    else:
        return error('Student not found')


# Add course
@app.route('/student/<string:course_name>', methods=['POST'])
@login_required
def register_course(course_name):
    student = Student.query.get(current_user.id)
    if student:
        course = Course.query.filter_by(course_name=course_name).first()
        if course:
            if course in student.courses:
                return error('Course already registered')
            if len(course.students) == course.max_students:
                return error('Course is full')
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
@app.route('/student/<string:course_name>', methods=['DELETE'])
@login_required
def drop_course(course_name):
    student = Student.query.get(current_user.id)
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
@app.route('/teacher')
@login_required
def show_courses_taught():
    teacher = Teacher.query.get(current_user.id)
    if teacher:
        courses = teacher.courses
        return jsonify([course.to_dict() for course in courses]), 200
    else:
        return error('Teacher not found')


# Show all students and their grades in a specific course
@app.route('/teacher/<string:course_name>')
@login_required
def show_students_in_course(course_name):
    teacher = Teacher.query.get(current_user.id)
    if teacher:
        course = Course.query.filter_by(course_name=course_name, teacher_id=teacher.id).first()
        if course:
            return jsonify([student.to_dict_grade(course_name) for student in course.students]), 200
        else:
            return error('Course not found')
    else:
        return error('Teacher not found')


# Change grade of student
@app.route('/teacher/<string:course_name>/<string:student_name>/<int:grade>', methods=['PUT'])
@login_required
def change_student_grade(course_name, student_name, grade):
    teacher = Teacher.query.get(current_user.id)
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
