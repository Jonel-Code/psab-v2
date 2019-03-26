# student Login web api

import json
from flask_restful import Resource, reqparse


# from core.dummy_fetch_student_info import get_student_info as dummy_student_info


def get_student_info(u: str, p: str):
    from core.models.StudentData import StudentData
    s: StudentData = StudentData.search_student(u)
    if s is None or s.full_name.lower() != p.lower():
        return None
    return s.to_json()


class EnhancedStudentLogin(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('student_id', help='student id is required', required=True)
        parser.add_argument('password', help='password is required', required=True)
        data = parser.parse_args()

        username = data['student_id']
        password = data['password']

        student_data = get_student_info(username, password)

        return {'content': student_data} if student_data is not None else {
            'message': 'no data found'}, 200 if student_data is not None else 404, {
                   'Access-Control-Allow-Origin': '*'}


class StudentLogin(Resource):
    # def get(self):
    #     parser = reqparse.RequestParser()
    #     parser.add_argument('student_id', help='student id is required', required=True)
    #     parser.add_argument('password', help='password is required', required=True)
    #     data = parser.parse_args()
    #
    #     username = data['student_id']
    #     password = data['password']
    #
    #     # student_data = get_student_info(username, password)
    #     student_data = dummy_student_info(username, password)
    #
    #     return student_data if student_data is not None else {
    #         'message': 'no data found'}, 200 if student_data is not None else 404, {
    #                'Access-Control-Allow-Origin': '*'}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('student_id', help='student id is required', required=True)
        parser.add_argument('password', help='password is required', required=True)
        data = parser.parse_args()

        username = data['student_id']
        password = data['password']

        # student_data = get_student_info(username, password)
        from core.models.StudentData import StudentData
        try:
            student_data = StudentData.query.filter_by(student_id=str(username).strip(),
                                                       full_name=str(password).strip()).first()

            return {'access': 'allow'} if student_data is not None else {
                'access': 'forbidden'}, 200 if student_data is not None else 404, {
                       'Access-Control-Allow-Origin': '*'}
        except Exception as e:
            return {'message', 'server error'}, 404, {'Access-Control-Allow-Origin': '*'}
