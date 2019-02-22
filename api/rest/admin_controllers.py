from flask_restful import Resource
from api.rest.quick_parser import quick_parse
from api.rest.extensions.response import response_checker


def get_curriculum(id_v: int):
    from core.models.Subject import Curriculum
    c = Curriculum.search_curriculum(id_v)
    return c


def new_subject(data):
    curriculum_id = 'curriculum_id'
    code = 'code'
    title = 'title'
    pre_req = 'pre_req'
    year = 'year'
    semester = 'semester'
    units = 'units'
    data_keys = data.keys()

    c_id = data[curriculum_id]
    _code = str(data[code]).strip()
    _title = data[title]
    _pre_req = []
    if pre_req in data_keys:
        dz = str(data[pre_req]).strip()
        _pre_req = dz.split(',')
    _year = data[year]
    _semester = data[semester]
    _units = data[units]

    from core.models.Subject import Curriculum, Subject
    from core.models.CurriculumEnums import YearEnum, SemesterEnum
    __year = YearEnum(_year)
    __semester = SemesterEnum(_semester)
    c: Curriculum = get_curriculum(c_id)

    rv = None
    res_code = 409
    if c is not None:
        s: Subject = Subject.check_subject(
            code=_code,
            title=_title,
            pre_req=_pre_req,
            year=__year,
            semester=__semester,
            units=_units,
            create_if_not_exist=True
        )
        ch = c.search_subject(s.code)
        if ch is None:
            c.add_a_subject(s)
            res_code = 200

        rv = {
            'subject_id': s.id,
            'note': 'added new subject' if ch is None else 'Subject already in Curriculum'
        }

    return response_checker(c, rv, res_code=res_code, err_msg='Subject not added', err_num=500)


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
        if len(c) == 0 or len(desc) == 0 or len(y) == 0 or len(dept) == 0:
            return response_checker(None, {}, err_msg='error in request', err_num=501)

        from core.models.Subject import Course, Department
        from core.models.Subject import Curriculum

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

            checker = Curriculum.query.filter_by(year=y, description=desc, course_id=_course.id).first()
            if checker is not None:
                return response_checker(None, {}, err_msg='Curriculum with same year and description detected',
                                        err_num=409)

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
        units = 'units'
        parser = quick_parse([
            (curriculum_id, True),
            (code, True),
            (title, True),
            (pre_req, False),
            (year, True),
            (semester, True),
            (units, True),
        ])
        data = parser.parse_args()

        rv = new_subject(data)
        return rv


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
            return response_checker(None, None, err_msg='not found', err_num=404)
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
        return response_checker(True, rv, err_msg=rv['message'], err_num=500)


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


class BulkSubjectUpload(Resource):
    def post(self):
        curriculum_id = 'curriculum_id'
        content = 'content'
        req_params: list((str, bool)) = [
            (curriculum_id, True),
            (content, True)
        ]
        data = quick_parse(req_params).parse_args()
        import json
        _c = json.loads(data[content])
        _cid = data[curriculum_id]

        from core.models.Subject import Curriculum
        curr = Curriculum.search_curriculum(int(_cid))
        if curr is None:
            return response_checker(True, {'message': 'curriculum id not found'}, res_code=404)

        errors = []
        if isinstance(_c, list):
            for x in _c:
                if isinstance(x, dict):
                    x_keys = x.keys()
                    _2_add = {
                        'curriculum_id': _cid,
                        'code': str(x['code']).replace(' ', ''),
                        'title': x['title'],
                        'year': x['year'],
                        'semester': x['semester'],
                        'units': x['units'],
                    }
                    if 'pre_req' in x_keys:
                        _2_add['pre_req'] = str(x['pre_req']).replace(' ', '')
                    rv, n, a = new_subject(_2_add)
                    if isinstance(n, int):
                        if n != 200:
                            _2_add['error'] = {
                                'code': n,
                                'note': rv['note']
                            }
                            errors.append(_2_add)
        rv = {
            'response': {
                'errors': errors
            }
        }

        return response_checker(True, rv)


