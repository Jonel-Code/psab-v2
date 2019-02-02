# student Login web api

import json
from flask_restful import Resource, reqparse
from core.dummy_fetch_student_info import get_student_info


class StudentLogin(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('student_id', help='student id is required', required=True)
        parser.add_argument('password', help='password is required', required=True)
        data = parser.parse_args()

        username = data['student_id']
        password = data['password']

        student_data = get_student_info(username, password)

        return student_data if student_data is not None else {'message': 'no data found'}, 200 if student_data is not None else 404, {
            'Access-Control-Allow-Origin': '*'}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('student_id', help='student id is required', required=True)
        parser.add_argument('password', help='password is required', required=True)
        data = parser.parse_args()

        username = data['student_id']
        password = data['password']

        student_data = get_student_info(username, password)

        return student_data if student_data is not None else {
            'message': 'no data found'}, 200 if student_data is not None else 404, {
                   'Access-Control-Allow-Origin': '*'}
