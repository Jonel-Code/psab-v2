from enum import Enum
import json

from core.algorithms import BUTreeAlgorithm


class EnumToList(Enum):
    @classmethod
    def keys_to_list(cls):
        return list(map(lambda y: y.value, cls))


class YearEnum(EnumToList):
    first = 'first'
    second = 'second'
    third = 'third'
    fourth = 'fourth'


class SemesterEnum(EnumToList):
    first = 'first'
    second = 'second'
    summer = 'summer'


class RemarksEnum(EnumToList):
    passed = 'passed'
    failed = 'failed'


class Subject:
    def __init__(self,
                 code: str = None,
                 title: str = None,
                 total_units: str = None,
                 prerequisite_codes: [str] = None,
                 year: YearEnum = None,
                 semester: SemesterEnum = None):
        self.code: str = code
        self.title: str = title
        self.total_units: str = total_units
        self._prerequisite_codes: [str] = prerequisite_codes
        self._year: YearEnum = year
        self._semester: SemesterEnum = semester

    def to_json(self):
        return {'code': self.code,
                'title': self.title,
                'total_units': self.total_units,
                'pre_req': ','.join(self.prerequisite_codes),
                'year': self.year, 'semester': self.semester}

    def __repr__(self):
        return json.dumps({'code': self.code, 'title': self.title, 'total_units': self.total_units,
                           'pre_req': self.prerequisite_codes, 'year': self.year, 'semester': self.semester})

    @property
    def prerequisite_codes(self):
        return self._prerequisite_codes if self._prerequisite_codes is not None else []

    @prerequisite_codes.setter
    def prerequisite_codes(self, val: [str]):
        self._prerequisite_codes = val

    @property
    def year(self):
        return self._year.name if self._year is not None else YearEnum.first.name

    @year.setter
    def year(self, val: YearEnum):
        self._year = val

    @property
    def semester(self):
        return self._semester.name if self._semester is not None else SemesterEnum.first.name

    @semester.setter
    def semester(self, val: YearEnum):
        self._semester = val

    def check_can_take(self, passed_subject_codes: [str] = None, year_standing: YearEnum = None) -> bool:
        if not self.prerequisite_codes:
            return True
        if self.prerequisite_codes != [] and self.prerequisite_codes[
            0] in YearEnum.keys_to_list() and year_standing is not None:
            year_enum_list = YearEnum.keys_to_list()
            student_year_index = year_enum_list.index(year_standing.name)
            in_lower_years = student_year_index >= year_enum_list.index(self.prerequisite_codes[0])
            print(f'code: {self.code}, in_year_scope: {in_lower_years}')
            # valid_year_preq = YearEnum[self.prerequisite_codes[0]] == YearEnum[year_enum_list[student_year_index]]
            return in_lower_years
        if passed_subject_codes is not None:
            return [z for z in self.prerequisite_codes if z in passed_subject_codes] == self.prerequisite_codes
        return False


