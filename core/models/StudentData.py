from deploy import db
from core.models.CurriculumEnums import YearEnum


class StudentData(db.Model):
    __tablename__ = 'studentData'

    student_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(30))
    course = db.Column(db.String(30))
    year = db.Column(db.Enum(YearEnum))

    def __init__(self,
                 student_id: int,
                 full_name: str,
                 course: str,
                 year: YearEnum):
        self.student_id = student_id
        self.full_name = full_name
        self.course = course
        self.year = year


class StudentGrades(db.Model):
    __tablename__ = 'studentGrades'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('studentData.student_id'))
    subject_code = db.Column(db.String(30))
    grade = db.Column(db.Float)

    def __init__(self,
                 student_id: int,
                 subject_code: str,
                 grade: float):
        self.student_id = student_id
        self.subject_code = subject_code
        self.grade = grade
