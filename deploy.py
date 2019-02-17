from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from instance.config import app_config
from api.rest import StudentLogin, AdminLogin, FacultyAccountCreate, NewCurriculumData, CurriculumData, \
    AddSubjectToCurriculum, StudentCurriculum, OpenSubject, DepartmentListing, DepartmentNew, GetDepartmentCurriculum
from api.rest.TestData import TestCall


def create_app(env_config):
    __app = Flask(__name__, instance_relative_config=True)
    __app.config.from_object(app_config[env_config])
    __app.config.from_pyfile('config.py')
    return __app


config_name = 'development'
# config_name = 'production'

app = create_app(config_name)
api = Api(app)
db = SQLAlchemy(app)

api.add_resource(StudentLogin, '/login')
# api.add_resource(curriculum_tree.CurriculumTree, '/curriculum_tree')
api.add_resource(AdminLogin, '/admin-login')
api.add_resource(FacultyAccountCreate, '/admin-create')
api.add_resource(NewCurriculumData, '/new-curriculum')
api.add_resource(DepartmentListing, '/all-department')
api.add_resource(DepartmentNew, '/new-department')
api.add_resource(CurriculumData, '/curriculum-data')
api.add_resource(AddSubjectToCurriculum, '/curriculum/add-subject')
api.add_resource(StudentCurriculum, '/curriculum/get-curriculum')
api.add_resource(OpenSubject, '/subjects/opened')
api.add_resource(GetDepartmentCurriculum, '/department-curriculum')
api.add_resource(TestCall, '/test')


if __name__ == '__main__':
    app.run()
    # db.create_all()
