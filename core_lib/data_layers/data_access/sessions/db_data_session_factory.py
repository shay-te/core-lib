from core_lib.data_layers.data_access.sessions.db_data_session import DBDataSession
from core_lib.factory.factory import Factory
from core_lib.helpers.instance_under_stack import InstanceUnderStack


class DBDataSessionFactory(Factory):

    def __init__(self, engine):
        self.engine = engine
        self.instance_under_path = InstanceUnderStack()
        self.session_to_count = {}

    def get(self, use_parent_instance=True, *args, **kwargs):
        if use_parent_instance:
            db_session = self.instance_under_path.get()
            if db_session:
                db_session_count = self.session_to_count[db_session]
                self.session_to_count[db_session] = db_session_count + 1
            else:
                db_session = DBDataSession(self.engine, use_parent_instance, self._on_db_session_exit)
                self.instance_under_path.store(db_session)
                self.session_to_count[db_session] = 1
            return db_session
        else:
            return DBDataSession(self.engine, use_parent_instance, self._on_db_session_exit)

    def _on_db_session_exit(self, db_session):
        if db_session.use_parent_instance: 
            instance_count = self.session_to_count[db_session]
            if instance_count is not None:
                instance_count = instance_count - 1
                self.session_to_count[db_session] = instance_count
                if instance_count == 0:
                    del self.session_to_count[db_session]
                    self.instance_under_path.remove(db_session)
                    db_session.close()
        else:
            db_session.close()
