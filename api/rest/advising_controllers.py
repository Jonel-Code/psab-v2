from flask_restful import Resource
from api.rest.extensions.response import response_checker


class AdvisingStats(Resource):
    def get(self):
        r_num = 200
        ad: list = []
        students: list = []
        try:
            from core.models.Subject import NewSemData
            from core.models.Faculty import AdvisingData
            curr_sem: NewSemData = NewSemData.get_current_semester()
            if curr_sem is None:
                return response_checker(None, {}, err_msg='No Semester selected', err_num=404)
            print('cs_json', curr_sem)
            cs_json = curr_sem.to_json()
            count = 0
            print('cs_json', cs_json)
            for x in cs_json['subjects']:
                cn: [AdvisingData] = AdvisingData.query.filter_by(available_subject_id=x['id']).all()
                ad.append({
                    'code': x['code'],
                    'student_count': len(cn)
                })
                count += len(cn)
                for s in cn:
                    if s.student_id not in students:
                        students.append(int(s.student_id))
            print('students', students)
        except Exception as e:
            r_num = 500
        rv = {'statistics': ad, 'student_this_sem_count': len(students)}
        return response_checker(True, rv, res_code=r_num)
