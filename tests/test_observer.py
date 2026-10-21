import enum
import unittest
import datetime

from geoalchemy2 import WKTElement

from core_lib.core_lib import CoreLib
from core_lib.observer.observer import Observer
from core_lib.observer.observer_listener import ObserverListener
from core_lib.observer.observer_registry import ObserverRegistry
from core_lib.observer.observer_decorator import Observe


class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3


class UserObserverListener(ObserverListener):
    EVENT = "EVENT"
    last_key = ""
    last_value = ""

    def update(self, key: str, value):
        UserObserverListener.last_key = key
        UserObserverListener.last_value = value


WIDGET_EVENT = 'WIDGET_EVENT'
WIDGET_OBSERVER = 'acme_widget_observer'


class RecordingObserverListener(ObserverListener):
    def __init__(self, events: list):
        self.events = events

    def update(self, key: str, value):
        self.events.append((key, value))


class FailingObserverListener(ObserverListener):
    def update(self, key: str, value):
        raise ValueError('widget listener failed')


class TestObserverWithDecorator(unittest.TestCase):
    # What the widget listener received and what the decorated methods did, in order.
    events = []

    @classmethod
    def setUpClass(cls):
        main_observer = Observer(UserObserverListener())
        CoreLib.observer_registry.register("main", main_observer)
        CoreLib.observer_registry.register(WIDGET_OBSERVER, Observer(RecordingObserverListener(cls.events)))

    @classmethod
    def tearDownClass(cls):
        CoreLib.observer_registry.unregister(WIDGET_OBSERVER)

    def setUp(self):
        TestObserverWithDecorator.events.clear()

    def test_value_param_name_sends_only_that_argument_after_the_method_ran(self):
        widget = {'name': 'widget'}

        self.assertIs(widget, self.save_widget(widget, 'urgent'))

        self.assertEqual([('saved', widget), (WIDGET_EVENT, widget)], TestObserverWithDecorator.events)

    def test_notify_after_skips_the_listener_when_the_method_raises(self):
        with self.assertRaisesRegex(ValueError, 'widget rejected'):
            self.save_widget('widget', fail=True)

        self.assertEqual([('saved', 'widget')], TestObserverWithDecorator.events)

    def test_notify_before_reaches_the_listener_first_even_when_the_method_raises(self):
        with self.assertRaisesRegex(ValueError, 'widget rejected'):
            self.save_widget_notify_before('widget', fail=True)

        self.assertEqual([(WIDGET_EVENT, 'widget'), ('saved', 'widget')], TestObserverWithDecorator.events)

    def test_unknown_observer_name_runs_the_method_and_notifies_nobody(self):
        self.assertEqual('widget', self.save_widget_to_unknown_observer('widget'))

        self.assertEqual([('saved', 'widget')], TestObserverWithDecorator.events)

    def test_observer_string(self):
        string = "hello world"
        self.notify_observer(string)
        self.assertEqual(string, UserObserverListener.last_value['var'])
        self.notify_observer("")
        self.assertEqual("", UserObserverListener.last_value['var'])
        self.notify_observer(None)
        self.assertEqual(UserObserverListener.last_value['var'], None)
        self.assertEqual("default_param", UserObserverListener.last_value['param'])

    def test_observer_number(self):
        self.notify_observer(14)
        self.assertEqual(UserObserverListener.last_value['var'], 14)
        self.notify_observer(14.0987)
        self.assertEqual(UserObserverListener.last_value['var'], 14.0987)

    def test_observer_bool(self):
        self.notify_observer(True)
        self.assertEqual(UserObserverListener.last_value['var'], True)
        self.notify_observer(False)
        self.assertEqual(UserObserverListener.last_value['var'], False)

    def test_observer_tuple(self):
        tpl = (("fruit", "apple"), ("fruit", "banana"), ("fruit", "cherry"))
        self.notify_observer(tpl)
        self.assertTupleEqual(UserObserverListener.last_value['var'], tpl)
        self.assertTupleEqual(UserObserverListener.last_value['var'][0], tpl[0])
        self.assertTupleEqual(UserObserverListener.last_value['var'][1], tpl[1])
        self.assertTupleEqual(UserObserverListener.last_value['var'][2], tpl[2])

        empty_tpl = ()
        self.notify_observer(empty_tpl)
        self.assertTupleEqual(UserObserverListener.last_value['var'], empty_tpl)

    def test_observer_list(self):
        lst = [["fruit", "apple"], ["fruit", "banana"], ["fruit", "cherry"]]
        self.notify_observer(lst)
        self.assertListEqual(UserObserverListener.last_value['var'], lst)
        self.assertListEqual(UserObserverListener.last_value['var'][0], lst[0])
        self.assertListEqual(UserObserverListener.last_value['var'][1], lst[1])
        self.assertListEqual(UserObserverListener.last_value['var'][2], lst[2])

        empty_lst = []
        self.notify_observer(empty_lst)
        self.assertListEqual(UserObserverListener.last_value['var'], empty_lst)

    def test_observer_enum(self):
        self.notify_observer(MyEnum.one)
        self.assertEqual(UserObserverListener.last_value['var'], MyEnum.one)
        self.notify_observer(MyEnum.two)
        self.assertEqual(UserObserverListener.last_value['var'], MyEnum.two)
        self.notify_observer(MyEnum.three)
        self.assertEqual(UserObserverListener.last_value['var'], MyEnum.three)

    def test_observer_object(self):
        dat = datetime.date(2022, 1, 1)
        dattime = datetime.datetime(2022, 1, 1)
        tpl = ("fruit", "apple")
        lst = ["fruit", "apple"]
        point = WKTElement('POINT(5 45)')
        dct = {
            'date': dat,
            'datetime': dattime,
            'tuple': tpl,
            'list': lst,
            'point': point,
        }
        self.notify_observer(dct)
        self.assertDictEqual(dct, UserObserverListener.last_value['var'])
        self.assertEqual(dat, UserObserverListener.last_value['var']['date'])
        self.assertEqual(dattime, UserObserverListener.last_value['var']['datetime'])
        self.assertTupleEqual(tpl, UserObserverListener.last_value['var']['tuple'])
        self.assertListEqual(lst, UserObserverListener.last_value['var']['list'])
        self.assertEqual(point, UserObserverListener.last_value['var']['point'])

        empty_dct = {}
        self.notify_observer(empty_dct)
        self.assertDictEqual(empty_dct, UserObserverListener.last_value['var'])

    @Observe(event_key=UserObserverListener.EVENT, notify_before=False, observer_name="main")
    def notify_observer(self, var, param="default_param"):
        return var

    @Observe(event_key=WIDGET_EVENT, value_param_name='widget', observer_name=WIDGET_OBSERVER)
    def save_widget(self, widget, note='', fail=False):
        TestObserverWithDecorator.events.append(('saved', widget))
        if fail:
            raise ValueError('widget rejected')
        return widget

    @Observe(event_key=WIDGET_EVENT, value_param_name='widget', observer_name=WIDGET_OBSERVER, notify_before=True)
    def save_widget_notify_before(self, widget, fail=False):
        TestObserverWithDecorator.events.append(('saved', widget))
        if fail:
            raise ValueError('widget rejected')
        return widget

    @Observe(event_key=WIDGET_EVENT, value_param_name='widget', observer_name='acme_observer_never_registered')
    def save_widget_to_unknown_observer(self, widget):
        TestObserverWithDecorator.events.append(('saved', widget))
        return widget


