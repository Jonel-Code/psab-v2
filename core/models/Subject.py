from deploy import db
from core.models.CurriculumEnums import YearEnum, SemesterEnum
from core.models.GeneralData import Course, Department


class Subject(db.Model):
    __tablename__ = 'subject'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30))
    title = db.Column(db.String(30))
    pre_req = db.Column(db.String(60))
    year = db.Column(db.Enum(YearEnum))
    semester = db.Column(db.Enum(SemesterEnum))

    def __init__(self,
                 code: str,
                 title: str,
                 pre_req: list(),
                 year: YearEnum,
                 semester: SemesterEnum):
        self.code = code
        self.title = title
        self.pre_req = self._pre_req_separator.join(pre_req)
        self.year = year
        self.semester = semester

    @property
    def _pre_req_separator(self):
        return ','

    @property
    def pre_requisite_codes(self) -> [str]:
        return self.pre_req.split(self._pre_req_separator)


class Curriculum(db.Model):
    __tablename__ = 'curriculum'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(30))
    description = db.Column(db.String(30))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    def __init__(self,
                 year: str,
                 description: str,
                 course: Course):
        self.year = year
        self.description = description
        self.course_id = course.id

    @property
    def subject_list(self) -> [Subject]:
        subjects_cur: [CurriculumSubjects] = CurriculumSubjects.query.filter_by(curriculum_id=self.id).all()
        return [Subject.query.filter_by(id=s.subject_id).first() for s in subjects_cur]

    def search_subject(self, subject_code: str) -> Subject:
        x: Subject = None
        for i in self.subject_list:
            if i.code == subject_code:
                x = i
        return x


class CurriculumSubjects(db.Model):
    __tablename__ = 'curriculumSubjects'

    id = db.Column(db.Integer, primary_key=True)
    curriculum_id = db.Column(db.Integer, db.ForeignKey('curriculum.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

    def __init__(self, curriculum: Curriculum, subject: Subject):
        self.curriculum_id = curriculum.id
        self.subject_id = subject.id


class AvailableSubjects(db.Model):
    __tablename__ = 'availableSubjects'

    id = db.Column(db.Integer, primary_key=True)
    sys_year = db.Column(db.Integer)
    semester = db.Column(db.Enum(SemesterEnum))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))

    def __init__(self, sys_year: int, semester: SemesterEnum, subject: Subject, department: Department):
        self.sys_year = sys_year
        self.semester = semester
        self.subject_id = subject.id
        self.department_id = department.id