class Curriculum:
    def __init__(self,
                 course: str = None,
                 year: str = None,
                 subjects: [Subject] = None):
        self.course: str = course
        self.year: str = year
        self._subjects: [Subject] = subjects

    def to_json(self):
        return {'course': self.course, 'year': self.year, 'subjects': [{"code": i.code,
                                                                        "title": i.title,
                                                                        "total_units": i.total_units,
                                                                        "pre_req": ','.join(i.prerequisite_codes),
                                                                        "year": i.year,
                                                                        "semester": i.semester} for i in self.subjects]}

    def __repr__(self):
        return json.dumps(
            {'course': self.course, 'year': self.year, 'subjects': str(self.subjects)}
        )

    @property
    def subjects(self):
        return self._subjects if self._subjects is not None else []

    @subjects.setter
    def subjects(self, val: [Subject]):
        self._subjects = val

    def prerequisite_to_object(self, subject_code: str):
        subject = self.find_subject(subject_code)
        return [self.find_subject(code) for code
                in subject.prerequisite_codes if
                self.find_subject(code) is not None]

    def find_subject(self, subject_code: str):
        subject: Subject = None
        for item in self.subjects:
            if item.code == subject_code:
                subject = item
        return subject

    def code_to_subject(self, subject_codes: [str]):
        return [self.find_subject(subject_code=i) for i in subject_codes]

    """
        A method that generates a list of subject objects that a student can take
    """

    def subjects_can_take(self, passed_subject_codes: [str], available_subjects: [str],
                          student_current_year: YearEnum = None):
        print('passed_subject_codes', passed_subject_codes)
        print('self.subjects:', self.subjects)
        in_curriculum = [i for i in self.subjects if i.code in available_subjects]
        not_taken = [i for i in in_curriculum if i.code not in passed_subject_codes]
        print('not_taken', not_taken)
        can_take = [i for i in not_taken if i.check_can_take(passed_subject_codes=passed_subject_codes)]
        # can_take = [i for i in not_taken if
        #             [z for z in i.prerequisite_codes if z in passed_subject_codes] == i.prerequisite_codes
        #             or i.prerequisite_codes == []
        #             ]
        can_take_subj_codes = [i.code for i in can_take]

        # determine if a subject with year prerequisite is can take or not
        if student_current_year is not None:
            year_enum_list = YearEnum.keys_to_list()
            # student_year_index = year_enum_list.index(student_current_year.name)
            subs_with_year_preq = [
                i for i in not_taken if i.prerequisite_codes != [] and i.prerequisite_codes[0] in year_enum_list]
            print('subs_with_year_preq', subs_with_year_preq)
            for i in subs_with_year_preq:
                not_in_can_take = i.code not in can_take_subj_codes
                if not_in_can_take and i.check_can_take(year_standing=student_current_year):
                    can_take.append(i)
                # in_lower_years = student_year_index >= year_enum_list.index(i.prerequisite_codes[0])
                # print(f'code: {i.code}, in_lower: {in_lower_years}')
                # valid_year_preq = YearEnum[i.prerequisite_codes[0]] == YearEnum[year_enum_list[student_year_index]]
                # not_in_can_take = i.code not in can_take_subj_codes
                # if not_in_can_take and (valid_year_preq or in_lower_years):
                #     can_take.append(i)

        return can_take

    def get_subjects_on_year(self, year: YearEnum):
        y = YearEnum.keys_to_list()
        year_index = y.index(year.name)
        return [i for i in self.subjects if y.index(i.year) == year_index]

    def get_subjects_on_year_semester(self, year: YearEnum, semester: SemesterEnum, ):
        y = YearEnum.keys_to_list()
        year_index = y.index(year.name)
        s = SemesterEnum.keys_to_list()
        sem_index = s.index(semester.name)
        return [i for i in self.subjects if
                y.index(i.year) == year_index and s.index(i.semester) == sem_index]

    def get_subject_codes_before(self, year: YearEnum, semester: SemesterEnum = None):
        subjects = []
        year_enum_list = YearEnum.keys_to_list()
        year_index = year_enum_list.index(year.name)
        sem_enum_list = SemesterEnum.keys_to_list()
        sem_index = sem_enum_list.index(semester.name)
        for i in range(year_index, -1, -1):
            sb = self.get_subjects_on_year(YearEnum[year_enum_list[i]])
            for x in sb:
                si = sem_enum_list.index(x.semester)
                if i < year_index:
                    subjects.append(x)
                elif i == year_index and si < sem_index:
                    subjects.append(x)
        return subjects

    def new_subjects_can_take(self, passed_subject_codes: [str], student_current_year: YearEnum = None):
        data = []
        for i in self._subjects:
            parent = i.code
            print('using parent:', parent)
            if len(i.prerequisite_codes) > 0:
                for c in i.prerequisite_codes:
                    data.append((parent, c))
            else:
                data.append(('', parent))

        tree = BUTreeAlgorithm(data)
        print('tree.leaf_nodes()', tree.leaf_nodes)
        if student_current_year:
            stud_yr_indx = YearEnum.keys_to_list().index(student_current_year.name)
            year_reqs = [YearEnum.keys_to_list()[i] for i in range(0, stud_yr_indx + 1)]
            for i in year_reqs:
                passed_subject_codes.append(i)
            print('new passed_subject_codes:', passed_subject_codes)
        for i in passed_subject_codes:
            tree.prune_leaf(i)
        return [i for i in tree.leaf_nodes if i not in YearEnum.keys_to_list()]


