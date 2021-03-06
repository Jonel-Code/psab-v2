from main_db import db_session


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

    # if self is db.Model:
    # else:
    #     raise ValueError('Must be inherited to a Model Class')
