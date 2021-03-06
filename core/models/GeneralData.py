# from deploy import db
# from core.models.Extension import SavableModel
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship, backref
from main_db import Base, SavableModel, db_engine, db_session


class Department(Base, SavableModel):
    __tablename__ = 'department'

    id = Column(Integer, primary_key=True)
    name = Column(String(256))

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


class Course(Base, SavableModel):
    __tablename__ = 'course'

    id = Column(Integer, primary_key=True)
    title = Column(String(256), unique=True)
    department_id = Column(Integer)
    # department_id = Column(Integer, ForeignKey('department.id'))

    def __init__(self, title: str, department: Department):
        self.title = title.lower()
        self.department_id = department.id

    @staticmethod
    def find_course_title(t: str):
        return Course.query.filter_by(title=t.lower()).first()

    @staticmethod
    def find_course_under_department(x: Department):
        return Course.query.filter_by(department_id=x.id).all()
