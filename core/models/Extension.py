from deploy import db


class SavableModel:
    def save(self):
        from sqlalchemy import exc
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except exc.IntegrityError:
            return None

    # if self is db.Model:
    # else:
    #     raise ValueError('Must be inherited to a Model Class')
