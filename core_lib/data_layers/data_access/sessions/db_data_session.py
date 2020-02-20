from sqlalchemy.orm import sessionmaker


class DBDataSession(object):

    def __init__(self, engine):
        self.engine = engine

    def __enter__(self):
        self.session = self._session()
        return self.session

    def __exit__(self, type, value, traceback):
        self.session.commit()
        self.session.flush()
        self.session.close()

    def _session(self):
        return sessionmaker(bind=self.engine, expire_on_commit=False)()
