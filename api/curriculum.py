import json
from flask_restful import Resource, reqparse

# from core.fetch_student_info import determine_curriculum, get_curriculum_subjects, get_student_info


class JsonCurriculum:

    def __init__(self, curriculum_json: str, curriculum_key: str):
        self.curriculum_json_path = curriculum_json
        self.json_curriculum_key = curriculum_key

    def get_curriculum(self):
        with open(self.curriculum_json_path) as curriculum:
            curriculum_data = json.load(curriculum)
        return curriculum_data[self.json_curriculum_key]

    def retrieve_all_curriculum(self):
        return self.get_curriculum()

    def retrieve_curriculum_year(self, curriculum_year: str):
        return self.get_curriculum()[curriculum_year]


class GetCurriculum(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('student_id', help='student id is required', required=True)
        parser.add_argument('password', help='password is required', required=True)
        data = parser.parse_args()

        taken_subjects = get_student_info(data['student_id'], data['password'])
        # _taken_codes = [taken['code'] for taken in taken_subjects]
        # _curr = determine_curriculum(student_info['id'], student_info['course'])
        # _subjects = get_curriculum_subjects(student_info['course'], _curr)
        # _untaken = [subject for subject in _subjects if subject['code'] not in _taken_codes]

        # print('student_info:', student_info)
        # print('curriculum:', _curr)
        # print('_subjects:', _subjects)
        print('taken_subjects:', taken_subjects)
        # print('_untaken:', _untaken)
        return taken_subjects, 200, {'Access-Control-Allow-Origin': '*'}


class DummyGetCurriculum(Resource):
    def get(self):
        def dummy_student_info():
            with open('resources/dummy_student_info.json') as curricudummy_student_info:
                data = json.load(curricudummy_student_info)
            return data['student_info'], data['subjects_taken']

        student_info, taken_subjects = dummy_student_info()
        _taken_codes = [taken['code'] for taken in taken_subjects]
        _curr = determine_curriculum(student_info['id'], student_info['course'])
        _subjects = get_curriculum_subjects(student_info['course'], _curr)
        _untaken = [subject for subject in _subjects if subject['code'] not in _taken_codes]

        print('student_info:', student_info)
        print('curriculum:', _curr)
        print('_subjects:', _subjects)
        print('taken_subjects:', taken_subjects)
        print('_untaken:', _untaken)
        return {'student_info': student_info,
                'curriculum': _curr,
                'curriculum_subjects': _subjects,
                'taken_subjects': taken_subjects,
                'untaken_subjects': _untaken}, 200, {'Access-Control-Allow-Origin': '*'}
