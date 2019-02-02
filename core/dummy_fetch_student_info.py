import json

from api.objects import Student, Subject, Curriculum, YearEnum, SemesterEnum, SubjectGrade, CurriculumSubjectCode, \
    CurriculumEquivalent, StudentObject, StatusEnum


def get_conversion_equivalent(course_code: str):
    with open('./resources/curriculum_equivalents.json') as av:
        data = json.load(av)
    return data[course_code]


def get_available_subjects():
    with open('./resources/subject_available.json') as av:
        data = json.load(av)
    return data['available_subjects']


def get_available_semester():
    with open('./resources/subject_available.json') as asem:
        data = json.load(asem)
    return data['open_semester']


def get_curriculum():
    with open('./resources/curriculum.json') as curriculum:
        curriculum_data = json.load(curriculum)
    return curriculum_data['curriculum']


def json_get_student_info():
    with open('./resources/dummy_student_info.json') as info:
        data = json.load(info)
    return data


# def json_get_student_info(info_json):
#     return json.load(info)


def get_student_info(username: str, password: str, incoming_semester='first', incoming_year='first'):
    # 1. load curriculum and student data
    json_curr = get_curriculum()
    stud_data = json_get_student_info()
    av_subs: [] = get_available_subjects()
    open_semester = get_available_semester()
    print('av_subs', av_subs)

    student_info = stud_data['student_info']
    name = student_info['name']
    id = student_info['id']
    student_year = student_info['year']
    course = student_info['course'].upper()
    course_curriculum = json_curr[course]
    stud_subs_taken = stud_data['subjects_taken']
    print('stud_subs_taken', stud_subs_taken)

    if not student_info or username != id or password != name:
        return None

    curriculum_years = [int(i) for i in course_curriculum.keys()]
    print('curriculum_years:', curriculum_years)

    # 1.1 create a curriculum equivalent object to handle curriculum equivalents
    equivalent_curriculum = get_conversion_equivalent(course)
    print('equivalent_curriculum:', equivalent_curriculum)
    cur_equivalent: [CurriculumEquivalent] = []
    for i in equivalent_curriculum:
        title = i['title']
        codes = i['codes']
        codes_obj = [CurriculumSubjectCode(curriculum_year=key, code=codes[key]) for key in codes.keys()]
        cur_equivalent.append(CurriculumEquivalent(title=title, codes=codes_obj))

    print('cur_equivalent', [i.title for i in cur_equivalent])

    # 2. determine student curriculum year
    stud_curriculum_year = Student.determine_curriculum_year(id, curriculum_years)
    print('using stud_curriculum_year:', stud_curriculum_year)

    # 3. fetch curriculum data based on curriculum year that will be used on student
    # then create set of Subject object under that curriculum year
    cur = course_curriculum[stud_curriculum_year]
    cur_subs = [Subject(code=s['code'],
                        title=s['title'],
                        total_units=s['total_units'],
                        prerequisite_codes=None if len(s['pre_req']) == 0 else [i for i in s[
                            'pre_req'].split(',')],
                        year=YearEnum[s['year']],
                        semester=SemesterEnum[s['semester']]
                        ) for s in cur['subjects']]

    # 4. create student curriculum object base on fetched subject data and used data for fetching it
    stud_cur: Curriculum = Curriculum(course=course,
                                      year=stud_curriculum_year,
                                      subjects=cur_subs)

    # 4.1 get subject codes for curriculum and change taken subject's code to match up with student curriculum
    raw_subs_taken_code = [i['code'] for i in stud_subs_taken]
    cur_subs_codes = [i.code for i in stud_cur.subjects]
    problem_subject_codes = list(set(raw_subs_taken_code).difference(cur_subs_codes))
    print('not in curriculum:', problem_subject_codes)

    # 4.2 convert all available subjects into set of new available subjects matching the student curriculum
    for i in cur_equivalent:
        print('using i.get_subject_codes:', i.get_subject_codes)
        for x in i.get_subject_codes:
            if x in av_subs:
                z = i.equivalent_on_year(stud_curriculum_year)
                print('with z value:', [q.code for q in z])
                if z:
                    print(f'found!: {z[0].code}, confict of: {x}')
                    indx = av_subs.index(x)
                    av_subs[indx] = z[0].code

    print('new av_subs:', av_subs)
    # get equivalent subject code for irregular students
    # 4.3 find equivalent of subjects not under the student curriculum
    for i in problem_subject_codes:
        problem_index = raw_subs_taken_code.index(i)
        grade = stud_subs_taken[problem_index]['grade']
        old_subj_code = stud_subs_taken[problem_index]['code']
        new_subj_code = ''
        for x in cur_equivalent:
            if x.equivalent_on_code(i):
                for z in x.equivalent_on_code(i):
                    if z.curriculum_year == stud_curriculum_year:
                        new_subj_code = z.code
                        break
        stud_subs_taken[problem_index] = {'grade': grade,
                                          'title': stud_subs_taken[problem_index]['title'],
                                          'total_units': stud_subs_taken[problem_index]['total_units'],
                                          'code': new_subj_code if len(new_subj_code) > 0 else old_subj_code}

    # 5. create SubjectGrade objects based on subject codes retrieved from loading student info
    subs_taken = []
    for i in stud_subs_taken:
        s_subject = stud_cur.find_subject(i['code'])
        if not s_subject:
            print('i_code problem:', i['code'])
            s_subject = Subject(code=i['code'], title=i['title'], total_units=i['total_units'])
        s_grade = float(i['grade'])
        subs_taken.append(SubjectGrade(s_subject, grade=s_grade))
    # subs_taken = [ for i in stud_subs_taken]

    # print('subs_taken,', [i.subject.code for i in subs_taken])

    # 6. create new student objects base on previous results
    for i in subs_taken:
        if i is not None:
            print('subs_taken', i)

    new_student = StudentObject(name=name,
                                id=id,
                                course=course,
                                year=student_year,
                                curriculum=stud_cur,
                                subject_taken=subs_taken if subs_taken else [])

    passed_subjects = new_student.passed_subject_codes
    print('passed_subjects', passed_subjects)
    new_can_take = new_student.curriculum.new_subjects_can_take(passed_subjects, YearEnum[new_student.year])
    print('new_can_take', new_can_take)

    can_take = new_student.curriculum.subjects_can_take(passed_subjects,
                                                        available_subjects=av_subs,
                                                        student_current_year=YearEnum[student_year])

    test_semester = SemesterEnum[open_semester]
    stud_status = new_student.student_status(semester=test_semester)
    back_subjects = new_student.back_subjects(semester=test_semester)

    # determine the subjects that a student can take if he's a regular or irregular student
    can_take_codes = [i.code for i in can_take]
    yearEnum_list = YearEnum.keys_to_list()
    y_index = yearEnum_list.index(new_student.year)
    if stud_status == StatusEnum.regular:
        print('stud_Status', stud_status)
        new_student_year = y_index + 1 if test_semester == SemesterEnum.first and y_index >= 1 else y_index
        reg_subj = new_student.curriculum.get_subjects_on_year_semester(YearEnum[yearEnum_list[new_student_year]],
                                                                        test_semester)
        print('reg_subj', reg_subj)
        can_take_codes = [i.code for i in reg_subj]

    student_curriculum_json = new_student.curriculum.to_json()

    subject_edges = []
    subject_nodes = []
    for i in new_student.curriculum.subjects:
        subject_nodes.append({'id': i.code, 'label': i.code, 'title': i.title})
        for x in i.prerequisite_codes:
            subject_edges.append({'parent': i.code, 'child': x})

    student_curriculum_json['paths'] = {'edges': subject_edges, 'nodes': subject_nodes}

    # yb = new_student.curriculum.get_subject_codes_before(year=YearEnum.second, semester=SemesterEnum.first)
    # print('yb', [i.title for i in yb])
    # test_student = StudentObject(name=name,
    #                              id=id,
    #                              course=course,
    #                              year=student_year,
    #                              curriculum=stud_cur,
    #                              subject_taken=subs_taken)
    # stud_status = test_student.student_status(semester=test_semester)
    # print(f'test_student status: {stud_status.name} as of year: {test_student.year}, semester: {test_semester.name}')

    # dummy login
    return {"name": new_student.name, "id": new_student.id, "course": new_student.course, "year": student_year,
            "status": stud_status.name, "incoming_semester": test_semester.name,
            "course_curriculum": student_curriculum_json,
            "subjects_taken": [i.to_json() for i in new_student.subject_taken],
            # 'can_take': [i.to_json() for i in can_take],
            'can_take': can_take_codes,
            # "back_subjects": [i.to_json() for i in back_subjects]
            "back_subjects": [i.code for i in back_subjects]
            }
