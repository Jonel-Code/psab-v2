from flask_restful import Resource
from api.rest.quick_parser import quick_parse
from api.rest.extensions.response import response_checker


def get_curriculum(id_v: int):
    from core.models.Subject import Curriculum
    c = Curriculum.search_curriculum(id_v)
    return c


class CurriculumData(Resource):
    def get(self):
        curriculum_id = 'curriculum_id'
        parser = quick_parse([
            (curriculum_id, True)
        ])
        data = parser.parse_args()

        c_id = data[curriculum_id]

        from core.models.Subject import Curriculum
        c: Curriculum = get_curriculum(c_id)

        rv = None
        if c is not None:
            rv = {
                'data_received': c.to_json
            }

        return response_checker(c, rv)


class NewCurriculumData(Resource):
    def post(self):
        year = 'year'
        description = 'description'
        course = 'course'
        department = 'department'
        par = quick_parse([
            (year, True),
            (description, True),
            (course, True),
            (department, True)
        ])
        data = par.parse_args()

        y = data[year]
        desc = data[description]
        c = str(data[course]).lower()
        dept = str(data[department]).lower()

        from core.models.Subject import Course, Department
        from core.models.Subject import Curriculum

        checker = Curriculum.query.filter_by(year=y, description=desc).first()
        if checker is not None:
            return response_checker(None, {}, err_msg='Curriculum with same year and description detected', err_num=401)

        c_data: Curriculum = None
        e_msg = 'Server Error'
        try:
            _department: Department = Department.search_dept(dept)
            if _department is None:
                _department = Department(dept)
                _department.save()
            _course: Course = Course.find_course_title(c)
            if _course is None:
                _course = Course(c, _department)
                _course.save()
            c_data = Curriculum(y, desc, _course)
            c_data.save()
        except Exception as e:
            e_msg = e

        rv = {}
        if c_data is not None:
            rv = {
                'message': f'added New Curriculum {c_data.description} for year {c_data.year}',
                'curriculum_id': c_data.id
            }
        return response_checker(c_data, rv, err_msg=e_msg, err_num=500)


class AddSubjectToCurriculum(Resource):
    def post(self):
        curriculum_id = 'curriculum_id'
        code = 'code'
        title = 'title'
        pre_req = 'pre_req'
        year = 'year'
        semester = 'semester'
        parser = quick_parse([
            (curriculum_id, True),
            (code, True),
            (title, True),
            (pre_req, False),
            (year, True),
            (semester, True),
        ])
        data = parser.parse_args()

        c_id = data[curriculum_id]
        _code = data[code]
        _title = data[title]
        _pre_req = str(data[pre_req]).split(',') if len(data[pre_req]) > 0 is not None else []
        _year = data[year]
        _semester = data[semester]

        from core.models.Subject import Curriculum, Subject
        from core.models.CurriculumEnums import YearEnum, SemesterEnum
        __year = YearEnum(_year)
        __semester = SemesterEnum(_semester)
        c: Curriculum = get_curriculum(c_id)

        rv = None
        if c is not None:
            s: Subject = Subject.check_subject(
                code=_code,
                title=_title,
                pre_req=_pre_req,
                year=__year,
                semester=__semester,
                create_if_not_exist=True
            )
            ch = c.search_subject(s.code)
            if ch is None:
                c.add_a_subject(s)

            rv = {
                'subject_id': s.id,
                'note': 'added new subject' if ch is None else 'Subject already in Curriculum'
            }

        return response_checker(c, rv, err_msg='Subject not added', err_num=500)


class StudentCurriculum(Resource):
    def get(self):
        req_params: list((str, bool)) = [
            ('student_id', True),
            ('course', True)
        ]
        data = quick_parse(req_params).parse_args()

        from core.models.StudentData import Course, nearest_curriculum
        sid = int(data['student_id'])
        c = Course.find_course_title(data['course'])
        prefix = '20'
        rv = {}
        if c is not None:
            cur = nearest_curriculum(str(sid), c.id, prefix)
            rv = cur.subject_list_to_json
            print(cur.subject_list_to_json)
        return {'curriculum': rv}, 200, {'Access-Control-Allow-Origin': '*'}


