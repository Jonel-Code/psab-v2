from deploy import db
from core.models.CurriculumEnums import YearEnum, SemesterEnum
from core.models.GeneralData import Course, Department
from core.models.Extension import SavableModel


class Subject(db.Model, SavableModel):
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
                 pre_req: list,
                 year: YearEnum,
                 semester: SemesterEnum):
        self.code = code
        self.title = title
        if len(pre_req) > 0:
            self.pre_req = self._pre_req_separator.join(pre_req)
        else:
            self.pre_req = ''
        self.year = year
        self.semester = semester

    @property
    def _pre_req_separator(self):
        return ','

    @property
    def pre_requisite_codes(self) -> [str]:
        return self.pre_req.split(self._pre_req_separator)

    @staticmethod
    def check_subject(code: str,
                      title: str,
                      pre_req: list,
                      year: YearEnum,
                      semester: SemesterEnum,
                      create_if_not_exist=False):
        sep = ','
        pre_req = sep.join(pre_req) if len(pre_req) > 0 else ''
        s: Subject = Subject.query.filter_by(
            code=code,
            title=title,
            pre_req=pre_req,
            year=year,
            semester=semester
        ).first()
        if s is None and create_if_not_exist:
            pre_req = pre_req.split(sep) if len(pre_req) > 0 else []
            s = Subject(
                code=code,
                title=title,
                pre_req=pre_req,
                year=year,
                semester=semester
            )
            s.save()
        return s

    def open_subject(self, sem: SemesterEnum, year: int, dept: Department):
        try:
            if not self.is_open_this_year_sem(sem, year, dept):
                a = AvailableSubjects(year, sem, self, dept)
                a.save()
        except Exception as e:
            print(e)
            return False
        return True

    def is_open_this_year_sem(self, sem: SemesterEnum, year: int, dept: Department):
        a = AvailableSubjects.query.filter_by(
            sys_year=year,
            semester=sem,
            subject_id=self.id,
            department_id=dept.id
        ).first()
        return a is not None


class Curriculum(db.Model, SavableModel):
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
        return [s.subject for s in subjects_cur]

    def search_subject(self, subject_code: str) -> Subject:
        x: Subject = None
        for i in self.subject_list:
            if i.code == subject_code:
                x = i
        return x

    def add_a_subject(self, subj: Subject):
        ns = CurriculumSubjects(curriculum=self, subject=subj)
        ns.save()

    def add_subjects(self, s_arr: [Subject]):
        for a in s_arr:
            self.add_a_subject(a)

    def remove_a_subject(self, subj: Subject):
        c_id = self.id
        s_id = subj.id
        CurriculumSubjects.query.filter_by(curriculum_id=c_id, subject_id=s_id).delete()
        db.session.commit()

    @staticmethod
    def search_curriculum(id_value: int):
        return Curriculum.query.filter_by(id=id_value).first()

    @property
    def subject_list_to_json(self):
        return [{'subject_id': s.id, 'subject_code': s.code, 'title': s.title, 'pre_req': s.pre_requisite_codes} for s
                in self.subject_list]

    @property
    def course(self) -> Course:
        return Course.query.filter_by(id=self.course_id).first()

    @property
    def to_json(self):
        return {
            'curriculum_id': self.id,
            'year': self.year,
            'description': self.description,
            'course': self.course.title,
            'subjects': self.subject_list_to_json
        }


class CurriculumSubjects(db.Model, SavableModel):
    __tablename__ = 'curriculumSubjects'

    id = db.Column(db.Integer, primary_key=True)
    curriculum_id = db.Column(db.Integer, db.ForeignKey('curriculum.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

    def __init__(self, curriculum: Curriculum, subject: Subject):
        self.curriculum_id = curriculum.id
        self.subject_id = subject.id

    @property
    def subject(self) -> Subject:
        return Subject.query.filter_by(id=self.subject_id).first()

    @staticmethod
    def remove_curriculum_subject(cur_subj: any):
        if cur_subj is CurriculumSubjects:
            try:
                CurriculumSubjects.query.filter_by(id=cur_subj.id).delete()
            except Exception as e:
                print('error:', e)
        db.session.commit()


class AvailableSubjects(db.Model, SavableModel):
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

    @property
    def subject(self):
        return Subject.query.filter_by(id=self.subject_id).first()

    @staticmethod
    def available_subjects_for_year_sem(year: int, sem: SemesterEnum, dept: Department):
        subj = AvailableSubjects.query.filter_by(
            sys_year=year,
            semester=sem,
            department_id=dept.id
        ).all()
        return [x.subject.code for x in subj]


class SubjectClusters(db.Model, SavableModel):
    __tablename__ = 'subjectClusters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90), unique=True)

    def __init__(self, name: str):
        self.name = name.lower()

    @property
    def subjects_under(self) -> [str]:
        s = SubjectEquivalents.query.filter_by(cluster_id=self.id).all()
        if len(s) == 0:
            return []
        return [x.subject_code for x in s]

    @staticmethod
    def search_cluster_name(n: str):
        return SubjectClusters.query.filter_by(name=n.lower()).first()


class SubjectEquivalents(db.Model, SavableModel):
    __tablename__ = 'subjectEquivalents'

    id = db.Column(db.Integer, primary_key=True)
    cluster_id = db.Column(db.Integer, db.ForeignKey('subjectClusters.id'))
    subject_code = db.Column(db.String(50))

    def __init__(self, cluster: SubjectClusters, subject_code: str):
        self.cluster_id = cluster.id
        self.subject_id = subject_code

    @property
    def subject_cluster(self):
        return SubjectClusters.query.filter_by(id=self.cluster_id).first()

    @staticmethod
    def search_subject_code(s_code: str) -> [str]:
        s: [SubjectEquivalents] = SubjectEquivalents.query.filter_by(subject_code=s_code).all()
        cid = []
        subject_codes = []
        if s is not None:
            for x in s:
                if x.cluster_id not in cid:
                    cid.append(x.cluster_id)
            for x in cid:
                subjects: [SubjectEquivalents] = SubjectEquivalents.query.filter_by(cluster_id=x).all()
                for z in subjects:
                    if z.subject_code not in subject_codes:
                        subject_codes.append(z.subject_code)
        return subject_codes

    @staticmethod
    def subj_equiv_in_cur(s_code: str, curriculum: Curriculum) -> [str]:
        c_subj = [x.code for x in curriculum.subject_list]
        equiv_subj = SubjectEquivalents.search_subject_code(s_code)
        res = []
        for x in equiv_subj:
            if x in c_subj and x not in res:
                res.append(x)
        return res
