from deploy import db
from core.models.Extension import SavableModel


class Department(db.Model, SavableModel):
    __tablename__ = 'department'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))

    def __init__(self, name: str):
        self.name = name.lower()

    @staticmethod
    def search_dept(name: str):
        return Department.query.filter_by(name=name.lower()).first()

    @staticmethod
    def all_department():
        return Department.query.all()

    @property
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Course(db.Model, SavableModel):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), unique=True)
    department_id = db.Column(db.Integer)
    # department_id = db.Column(db.Integer, db.ForeignKey('department.id'))

    def __init__(self, title: str, department: Department):
        self.title = title.lower()
        self.department_id = department.id

    @staticmethod
    def find_course_title(t: str):
        return Course.query.filter_by(title=t.lower()).first()

    @staticmethod
    def find_course_under_department(x: Department):
        return Course.query.filter_by(department_id=x.id).all()