class TestObserverWithRegistry(unittest.TestCase):
    main_observer = Observer(UserObserverListener())

    @classmethod
    def setUpClass(cls):
        observer_factory = ObserverRegistry()
        observer_factory.register("main", TestObserverWithRegistry.main_observer)

    def test_observer_string(self):
        string = "hello world"
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, "")
        self.assertEqual("", UserObserverListener.last_value)

        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, string)
        self.assertEqual(string, UserObserverListener.last_value)

        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, None)
        self.assertEqual(None, UserObserverListener.last_value)

    def test_observer_number(self):
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, 14)
        self.assertEqual(UserObserverListener.last_value, 14)
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, 14.0987)
        self.assertEqual(UserObserverListener.last_value, 14.0987)

    def test_observer_bool(self):
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, True)
        self.assertEqual(UserObserverListener.last_value, True)
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, False)
        self.assertEqual(UserObserverListener.last_value, False)

    def test_observer_tuple(self):
        tpl = (("fruit", "apple"), ("fruit", "banana"), ("fruit", "cherry"))
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, tpl)
        self.assertTupleEqual(UserObserverListener.last_value, tpl)
        self.assertTupleEqual(UserObserverListener.last_value[0], tpl[0])
        self.assertTupleEqual(UserObserverListener.last_value[1], tpl[1])
        self.assertTupleEqual(UserObserverListener.last_value[2], tpl[2])

        empty_tpl = ()
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, empty_tpl)
        self.assertTupleEqual(UserObserverListener.last_value, empty_tpl)

    def test_observer_list(self):
        lst = [["fruit", "apple"], ["fruit", "banana"], ["fruit", "cherry"]]
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, lst)
        self.assertListEqual(UserObserverListener.last_value, lst)
        self.assertListEqual(UserObserverListener.last_value[0], lst[0])
        self.assertListEqual(UserObserverListener.last_value[1], lst[1])
        self.assertListEqual(UserObserverListener.last_value[2], lst[2])

        empty_lst = []
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, empty_lst)
        self.assertListEqual(UserObserverListener.last_value, empty_lst)

    def test_observer_enum(self):
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, MyEnum.one)
        self.assertEqual(UserObserverListener.last_value, MyEnum.one)
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, MyEnum.two)
        self.assertEqual(UserObserverListener.last_value, MyEnum.two)
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, MyEnum.three)
        self.assertEqual(UserObserverListener.last_value, MyEnum.three)

    def test_observer_object(self):
        dat = datetime.date(2022, 1, 1)
        dattime = datetime.datetime(2022, 1, 1)
        tpl = ("fruit", "apple")
        lst = ["fruit", "apple"]
        point = WKTElement('POINT(5 45)')
        dct = {
            'date': dat,
            'datetime': dattime,
            'tuple': tpl,
            'list': lst,
            'point': point,
        }
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, dct)
        self.assertDictEqual(dct, UserObserverListener.last_value)
        self.assertEqual(dat, UserObserverListener.last_value['date'])
        self.assertEqual(dattime, UserObserverListener.last_value['datetime'])
        self.assertTupleEqual(tpl, UserObserverListener.last_value['tuple'])
        self.assertListEqual(lst, UserObserverListener.last_value['list'])
        self.assertEqual(point, UserObserverListener.last_value['point'])

        empty_dct = {}
        TestObserverWithRegistry.main_observer.notify(UserObserverListener.EVENT, empty_dct)
        self.assertDictEqual(empty_dct, UserObserverListener.last_value)

    def test_detached_listener_is_no_longer_notified(self):
        detached_events = []
        attached_events = []
        detached_listener = RecordingObserverListener(detached_events)
        observer = Observer(detached_listener)
        observer.attach(RecordingObserverListener(attached_events))

        observer.detach(detached_listener)
        observer.notify(WIDGET_EVENT, 'widget')

        self.assertEqual([], detached_events)
        self.assertEqual([(WIDGET_EVENT, 'widget')], attached_events)

    def test_failing_listener_is_logged_raised_to_the_caller_and_stops_later_listeners(self):
        later_events = []
        observer = Observer(FailingObserverListener())
        observer.attach(RecordingObserverListener(later_events))

        with self.assertLogs('core_lib.observer.observer', level='ERROR') as logs:
            with self.assertRaisesRegex(ValueError, 'widget listener failed'):
                observer.notify(WIDGET_EVENT, 'widget')

        self.assertEqual(1, len(logs.records))
        self.assertEqual('error while Observer.notify on key: `WIDGET_EVENT`', logs.records[0].getMessage())
        self.assertEqual([], later_events)
