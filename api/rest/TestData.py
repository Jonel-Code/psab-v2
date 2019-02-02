from flask_restful import Resource
from api.rest.quick_parser import quick_parse


class SendTest(Resource):
    def get(self):
        req_params: list((str, bool)) = [
            ('student_id', True)
        ]
        data = quick_parse(req_params).parse_args()
        from core.models.StudentData import StudentData
        ret_val: StudentData = StudentData.query.filter_by(student_id=data['student_id']).first()
        return {'result': f'data available {ret_val.student_id}'}, 200, {'Access-Control-Allow-Origin': '*'}

    def post(self):
        req_params: list((str, bool)) = [
            ('student_id', True),
            ('full_name', True),
            ('course', True),
            ('year', True)
        ]
        data = quick_parse(req_params).parse_args()

        student_id = data['student_id']
        full_name = data['full_name']
        course = data['course']
        year = int(data['year'])

        from core.models.StudentData import StudentData
        from core.models.CurriculumEnums import YearEnum
        from deploy import db
        stud_year = YearEnum.to_list()[year - 1]
        student_data = StudentData(student_id,
                                   full_name,
                                   course,
                                   YearEnum(stud_year))
        db.session.add(student_data)
        db.session.commit()
        added = StudentData.query.filter_by(student_id=student_id).first()

        return {'result': f'data post {added.student_id}'}, 200, {
            'Access-Control-Allow-Origin': '*'}
