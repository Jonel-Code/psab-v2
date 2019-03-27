import os
from flask import Flask, send_file, request, make_response
from flask_restful import Api
# from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit

from general_config import config_name

from instance.config import app_config
from api.rest import StudentLogin, AdminLogin, FacultyAccountCreate, NewCurriculumData, CurriculumData, \
    AddSubjectToCurriculum, StudentCurriculum, OpenSubject, DepartmentListing, DepartmentNew, GetDepartmentCurriculum, \
    BulkSubjectUpload, DeleteCurriculum, UploadStudentData, DeleteStudentData, UploadStudentGrade, EnhancedStudentLogin, \
    OpenSubjectEnhance
# from api.rest.TestData import TestCall

from main_db import db_session


def create_app(env_config):
    __app = Flask(__name__, instance_relative_config=True)
    __app.config.from_object(app_config[env_config])
    __app.config.from_pyfile('config.py')
    return __app, app_config[env_config]


# config_name = 'production'

JRXML_BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + \
                 '\\reports\\jrxml\\'
OUTPUT_BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + \
                  '/reports/output/'
REPORT_RESOURCES = os.path.dirname(os.path.abspath(__file__)) + \
                   '/resources/'
REPORT_EFF_EXPIRATION_DAYS = 30

APP_DIR = os.path.dirname(__file__)

app, config = create_app(config_name)
api = Api(app)
socketio = SocketIO(app)


@socketio.on('connect', namespace='/advising')
def test_connect():
    # need visibility of the global thread object
    print('Client connected to advising')


@socketio.on('new advising form submitted', namespace='/advising')
def test_connect():
    # need visibility of the global thread object
    print('emitting new advising form submitted')


from flask_restful import Resource


class AdvisingDataEmitter(Resource):
    def post(self):
        req_params: list((str, bool)) = [
            ('content', False)
        ]
        print('fired AdvisingDataEmitter')
        from api.rest.quick_parser import quick_parse
        data = quick_parse(req_params).parse_args()
        to_emit = {}
        if not data['content'] == None:
            import json
            to_emit = json.loads(data['content'])
        socketio.emit('new advising form submitted',
                      {'data': to_emit},
                      namespace='/advising')
        # emit('test-emit', 'Change has been made', broadcast=True)
        return {'fired': 'okay'}, 200, {'Access-Control-Allow-Origin': '*'}


class Te(Resource):
    def get(self):
        req_params: list((str, bool)) = [
            ('content', False)
        ]
        from api.rest.quick_parser import quick_parse
        data = quick_parse(req_params).parse_args()
        socketio.emit('my event',
                      {'test': 'okay', 'passed': data['content']},
                      namespace='/advising')
        # emit('test-emit', 'Change has been made', broadcast=True)
        print('fired')
        return {'fired': 'okay'}, 200, {'Access-Control-Allow-Origin': '*'}


# from api.sockets import AdvisingConfigs, advising_socket_emit
#                 socket_rv = {'content': {'removed': rem_s_codes, 'added': s_codes}}
#                 advising_socket_emit(AdvisingConfigs.new_advising_form_submitted, socket_rv)

# db = SQLAlchemy(app)
# db = db_session


@app.teardown_appcontext
def shutdown_session(exception=None):
    # app.run()
    db_session.remove()


@app.route('/get_report_resource')
def get_image():
    try:
        filename = REPORT_RESOURCES + request.args.get('name')
        print('filename', filename)
        print('host', request.url_root)
        if not os.path.isfile(filename):
            return make_response('<h1>404 not found<h1>', 404)
        return send_file(filename, mimetype='image/jpg')
    except Exception:
        return make_response('<h1>Server Error<h1>', 500)


api.add_resource(Te, '/test/emmit')

api.add_resource(EnhancedStudentLogin, '/new-login')

api.add_resource(StudentLogin, '/login')
# api.add_resource(curriculum_tree.CurriculumTree, '/curriculum_tree')

api.add_resource(AdminLogin, '/admin-login')

api.add_resource(FacultyAccountCreate, '/admin-create')

api.add_resource(NewCurriculumData, '/new-curriculum')

api.add_resource(DepartmentListing, '/all-department')

api.add_resource(DepartmentNew, '/new-department')

api.add_resource(CurriculumData, '/curriculum-data')

api.add_resource(AddSubjectToCurriculum, '/curriculum/add-subject')

api.add_resource(BulkSubjectUpload, '/curriculum/add-bulk-subject')

api.add_resource(StudentCurriculum, '/curriculum/get-curriculum')

api.add_resource(DeleteCurriculum, '/curriculum/remove-by-id')

api.add_resource(OpenSubject, '/subjects/opened')

api.add_resource(GetDepartmentCurriculum, '/department-curriculum')

api.add_resource(UploadStudentData, '/student/upload-data')

api.add_resource(DeleteStudentData, '/student/delete-data')

api.add_resource(UploadStudentGrade, '/student/upload-grade')

# api.add_resource(TestCall, '/test')

api.add_resource(OpenSubjectEnhance, '/open-subject-enhance')

from api.rest.admin_controllers import SemDataListing, SemDataRemove, SemDataActivate, SaveAdvisingForm
from api.rest.reports_controller import AdvisingForm

api.add_resource(SemDataListing, '/sem-data-listing')
api.add_resource(SemDataRemove, '/sem-data-remove')
api.add_resource(SemDataActivate, '/sem-data-activate')

api.add_resource(AdvisingForm, '/advising_form')
api.add_resource(SaveAdvisingForm, '/save_advising_data')
# SemDataRemove

from api.rest.advising_controllers import AdvisingStats

api.add_resource(AdvisingStats, '/advising-stats')

api.add_resource(AdvisingDataEmitter, '/socket/advising-stats')

if __name__ == '__main__':
    app.run()
    socketio.run(app)
