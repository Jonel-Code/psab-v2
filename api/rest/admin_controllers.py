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
        c = data[course]
        dept = data[department]

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
            c_data = Curriculum(y, desc, _course)
            c_data.save()
        except Exception as e:
            e_msg = e

        rv = None
        if c_data is not None:
            rv = {
                'message': f'added New Curriculum {c_data.description} for year {c_data.year}',
                'curriculum_id': c_data.id
            }
        return response_checker(c_data, rv, err_msg=e_msg, err_num=500)
