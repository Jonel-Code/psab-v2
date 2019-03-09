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
    units = db.Column(db.Integer)

    def __init__(self,
                 code: str,
                 title: str,
                 pre_req: list,
                 year: YearEnum,
                 semester: SemesterEnum,
                 units: int):
        self.units = units
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
        r = []
        if len(self.pre_req) > 0:
            r = self.pre_req.split(self._pre_req_separator)
        return r

    @staticmethod
    def check_subject(code: str,
                      title: str,
                      pre_req: list,
                      year: YearEnum,
                      semester: SemesterEnum,
                      units: int,
                      create_if_not_exist=False):
        sep = ','
        pre_req = sep.join(pre_req) if len(pre_req) > 0 else ''
        s: Subject = Subject.query.filter_by(
            code=code,
            title=title,
            pre_req=pre_req,
            year=year,
            semester=semester,
            units=units
        ).first()
        if s is None and create_if_not_exist:
            pre_req = pre_req.split(sep) if len(pre_req) > 0 else []
            s = Subject(
                code=code,
                title=title,
                pre_req=pre_req,
                year=year,
                semester=semester,
                units=units
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

    @property
    def to_json(self):
        return {
            'subject_id': self.id,
            'subject_code': self.code,
            'title': self.title,
            'pre_req': self.pre_requisite_codes,
            'units': self.units,
            'semester': self.semester.name,
            'year': self.year.name
        }


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

    @staticmethod
    def curriculum_under_course(x: Course):
        return Curriculum.query.filter_by(course_id=x.id).all()

    @property
    def subject_list_to_json(self):
        return [s.to_json for s
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

    @property
    def to_json_lite(self):
        return {
            'curriculum_id': self.id,
            'year': self.year,
            'description': self.description,
            'course': self.course.title
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


class NewSemData(db.Model, SavableModel):
    __tablename__ = 'newSemData'

    id = db.Column(db.Integer, primary_key=True)
    sys_year = db.Column(db.String(50))
    semester = db.Column(db.Enum(SemesterEnum))
    is_current_semester = db.Column(db.Boolean)

    def __init__(self, sys_year: str, semester: SemesterEnum):
        if not NewSemData.new_sem_is_unique(sys_year.strip(), semester):
            raise Exception('duplicate Data Detected')
        l = NewSemData.latest_id()
        self.id = 0 if l is None else l.id + 1
        self.sys_year = sys_year.strip()
        self.semester = semester
        self.use_as_current()

    def use_as_current(self):
        o = NewSemData.query.filter_by().all()
        for x in o:
            if x.id == self.id:
                x.is_current_semester = True
                continue
            x.is_current_semester = False
        db.session.commit()

    @staticmethod
    def get_current_semester():
        l = NewSemData.query.filter_by(is_current_semester=True).first()
        if l is None:
            l = NewSemData.latest_id()
        return l

    @staticmethod
    def latest_id():
        ls = NewSemData.query.order_by(NewSemData.id.desc()).first()
        return ls

    @staticmethod
    def new_sem_is_unique(sys_year: str, sem: SemesterEnum):
        rv = NewSemData.query.filter_by(sys_year=sys_year, semester=sem).first()
        print('rv', rv)
        return rv is None

    def to_json(self):
        s = AvailableSubjectEnhance.query.filter_by(new_sem_id=self.id).all()
        s_l = []
        if s is not None:
            s_l = [{'id': q.id, 'code': q.subject_code} for q in s]
        rv = {
            'year': self.sys_year,
            'semester': self.semester.name,
            'subjects': s_l
        }
        return rv

    def to_json_lite(self):
        rv = {
            'id': self.id,
            'year': self.sys_year,
            'semester': self.semester.value,
            'activated': self.is_current_semester
        }
        return rv

    def delete_sem_data(self):
        s = AvailableSubjectEnhance.query.filter_by(new_sem_id=self.id).all()
        for x in s:
            x.delete_avail_sub()
        NewSemData.query.filter_by(id=self.id).delete()
        db.session.commit()


class AvailableSubjectEnhance(db.Model, SavableModel):
    __tablename__ = 'availableSubjectEnhance'

    id = db.Column(db.Integer, primary_key=True)
    # sys_year = db.Column(db.Integer)
    # semester = db.Column(db.Enum(SemesterEnum))
    new_sem_id = db.Column(db.Integer, db.ForeignKey('newSemData.id'))
    subject_code = db.Column(db.String(50))

    def __init__(self, new_sem_data: NewSemData, subject_code: str):
        if not AvailableSubjectEnhance.is_unique(new_sem_data, subject_code):
            raise Exception('duplicate entry of subject this year and semester')
        self.subject_code = subject_code
        self.new_sem_id = new_sem_data.id

    @property
    def new_sem(self) -> NewSemData:
        return NewSemData.query.filter_by(id=self.new_sem_id).first()

    @property
    def sys_year(self):
        return self.new_sem.sys_year

    @property
    def semester(self):
        return self.new_sem.semester

    @staticmethod
    def is_unique(new_sem_data: NewSemData, subject_code: str):
        z = AvailableSubjectEnhance.query.filter_by(
            new_sem_id=new_sem_data.id,
            subject_code=subject_code
        ).first()
        return z is None

    @staticmethod
    def get_opened_subjects(new_sem_data: NewSemData):
        z = AvailableSubjectEnhance.query.filter_by(
            new_sem_id=new_sem_data.id
        ).all()
        return z

    def to_json(self):
        return {
            'school_year': self.sys_year,
            'semester': self.semester.value,
            'subject_code': self.subject_code
        }

    def delete_avail_sub(self):
        from core.models.Faculty import AdvisingData
        AdvisingData.query.filter_by(available_subject_id=self.id).delete()
        AvailableSubjectEnhance.query.filter_by(id=self.id).delete()
        db.session.commit()

# class AdvisingFormData(db.Model, SavableModel):
#     __tablename__ = 'advisingFormData'
#
#     id = db.Column(db.Integer, primary_key=True)
#     student_id = db.column(db.Integer)
#     avail_subject_id = db.Column(db.Integer, db.ForeignKey('availableSubjectEnhance.id'))
