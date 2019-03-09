from deploy import db
from core.models.GeneralData import Department
from core.models.Subject import AvailableSubjectEnhance
from core.models.StudentData import StudentData
from core.models.Extension import SavableModel
import enum


class AccountType(enum.Enum):
    Admin = 'Admin'
    Common = 'Common'

    @staticmethod
    def is_account_type_valid(s: str) -> bool:
        return s in [x.value for x in AccountType]


class FacultyAccounts(db.Model, SavableModel):
    __tablename__ = 'facultyAccounts'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    account_name = db.Column(db.String(30), unique=True)
    account_password = db.Column(db.String(64))
    account_type = db.Column(db.Enum(AccountType))

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


class AdvisingData(db.Model, SavableModel):
    __tablename__ = 'advisingData'

    id = db.Column(db.Integer, primary_key=True)
    available_subject_id = db.Column(db.Integer, db.ForeignKey('availableSubjectEnhance.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('studentData.student_id'))

    def __init__(self, available_subject: AvailableSubjectEnhance, student: StudentData):
        self.available_subject_id = available_subject.id
        self.student_id = student.student_id
