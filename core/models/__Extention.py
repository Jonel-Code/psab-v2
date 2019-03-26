from deploy import db


class SavableModel:
    def save(self, do_commit=True):
        from sqlalchemy import exc
        try:
            db.session.add(self)
            if do_commit:
                db.session.commit()
            # db.session.close()
            return self
        except exc.IntegrityError:
            return None

    # if self is db.Model:
    # else:
    #     raise ValueError('Must be inherited to a Model Class')
