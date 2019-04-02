# from enum import Enum

# from deploy import db
from core.models.CurriculumEnums import YearEnum
from core.models.GeneralData import Course
# from core.models.Extension import SavableModel

from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship, backref
from main_db import Base, SavableModel, db_engine, db_session

MIN_PASSED_GRADE = 3.0
MAX_PASSED_GRADE = 0.01


def grade_is_passed(grade: float):
    return MIN_PASSED_GRADE >= grade >= MAX_PASSED_GRADE


def nearest_curriculum(student_id: str, course_id: int, year_prefix: str):
    from .Subject import Curriculum
    ys = Curriculum.query.filter_by(course_id=course_id).all()
    if ys is None:
        return None

    try:
        _cur = Curriculum.query.filter_by(course_id=course_id).all()
        _latest_cur_id = max([x.id for x in _cur])
        _cur_year = Curriculum.query.filter_by(id=_latest_cur_id).first().year
        _y = [str(x.year).split('-') for x in ys]
        _e = str(student_id)[0:2]
        _year_entry = str(year_prefix + str(_e))
        _curr_nearest: [] = str(_cur_year).split('-')
        _cur_year = None
        _nearest_dist_x = 999
        print('_y', _y)
        print('_year_entry', _year_entry)
        _latest_by_year = None
        for _i in _y:
            _dist_x = abs(int(_year_entry) - int(_i[0]))
            # _dist_y = abs(int(_year_entry) - int(_i[1]))
            if int(_nearest_dist_x) > _dist_x and int(_i[0]) <= int(_year_entry):
                _curr_nearest = _i
                _cur_year = '-'.join([str(z) for z in _curr_nearest])
                _nearest_dist_x = _dist_x
            print('_i', _i)
            print('_dist_x', _dist_x)
            if _latest_by_year is None:
                _latest_by_year = _i
            else:
                if _latest_by_year[0] < _i[0]:
                    _latest_by_year = _i

        if _cur_year is None:
            _cur_year = '-'.join(_latest_by_year)

        # y = [int(x.year) for x in ys]
        # e = str(student_id)[0:2]
        # year_entry = str(year_prefix + e + str(int(e) + 1))
        # loe = [x for x in y if x <= int(year_entry)]
        # print('year_entry', year_entry)
        # print('y', y)
        # print('loe', loe)
        # cur_year = str(max(loe) if len(loe) > 0 else max(y))
        cur_year = _cur_year
        print('cur_year', cur_year)
        cur = Curriculum.query.filter_by(course_id=course_id, year=str(cur_year)).all()
        latest_cur_id = max([x.id for x in cur])
        return Curriculum.query.filter_by(id=latest_cur_id).first()
    except Exception as E:
        print(E)
        return None


class StatusEnum(Enum):
    regular = 'regular'
    irregular = 'irregular'


class StudentData(Base, SavableModel):
    __tablename__ = 'studentData'

    student_id = Column(Integer, primary_key=True)
    full_name = Column(String(256))
    course_id = Column(Integer)
    # course_id = Column(Integer, ForeignKey('course.id'))
    year = Column(Enum(YearEnum))

    def __init__(self,
                 student_id: int,
                 full_name: str,
                 course: Course,
                 year: YearEnum):
        self.student_id = student_id
        self.full_name = full_name.lower()
        self.course_id = course.id
        self.year = year

    @property
    def student_full_name(self):
        return self.full_name.lower()

    @student_full_name.setter
    def student_full_name(self, val: str):
        self.full_name = val.lower()

    @property
    def course(self):
        return Course.query.filter_by(id=self.course_id).first()

    @property
    def curriculum(self):
        prefix = '20'
        return nearest_curriculum(str(self.student_id), self.course_id, prefix)

    @property
    def student_subjects(self) -> [any]:
        if self.curriculum is None:
            return []
        return self.curriculum.subject_list_to_json

    @property
    def grades(self):
        return StudentGrades.query.filter_by(student_id=self.student_id).all()

    @property
    def passed_subjects(self):
        p = []
        for x in self.grades:
            z: StudentGrades = x
            if grade_is_passed(float(z.grade)):
                p.append(str(z.subject_code))
        return p

    def grades_2_list(self):
        return [
            {
                'code': g.subject_code,
                'grade': g.grade
            } for g in self.grades
        ]

    def to_json(self):
        return {
            'id': self.student_id,
            'name': self.full_name,
            'year': self.year.name,
            'course': self.course.title,
            'course_curriculum': self.curriculum.to_json,
            'grades': self.grades_2_list()
        }

    @staticmethod
    def search_student(sid):
        return StudentData.query.filter_by(student_id=int(sid)).first()


class StudentGrades(Base, SavableModel):
    __tablename__ = 'studentGrades'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer)
    # student_id = Column(Integer, ForeignKey('studentData.student_id'))
    subject_code = Column(String(60))
    grade = Column(Float)

    def __init__(self,
                 student_id: int,
                 subject_code: str,
                 grade: float):
        self.student_id = student_id
        self.subject_code = subject_code
        self.grade = grade

    @staticmethod
    def check_grade(sid: int, scode: str):
        return StudentGrades.query.filter_by(student_id=sid, subject_code=scode).first()
