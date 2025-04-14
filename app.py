# main.py

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite4"
db = SQLAlchemy(app)

courses = db.Table( "courses",
    db.Column("teacher_id", db.Integer, db.ForeignKey("teacher.id")),
    db.Column("student_id", db.Integer, db.ForeignKey("student.id")),
    db.Column("course_name", db.String, nullable=False),
    db.Column("time", db.String, nullable=False),
    db.Column("students_enrolled", db.Integer, nullable=False),
    db.Column("grade", db.Integer, nullable=False),
)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    legal_name = db.Column(db.String(), nullable=False)
    students = db.relationship("Student", secondary=courses, back_populates="teachers")

    def to_dict(self):
        return {
            "legal_name": self.legal_name,
            "teachers": self.teachers,
        }

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    legal_name = db.Column(db.String(), nullable=False)
    teachers = db.relationship("Teacher", secondary=courses, back_populates="students")

    def to_dict(self):
        return {
            "legal_name": self.legal_name,
            "teachers": self.teachers,
        }

@app.route('/')
def index():
    return render_template("index.html")


admin_name = ''
admin_password = ''
@app.route('/create', methods=['GET','POST'])
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
		elif statue == 'admin' and admin_name == '':
			admin_name = username
			admin_password = password
			return jsonify({"success": True})
		else:
			return "404"


@app.route('/<string:username>/<string:password>')
def show_user_page(username, password):
    student = Student.query.filter_by(username=username).first()
    if student and student.password == password:
        return render_template("studentTemplate.html", name=student.legal_name)

    teacher = Teacher.query.filter_by(username=username).first()
    if teacher and teacher.password == password:
        return render_template("teacherTemplate.html", name=teacher.legal_name)

    if username == admin_name and password == admin_password:
        return render_template("adminTemplate.html", name=admin_name)

    return "404"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
        db.drop_all()
