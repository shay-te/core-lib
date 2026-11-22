import threading

from sqlalchemy import event

EVENT_COMMIT = 'commit'
EVENT_ROLLBACK = 'rollback'
EVENT_CHECKOUT = 'checkout'
EVENT_CHECKIN = 'checkin'


class EngineEventCounter(object):
    """Counts COMMITs, ROLLBACKs and pool checkouts / checkins on one engine while the `with`
    block runs, from every thread; the listeners are removed when it ends."""

    def __init__(self, engine):
        self._engine = engine
        self._lock = threading.Lock()
        self._counts = {EVENT_COMMIT: 0, EVENT_ROLLBACK: 0, EVENT_CHECKOUT: 0, EVENT_CHECKIN: 0}
        self._listeners = [(name, self._listener_for(name)) for name in self._counts]

    @property
    def commits(self) -> int:
        return self._counts[EVENT_COMMIT]

    @property
    def rollbacks(self) -> int:
        return self._counts[EVENT_ROLLBACK]

    @property
    def checkouts(self) -> int:
        return self._counts[EVENT_CHECKOUT]

    @property
    def checkins(self) -> int:
        return self._counts[EVENT_CHECKIN]

    def __enter__(self):
        for name, listener in self._listeners:
            event.listen(self._engine, name, listener)
        return self

    def __exit__(self, exec_type, exec_value, traceback):
        for name, listener in self._listeners:
            event.remove(self._engine, name, listener)
        return False

    def _listener_for(self, name: str):
        def count(*args):
            with self._lock:
                self._counts[name] += 1
        return count
