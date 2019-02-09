from deploy import db
from core.models.Extension import SavableModel


class Department(db.Model, SavableModel):
    __tablename__ = 'department'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    def __init__(self, name: str):
        self.name = name.lower()

    @staticmethod
    def search_dept(name: str):
        return Department.query.filter_by(name=name).first()


class Course(db.Model, SavableModel):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))

    def __init__(self, title: str, department: Department):
        self.title = title.lower()
        self.department_id = department.id

    @staticmethod
    def find_course_title(t: str):
        return Course.query.filter_by(title=t.lower()).first()
