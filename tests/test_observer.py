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


class TestObserverWithDecorator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        main_observer = Observer(UserObserverListener())
        CoreLib.observer_registry.register("main", main_observer)

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
