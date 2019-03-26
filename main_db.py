from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from general_config import general_config

engine = create_engine(general_config.SQLALCHEMY_DATABASE_URI, convert_unicode=True)
db_engine = engine.connect()
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    from core.models.StudentData import StudentData, StudentGrades
    # from core.models.Subject import *
    # from core.models.GeneralData import *
    # from core.models.Faculty import *
    Base.metadata.create_all(bind=engine)


class SavableModel:
    def save(self, do_commit=True):
        from sqlalchemy import exc
        try:
            db_session.add(self)
            if do_commit:
                db_session.commit()
            # db.session.close()
            return self
        except exc.IntegrityError:
            return None
