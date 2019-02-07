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
        print('_pre_req', _pre_req)
        print('len(_pre_req)', len(_pre_req))
        print('data[pre_req]', data[pre_req])
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
