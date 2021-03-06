from enum import Enum

from deploy import db
from core.models.CurriculumEnums import YearEnum
from core.models.GeneralData import Course
from core.models.Extension import SavableModel

MIN_PASSED_GRADE = 3.0
MAX_PASSED_GRADE = 0.01


def grade_is_passed(grade: float):
    return MIN_PASSED_GRADE >= grade >= MAX_PASSED_GRADE


def nearest_curriculum(student_id: str, course_id: int, year_prefix: str):
    from .Subject import Curriculum
    ys = Curriculum.query.filter_by(course_id=course_id).all()
    if ys is None:
        return None
    y = [int(x.year) for x in ys]
    e = str(student_id)[0:2]
    year_entry = str(year_prefix + e + str(int(e) + 1))
    loe = [x for x in y if x <= int(year_entry)]
    print('year_entry', year_entry)
    print('y', y)
    print('loe', loe)
    cur_year = str(max(loe) if len(loe) > 0 else max(y))
    print('cur_year', cur_year)
    cur = Curriculum.query.filter_by(course_id=course_id, year=str(cur_year)).all()
    latest_cur_id = max([x.id for x in cur])
    return Curriculum.query.filter_by(id=latest_cur_id).first()


class StatusEnum(Enum):
    regular = 'regular'
    irregular = 'irregular'


class StudentData(db.Model, SavableModel):
    __tablename__ = 'studentData'

    student_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(256))
    course_id = db.Column(db.Integer)
    # course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    year = db.Column(db.Enum(YearEnum))

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


class StudentGrades(db.Model, SavableModel):
    __tablename__ = 'studentGrades'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer)
    # student_id = db.Column(db.Integer, db.ForeignKey('studentData.student_id'))
    subject_code = db.Column(db.String(60))
    grade = db.Column(db.Float)

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
