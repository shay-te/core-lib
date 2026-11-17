import threading

from core_lib.connection.connection import Connection

EVENT_ENTER = 'enter'
EVENT_FLUSH = 'flush'
EVENT_EXIT = 'exit'
NO_ERROR = (None, None, None)  # the exit arguments of a clean end: a commit


class RecordingConnection(Connection):
    """A third-party connection that records every lifecycle call, with the calling thread.

    `calls` holds `(event, thread_id, exit_arguments)` for this connection; `journal` is shared
    with other connections, so a test can read the order across factories as `(connection, event,
    exit_arguments)`. It fails its commit (`__exit__` with no exception) or its rollback when told."""

    def __init__(self, journal: list, commit_error: BaseException = None, rollback_error: BaseException = None):
        self.journal = journal
        self.commit_error = commit_error
        self.rollback_error = rollback_error
        self.resource = object()
        self.calls = []

    def __enter__(self):
        self._record(EVENT_ENTER, None)
        return self.resource

    def flush(self):
        self._record(EVENT_FLUSH, None)

    def __exit__(self, exec_type, exec_value, traceback):
        self._record(EVENT_EXIT, (exec_type, exec_value, traceback))
        if exec_type is None and self.commit_error is not None:
            raise self.commit_error
        if exec_type is not None and self.rollback_error is not None:
            raise self.rollback_error
        return False

    def events(self) -> list:
        return [call[0] for call in self.calls]

    def exit_arguments(self) -> list:
        return [call[2] for call in self.calls if call[0] == EVENT_EXIT]

    def thread_ids(self) -> set:
        return {call[1] for call in self.calls}

    def _record(self, event: str, exit_arguments):
        self.calls.append((event, threading.get_ident(), exit_arguments))
        self.journal.append((self, event, exit_arguments))
