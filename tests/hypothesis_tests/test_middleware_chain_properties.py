"""Property-based tests for middleware.middleware_chain.MiddlewareChain."""
import unittest

from hypothesis import given, strategies as st

from core_lib.middleware.middleware import Middleware
from core_lib.middleware.middleware_chain import MiddlewareChain
from tests.hypothesis_tests._settings import SETTINGS


class _Recorder(Middleware):
    def __init__(self, label):
        self.label = label
        self.calls = []

    def handle(self, context):
        self.calls.append(context)


class TestMiddlewareChainProperties(unittest.TestCase):
    @given(n=st.integers(min_value=0, max_value=20))
    @SETTINGS
    def test_add_n_middlewares_then_execute_invokes_each_once(self, n):
        chain = MiddlewareChain()
        mws = [_Recorder(i) for i in range(n)]
        for m in mws:
            chain.add(m)
        chain.execute({'ctx': 'value'})
        for m in mws:
            self.assertEqual(m.calls, [{'ctx': 'value'}])

    @given(n=st.integers(min_value=0, max_value=20))
    @SETTINGS
    def test_clear_yields_no_invocations(self, n):
        chain = MiddlewareChain()
        mws = [_Recorder(i) for i in range(n)]
        for m in mws:
            chain.add(m)
        chain.clear()
        chain.execute({'ctx': 'value'})
        for m in mws:
            self.assertEqual(m.calls, [])

    @given(n=st.integers(min_value=1, max_value=10))
    @SETTINGS
    def test_remove_then_execute_skips_removed(self, n):
        chain = MiddlewareChain()
        mws = [_Recorder(i) for i in range(n)]
        for m in mws:
            chain.add(m)
        # Remove the first one
        target = mws[0]
        chain.remove(target)
        chain.execute({})
        self.assertEqual(target.calls, [])
        for other in mws[1:]:
            self.assertEqual(other.calls, [{}])

    @given(
        contexts=st.lists(
            st.dictionaries(st.text(min_size=1, max_size=5), st.integers(), max_size=5),
            min_size=1,
            max_size=10,
        )
    )
    @SETTINGS
    def test_execute_with_many_contexts_records_each(self, contexts):
        chain = MiddlewareChain()
        recorder = _Recorder('r')
        chain.add(recorder)
        for ctx in contexts:
            chain.execute(ctx)
        self.assertEqual(recorder.calls, contexts)
