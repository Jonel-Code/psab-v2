# app.py


# import json
# from api.curriculum import DummyGetCurriculum
# from core.fetch_student_info import determine_curriculum, get_curriculum_subjects

from flask import Flask, render_template
from flask_restful import Api

from instance.config import app_config
from api.rest import student_login, curriculum_tree


def create_app(env_config):
    __app = Flask(__name__, instance_relative_config=True)
    __app.config.from_object(app_config[env_config])
    __app.config.from_pyfile('config.py')
    return __app


config_name = 'development'

app = create_app(config_name)
api = Api(app)

api.add_resource(student_login.StudentLogin, '/login')
api.add_resource(curriculum_tree.CurriculumTree, '/curriculum_tree')

# api.add_resource(DummyGetCurriculum, '/dummy')
#
# def get_curriculum():
#     with open('resources/curriculum.json') as curriculum:
#         curriculum_data = json.load(curriculum)
#     return curriculum_data['curriculum']
#
#
# BSCS_curriculum = get_curriculum()['BSCS']
# BSIT_curriculum = get_curriculum()['BSIT']
# ACT_curriculum = get_curriculum()['ACT']

if __name__ == '__main__':
    app.run()
    # print(BSCS_curriculum)
    # print(BSIT_curriculum)
    # print(ACT_curriculum)
    # print('hello world!')
    #
    #
    # def dummy_student_info():
    #     with open('resources/dummy_student_info.json') as curricudummy_student_info:
    #         data = json.load(curricudummy_student_info)
    #     return data['student_info'], data['subjects_taken']
    #
    #
    # student_info, taken_subjects = dummy_student_info()
    # _taken_codes = [taken['code'] for taken in taken_subjects]
    # _curr = determine_curriculum(student_info['id'], student_info['course'])
    # _subjects = get_curriculum_subjects(student_info['course'], _curr)
    # _untaken = [subject for subject in _subjects if subject['code'] not in _taken_codes]
    #
    # print('student_info:', student_info)
    # print('curriculum:', _curr)
    # print('_subjects:', _subjects)
    # print('taken_subjects:', taken_subjects)
    # print('_untaken:', _untaken)