class OpenSubject(Resource):
    def get(self):
        req_params: list((str, bool)) = [
            ('year', True),
            ('semester', True),
            ('department', True)
        ]
        data = quick_parse(req_params).parse_args()
        from core.models.GeneralData import Department
        from core.models.CurriculumEnums import SemesterEnum
        from core.models.Subject import AvailableSubjects
        d = Department.search_dept(data['department'])
        sem = SemesterEnum(data['semester'])
        y = data['year']
        subs = AvailableSubjects.available_subjects_for_year_sem(y, sem, d)
        return {'available_subjects': subs}, 200, {'Access-Control-Allow-Origin': '*'}

    def post(self):
        req_params: list((str, bool)) = [
            ('department', True),
            ('year', True),
            ('semester', True),
            ('subject_id', True)
        ]
        data = quick_parse(req_params).parse_args()
        sid = int(data['subject_id'])

        from core.models.Subject import Subject

        s: Subject = Subject.query.filter_by(id=sid).first()
        print('is s', s)
        rv = 'error in server'
        if s is not None:
            from core.models.GeneralData import Department
            from core.models.CurriculumEnums import SemesterEnum
            d = Department.search_dept(data['department'])
            sem = SemesterEnum(data['semester'])
            year = data['year']
            added = s.open_subject(sem, year, d)
            if added:
                rv = f'Opened Subject this {year} on {sem.value}'
        return {'message': rv}, 200


class NewSubjectCluster(Resource):
    def get(self):
        req_params: list((str, bool)) = [
            ('name', True)
        ]
        data = quick_parse(req_params).parse_args()

        from core.models.Subject import SubjectClusters

        s: SubjectClusters = SubjectClusters.search_cluster_name(data['name'])
        if s is None:
            return response_checker(None, None, 'not found', 404)
        rv = {'found': s.subjects_under}
        return response_checker(True, rv)

    def post(self):
        req_params: list((str, bool)) = [
            ('name', True)
        ]
        data = quick_parse(req_params).parse_args()
        name = data['name']

        from core.models.Subject import SubjectClusters

        s: SubjectClusters = SubjectClusters.search_cluster_name(name)
        if s is not None:
            return response_checker(None, None, 'duplicate subject cluster name', 404)
        rv = {}

        try:
            ns = SubjectClusters(name=name)
            ns.save()
            rv = {
                'message': f'successfully created subject cluster',
                'id': ns.id,
                'name': ns.name
            }
        except Exception as e:
            rv = {'message': e}
        return response_checker(True, rv, rv['message'], 500)


class GetSubjectEquivalent(Resource):
    def get(self):
        req_params: list((str, bool)) = [
            ('subject_code', True),
            ('curriculum_id', True)
        ]
        data = quick_parse(req_params).parse_args()

        from core.models.Subject import SubjectEquivalents, Curriculum

        cur = Curriculum.search_curriculum(int(data['curriculum_id']))
        code = data['subject_code']
        res = SubjectEquivalents.subj_equiv_in_cur(code, cur)
        rv = {'result': res}
        return response_checker(True, rv)


class GetDepartmentCurriculum(Resource):
    def get(self):
        department = 'department'
        req_params: list((str, bool)) = [
            (department, True)
        ]
        data = quick_parse(req_params).parse_args()

        from core.models.Subject import Curriculum
        from core.models.GeneralData import Department, Course
        d: Department = Department.search_dept(data[department])
        if d is None:
            return response_checker(True, {})
        rv = {'result': []}
        c: [Course] = Course.find_course_under_department(d)
        if len(c) > 0:
            c_titles = [{
                'curriculum_data': [
                    q.to_json_lite for q in Curriculum.curriculum_under_course(z)
                ]
            } for z in c]
            rv['result'] = c_titles

        return response_checker(True, rv)
