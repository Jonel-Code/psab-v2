from flask_restful import Resource
from api.rest.quick_parser import quick_parse
from api.rest.extensions.response import response_checker
from flask import make_response

from pyreportjasper import JasperPy
import tempfile
import json
import os

jasper = JasperPy()

FILE_NAME = 'advising_form'
input_file = ''


def reset_input_file(_dir):
    input_file = _dir


def check_and_create_dir(_dir):
    if not os.path.isdir(_dir):
        os.mkdir(_dir)
    return True


def compiling():
    jasper.compile(input_file)


def processing(parameters, directory, db_conn=None, fname=''):
    print('directory', directory)
    output_file = directory
    if len(fname.strip()) > 0:
        output_file += '/' + fname
    created = check_and_create_dir(output_file)
    if created:
        print('created a dir ' + output_file)
    db_conn = db_conn if db_conn is not None else ''
    print('parameters ', parameters)
    print('input_file ', input_file)
    jasper.process(
        input_file, output_file=output_file, parameters=parameters, format_list=["pdf"], db_connection=db_conn)
    return output_file


def filter_parameters(request_args):
    list_parameters = jasper.list_parameters(input_file)
    parameters = {}
    for key in list_parameters:
        if key in request_args:
            parameters[key] = request_args[key]
    return parameters


class AdvisingForm(Resource):
    def get(self):
        req_params: list((str, bool)) = [
            ('student_id', True),
            ('semester_id', True),
            ('subjects_content', True),
        ]
        from deploy import JRXML_BASE_DIR, OUTPUT_BASE_DIR, app, request, REPORT_EFF_EXPIRATION_DAYS
        from core.models.Subject import NewSemData, SemesterEnum
        from core.models.StudentData import StudentData
        import datetime
        import json
        fname = 'advising_form'
        global input_file
        input_file = JRXML_BASE_DIR + fname + '.jrxml'
        # reset_input_file(_input_file)
        print('input_file', input_file)
        se = SemesterEnum.to_list()

        data = quick_parse(req_params).parse_args()
        sem_data: NewSemData = NewSemData.query.filter_by(id=data['semester_id']).first()
        stud: StudentData = StudentData.query.filter_by(student_id=int(data['student_id'])).first()
        if sem_data is None or stud is None:
            return response_checker(True, {'error': 'data not found'}, res_code=404)
        n = datetime.datetime.now().date() + datetime.timedelta(days=REPORT_EFF_EXPIRATION_DAYS)
        data['api_resource_url'] = request.url_root
        data['effectivity_date'] = str(n.strftime('%B %d %Y'))
        data['academic_year'] = str(sem_data.sys_year)
        data['semester'] = str(se.index(sem_data.semester.value))
        data['student_name'] = str(stud.student_full_name)
        to_add_content = [{}]
        d_cont = json.loads(data['subjects_content'])
        if isinstance(d_cont, list):
            for s in d_cont:
                to_add_content.append({
                    "subject": s['subject'],
                    "units": s['units']
                })

        data_content = {
            "content": to_add_content
        }
        parameters = filter_parameters(data)

        try:
            with tempfile.TemporaryDirectory(dir=OUTPUT_BASE_DIR) as directory:
                tfile = tempfile.NamedTemporaryFile(
                    prefix=data['student_id'],
                    suffix='.json',
                    dir=directory,
                    mode='w',
                    delete=False)

                tfile_name = tfile.name
                print('tfile_name', tfile_name)
                json.dump(data_content, tfile)
                tfile.close()
                json_query = 'content'
                db_connection = {
                    'data_file': tfile_name,
                    'driver': 'json',
                    'json_query': json_query,
                }
                print('db_connection', db_connection)
                out_file_dir = processing(parameters,
                                          directory,
                                          db_conn=db_connection,
                                          fname=data['student_id'])

                out_file_dir += f'/{FILE_NAME}.pdf'
                with app.open_resource(out_file_dir) as f:
                    content = f.read()
                    resposta = make_response(content)
                    resposta.headers['Content-Type'] = 'application/pdf; charset=utf-8'
                    resposta.headers['Access-Control-Allow-Origin'] = '*'
                    # resposta.headers['Content-Disposition'] = 'inline; filename=hello_world_params.pdf'
                    return resposta
        except IOError:
            return response_checker(True, {'error': 'forbidden'}, res_code=403)
