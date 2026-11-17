from core_lib.connection.connection_factory import ConnectionFactory
from tests.test_data.recording_connection import RecordingConnection


class RecordingConnectionFactory(ConnectionFactory):
    """A factory written the way a third-party library would: its `get()` builds a new
    `RecordingConnection` per call, kept in `created`; `create_calls` holds each call's arguments."""

    def __init__(self, journal: list = None, commit_error: BaseException = None,
                 rollback_error: BaseException = None, create_error: BaseException = None):
        self.journal = [] if journal is None else journal
        self.commit_error = commit_error
        self.rollback_error = rollback_error
        self.create_error = create_error
        self.created = []
        self.create_calls = []

    def get(self, *args, **kwargs) -> RecordingConnection:
        self.create_calls.append((args, kwargs))
        if self.create_error is not None:
            raise self.create_error
        connection = RecordingConnection(self.journal, self.commit_error, self.rollback_error)
        self.created.append(connection)
        return connection