class SubjectGrade:
    def __init__(self, subject: Subject,
                 grade: float = None):
        self.subject = subject
        self.grade = grade
        self.remark = RemarksEnum.failed if grade is None else (
            RemarksEnum.passed if 0 < grade <= 3 else RemarksEnum.failed)

    def to_json(self):
        return {"code": self.subject.code,
                # "title": self.subject.title,
                # "total_units": self.subject.total_units,
                "grade": self.grade}


class Student:
    def __init__(self, name: str,
                 id: str,
                 course: str,
                 year: str,
                 curriculum: Curriculum,
                 subject_taken: [SubjectGrade]):
        self.name = name
        self.id = id
        self.course = course
        self._year = YearEnum[year]
        self.curriculum: Curriculum = curriculum
        self.subject_taken = subject_taken

    @property
    def year(self):
        return self._year.name

    @year.setter
    def year(self, val: YearEnum):
        self._year = val

    @property
    def curriculum_year(self):
        return self.curriculum.year

    @property
    def passed_subject_codes(self):
        return [i.subject.code for i in self.subject_taken if i.remark is not RemarksEnum.failed]

    @property
    def remaining_subjects(self):
        passed_subject_codes = self.passed_subject_codes
        print('passed_subject_codes ', passed_subject_codes)
        print('curriculum.subjects ', len(self.curriculum.subjects))
        return [i for i in self.curriculum.subjects if i.code not in passed_subject_codes]

    @staticmethod
    def determine_curriculum_year(student_id: str, curriculum_years: [int]):
        entry_year = "20" + str(student_id[0:2]) + str(int(student_id[0:2]) + 1)
        lowest_or_equal = [i for i in curriculum_years if i <= int(entry_year)]
        return str(max(lowest_or_equal)) if len(lowest_or_equal) > 0 else str(max(curriculum_years))


class CurriculumSubjectCode:
    def __init__(self, curriculum_year: str, code: str):
        self.curriculum_year: str = curriculum_year
        self.code = code


class CurriculumEquivalent:
    def __init__(self, title: str, codes: [CurriculumSubjectCode]):
        self.title: str = title
        self.codes: [CurriculumSubjectCode] = codes

    @property
    def get_subject_codes(self):
        return [i.code for i in self.codes]

    @property
    def get_curriculum_years(self):
        return [i.curriculum_year for i in self.codes]

    def in_codes(self, subject_code: str) -> bool:
        return subject_code in self.get_subject_codes

    def equivalent_on_code(self, subject_code: str):
        if subject_code in self.get_subject_codes:
            return [v for i, v in enumerate(self.codes) if i != self.get_subject_codes.index(subject_code)]
        return None

    def equivalent_on_year(self, curriculum_year: str):
        if curriculum_year in self.get_curriculum_years:
            # return [v for i, v in enumerate(self.codes) if i == self.get_curriculum_codes.index(curriculum_year)]
            return [v for v in self.codes if v.curriculum_year == curriculum_year]
        return None


class SetCurriculumEquivalent:
    def __init__(self, curriculum_equivalent_set: [CurriculumEquivalent]):
        self.curriculum_equivalent_set: [CurriculumEquivalent] = curriculum_equivalent_set

    # def search_code(self, code: str):
    #     for i in self.curriculum_equivalent_set:
    #         equivalent_on_code = i.equivalent_on_code(code)
    #


class StatusEnum(Enum):
    regular = 'regular'
    irregular = 'irregular'