class DeleteCurriculum(Resource):
    def post(self):
        curriculum_id = 'curriculum_id'
        req_params: list((str, bool)) = [
            (curriculum_id, True)
        ]
        data = quick_parse(req_params).parse_args()
        cid = data[curriculum_id]
        msg = 'deleted'
        r_num = 200
        from core.models.Subject import Curriculum, CurriculumSubjects, db
        Curriculum.query.filter_by(id=cid).delete()
        CurriculumSubjects.query.filter_by(curriculum_id=cid).delete()
        db.session.commit()
        # try:
        #
        # except Exception as e:
        #     msg = e
        #     r_num = 500
        rv = {'message': msg}
        return response_checker(True, rv, res_code=r_num)


class DeleteStudentData(Resource):
    def post(self):
        student_id = 'student_id'
        req_params: list((str, bool)) = [
            (student_id, True)
        ]
        data = quick_parse(req_params).parse_args()
        sid = data[student_id]
        msg = 'deleted'
        r_num = 200
        try:
            from core.models.StudentData import StudentData, db
            StudentData.query.filter_by(student_id=sid).delete()
            db.session.commit()
        except Exception as e:
            msg = e
            r_num = 500
        rv = {'message': msg}
        return response_checker(True, rv, res_code=r_num)


class UploadStudentData(Resource):
    def post(self):
        content = 'content'
        req_params: list((str, bool)) = [
            (content, True)
        ]
        data = quick_parse(req_params).parse_args()
        import json
        c = json.loads(data[content])
        err_items = []
        uploaded = []
        from core.models.StudentData import StudentData, Course
        from core.models.CurriculumEnums import YearEnum

        def req_ok(r_f):
            for r in r_f:
                if r is None:
                    return False
            return True

        if isinstance(c, list):
            for s in c:
                s_id = s['student_id']
                s_fn = s['full_name']
                s_c = s['course']
                s_y = s['year']
                req_f = [s_id, s_fn, s_c, s_y]
                r_ok = req_ok(req_f)
                err_items.append(s_id)
                if not r_ok:
                    err_items.append(s)
                    continue
                es = StudentData.search_student(s_id)
                if es is None:
                    continue

                z = StudentData.search_student(s_id)
                if z is not None:
                    continue
                _s_c = Course.find_course_title(s_c)
                if _s_c is None:
                    continue

                z: StudentData = StudentData(s_id, s_fn, _s_c, YearEnum(s_y))
                z.save()
                uploaded.append(z.student_id)
                del err_items[-1]
        rv = {'response': {
            'uploaded': uploaded,
            'errors': err_items
        }}
        return response_checker(True, rv, res_code=200)


class UploadStudentGrade(Resource):
    def post(self):
        content = 'content'
        req_params: list((str, bool)) = [
            (content, True)
        ]
        data = quick_parse(req_params).parse_args()
        import json
        c = json.loads(data[content])
        err_items = []
        uploaded = []
        updated = []
        from core.models.StudentData import StudentGrades, db

        def req_ok(r_f):
            for r in r_f:
                if r is None:
                    return False
            return True

        if isinstance(c, list):
            for s in c:
                s_id = int(s['student_id'])
                s_scode = str(s['subject_code']).replace(' ', '')
                s_g = float(s['grade'])
                req_f = [s_id, s_scode, s_g]
                r_ok = req_ok(req_f)
                err_items.append(s_id)
                if not r_ok:
                    err_items.append(s)
                    continue
                sg_c: StudentGrades = StudentGrades.check_grade(s_id, s_g)
                if sg_c is None:
                    z: StudentGrades = StudentGrades(s_id, s_scode, s_g)
                    z.save()
                    uploaded.append(z.student_id)
                    del err_items[-1]
                else:
                    sg_c.grade = s_g
                    updated.append(
                        {'student_id': sg_c.student_id, 'subject_code': sg_c.subject_code, 'grade': sg_c.grade}
                    )
                    del err_items[-1]
                    db.session.commit()

        rv = {'response': {
            'uploaded': uploaded,
            'updated': updated,
            'errors': err_items
        }}
        return response_checker(True, rv, res_code=200)
