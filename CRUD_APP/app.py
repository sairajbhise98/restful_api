from flask import Flask
from flask_restful import Resource, Api, fields, reqparse, abort, marshal_with
from flask_sqlalchemy import SQLAlchemy

# App
app = Flask(__name__)
api = Api(app)

# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:root@localhost/school'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Database Table
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    course = db.Column(db.String(20))


# Configuration of parser
student_post_args = reqparse.RequestParser()
student_put_args = reqparse.RequestParser()

# Post Request args
student_post_args.add_argument('first_name', type=str, help="first name is required..", required=True)
student_post_args.add_argument('last_name', type=str, help="last name is required..", required=True)
student_post_args.add_argument('course', type=str, help="course is required..", required=True)

# Put request args
student_put_args.add_argument('first_name', type=str)
student_put_args.add_argument('last_name', type=str)
student_put_args.add_argument('course', type=str)

# fields
resource_fields = {
    'id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'course': fields.String
}


class AddStudent(Resource):
    @marshal_with(resource_fields)
    def get(self, stud_id):
        stud = Student.query.filter_by(id=stud_id).first()
        if not stud:
            abort(404, "Student not found..")
        return stud

    @marshal_with(resource_fields)
    def post(self, stud_id):
        args = student_post_args.parse_args()
        stud = Student.query.filter_by(id=stud_id).first()
        if stud:
            abort(409, "Student id is taken..")
        entry = Student(first_name=args['first_name'], last_name=args["last_name"], course=['course'])
        db.session.add(entry)
        db.session.commit()
        return entry, 201

    @marshal_with(resource_fields)
    def delete(self, stud_id):
        stud = Student.query.filter_by(id=stud_id).first()
        if not stud:
            abort(404, "Student with given id not found..")
        db.session.delete(stud)
        db.session.commit()
        return stud

    @marshal_with(resource_fields)
    def put(self, stud_id):
        args = student_put_args.parse_args()
        stud = Student.query.filter_by(id=stud_id).first()
        if not stud:
            abort(404, "No student with given id..")
        if args['first_name']:
            stud.first_name = args['first_name']
        if args['last_name']:
            stud.last_name = args['last_name']
        if args['course']:
            stud.course = args['course']
        db.session.commit()
        return stud


class StudentList(Resource):
    def get(self):
        all_student = Student.query.all()
        students = {}
        for stud in all_student:
            students[stud.id] = {'first_name': stud.first_name, 'last_name': stud.last_name, 'course': stud.course}
        return students


# Configuration of URI
api.add_resource(AddStudent, '/student/<int:stud_id>')
api.add_resource(StudentList, '/students')

if __name__ == "__main__":
    app.run(debug=True)
