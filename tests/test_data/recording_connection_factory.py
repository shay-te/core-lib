from core_lib.connection.transactional_connection_factory import TransactionalConnectionFactory
from tests.test_data.recording_connection import RecordingConnection


class RecordingConnectionFactory(TransactionalConnectionFactory):
    """A transactional connection factory, like `SqlAlchemyConnectionFactory`. `created` keeps every
    connection it built; `connect_attempts` counts every attempt to build one."""

    def __init__(self, journal: list = None, commit_error: BaseException = None,
                 rollback_error: BaseException = None, create_error: BaseException = None):
        self.journal = [] if journal is None else journal
        self.commit_error = commit_error
        self.rollback_error = rollback_error
        self.create_error = create_error
        self.created = []
        self.connect_attempts = 0

    def identity(self) -> str:
        return 'recording {}'.format(id(self))   # every recording factory is its own: none share a connection

    def create_connection(self) -> RecordingConnection:
        self.connect_attempts += 1
        if self.create_error is not None:
            raise self.create_error
        connection = RecordingConnection(self.journal, self.commit_error, self.rollback_error)
        self.created.append(connection)
        return connection