class StudentObject(Student):
    def __init__(self, name: str, id: str, course: str, year: str, curriculum: Curriculum,
                 subject_taken: [SubjectGrade]):
        super().__init__(name, id, course, year, curriculum, subject_taken)

    # irregular students are students with back subjects, the rest are regular
    def student_status(self, semester: SemesterEnum = SemesterEnum.first):
        return StatusEnum.regular if len(self.back_subjects(semester)) == 0 else StatusEnum.irregular

    def back_subjects(self, semester: SemesterEnum = SemesterEnum.first):
        subject_under_year = self.curriculum.get_subject_codes_before(YearEnum[self.year], semester)
        sub_codes = [i.code for i in subject_under_year]
        all_passed_codes = [i.subject.code for i in self.subject_taken if i.remark == RemarksEnum.passed]
        missing = list(set(sub_codes).difference(set(all_passed_codes)))
        return [self.curriculum.find_subject(i) for i in missing]

# if __name__ == '__main__':
#     # print(Student.determine_curriculum_year('14118081', [201617, 201314, 201718]))
#     # print(YearEnum.keys_to_list())
#     # test = YearEnum.first
#     # print(test.name)
#     # print(YearEnum['first'])
#     x = [1, 2]
#     y = [1, 3, 4, 2]
#     z = [i for i in x if i in y]
#     print(x)
#     print(y)
#     print(z)
#     print(z == x)
#     cur_year = YearEnum.second
#     year_list = YearEnum.keys_to_list()
#     print(year_list[year_list.index(cur_year.name) + 1])
#
#     import json
#
#
#     def get_curriculum():
#         with open('../resources/curriculum.json') as curriculum:
#             curriculum_data = json.load(curriculum)
#         return curriculum_data['curriculum']
#
#
#     def get_student_info():
#         with open('../resources/dummy_student_info.json') as info:
#             data = json.load(info)
#         return data
#
#
#     # steps for creating new student object
#
#     # 1. load curriculum and student data
#     json_curr = get_curriculum()
#     stud_data = get_student_info()
#
#     # 2. set values on variables
#     student_info = stud_data['student_info']
#     name = student_info['name']
#     id = student_info['id']
#     course = student_info['course'].upper()
#     course_curriculum = json_curr[course]
#     stud_subs_taken = stud_data['subjects_taken']
#
#     # 3. determine list of curriculum years
#     curriculum_years = [int(i) for i in course_curriculum.keys()]
#     print('curriculum_years:', curriculum_years)
#
#     # 4. determine student curriculum year
#     stud_curriculum_year = Student.determine_curriculum_year(id, curriculum_years)
#     print('using stud_curriculum_year:', stud_curriculum_year)
#
#     # 5. fetch curriculum data based on curriculum year that will be used on student
#     # then create set of Subject object under that curriculum year
#     cur = course_curriculum[stud_curriculum_year]
#     cur_subs = [Subject(code=s['code'],
#                         title=s['title'],
#                         total_units=s['total_units'],
#                         prerequisite_codes=[i for i in s['pre_req'].split(',')],
#                         year=YearEnum[s['year']],
#                         semester=SemesterEnum[s['semester']]
#                         ) for s in cur['subjects']]
#
#     # 6. create student curriculum object base on fetched subject data and used data for fetching it
#     stud_cur = Curriculum(course=course,
#                           year=stud_curriculum_year,
#                           subjects=cur_subs)
#
#     # 7. create SubjectGrade objects based on subject codes retrieved from loading student info
#     subs_taken = [SubjectGrade(stud_cur.find_subject(i['code']), grade=float(i['grade'])) for i in stud_subs_taken]
#
#     # 8. create new student objects base on previous results
#     new_student = Student(student_info={'name': name, 'id': id, 'course': course},
#                           curriculum=stud_cur,
#                           subject_taken=subs_taken)
#     print('new_student.remaining_subjects:', len(new_student.remaining_subjects))
