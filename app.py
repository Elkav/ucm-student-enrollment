from flask import Flask, request, render_template, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

enrollments = db.Table('enrollments',
    db.Column("student_id", db.Integer, db.foreignkey('student.id'), primary_key=True),
    db.Column('class_id', db.Integer, db.foreignkey('class.id'), primary_key=True)
)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    class_enrolled = db.relationship()
    def __repr__(self):
        return '<User %r>' % self.username

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    def __repr__(self):
        return '<User %r>' % self.username

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), unique=True, nullable=False)
    teacher = db.Column(db.Integer, db.foreignKey('user.id'))
    time = db.Column(db.String(80))
    students_enrolled = db.relationship()
    max_students = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return '<Class %r>' % self.course_name

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5000)