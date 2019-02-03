# admin Login web api

from flask_restful import Resource
from api.rest.quick_parser import quick_parse
from api.rest.extensions.response import response_checker


def check_user(u: str, p: str):
    from core.models.Faculty import FacultyAccounts
    return FacultyAccounts.query.filter_by(account_name=u, account_password=p).first()


def create_faculty_user(u: str, p: str, d: str, a_t):
    from core.models.Faculty import FacultyAccounts
    from core.models.GeneralData import Department
    dept = Department.search_dept(d)
    if dept is None:
        dept = Department(d)
        dept = dept.save()
    acc = FacultyAccounts(u, p, dept, a_t)
    if acc is None:
        return None
    xacc = acc.save()
    return xacc


class AdminLogin(Resource):
    def get(self):
        parser = quick_parse([
            ('faculty_id', True),
            ('password', True)
        ])
        data = parser.parse_args()

        username = data['faculty_id']
        password = data['password']

        from core.models.Faculty import FacultyAccounts
        f_data: FacultyAccounts = check_user(username, password)
        rv = None
        if f_data is not None:
            rv = {
                'account_data': {
                    'id': f_data.id,
                    'name': f_data.account_name,
                    'department': f_data.department,
                    'account_type': f_data.account_type.value
                }
            }

        return response_checker(f_data, rv)


class FacultyAccountCreate(Resource):
    def post(self):
        parser = quick_parse([
            ('faculty_id', True),
            ('password', True),
            ('department', True),
            ('account_type', False),
        ])
        data = parser.parse_args()
        from core.models.Faculty import FacultyAccounts, AccountType

        username = data['faculty_id']
        password = data['password']
        department = data['department']
        a_type = data['account_type']

        a_t = AccountType.Common
        if a_type is not None and AccountType.is_account_type_valid(a_type):
            a_t = AccountType(a_type)

        f_data: FacultyAccounts = create_faculty_user(username, password, department, a_t)
        ret_v = None
        if f_data is not None:
            ret_v = {
                'account_data': {
                    'username': f_data.account_name,
                    'department': f_data.department,
                    'account_type': f_data.account_type.value
                }
            }
        return response_checker(f_data, ret_v, err_msg='Account_name already Exist', err_num=409)
