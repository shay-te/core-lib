"""Property-based tests for observer.observer.Observer."""
import unittest

from hypothesis import given, strategies as st

from core_lib.observer.observer import Observer
from core_lib.observer.observer_listener import ObserverListener
from tests.hypothesis_tests._settings import SETTINGS


class _Recorder(ObserverListener):
    def __init__(self):
        self.events = []

    def update(self, key, value):
        self.events.append((key, value))


class TestObserverProperties(unittest.TestCase):
    @given(n=st.integers(min_value=0, max_value=15))
    @SETTINGS
    def test_attach_n_listeners_then_notify_invokes_each(self, n):
        obs = Observer(listener_type=_Recorder)
        listeners = [_Recorder() for _ in range(n)]
        for l in listeners:
            obs.attach(l)
        obs.notify('k', 'v')
        for l in listeners:
            self.assertEqual(l.events, [('k', 'v')])

    @given(n=st.integers(min_value=1, max_value=10))
    @SETTINGS
    def test_detach_listener_no_longer_invoked(self, n):
        obs = Observer(listener_type=_Recorder)
        listeners = [_Recorder() for _ in range(n)]
        for l in listeners:
            obs.attach(l)
        target = listeners[0]
        obs.detach(target)
        obs.notify('k', 'v')
        self.assertEqual(target.events, [])
        for other in listeners[1:]:
            self.assertEqual(other.events, [('k', 'v')])

    @given(
        events=st.lists(
            st.tuples(st.text(min_size=1, max_size=5), st.integers()),
            min_size=1,
            max_size=15,
        )
    )
    @SETTINGS
    def test_notify_sequence_recorded_in_order(self, events):
        obs = Observer(listener_type=_Recorder)
        listener = _Recorder()
        obs.attach(listener)
        for k, v in events:
            obs.notify(k, v)
        self.assertEqual(listener.events, events)
