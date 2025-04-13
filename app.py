from flask import Flask, request, render_template, abort
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_admin import Admin
from flask_admin.base import MenuLink
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# association table for many-to-many relationship between students and classes
enrollments = db.Table('enrollments',
    db.Column("student_id", db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('class.id'), primary_key=True)
)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), unique=True, nullable=False)
    time = db.Column(db.String(80))
    max_students = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    # many-to-many relationship (one student has many classes, one class has many students)
    students = db.relationship('Student', secondary=enrollments, backref=db.backref('classes'), lazy='dynamic')

    # secondary=enrollments allows enrollments to be used as a bridge between Class and Students
    # allowing the many-to-many relationship between them

    # backref generates an equivalent column in Student which allows Student.classes to be called
    # to retrieve the list of classes a student is taking
    # (so it is not necessary to copy this line of code over to Student to complete the many-to-many relationship)

    # lazy=dynamic means that the relationship attribute doesn't immediately load the objects,
    # it 

    def __repr__(self):
        return '<Class %r>' % self.course_name


# create a base User model as a parent for Student/Teacher/Admin
# (not sure yet if we need all 3 subclasses, but they're here for now)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    # a column for the user's role (deb)
    role = db.Column(db.String(50))

    # type is a discriminator, set per-subclass based on that class's polymorphic identity
    type = db.Column(db.String(32), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity':'user',   # this base User class has a polymorphic identity of 'user'
        'polymorphic_on':type           # the polymorphic_identity value is stored in type
    }

    # a password checker (deb)
    #This method is checking if a given password matches the password stored in the User object.
    def check_password(self, password): # self.password is the password that is stored in the database for that specific user
        return self.password == password
    
    def __repr__(self):
        return '<User %r>' % self.username


class Student(User): # subclass of User
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity':'student',
    }
    def __repr__(self):
        return '<Student %r>' % self.username

class Teacher(User): # subclass of User
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    # one-to-many relationship (one teacher has many classes)
    classes = db.relationship('Class', backref=db.backref('teacher'), lazy=True)
    __mapper_args__ = {
        'polymorphic_identity':'teacher',
    }
    def __repr__(self):
        return '<Teacher %r>' % self.username

class Admin(User): # subclass of User
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity':'admin',
    }
    def __repr__(self):
        return '<Admin %r>' % self.username

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')


# attempt at putting in create function from issues
admin_name = ''
admin_password = ''
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template("create.html")
    
    data = request
    username = data["username"]
    password = data["password"]
    statue = data["statue"]
    if statue == 'student':
        if Student.query.filter_by(username=username).first():
            return '400'
        student = Student(username=username, password=password)
        db.session.add(student)
        db.session.commit()
        return student.to_dict()
    elif statue == 'teacher':
        if Teacher.query.filter_by(username=username).first():
            return '400'
        teacher = Teacher(username=username, password=password)
        db.session.add(teacher)
        db.session.commit()
        return teacher.to_dict()
    elif statue == 'admin' and admin_name == '':
        admin_name = username
        admin_password = password
        return True
    else:
        return '404'

if __name__ == '__main__':
    app.run(port=5000)