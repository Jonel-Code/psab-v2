# from deploy import db
from core.models.GeneralData import Department
from core.models.Subject import AvailableSubjectEnhance
from core.models.StudentData import StudentData
# from core.models.Extension import SavableModel
import enum

from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship, backref
from main_db import Base, SavableModel, db_engine, db_session


class AccountType(enum.Enum):
    Admin = 'Admin'
    Common = 'Common'

    @staticmethod
    def is_account_type_valid(s: str) -> bool:
        return s in [x.value for x in AccountType]


class FacultyAccounts(Base, SavableModel):
    __tablename__ = 'facultyAccounts'

    id = Column(Integer, primary_key=True)
    department_id = Column(Integer)
    # department_id = Column(Integer, ForeignKey('department.id'))
    account_name = Column(String(256), unique=True)
    account_password = Column(String(256))
    account_type = Column(Enum(AccountType))

    def __init__(self,
                 account_name: str,
                 account_password: str,
                 department: Department,
                 account_type: AccountType):
        self.account_name = account_name
        self.account_password = account_password
        self.department_id = department.id
        self.account_type = account_type

    @property
    def department(self) -> str:
        d: Department = Department.query.filter_by(id=self.department_id).first()
        return d.name


class AdvisingData(Base, SavableModel):
    __tablename__ = 'advisingData'

    id = Column(Integer, primary_key=True)
    available_subject_id = Column(Integer)
    # available_subject_id = Column(Integer, ForeignKey('availableSubjectEnhance.id'))
    student_id = Column(Integer)
    # student_id = Column(Integer, ForeignKey('studentData.student_id'))

    def __init__(self, available_subject: AvailableSubjectEnhance, student: StudentData):
        self.available_subject_id = available_subject.id
        self.student_id = student.student_id
