if __name__ == '__main__':
    from deploy import db
    from core.models.StudentData import *
    from core.models.Subject import *
    from core.models.GeneralData import *
    from core.models.Faculty import *
    db.create_all()
    exit()
